"""V0.3 single-body anatomical verification.

CHANGE FROM V0.2: the mere presence of another overlapping detection no longer invalidates a pose. A pose is instead tested for being a
coherent single-person skeleton, and emitted only if no contamination signal fires AND (when overlap or a merge risk is present) POSITIVE
coherence evidence exists. Signals:
  geometry     limb-length / torso-symmetry / landmark-inside-own-box / scale (as V0.2: plausibility only)
  temporal     torso-centred joint motion since the identity's previous emitted skeleton (global camera/body translation removed)
  appearance   per-region colour votes: regions whose appearance matches the OTHER wrestler more than this one (mass-weighted)
  shared joint a non-duplicate detection claims >= SHARE_MIN_JOINTS of the same joint positions
POSITIVE coherence = (temporal check applicable and passed) OR (appearance own-identity vote mass >= VERIFY_OWN_MASS_MIN, no contra-votes).
LIMITS (documented): none of these proves a skeleton belongs to one body. A contaminated skeleton that is geometrically plausible, temporally
persistent, whose contaminated regions look like the target (or are not discriminative), and that has no overlapping detection or merge risk will
pass as GEOMETRY_ONLY and be emitted as PARTIAL at most. Appearance votes need regions where A and B look different."""
import numpy as np, math
from appearance import REGION_MASS
PAIRS = dict(upper_arm=[(5, 7), (6, 8)], forearm=[(7, 9), (8, 10)], thigh=[(11, 13), (12, 14)], shank=[(13, 15), (14, 16)])
TORSO = [5, 6, 11, 12]
def _iou_cover(a, b):
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]); i = max(0, x2-x1) * max(0, y2-y1)
    aa = (a[2]-a[0]) * (a[3]-a[1]); ab = (b[2]-b[0]) * (b[3]-b[1]); u = aa + ab - i
    return (i / u if u > 0 else 0.0), (i / ab if ab > 0 else 0.0)
def body_scale(kp, obs, C):
    c = []; sh = [i for i in (5, 6) if obs[i]]; hp = [i for i in (11, 12) if obs[i]]
    if sh and hp: c.append(float(np.linalg.norm(kp[sh].mean(0) - kp[hp].mean(0))))
    if obs[5] and obs[6]: c.append(C.SCALE_SHOULDER_W_MULT * float(np.linalg.norm(kp[5] - kp[6])))
    if obs[11] and obs[12]: c.append(C.SCALE_HIP_W_MULT * float(np.linalg.norm(kp[11] - kp[12])))
    return max(c) if c else None
def temporal_check(kp, obs, prev, C):
    """Torso-centred joint displacement vs previous emitted skeleton of the same identity. Returns dict(applicable, n, fail_joints, median_rel)."""
    both = obs & prev["obs"]; tj = [i for i in TORSO if both[i]]
    if len(tj) < C.REL_MIN_TORSO_JOINTS or both.sum() < C.REL_MIN_JOINTS: return dict(applicable=False, n=int(both.sum()), fail_joints=0, median_rel=None)
    c0 = kp[tj].mean(0); c1 = prev["kp"][tj].mean(0); rel = np.linalg.norm((kp[both] - c0) - (prev["kp"][both] - c1), axis=1) / prev["S"]
    lim = C.REL_JOINT_DISP_SCALES * max(1, prev["frame_gap"])
    return dict(applicable=True, n=int(both.sum()), fail_joints=int((rel > lim).sum()), median_rel=float(np.median(rel)))
