"""Diagnostic report generator (ANALYSIS ONLY: reads outputs, changes nothing).
usage: diagnose.py tracking.csv landmarks_raw.csv cuts.json raw_detections.pkl report.md failure_frames.csv"""
import sys, json, pickle, pandas as pd, numpy as np
csv, lmcsv, cutsj, dpkl, out, failcsv = sys.argv[1:7]
df=pd.read_csv(csv); lm=pd.read_csv(lmcsv); cuts=json.load(open(cutsj)); dets=pickle.load(open(dpkl,"rb"))
N=len(df); fps=30000/1001; T=lambda f: f"{f/fps:.2f}s"; TRACKED=["MEASURED","PARTIAL"]
fail=[]  # (frame, reason)
L=[]; add=L.append
def pct(n): return f"{100*n/N:.1f}% ({n}/{N})"
def runs(mask,minlen=1):
    r=[];s=None
    for i,v in enumerate(mask):
        if v and s is None: s=i
        if s is not None and (not v or i==len(mask)-1):
            e=i if v else i-1
            if e-s+1>=minlen: r.append((s,e))
            s=None
    return r
add("# V0.1 Baseline Diagnostic Report (frozen algorithm)\n")
add("> Pose-derived, **unvalidated** 2D pixel-space estimates. No ground truth exists for this clip, so nothing below measures accuracy; it measures pipeline behaviour and flags suspicious output. No distance/velocity/acceleration/exposure variables are computed.\n")
add("## 1. Frame status distribution")
for s in ["MEASURED","PARTIAL","PREDICTED","UNRESOLVED"]: add(f"- **{s}**: {pct(int((df.status==s).sum()))}")
add(f"- Frames with a Cena identity assigned (any status): {pct(int((df.identity!='unassigned').sum()))}")
add(f"- Frames with NO candidate accepted as Cena (identity 'unassigned' or predicted): {pct(int((df.identity_basis.isin(['none','prediction'])).sum()))}")
add("\n## 2. Camera cuts")
cl=[c['frame'] for c in cuts['cuts']]
add(f"- {len(cl)} detected cuts (0-based first frame of new shot): "+", ".join(f"{c} ({T(c)})" for c in cl))
add(f"- Photometric events judged NOT cuts: {[p['frame'] for p in cuts['photometric_events']]}")
add("- Method: HSV-hist + pixel-difference candidates, then ORB/RANSAC background registration; NOT validated against a human cut list. Least certain: 434, 1062/1070 (adjacent events, pan/zoom vs cut).")
add("\n## 3. Per camera-segment status")
for k,g in df.groupby("camera_segment"):
    f0,f1=int(g.frame.min()),int(g.frame.max()); vc=g.status.value_counts(normalize=True)
    add(f"- seg {k:2d} f{f0}-{f1} ({T(f0)}-{T(f1)}, {len(g)} fr): MEAS {vc.get('MEASURED',0):.0%} PART {vc.get('PARTIAL',0):.0%} PRED {vc.get('PREDICTED',0):.0%} UNRES {vc.get('UNRESOLVED',0):.0%}")
add("\n## 4. Reacquisition latency after each cut (and video start)")
add("Latency = frames from the first frame of a shot until the first MEASURED/PARTIAL frame in that shot. The tracker resets spatial state at every cut, so acquisition after a cut relies on denim appearance only.")
starts=[0]+cl; ends=[c-1 for c in cl]+[N-1]
for a,b in zip(starts,ends):
    g=df[(df.frame>=a)&(df.frame<=b)]; tr=g[g.status.isin(TRACKED)]
    prev_tracked = (a>0) and df.loc[a-1,"status"] in TRACKED+["PREDICTED"]
    if len(tr)==0: add(f"- shot f{a}-{b}: **never acquired** in {len(g)} frames"); fail.append((a,"shot_never_acquired")); continue
    lat=int(tr.frame.min())-a; add(f"- shot f{a}-{b}: first tracked frame f{int(tr.frame.min())}, latency {lat} fr ({lat/fps:.2f}s); tracked {len(tr)}/{len(g)} fr; previous shot ended {'tracked/predicted' if prev_tracked else 'untracked'}")
    if lat>=10: fail.append((a,f"slow_reacquisition_{lat}fr"))
add("\n## 5. Tracking-loss events (within a shot, after having been tracked)")
add("Loss = run of non-tracked frames (PREDICTED/UNRESOLVED) that follows a MEASURED/PARTIAL frame in the same camera segment. 'Recovery' = next tracked frame in that segment.")
nloss=0
for k,g in df.groupby("camera_segment"):
    g=g.reset_index(drop=True); nt=~g.status.isin(TRACKED).values; seen=False
    for a,b in runs(nt):
        seen=g.status.iloc[:a].isin(TRACKED).any()
        if not seen: continue
        nloss+=1; fa,fb=int(g.frame[a]),int(g.frame[b]); rec = b+1<len(g)
        add(f"- f{fa}-{fb} ({T(fa)}-{T(fb)}, {fb-fa+1} fr): {'recovered at f'+str(int(g.frame[b+1])) if rec else 'segment ended without recovery'}; statuses {g.status.iloc[a:b+1].value_counts().to_dict()}")
        if fb-fa+1>=5: fail.append((fa,f"tracking_loss_{fb-fa+1}fr"))
