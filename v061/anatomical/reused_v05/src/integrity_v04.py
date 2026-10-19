"""V0.4 single-body anatomical integrity. CHANGES FROM V0.3 (see docs/V0.4_DEVELOPMENT_CHANGELOG.md):
 * temporal coherence is NOT positive anatomical evidence on its own: a candidate with overlap context or merge risk is UNVERIFIED unless there is INDEPENDENT
   positive evidence; without overlap/merge risk temporal-only coherence yields tier TEMPORAL_ONLY (never 'verified').
 * new contamination signal PART_IDENTITY_CONFLICT: embedding evidence for the UPPER part and the LOWER part of ONE skeleton point at different people.
 * new independent positive evidence APPEARANCE_PART_COHERENT: >= PART_MIN_N usable parts all support the assigned identity.
 * geometry, torso-centred temporal joint check, regional colour votes and shared-joint conflict are unchanged from V0.3.
Tiers: FAIL | UNVERIFIED | PASS with tier INDEPENDENT | TEMPORAL_ONLY | GEOMETRY_ONLY.
LIMITS: none of this proves a skeleton belongs to one body. It can detect (a) different-person upper/lower halves when the embedding separates the people, (b) abrupt joint
ownership changes between adjacent frames, (c) another detection claiming the same joints, (d) colour-region conflicts. It cannot detect mixing inside one part, or a merged
detection whose parts all resemble the assigned identity."""
import numpy as np, math
from appearance import REGION_MASS
from integrity_v03 import PAIRS, TORSO, _iou_cover, body_scale, temporal_check
def part_check(cues, X, A):
    """cues: reid cues for the candidate (reid_v04.ReidModel.cues). -> dict(coherent, conflict, detail)."""
    parts = {k: c for k, c in cues.items() if k in ("upper", "lower") and c["r"] >= A.PART_R_MIN}
    ss = {k: c["s"][X] for k, c in parts.items()}; detail = ";".join(f"{k}={v:+.2f}" for k, v in ss.items())
    conflict = len(ss) >= 2 and min(ss.values()) <= A.PART_CONFLICT_S and max(ss.values()) >= -A.PART_CONFLICT_S
    coherent = len(ss) >= A.PART_MIN_N and min(ss.values()) >= A.PART_COHERENT_S
    return dict(coherent=bool(coherent), conflict=bool(conflict), detail=detail, n_parts=len(ss))
def evaluate(j, d, kp_conf, C, prev, votes, merge_risk, parts):
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
    tmp = None; pos_temp = []; pos_ind = []
    if prev is not None and S is not None and prev["frame_gap"] <= C.TEMPORAL_MAX_GAP:
        r = S / prev["S"]
        if not (C.TEMPORAL_SCALE_MIN <= r <= C.TEMPORAL_SCALE_MAX): reasons.append("TEMPORAL_SCALE_JUMP")
        tmp = temporal_check(kp, obs, prev, C)
        if tmp["applicable"]:
            if tmp["fail_joints"] >= C.REL_FAIL_JOINTS: reasons.append("TEMPORAL_JOINT_JUMP")
            elif "TEMPORAL_SCALE_JUMP" not in reasons: pos_temp.append("TEMPORAL_COHERENT")
    own = sum(REGION_MASS[r] for r, v in votes.items() if v > 0); contam = sum(REGION_MASS[r] for r, v in votes.items() if v < 0)
    if contam >= C.CONTAM_MASS_MAX: reasons.append("APPEARANCE_SEGMENT_CONFLICT")
    elif own >= C.VERIFY_OWN_MASS_MIN and contam == 0: pos_ind.append("APPEARANCE_REGION_CONSISTENT")
    if parts["conflict"]: reasons.append("PART_IDENTITY_CONFLICT")
    elif parts["coherent"]: pos_ind.append("APPEARANCE_PART_COHERENT")
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
    elif pos_ind: status, tier = "PASS", "INDEPENDENT"
    elif ov or merge_risk: status, tier = "UNVERIFIED", ""
    elif pos_temp: status, tier = "PASS", "TEMPORAL_ONLY"
    else: status, tier = "PASS", "GEOMETRY_ONLY"
    return dict(status=status, tier=tier, reasons=sorted(set(reasons)), overlap_context=ov, merge_risk=bool(merge_risk), overlap_info=info, S=S, positive_independent=pos_ind, positive_temporal=pos_temp,
                own_mass=round(own, 3), contam_mass=round(contam, 3), temporal=tmp, parts=parts)