def evaluate(j, d, kp_conf, C, prev, votes, merge_risk):
    """j: selected detection index in frame dict d; prev: dict(kp,obs,S,frame_gap) of this identity's last emitted skeleton in this shot, or None;
    votes: region -> +1/-1/0 (appearance.region_votes); merge_risk: bool (opponent last seen here and now unaccounted for).
    -> dict(status PASS|FAIL|UNVERIFIED, tier VERIFIED|GEOMETRY_ONLY|'', reasons, overlap_context, overlap_info, S, positive[list], own_mass, contam_mass, temporal)."""
    kp = d["kp"][j]; kc = d["kpc"][j]; box = d["box"][j]; obs = kc >= kp_conf; diag = math.hypot(box[2]-box[0], box[3]-box[1])
    reasons = []; S = body_scale(kp, obs, C)
    if S is None or S < 1e-6: reasons.append("NO_BODY_SCALE")
    else:
        for seg, prs in PAIRS.items():
            for a, b in prs:
                if obs[a] and obs[b] and np.linalg.norm(kp[a]-kp[b]) > C.LIMB_MAX_RATIO[seg] * S: reasons.append(f"LIMB_TOO_LONG:{seg}")
        if obs[5] and obs[11] and obs[6] and obs[12]:
            l, r = np.linalg.norm(kp[5]-kp[11]), np.linalg.norm(kp[6]-kp[12])
            if min(l, r) / max(l, r, 1e-6) < C.TORSO_SIDE_RATIO_MIN: reasons.append("TORSO_SIDES_ASYMMETRIC")
    m = C.LM_OUTSIDE_BOX_MARGIN_FRAC * diag
    if any(obs[i] and (kp[i][0] < box[0]-m or kp[i][0] > box[2]+m or kp[i][1] < box[1]-m or kp[i][1] > box[3]+m) for i in range(17)): reasons.append("LANDMARK_OUTSIDE_OWN_BOX")
    tmp = None; positive = []
    if prev is not None and S is not None and prev["frame_gap"] <= C.TEMPORAL_MAX_GAP:
        r = S / prev["S"]
        if not (C.TEMPORAL_SCALE_MIN <= r <= C.TEMPORAL_SCALE_MAX): reasons.append("TEMPORAL_SCALE_JUMP")
        tmp = temporal_check(kp, obs, prev, C)
        if tmp["applicable"]:
            if tmp["fail_joints"] >= C.REL_FAIL_JOINTS: reasons.append("TEMPORAL_JOINT_JUMP")
            elif "TEMPORAL_SCALE_JUMP" not in reasons: positive.append("TEMPORAL_COHERENT")
    own = sum(REGION_MASS[r] for r, v in votes.items() if v > 0); contam = sum(REGION_MASS[r] for r, v in votes.items() if v < 0)
    if contam >= C.CONTAM_MASS_MAX: reasons.append("APPEARANCE_SEGMENT_CONFLICT")
    elif own >= C.VERIFY_OWN_MASS_MIN and contam == 0: positive.append("APPEARANCE_CONSISTENT")
    info = []; ov = False; conflict = False
    for o in range(len(d["conf"])):
        if o == j: continue
        iou, cover = _iou_cover(box, d["box"][o]); ok_ = d["kpc"][o] >= kp_conf
        shared = int(sum(1 for i in range(17) if obs[i] and ok_[i] and np.linalg.norm(kp[i]-d["kp"][o][i]) < C.SHARE_DIST_FRAC * diag))
        if shared >= C.SHARE_MIN_JOINTS:
            if iou >= C.DUP_IOU: info.append(dict(det=o, kind="duplicate_ignored", iou=round(float(iou), 2))); continue
            conflict = True; info.append(dict(det=o, kind="shared_joints", shared=shared, iou=round(float(iou), 2))); continue
        inside = int(sum(1 for i in range(17) if ok_[i] and box[0] <= d["kp"][o][i][0] <= box[2] and box[1] <= d["kp"][o][i][1] <= box[3]))
        if iou >= C.OVERLAP_IOU or cover >= C.OVERLAP_COVER_OTHER or inside >= C.OVERLAP_OTHER_JOINTS_INSIDE:
            ov = True; info.append(dict(det=o, kind="overlap", iou=round(float(iou), 2), cover_other=round(float(cover), 2), other_joints_inside=inside, conf=round(float(d["conf"][o]), 2)))
    if conflict: reasons.append("SHARED_JOINT_CONFLICT")
    if reasons: status, tier = "FAIL", ""
    elif positive: status, tier = "PASS", "VERIFIED"
    elif ov or merge_risk: status, tier = "UNVERIFIED", ""
    else: status, tier = "PASS", "GEOMETRY_ONLY"
    return dict(status=status, tier=tier, reasons=sorted(set(reasons)), overlap_context=ov, merge_risk=bool(merge_risk), overlap_info=info, S=S, positive=positive, own_mass=round(own, 3), contam_mass=round(contam, 3), temporal=tmp)
