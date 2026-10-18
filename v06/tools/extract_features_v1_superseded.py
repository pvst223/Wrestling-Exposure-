"""Hash-keyed, resumable feature extraction: ONE crop per gated candidate (detection box, letterboxed 224x224 grey 114, same crop recipe as V0.5 crop224), any registered backbone.
Cache key = sha256(video_sha, dets_sha, crop_params, backbone_id, backbone_weights_sha). Existing cache with the same key is reused (no recompute).
Backbone adapters: 'mobileclip_b' (local TorchScript weights via V0.5 loader) and 'timm_local' (a timm/torchvision model whose weights file the user supplies; used for person-reID/DINOv2 when available).
This script is scaffolding: it is not run on any footage until the preregistration is frozen."""
import sys,os,json,pickle,hashlib,argparse,time
import numpy as np,cv2,torch
CROP=dict(size=224,pad=114,min_side=24,det_conf_gate=0.3,min_box_h=50)
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()
def crop(im,box,p=CROP):
    x1,y1,x2,y2=[int(round(v)) for v in box]; x1=max(0,x1);y1=max(0,y1);x2=min(im.shape[1],x2);y2=min(im.shape[0],y2)
    if x2-x1<p["min_side"] or y2-y1<p["min_side"]: return None
    c=im[y1:y2,x1:x2]; h,w=c.shape[:2]; s=max(h,w); pad=np.zeros((s,s,3),np.uint8)+p["pad"]; pad[(s-h)//2:(s-h)//2+h,(s-w)//2:(s-w)//2+w]=c
    return cv2.cvtColor(cv2.resize(pad,(p["size"],p["size"]),interpolation=cv2.INTER_AREA),cv2.COLOR_BGR2RGB)
def load_backbone(kind,weights,arch=None,v05_src="/home/claude/proj/holdout1/src"):
    if kind=="mobileclip_b":
        sys.path.insert(0,v05_src); sys.path.insert(0,os.path.join(v05_src,"third_party")); import embed_crops as EC; m=EC.load_encoder(weights); mean=None
    elif kind=="timm_local":
        import timm; m=timm.create_model(arch,pretrained=False,num_classes=0); sd=torch.load(weights,map_location="cpu"); r=m.load_state_dict(sd.get("state_dict",sd),strict=False); bad=[k for k in r.missing_keys]; 
        if bad: raise SystemExit("WEIGHTS DO NOT MATCH ARCH (missing keys, refusing silent partial load): "+str(bad[:5])+" ... n_missing=%d n_unexpected=%d"%(len(bad),len(r.unexpected_keys)))
        m.eval(); mean=(0.485,0.456,0.406)
    else: raise SystemExit("unknown backbone "+kind)
    return m,mean
@torch.no_grad()
def embed(m,mean,arrs,bs=16):
    out=[]
    for i in range(0,len(arrs),bs):
        x=torch.from_numpy(np.stack(arrs[i:i+bs])).permute(0,3,1,2).float()/255.0
        if mean is not None: x=(x-torch.tensor(mean).view(1,3,1,1))/torch.tensor((0.229,0.224,0.225)).view(1,3,1,1)
        e=m(x).float(); out.append((e/e.norm(dim=1,keepdim=True).clamp_min(1e-12)).numpy())
    return np.concatenate(out)
def cache_key(video,dets,backbone_id,weights):
    return hashlib.sha256("|".join([sha(video),sha(dets),json.dumps(CROP,sort_keys=True),backbone_id,sha(weights)]).encode()).hexdigest()[:16]
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--video");ap.add_argument("--dets");ap.add_argument("--backbone");ap.add_argument("--weights");ap.add_argument("--arch");ap.add_argument("--out_dir");ap.add_argument("--stride",type=int,default=1);a=ap.parse_args()
    torch.set_num_threads(os.cpu_count() or 2); torch.manual_seed(0); key=cache_key(a.video,a.dets,a.backbone,a.weights); out=os.path.join(a.out_dir,f"feat_{a.backbone}_{key}.npz")
    if os.path.exists(out): print("cache hit",out); return
    dets=pickle.load(open(a.dets,"rb")); m,mean=load_backbone(a.backbone,a.weights,a.arch); cap=cv2.VideoCapture(a.video); K=[];A=[];t0=time.time()
    for t in range(len(dets)):
        ok,im=cap.read()
        if not ok: break
        if t%a.stride: continue
        d=dets[t]
        for j in range(len(d["conf"])):
            b=d["box"][j]
            if d["conf"][j]>=CROP["det_conf_gate"] and (b[3]-b[1])>=CROP["min_box_h"]:
                c=crop(im,b)
                if c is not None: K.append((t,j)); A.append(c)
    E=embed(m,mean,A); K=np.array(K,np.int32); os.makedirs(a.out_dir,exist_ok=True)
    np.savez_compressed(out,frame=K[:,0],det=K[:,1],emb=E,meta=json.dumps(dict(video_sha=sha(a.video),backbone=a.backbone,weights_sha=sha(a.weights),crop=CROP,stride=a.stride,wall_s=round(time.time()-t0,1))))
    print("wrote",out,len(K),"crops",round(time.time()-t0),"s")
if __name__=="__main__": main()
