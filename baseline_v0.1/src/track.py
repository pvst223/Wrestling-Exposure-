"""V0.1 Cena identity + COM tracker. Consumes cached pose detections (stage1) and cuts.json.
PRE-REGISTERED PARAMETERS (fixed before inspecting results; see CONFIG)."""
import sys, json, pickle, math, cv2, numpy as np, pandas as pd
sys.path.insert(0, "src")
from com_model import compute_com, NAMES, SEGMENT_NAMES
CONFIG = dict(
    KP_CONF=0.5,              # landmark counted as 'observed' only if keypoint conf >= this
    DET_CONF=0.30, MIN_BOX_H=50,   # person-detection gates (px at 640x360); removes small crowd false positives
    MEASURED_MASS=0.85,       # MEASURED: trunk observed AND observed segment mass >= 0.85
    PARTIAL_MASS=0.40,        # PARTIAL : observed segment mass >= 0.40 (else UNRESOLVED)
    D_THR=0.06,               # denim fraction (lower 65% of box) to accept identity by appearance
    D_CONT=0.02, IOU_CONT=0.40, MAX_PRED_GAP=15, PRED_DECAY=0.90, CUT_BANNER_FRAMES=8,
    SEED_FRAME=99, SEED_DET=0, # MANUAL seed: Cena = detection #0 in frame 99 (chosen by visual inspection)
)
# DISPLAY-ONLY settings (added for the baseline run; they affect drawing only, never tracking/COM/status/confidence/export)
DISPLAY = dict(KP_CONF=0.70, MAX_BONE_FRAC_OF_BOX_DIAG=0.75)
def iou(a, b):
    x1,y1=max(a[0],b[0]),max(a[1],b[1]); x2,y2=min(a[2],b[2]),min(a[3],b[3]); i=max(0,x2-x1)*max(0,y2-y1)
    u=(a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-i; return i/u if u>0 else 0.0
def calibrate_denim(frame, kp, kc):
    """Learn the denim colour rule from Cena's thigh pixels in the seed frame."""
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV); m=np.zeros(frame.shape[:2],np.uint8)
    for h,k in ((11,13),(12,14)):
        if kc[h]>.5 and kc[k]>.5:
            p,q=kp[h],kp[k]; v=q-p; n=np.array([-v[1],v[0]])/(np.linalg.norm(v)+1e-6); w=0.3*np.linalg.norm(v)
            cv2.fillConvexPoly(m,np.array([p+n*w,p-n*w,q-n*w,q+n*w]).astype(np.int32),1)
    px=hsv[m>0]; assert len(px)>50, "seed thigh region too small"
    H=px[:,0].astype(float); S=px[:,1].astype(float); V=px[:,2].astype(float)
    hmed=np.median(H); hspread=float(np.clip(3*np.median(np.abs(H-hmed)),8,18))
    return dict(h_lo=hmed-hspread,h_hi=hmed+hspread,s_lo=max(35.,np.percentile(S,10)*0.7),v_lo=np.percentile(V,2)*0.8,v_hi=min(255.,np.percentile(V,98)*1.15),n_seed_px=int(len(px)),h_med=float(hmed))
def denim_frac(frame_hsv, box, rule):
    x1,y1,x2,y2=[int(round(v)) for v in box]; x1,y1=max(0,x1),max(0,y1); x2,y2=min(frame_hsv.shape[1],x2),min(frame_hsv.shape[0],y2)
    if x2-x1<4 or y2-y1<4: return 0.0
    yy=y1+int(0.35*(y2-y1)); roi=frame_hsv[yy:y2,x1:x2]
    m=((roi[...,0]>=rule["h_lo"])&(roi[...,0]<=rule["h_hi"])&(roi[...,1]>=rule["s_lo"])&(roi[...,2]>=rule["v_lo"])&(roi[...,2]<=rule["v_hi"]))
    return float(m.mean())
