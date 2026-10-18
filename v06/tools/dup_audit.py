"""Duplicate / overlapping-footage audit (deterministic, model-free). dHash (9x8 gray) on normalized frames sampled at 1 fps (usable frames only) per clip.
 - cross-clip: for every pair of clips, min Hamming distance between any frame pair; reports pairs with distance <= 6 (near-duplicate frames) -> overlapping source footage.
 - within-clip: pairs of frames >= 3 s apart with distance <= 6 -> repeated footage (possible replay).
Limit: replays shown from another angle/slow motion/with graphics are NOT reliably detected by this method."""
import cv2,numpy as np,glob,os,json,itertools,sys
LIMIT={"b2_videoplayback_2":1934}
def dh(im):
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY); g=cv2.resize(g,(9,8),interpolation=cv2.INTER_AREA); return (g[:,1:]>g[:,:-1]).flatten()
H={};T={}
for p in sorted(glob.glob("frozen/norm/*.mp4")):
    c=os.path.basename(p)[:-4]; cap=cv2.VideoCapture(p); n=int(cap.get(7)); lim=min(n,LIMIT.get(c,n)); hs=[];ts=[]
    for i in range(0,lim,30):
        cap.set(1,i); ok,im=cap.read()
        if ok:
            if cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).std()<12: continue   # skip black/uniform frames (hash is uninformative)
            h=dh(im)
            hs.append(h); ts.append(i/30)
    H[c]=np.array(hs); T[c]=np.array(ts)
res={"cross_clip":[],"within_clip":[]}
for a,b in itertools.combinations(H,2):
    d=(H[a][:,None,:]!=H[b][None,:,:]).sum(2); m=int(d.min()); i,j=np.unravel_index(d.argmin(),d.shape); res["cross_clip"].append(dict(a=a,b=b,min_hamming=m,t_a=float(T[a][i]),t_b=float(T[b][j]),near_duplicate=m<=6))
for c in H:
    d=(H[c][:,None,:]!=H[c][None,:,:]).sum(2); n=len(H[c]); cnt=0;best=64;prs=[]
    for i in range(n):
        for j in range(i+3,n):
            if d[i,j]<=6: cnt+=1; prs.append((float(T[c][i]),float(T[c][j]),int(d[i,j])))
            best=min(best,int(d[i,j]))
    res["within_clip"].append(dict(clip=c,frames_sampled=n,pairs_le6_gap_ge3s=cnt,min_hamming=best,pairs=prs))
json.dump(res,open("frozen/dup_audit.json","w"),indent=1)
for r in res["cross_clip"]: print("X",r["a"],r["b"],r["min_hamming"],"NEAR-DUP" if r["near_duplicate"] else "")
for r in res["within_clip"]: print("W",r["clip"],r["frames_sampled"],r["pairs_le6_gap_ge3s"],r["min_hamming"],r["pairs"])
