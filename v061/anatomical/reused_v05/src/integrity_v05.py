"""V0.5 anatomical PLAUSIBILITY and cross-body CUES (ownership itself is decided in ownership_v05 + track_v05).
CHANGES FROM V0.4 (docs/V0.5_CHANGELOG.md): no 'positive' anatomical evidence is produced here any more. In V0.4, APPEARANCE_PART_COHERENT and temporal coherence could lift a skeleton to
PASS/INDEPENDENT or PASS/TEMPORAL_ONLY; that let appearance vouch for ownership. In V0.5 appearance can only VETO (PART_IDENTITY_CONFLICT, APPEARANCE_SEGMENT_CONFLICT); coherence is logged as a
diagnostic and counts for nothing. Outputs: reasons (plausibility failures and cross-body cues), overlap context (diagnostic), temporal check numbers.
CROSS_BODY_CUES are the reasons that indicate landmarks from more than one person (they force ownership state MIXED_BODY_SUSPECTED); the rest are plain plausibility failures."""
import numpy as np, math
from appearance import REGION_MASS
from integrity_v03 import PAIRS, TORSO, _iou_cover, body_scale, temporal_check
from integrity_v04 import part_check
CROSS_BODY_PREFIXES = ("LIMB_TOO_LONG", "TORSO_SIDES_ASYMMETRIC", "SHARED_JOINT_CONFLICT", "PART_IDENTITY_CONFLICT", "TEMPORAL_JOINT_JUMP", "APPEARANCE_SEGMENT_CONFLICT")
def is_cross_body(reason): return reason.startswith(CROSS_BODY_PREFIXES)
def evaluate(j, d, kp_conf, C, prev, votes, parts):
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
    tmp = None
    if prev is not None and S is not None and prev["frame_gap"] <= C.TEMPORAL_MAX_GAP:
        r = S / prev["S"]
        if not (C.TEMPORAL_SCALE_MIN <= r <= C.TEMPORAL_SCALE_MAX): reasons.append("TEMPORAL_SCALE_JUMP")
        tmp = temporal_check(kp, obs, prev, C)
        if tmp["applicable"] and tmp["fail_joints"] >= C.REL_FAIL_JOINTS: reasons.append("TEMPORAL_JOINT_JUMP")
    own = sum(REGION_MASS[r] for r, v in votes.items() if v > 0); contam = sum(REGION_MASS[r] for r, v in votes.items() if v < 0)
    if contam >= C.CONTAM_MASS_MAX: reasons.append("APPEARANCE_SEGMENT_CONFLICT")
    if parts["conflict"]: reasons.append("PART_IDENTITY_CONFLICT")
    info = []; ov = False; conflict = False; others = []
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
    reasons = sorted(set(reasons))
    return dict(status="FAIL" if reasons else "PASS", reasons=reasons, cross_body=[r for r in reasons if is_cross_body(r)], plain=[r for r in reasons if not is_cross_body(r)],
                overlap_context=ov, overlap_info=info, S=S, own_mass=round(own, 3), contam_mass=round(contam, 3), temporal=tmp, parts=parts)
