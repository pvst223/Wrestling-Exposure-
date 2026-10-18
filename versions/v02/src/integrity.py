"""V0.2 single-body anatomical-integrity and overlap-context checks. FAIL CLOSED: anything not positively verified is not emitted.
These are GEOMETRIC PLAUSIBILITY checks on 2D keypoints; they cannot prove a skeleton belongs to one body (no ground truth for that
exists), and a merged-body skeleton that happens to be geometrically plausible AND shows no other person detection nearby will pass."""
import numpy as np, math
PAIRS = dict(upper_arm=[(5, 7), (6, 8)], forearm=[(7, 9), (8, 10)], thigh=[(11, 13), (12, 14)], shank=[(13, 15), (14, 16)])
def _iou_cover(a, b):
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]); i = max(0, x2-x1) * max(0, y2-y1)
    aa = (a[2]-a[0]) * (a[3]-a[1]); ab = (b[2]-b[0]) * (b[3]-b[1]); u = aa + ab - i
    return (i / u if u > 0 else 0.0), (i / ab if ab > 0 else 0.0)
def body_scale(kp, obs, C):
    """Robust torso-scale S = largest of: shoulder-mid->hip-mid length, 1.15*shoulder width, 1.5*hip width (largest resists foreshortening of any one)."""
    c = []
    sh = [i for i in (5, 6) if obs[i]]; hp = [i for i in (11, 12) if obs[i]]
    if sh and hp: c.append(float(np.linalg.norm(kp[sh].mean(0) - kp[hp].mean(0))))
    if obs[5] and obs[6]: c.append(C.SCALE_SHOULDER_W_MULT * float(np.linalg.norm(kp[5] - kp[6])))
    if obs[11] and obs[12]: c.append(C.SCALE_HIP_W_MULT * float(np.linalg.norm(kp[11] - kp[12])))
    return max(c) if c else None
def evaluate(j, d, kp_conf, C, prev=None):
    """j: index of selected detection in frame dict d. prev: dict(kp,obs,S,frame_gap) of last emitted skeleton in this shot or None.
    Returns dict(status in PASS|FAIL|OVERLAP_UNVERIFIED, reasons[list], overlap_context, overlap_info, S)."""
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
        # RUN-2 CHANGE (documented): lateral-separation checks (shoulder/hip coincidence, minimum shoulder width) were REMOVED. They
        # contradict the foreshortening principle: in profile/back views shoulders and hips legitimately project almost onto each other.
    m = C.LM_OUTSIDE_BOX_MARGIN_FRAC * diag
    if any(obs[i] and (kp[i][0] < box[0]-m or kp[i][0] > box[2]+m or kp[i][1] < box[1]-m or kp[i][1] > box[3]+m) for i in range(17)): reasons.append("LANDMARK_OUTSIDE_OWN_BOX")
    if prev is not None and S is not None and prev["frame_gap"] <= C.TEMPORAL_MAX_GAP:
        r = S / prev["S"]
        if not (C.TEMPORAL_SCALE_MIN <= r <= C.TEMPORAL_SCALE_MAX): reasons.append("TEMPORAL_SCALE_JUMP")
        both = obs & prev["obs"]
        if both.sum() >= 4:
            disp = float(np.median(np.linalg.norm(kp[both] - prev["kp"][both], axis=1))) / prev["S"]
            if disp > C.TEMPORAL_JOINT_DISP_SCALES: reasons.append("TEMPORAL_JOINT_JUMP")
    # ---- overlap context: any OTHER person detection (down to the raw detector floor) that overlaps, or whose joints lie inside, the selected box
    info = []; ov = False
    for o in range(len(d["conf"])):
        if o == j: continue
        iou, cover = _iou_cover(box, d["box"][o])
        ok_ = d["kpc"][o] >= kp_conf
        shared = int(sum(1 for i in range(17) if obs[i] and ok_[i] and np.linalg.norm(kp[i]-d["kp"][o][i]) < C.SHARE_DIST_FRAC * diag))
        if shared >= C.SHARE_MIN_JOINTS and iou >= C.DUP_IOU: info.append(dict(det=o, kind="duplicate_ignored", iou=round(iou, 2))); continue
        inside = int(sum(1 for i in range(17) if ok_[i] and box[0] <= d["kp"][o][i][0] <= box[2] and box[1] <= d["kp"][o][i][1] <= box[3]))
        if iou >= C.OVERLAP_IOU or cover >= C.OVERLAP_COVER_OTHER or inside >= C.OVERLAP_OTHER_JOINTS_INSIDE:
            ov = True; info.append(dict(det=o, kind="overlap", iou=round(iou, 2), cover_other=round(cover, 2), other_joints_inside=inside, conf=round(float(d["conf"][o]), 2)))
    status = "FAIL" if reasons else ("OVERLAP_UNVERIFIED" if ov else "PASS")
    return dict(status=status, reasons=sorted(set(reasons)), overlap_context=ov, overlap_info=info, S=S)
