"""Deterministic tracklet construction from cached pose detections (frozen PREPROCESSING_V1). Greedy IoU association inside shots; no identity model, no labels.
Outputs frozen/tracklets/<clip>.json: list of tracklets {tid, clip, shot, frames, boxes, mean_h, n_det}. Only gated detections (conf>=0.3, box height>=50 px at 360p) are used; tracklets need >=5 detections."""
import sys,os,json,pickle,numpy as np
CONF=0.3; MINH=50; IOU=0.3; MAXGAP=2; MINDET=5; STRIDE=3
SHOTFILE={"b1_hbk_raw_20050502":"batch1/sheets/hbk_superkick_raw_20050502.cuts.txt","b1_orton_rollins_wm31":"batch1/sheets/orton_rollins_wm31.cuts.txt","b1_rock_hhh_judgmentday2000":"batch1/sheets/rock_hhh_judgmentday2000.cuts.txt","b2_batch2_clip_condensed":"batch2/sheets/b2_batch2_clip_condensed.cuts.txt","b2_videoplayback_2":"batch2/sheets/b2_videoplayback_2.cuts.txt","b2_videoplayback_5":"batch2/sheets/b2_videoplayback_5.cuts.txt"}
LIMIT={"b2_videoplayback_2":1934}
def shots(clip,nframes):
    t=sorted(float(x) for x in open(SHOTFILE[clip]).read().split()); d=[]
    for x in t:
        if not d or x-d[-1]>=0.25: d.append(x)
    lim=min(nframes,LIMIT.get(clip,nframes)); b=[0]+[int(round(x*30)) for x in d if int(round(x*30))<lim]+[lim]; return [(b[i],b[i+1]) for i in range(len(b)-1)]
def iou(a,b):
    x1=max(a[0],b[0]);y1=max(a[1],b[1]);x2=min(a[2],b[2]);y2=min(a[3],b[3]); i=max(0,x2-x1)*max(0,y2-y1); u=(a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-i; return i/u if u>0 else 0
def build(clip,dets,nframes):
    out=[];tid=0
    for si,(s,e) in enumerate(shots(clip,nframes)):
        active=[];done=[]
        for f in range(s,e):
            if f%STRIDE or f not in dets: continue
            d=dets[f]; cand=[(d["box"][j],j) for j in range(len(d["conf"])) if d["conf"][j]>=CONF and (d["box"][j][3]-d["box"][j][1])>=MINH]
            pairs=sorted(((iou(a["boxes"][-1],b),ai,bi) for ai,a in enumerate(active) for bi,(b,_) in enumerate(cand)),reverse=True); ua=set();ub=set()
            for v,ai,bi in pairs:
                if v<IOU or ai in ua or bi in ub: continue
                ua.add(ai);ub.add(bi);active[ai]["frames"].append(f);active[ai]["boxes"].append([float(x) for x in cand[bi][0]]);active[ai]["dets"].append(cand[bi][1]);active[ai]["last"]=f
            for bi,(b,j) in enumerate(cand):
                if bi not in ub: active.append(dict(frames=[f],boxes=[[float(x) for x in b]],dets=[j],last=f))
            keep=[]
            for a in active:
                (keep if f-a["last"]<=MAXGAP*STRIDE else done).append(a)
            active=keep
        for a in active+done:
            if len(a["frames"])>=MINDET:
                hs=[b[3]-b[1] for b in a["boxes"]]; out.append(dict(tid=f"{clip}:s{si}:t{tid}",clip=clip,shot=si,shot_frames=[s,e],frames=a["frames"],boxes=a["boxes"],mean_h=float(np.mean(hs)),n_det=len(a["frames"]))); tid+=1
    return out
if __name__=="__main__":
    clip=sys.argv[1]; nfr=int(sys.argv[2]); dets=pickle.load(open(f"frozen/dets/dets_{clip}.pkl","rb")); T=build(clip,dets,nfr); os.makedirs("frozen/tracklets",exist_ok=True)
    json.dump(T,open(f"frozen/tracklets/{clip}.json","w")); print(clip,"processed frames",len(dets),"tracklets",len(T),"shots with tracklets",len({t["shot"] for t in T}))