def run(video, dets_pkl, cuts_json, out_csv, out_mp4, out_diag_json, fps_override=None, max_frames=None):
    dets=pickle.load(open(dets_pkl,"rb")); cuts=sorted(c["frame"] for c in json.load(open(cuts_json))["cuts"])
    cutset=set(cuts); cap=cv2.VideoCapture(video); fps=cap.get(cv2.CAP_PROP_FPS); W=int(cap.get(3)); Hh=int(cap.get(4))
    N=len(dets) if max_frames is None else min(len(dets),max_frames); C=CONFIG
    # ---- calibrate on seed frame
    cap.set(cv2.CAP_PROP_POS_FRAMES,C["SEED_FRAME"]); ok,sf=cap.read(); d=dets[C["SEED_FRAME"]]
    rule=calibrate_denim(sf,d["kp"][C["SEED_DET"]],d["kpc"][C["SEED_DET"]]); print("denim rule:",rule)
    cap.set(cv2.CAP_PROP_POS_FRAMES,0)
    tmp=out_mp4+".raw.mp4"; vw=cv2.VideoWriter(tmp,cv2.VideoWriter_fourcc(*"mp4v"),fps,(W,Hh))
    rows=[]; lm_rows=[]; seg=0; prev_box=None; prev_com=None; vel=np.zeros(2); gap=999; last_conf=0.0; last_cut=-999; prev_sel_center=None
    for t in range(N):
        ok,frame=cap.read()
        if not ok: break
        is_cut=t in cutset
        if is_cut: seg+=1; prev_box=None; prev_com=None; vel=np.zeros(2); gap=999; last_cut=t; prev_sel_center=None
        hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV); d=dets[t]
        cands=[]
        for j in range(len(d["conf"])):
            b=d["box"][j]
            if d["conf"][j]<C["DET_CONF"] or (b[3]-b[1])<C["MIN_BOX_H"]: continue
            D=denim_frac(hsv,b,rule); I=iou(b,prev_box) if (prev_box is not None and gap<=5) else 0.0
            by_app = D>=C["D_THR"]; by_cont = (I>=C["IOU_CONT"] and D>=C["D_CONT"])
            if by_app or by_cont: cands.append((D/0.15+I, j, D, I, "appearance" if by_app else "continuity"))
        flags=[]; sel=None
        if cands:
            cands.sort(reverse=True); sel=cands[0]
            if len(cands)>1 and cands[0][0]-cands[1][0]<0.15: flags.append("ambiguous")
        status="UNRESOLVED"; identity="unassigned"; basis="none"; conf=0.0; com=None; vm=np.nan; unc=np.nan; nlm=0; segs={}; src="none"; D_sel=np.nan; detc=np.nan
        if sel is not None:
            _,j,D_sel,I,basis=sel; kp=d["kp"][j]; kc=d["kpc"][j]; box=d["box"][j]; detc=float(d["conf"][j])
            r=compute_com(kp,kc,C["KP_CONF"]); vm=r["visible_mass"]; nlm=r["n_landmarks"]; segs=r["segments"]
            identity="Cena" if basis=="appearance" else "Cena(continuity)"
            if r["com"] is not None and vm>=C["PARTIAL_MASS"]:
                status="MEASURED" if (vm>=C["MEASURED_MASS"] and segs.get("trunk")) else "PARTIAL"
                com=r["com"]; unc=r["unc_px"]; src="landmarks"
                idc=min(1.0,D_sel/0.15) if basis=="appearance" else 0.6
                lmf=float(np.mean(kc[kc>=C["KP_CONF"]])) if nlm else 0.0
                conf=float(detc*idc*lmf)
                if prev_sel_center is not None and np.hypot(*(com-prev_sel_center))>0.8*math.hypot(box[2]-box[0],box[3]-box[1]): flags.append("jump")
                if prev_com is not None: vel=0.5*vel+0.5*(com-prev_com)
                prev_com=com.copy(); prev_sel_center=com.copy(); last_conf=conf; gap=0; prev_box=box.copy()
            else:
                gap+=1; prev_box=box.copy()   # identity found but anatomy insufficient: keep box for continuity, no COM
                status="UNRESOLVED"
        else:
            gap+=1
        if status=="UNRESOLVED" and com is None and prev_com is not None and gap<=C["MAX_PRED_GAP"] and sel is None:
            k=gap; pc=prev_com+vel*k*0.5; # damped constant-velocity; decays
            com=pc; status="PREDICTED"; src="temporal_prediction"; conf=last_conf*(C["PRED_DECAY"]**k)*0.5; identity="Cena(predicted)"; basis="prediction"; unc=np.nan
        if status=="UNRESOLVED": identity="Cena(unresolved)" if sel is not None else "unassigned"
        banner = (t-last_cut)<C["CUT_BANNER_FRAMES"] and last_cut>=0
        row=dict(frame=t,time_s=round(t/fps,4),camera_segment=seg,identity=identity,identity_basis=basis,
                 COM_x_pixel=(None if com is None else round(float(com[0]),2)),COM_y_pixel=(None if com is None else round(float(com[1]),2)),
                 tracking_confidence=round(conf,4),status=status,visible_landmarks=nlm,camera_cut=bool(is_cut),
                 visible_mass_fraction=(None if np.isnan(vm) else round(vm,3)),com_uncertainty_px_heuristic=(None if (unc is None or (isinstance(unc,float) and np.isnan(unc))) else round(float(unc),1)),
                 com_source=src,denim_fraction=(None if np.isnan(D_sel) else round(D_sel,3)),det_conf=(None if np.isnan(detc) else round(detc,3)),
                 n_candidates=len(cands),flags=";".join(flags),
                 missing_landmarks=";".join(NAMES[i] for i in range(17) if sel is not None and d["kpc"][sel[1]][i]<C["KP_CONF"]) if sel is not None else "",
                 observed_segments=";".join(k for k,v in segs.items() if v))
        rows.append(row)
        if sel is not None:   # EXPORT-ONLY: raw landmark predictions of the selected detection, regardless of display filtering
            _j=sel[1]; _kp=d["kp"][_j]; _kc=d["kpc"][_j]
            for i in range(17):
                lm_rows.append(dict(frame=t,selected_det_index=_j,landmark=NAMES[i],x_pixel=round(float(_kp[i][0]),2),y_pixel=round(float(_kp[i][1]),2),
                                    keypoint_conf=round(float(_kc[i]),4),used_for_status_com=bool(_kc[i]>=C["KP_CONF"]),drawn_in_overlay=bool(_kc[i]>=DISPLAY["KP_CONF"])))
        # ---- annotate
        im=frame.copy(); colors=dict(MEASURED=(0,200,0),PARTIAL=(0,215,255),PREDICTED=(0,140,255),UNRESOLVED=(0,0,230))
        others=[j for j in range(len(d["conf"])) if d["conf"][j]>=C["DET_CONF"] and (d["box"][j][3]-d["box"][j][1])>=C["MIN_BOX_H"] and (sel is None or j!=sel[1])]
        for j in others:
            x1,y1,x2,y2=d["box"][j].astype(int); cv2.rectangle(im,(x1,y1),(x2,y2),(150,150,150),1); cv2.putText(im,"other",(x1,y1+11),cv2.FONT_HERSHEY_SIMPLEX,0.35,(180,180,180),1)
        if sel is not None:
            j=sel[1]; kp=d["kp"][j]; kc=d["kpc"][j]; x1,y1,x2,y2=d["box"][j].astype(int); cv2.rectangle(im,(x1,y1),(x2,y2),colors[status],1)
            # ---- DISPLAY-ONLY filtering (does not touch tracking, COM, status, confidence or exported data)
            bdiag=math.hypot(x2-x1,y2-y1)
            def _disp(i): return kc[i]>=DISPLAY["KP_CONF"]
            for a,b in [(5,6),(5,7),(7,9),(6,8),(8,10),(5,11),(6,12),(11,12),(11,13),(13,15),(12,14),(14,16)]:
                if _disp(a) and _disp(b) and np.hypot(*(kp[a]-kp[b]))<=DISPLAY["MAX_BONE_FRAC_OF_BOX_DIAG"]*bdiag:
                    cv2.line(im,tuple(kp[a].astype(int)),tuple(kp[b].astype(int)),(255,200,0),1)
            for i in range(17):
                if _disp(i): cv2.circle(im,tuple(kp[i].astype(int)),2,(255,255,0),-1)
        if com is not None:
            cx,cy=int(com[0]),int(com[1]); col=colors[status]
            if status=="PREDICTED":
                cv2.circle(im,(cx,cy),10,col,1)
            else:
                dia=np.array([[cx,cy-9],[cx+9,cy],[cx,cy+9],[cx-9,cy]],np.int32)   # filled diamond = COM (landmarks are small cyan dots)
                cv2.fillConvexPoly(im,dia,col); cv2.polylines(im,[dia],True,(0,0,0),1)
            cv2.line(im,(cx-15,cy),(cx+15,cy),(0,0,0),3); cv2.line(im,(cx,cy-15),(cx,cy+15),(0,0,0),3)
            cv2.line(im,(cx-15,cy),(cx+15,cy),col,1); cv2.line(im,(cx,cy-15),(cx,cy+15),col,1)
            cv2.putText(im,"COM",(cx+11,cy-11),cv2.FONT_HERSHEY_SIMPLEX,0.38,(0,0,0),2); cv2.putText(im,"COM",(cx+11,cy-11),cv2.FONT_HERSHEY_SIMPLEX,0.38,col,1)
        cv2.rectangle(im,(0,0),(W,38),(0,0,0),-1)
        cv2.putText(im,f"f{t} {t/fps:5.2f}s seg{seg}",(4,13),cv2.FONT_HERSHEY_SIMPLEX,0.42,(255,255,255),1)
        cv2.putText(im,f"{identity} [{basis}] conf {conf:.2f}",(4,28),cv2.FONT_HERSHEY_SIMPLEX,0.42,(255,255,255),1)
        cv2.putText(im,status,(W-120,22),cv2.FONT_HERSHEY_SIMPLEX,0.6,colors[status],2)
        if banner: cv2.putText(im,"CAMERA CUT - track reset",(W//2-110,60),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,255),2)
        vw.write(im)
    vw.release(); df=pd.DataFrame(rows); df.to_csv(out_csv,index=False); pd.DataFrame(lm_rows).to_csv(out_csv.replace('.csv','_landmarks_raw.csv'),index=False)
    import subprocess; subprocess.run(["ffmpeg","-v","error","-y","-i",tmp,"-c:v","libx264","-pix_fmt","yuv420p","-crf","20",out_mp4],check=True)
    import os; os.remove(tmp); json.dump(dict(config=C,denim_rule=rule,cuts=cuts,n_frames=N),open(out_diag_json,"w"),indent=1)
    return df
if __name__=="__main__":
    df=run("input.mp4","out/raw_detections.pkl","out/cuts.json","out/tracking.csv","out/annotated.mp4","out/run_meta.json")
    print(df.status.value_counts())
