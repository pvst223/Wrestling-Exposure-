"""Whole-body COM from COCO-17 keypoints using the Dempster segment model as tabulated in Winter (2009),
lumped segments (hand folded into forearm, foot into leg) because COCO has no hand/foot landmarks.
Verified against the table reproduced at nbviewer.jupyter.org/github/demotu/BMC/.../BodySegmentParameters.ipynb

Segment            mass frac   COM from proximal   proximal -> distal landmark
 head+neck          0.081       (assumption: ear/eye/nose centroid)   -
 trunk              0.497       0.500               shoulder midpoint -> hip midpoint
 upper arm (x2)     0.028       0.436               shoulder -> elbow
 forearm+hand (x2)  0.022       0.682               elbow -> wrist
 thigh (x2)         0.100       0.433               hip -> knee
 leg+foot (x2)      0.061       0.606               knee -> ankle
Sum = 1.000.

KNOWN LIMITS (documented, not hidden):
 * Dempster data = 8 elderly male cadavers; segment proportions of a muscular athlete differ.
 * COCO joint locations are not identical to Dempster's anatomical landmarks (e.g. COCO 'hip' != hip joint centre).
 * Head+neck COM position is an assumption, not from the table (table value 1.0 refers to a different origin).
 * 2D pixel projection only; no depth, no scale, no units other than pixels.
 * Partial COM = COM of the *visible* mass only (renormalised). It is biased toward the visible segments by an
   unknown amount; com_uncertainty_px is a heuristic bound, NOT a calibrated confidence interval."""
import numpy as np
NOSE,LEYE,REYE,LEAR,REAR,LSH,RSH,LEL,REL,LWR,RWR,LHIP,RHIP,LKN,RKN,LAN,RAN = range(17)
NAMES=["nose","L_eye","R_eye","L_ear","R_ear","L_shoulder","R_shoulder","L_elbow","R_elbow","L_wrist","R_wrist","L_hip","R_hip","L_knee","R_knee","L_ankle","R_ankle"]
# (name, mass, com_frac, proximal_idx, distal_idx)
LIMBS=[("upper_arm_L",.028,.436,LSH,LEL),("upper_arm_R",.028,.436,RSH,REL),
       ("forearm_hand_L",.022,.682,LEL,LWR),("forearm_hand_R",.022,.682,REL,RWR),
       ("thigh_L",.100,.433,LHIP,LKN),("thigh_R",.100,.433,RHIP,RKN),
       ("leg_foot_L",.061,.606,LKN,LAN),("leg_foot_R",.061,.606,RKN,RAN)]
HEAD_IDX=[NOSE,LEYE,REYE,LEAR,REAR]; HEAD_M=.081; TRUNK_M=.497
SEGMENT_NAMES=["head"]+["trunk"]+[l[0] for l in LIMBS]
def compute_com(kp, kc, thr=0.5):
    """kp (17,2) px, kc (17,) conf. Returns dict(com(2)|None, visible_mass, segments{name:bool}, n_landmarks, unc_px)."""
    ok = kc >= thr; segs={}; pts=[]; ms=[]
    h=[i for i in HEAD_IDX if ok[i]]
    segs["head"]=len(h)>0
    if h: pts.append(kp[h].mean(0)); ms.append(HEAD_M)
    tr_ok = ok[LSH] and ok[RSH] and ok[LHIP] and ok[RHIP]
    segs["trunk"]=bool(tr_ok)
    if tr_ok:
        sm=(kp[LSH]+kp[RSH])/2; hm=(kp[LHIP]+kp[RHIP])/2; pts.append(sm+0.5*(hm-sm)); ms.append(TRUNK_M)
    for name,m,f,p,d in LIMBS:
        v=bool(ok[p] and ok[d]); segs[name]=v
        if v: pts.append(kp[p]+f*(kp[d]-kp[p])); ms.append(m)
    vm=float(sum(ms))
    if vm==0: return dict(com=None,visible_mass=0.0,segments=segs,n_landmarks=int(ok.sum()),unc_px=None)
    com=(np.array(pts)*np.array(ms)[:,None]).sum(0)/vm
    vis=kp[ok]; scale=float(np.hypot(*(vis.max(0)-vis.min(0)))) if len(vis)>1 else 0.0
    return dict(com=com,visible_mass=vm,segments=segs,n_landmarks=int(ok.sum()),unc_px=(1-vm)*scale)
if __name__=="__main__":
    # synthetic sanity test: standing figure, symmetric -> COM x must equal midline; full mass = 1.0
    kp=np.zeros((17,2)); kc=np.ones(17)
    kp[NOSE]=(100,20); kp[LEYE]=(97,17); kp[REYE]=(103,17); kp[LEAR]=(93,20); kp[REAR]=(107,20)
    kp[LSH]=(85,40); kp[RSH]=(115,40); kp[LEL]=(80,70); kp[REL]=(120,70); kp[LWR]=(78,100); kp[RWR]=(122,100)
    kp[LHIP]=(90,100); kp[RHIP]=(110,100); kp[LKN]=(90,140); kp[RKN]=(110,140); kp[LAN]=(90,180); kp[RAN]=(110,180)
    r=compute_com(kp,kc); print("full:",r["com"],r["visible_mass"]); assert abs(r["visible_mass"]-1.0)<1e-9 and abs(r["com"][0]-100)<1e-6
    kc2=kc.copy(); kc2[[LKN,RKN,LAN,RAN]]=0; r=compute_com(kp,kc2); print("no legs:",r["com"],round(r["visible_mass"],3),round(r["unc_px"],1))
    print("sanity tests OK")
