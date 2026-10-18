"""Phase 1 feature extraction v2 (closure B1-B3, PHASE1_IMPLEMENTATION_CLOSURE_V1). Supersedes extract_features_v1_superseded.py.
Embeds ONE frozen 224x224 letterbox crop (pad 114, INTER_AREA) per retained-tracklet detection listed in EXTRACTION_FRAME_MANIFEST_V1.csv, for one pinned backbone.
Frames are the sorted ACTUAL keys of the frozen detection dict (ascending; sparse stride-3 keys); nothing is synthesised, the detector is never re-run, frozen detections are never modified.
Backbone adapters (explicit, pinned; each strict-loads and refuses partial loads):
  mobileclip_b    : V0.5 TorchScript loader, input [0,1] RGB, NO mean/std normalisation.
  dinov2_vits14   : official facebookresearch/dinov2 code (commit in registry), no registers, strict load, 224x224 crop, ImageNet mean/std, eval, CLS embedding after final norm (384-d).
  osnet_x1_0      : official deep-person-reid osnet.py, strict load of the MSMT17 combineall checkpoint, OSNET_INPUT_CLOSURE_V1: PIL.Image.fromarray(crop) -> resize (W=128,H=256) PIL BILINEAR -> ToTensor [0,1] -> ImageNet mean/std, eval, 512-d pre-classifier feature.
All outputs are L2-normalised here. This module must not run on experimental footage before bake-off authorisation (main() calls the fail-closed guard)."""
import sys,os,json,hashlib,argparse,time,csv,importlib.util
import numpy as np,cv2,torch
CROP=dict(size=224,pad=114,min_side=24)
IMNET_MEAN=(0.485,0.456,0.406); IMNET_STD=(0.229,0.224,0.225)
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
# ---------- pure preprocessing (RGB uint8 HxWx3 -> float tensor NCHW), unit-testable ----------
def prep_unit(arrs):                      # mobileclip_b: [0,1], no normalisation
    return torch.from_numpy(np.stack(arrs)).permute(0,3,1,2).float()/255.0
def prep_imagenet(arrs):                  # dinov2_vits14: 224x224 unchanged, ImageNet mean/std
    x=prep_unit(arrs); return (x-torch.tensor(IMNET_MEAN).view(1,3,1,1))/torch.tensor(IMNET_STD).view(1,3,1,1)
def prep_osnet(arrs):                     # OSNET_INPUT_CLOSURE_V1
    from PIL import Image
    out=[]
    for a in arrs:
        im=Image.fromarray(a).resize((128,256),Image.BILINEAR)          # (W,H); anisotropic; official test-time interpolation
        out.append(np.asarray(im,dtype=np.uint8))
    x=torch.from_numpy(np.stack(out)).permute(0,3,1,2).float()/255.0
    return (x-torch.tensor(IMNET_MEAN).view(1,3,1,1))/torch.tensor(IMNET_STD).view(1,3,1,1)
PREP={"mobileclip_b":prep_unit,"dinov2_vits14":prep_imagenet,"osnet_x1_0":prep_osnet}
EXPECT_DIM={"dinov2_vits14":384,"osnet_x1_0":512}
def load_backbone(kind,weights,code_dir=None,v05_src="/home/claude/proj/holdout1/src"):
    if kind=="mobileclip_b":
        sys.path.insert(0,v05_src); sys.path.insert(0,os.path.join(v05_src,"third_party")); import embed_crops as EC; return EC.load_encoder(weights)
    sd=torch.load(weights,map_location="cpu",weights_only=True); sd=sd.get("state_dict",sd) if isinstance(sd,dict) else sd
    sd={(k[7:] if k.startswith("module.") else k):v for k,v in sd.items()}
    if kind=="dinov2_vits14":
        sys.path.insert(0,code_dir); from dinov2.hub.backbones import dinov2_vits14
        m=dinov2_vits14(pretrained=False); m.load_state_dict(sd,strict=True)
        if getattr(m,"num_register_tokens",0)!=0: raise SystemExit("register tokens present: forbidden")
    elif kind=="osnet_x1_0":
        spec=importlib.util.spec_from_file_location("osnet_official",os.path.join(code_dir,"torchreid","models","osnet.py")); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        ncls=int(sd["classifier.weight"].shape[0]); m=mod.osnet_x1_0(num_classes=ncls,pretrained=False); m.load_state_dict(sd,strict=True)
    else: raise SystemExit("unknown backbone "+kind)
    return m.eval()