if nloss==0: add("- none")
add(f"- Total loss events: {nloss}")
add("\n## 6. Suspected identity problems (heuristic flags only — NOT confirmed switches)")
fl=df["flags"].fillna("")
for name in ["jump","ambiguous"]:
    ff=df[fl.str.contains(name)].frame.tolist(); add(f"- flag '{name}': {len(ff)} frames: {ff[:60]}{' ...' if len(ff)>60 else ''}"); [fail.append((f,f"flag_{name}")) for f in ff]
cont=df[df.identity_basis=='continuity']; add(f"- identity held by continuity only (weak colour evidence): {len(cont)} frames; runs: {[(a,b) for a,b in runs((df.identity_basis=='continuity').values,3)]}")
add("- Identity = denim-shorts colour + continuity. It cannot distinguish Cena from another person wearing blue denim, and cannot verify identity when shorts are out of view (close-ups). Manual visual spot-check results are in `audit_manual_spotcheck.md`.")
# overlap analysis
sel=lm.drop_duplicates("frame").set_index("frame").selected_det_index.to_dict(); ov=np.zeros(N)
def _iou(a,b):
    x1,y1=max(a[0],b[0]),max(a[1],b[1]); x2,y2=min(a[2],b[2]),min(a[3],b[3]); i=max(0,x2-x1)*max(0,y2-y1)
    u=(a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-i; return i/u if u>0 else 0
for t,j in sel.items():
    d=dets[t]; b=d["box"][j]
    for k in range(len(d["conf"])):
        if k!=j and d["conf"][k]>=0.30 and (d["box"][k][3]-d["box"][k][1])>=50: ov[t]=max(ov[t],_iou(b,d["box"][k]))
df["max_overlap_iou"]=ov
add("\n## 7. Overlap / grappling sequences (selected box overlaps another person box, IoU>=0.30; runs>=5 fr)")
orr=runs(ov>=0.30,5)
for a,b in orr:
    g=df[(df.frame>=a)&(df.frame<=b)]; add(f"- f{a}-{b} ({T(a)}-{T(b)}): status {g.status.value_counts().to_dict()}, mean conf {g.tracking_confidence.mean():.2f}, flags {int((g["flags"].fillna('')!='').sum())}"); fail.append((a,f"overlap_sequence_{b-a+1}fr"))
if not orr: add("- none")
add(f"- Frames with overlap IoU>=0.30: {int((ov>=0.30).sum())}; of which labelled MEASURED: {int(((ov>=0.30)&(df.status=='MEASURED')).sum())} (MEASURED during heavy overlap is suspect: occluded joints may be inferred)")
add("\n## 8. Landmark availability / failure pattern (selected-Cena frames; 'available' = keypoint conf>=0.5)")
nsel=lm.frame.nunique(); add(f"- Frames with a selected Cena detection: {nsel}")
av=lm.groupby("landmark").agg(avail=("used_for_status_com","mean"),drawn=("drawn_in_overlay","mean"),mean_conf=("keypoint_conf","mean")).sort_values("avail")
for k,r in av.iterrows(): add(f"- {k:11s}: available {r.avail:.0%}, shown in overlay (>=0.70) {r.drawn:.0%}, mean conf {r.mean_conf:.2f}")
add("- Pattern by segment type is in the CSV (`missing_landmarks`, `observed_segments`).")
add("\n## 9. Anatomically / geometrically suspicious pose predictions (2D heuristics; suspicious, not proof)")
BONES=[(5,7,"L_upper_arm"),(7,9,"L_forearm"),(6,8,"R_upper_arm"),(8,10,"R_forearm"),(11,13,"L_thigh"),(13,15,"L_shank"),(12,14,"R_thigh"),(14,16,"R_shank")]
sus={}
P=lm.pivot_table(index="frame",columns="landmark",values=["x_pixel","y_pixel","keypoint_conf"])
from com_model import NAMES
for t in P.index:
    d=dets[t]; j=int(sel[t]); b=d["box"][j]; diag=np.hypot(b[2]-b[0],b[3]-b[1]); kp=d["kp"][j]; kc=d["kpc"][j]; why=[]
    for a,c,n in BONES:
        if kc[a]>=0.5 and kc[c]>=0.5 and np.hypot(*(kp[a]-kp[c]))>0.5*diag: why.append(f"{n}_too_long")
    for a,c,n in [(15,16,"ankles"),(9,10,"wrists"),(13,14,"knees")]:
        if kc[a]>=0.5 and kc[c]>=0.5 and np.hypot(*(kp[a]-kp[c]))<2.0: why.append(f"{n}_coincident")
    out_n=sum(1 for i in range(17) if kc[i]>=0.5 and (kp[i][0]<b[0]-10 or kp[i][0]>b[2]+10 or kp[i][1]<b[1]-10 or kp[i][1]>b[3]+10))
    if out_n: why.append(f"{out_n}_landmarks_outside_own_box")
    if why: sus[t]=why
add(f"- {len(sus)} of {nsel} selected frames have >=1 geometric warning (limb > 0.5x box diagonal; coincident L/R joints; landmarks outside own box)")
from collections import Counter
cnt=Counter(("landmarks_outside_own_box" if w[0].isdigit() else w) for v in sus.values() for w in v); add(f"- warning types: {dict(cnt)}")
sr=runs(np.array([t in sus for t in range(N)]),5); add("- runs >=5 frames: "+", ".join(f"f{a}-{b}" for a,b in sr[:40]))
for t,w in sus.items(): fail.append((t,"pose_geometry:"+"|".join(w)))
add("\n## 10. COM anomalies (pose-derived COM; checks are internal consistency only)")
tr=df[df.COM_x_pixel.notna()&df.status.isin(TRACKED)].copy(); an=0; massj=[]
bx={t:dets[t]["box"][int(sel[t])] for t in tr.frame if t in sel}
outside=[t for t,r in tr.set_index("frame").iterrows() if t in bx and not (bx[t][0]-5<=r.COM_x_pixel<=bx[t][2]+5 and bx[t][1]-5<=r.COM_y_pixel<=bx[t][3]+5)]
add(f"- COM outside own person box (+-5px): {len(outside)} frames {outside[:30]}"); [fail.append((f,"com_outside_box")) for f in outside]
prev=None
for _,r in tr.iterrows():
    if prev is not None and r.frame==prev.frame+1 and r.camera_segment==prev.camera_segment:
        dm=abs(r.visible_mass_fraction-prev.visible_mass_fraction); sh=np.hypot(r.COM_x_pixel-prev.COM_x_pixel,r.COM_y_pixel-prev.COM_y_pixel)
        b=bx.get(int(r.frame)); diag=np.hypot(b[2]-b[0],b[3]-b[1]) if b is not None else np.nan
        if dm>=0.25: massj.append((int(r.frame),round(dm,2),(round(float(sh/diag),2) if diag==diag else None)))
    prev=r
add(f"- Frames where visible-mass fraction changed >=0.25 between consecutive tracked frames (COM can jump from landmark dropout alone, not from motion): {len(massj)}; first 25 (frame, dMass, COMshift/boxdiag): {massj[:25]}")
for f,_,_ in massj: fail.append((f,"com_mass_discontinuity"))
add("- Systematic caveats: Dempster cadaver proportions; COCO joints != anatomical landmarks; PARTIAL COM = centroid of visible mass only (biased toward visible segments); PREDICTED COM is a damped constant-velocity extrapolation in pixel space.")
add("\n## 11. Difficult sequences (runs >=10 frames)")
for name,mask in [("UNRESOLVED",(df.status=="UNRESOLVED").values),("PREDICTED",(df.status=="PREDICTED").values),("tracked but confidence<0.30",((df.tracking_confidence<0.3)&df.status.isin(TRACKED)).values)]:
    rr=runs(mask,10); add(f"- {name}: "+(", ".join(f"f{a}-{b} ({T(a)}-{T(b)})" for a,b in rr) if rr else "none"))
add("\n## 12. Known limitations of this baseline (not repaired, by design)")
add("- 'MEASURED' = enough keypoints above model confidence 0.5, NOT proof the anatomy was visible.\n- tracking_confidence is a heuristic product, not a calibrated probability.\n- Identity by manual seed + clothing colour + continuity; not a general re-ID method.\n- Single-target only; opponent/referee are never tracked.\n- Pixel coordinates are camera-dependent; values are not comparable across camera segments.")
open(out,"w").write("\n".join(L))
fdf=pd.DataFrame(fail,columns=["frame","reason"]); fdf["time_s"]=(fdf.frame/fps).round(2)
fdf=fdf.groupby("frame").agg(time_s=("time_s","first"),reasons=("reason",lambda r:"; ".join(sorted(set(r))))).reset_index(); fdf.to_csv(failcsv,index=False)
df.to_csv(csv.replace(".csv","_with_overlap.csv"),index=False)
print("\n".join(L)); print("\nfailure/ambiguous frames listed:",len(fdf))