@torch.no_grad()
def embed(m,kind,arrs,bs=16):
    out=[]
    for i in range(0,len(arrs),bs):
        e=m(PREP[kind](arrs[i:i+bs])).float()
        if kind in EXPECT_DIM and e.shape[-1]!=EXPECT_DIM[kind]: raise SystemExit(f"unexpected embedding dim {e.shape} for {kind}")
        out.append((e/e.norm(dim=1,keepdim=True).clamp_min(1e-12)).numpy())
    return np.concatenate(out)
def manifest_rows(path):
    """Reads the frozen extraction-frame manifest; returns rows grouped by clip in ascending (frame,det) order."""
    rows=list(csv.DictReader(open(path))); out={}
    for r in rows: out.setdefault(r["clip"],[]).append((int(r["frame"]),int(r["det"]),r["tid"],int(r["crop_ok"])))
    for c in out: out[c].sort(key=lambda x:(x[0],x[1]))
    return out
def extract_clip(video,dets,rows,m,kind,bs=16):
    """Sparse-safe (B1): visits only manifest frames, ascending, using dets[frame] for keys that exist; never indexes missing keys."""
    need={}
    for f,j,tid,ok in rows: need.setdefault(f,[]).append((j,tid,ok))
    frames=sorted(need); cap=cv2.VideoCapture(video); K=[];A=[];t=0;pos=-1
    for f in frames:
        if f not in dets: raise SystemExit(f"manifest frame {f} absent from frozen detections")
        while pos<f:
            ok,im=cap.read(); pos+=1
            if not ok: raise SystemExit("video ended before manifest frame "+str(f))
        for j,tid,okc in need[f]:
            c=crop(im,dets[f]["box"][j])
            if c is None:
                if okc: raise SystemExit("crop failed but manifest said crop_ok")
                continue
            K.append((f,j)); A.append(c)
    E=embed(m,kind,A,bs); return np.array(K,np.int32),E
def cache_key(video,dets,manifest,kind,weights):
    return hashlib.sha256("|".join([sha(video),sha(dets),sha(manifest),json.dumps(CROP,sort_keys=True),kind,sha(weights)]).encode()).hexdigest()[:16]
def main():
    ap=argparse.ArgumentParser(); [ap.add_argument(x) for x in ("--clip","--video","--dets","--manifest","--backbone","--weights","--code_dir","--out_dir","--frozen_dir")]; a=ap.parse_args()
    from authorization_guard import require_bakeoff_authorization; require_bakeoff_authorization(a.frozen_dir)
    import pickle
    torch.set_num_threads(os.cpu_count() or 2); torch.manual_seed(0); key=cache_key(a.video,a.dets,a.manifest,a.backbone,a.weights); out=os.path.join(a.out_dir,f"feat_{a.backbone}_{a.clip}_{key}.npz")
    if os.path.exists(out): print("cache hit",out); return
    rows=manifest_rows(a.manifest)[a.clip]; dets=pickle.load(open(a.dets,"rb")); m=load_backbone(a.backbone,a.weights,a.code_dir); t0=time.time()
    K,E=extract_clip(a.video,dets,rows,m,a.backbone); os.makedirs(a.out_dir,exist_ok=True)
    np.savez_compressed(out,frame=K[:,0],det=K[:,1],emb=E,meta=json.dumps(dict(video_sha=sha(a.video),backbone=a.backbone,weights_sha=sha(a.weights),manifest_sha=sha(a.manifest),crop=CROP,wall_s=round(time.time()-t0,1))))
    print("wrote",out,len(K),"crops")
if __name__=="__main__": main()
