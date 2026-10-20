"""Anatomy V2 (C3) pure decision logic. No cv2, no model, no file access. Implements exactly ANATOMY_V2_C3_JOINT_TWO_BODY_OWNERSHIP_DETAILED_DESIGN_V1 + C3_ANCHOR_INDEPENDENCE_CORRECTION_V1.
Principle: unique supported current-frame ownership or WITHHOLD. Nothing here produces, moves or copies a landmark coordinate."""
STRUCT = dict(MIN_VIEWS=2, MAX_CAST=3, EXT_FRAMES=1, STRIDE=3)   # structural, not tuned (constants audit table, correction section 6)
REGION_LANDMARKS = {"torso": (5, 6, 11, 12), "arm_L": (5, 7), "arm_R": (6, 8), "thigh_L": (11, 13), "thigh_R": (12, 14), "shank_L": (13, 15), "shank_R": (14, 16), "head": (0,)}
ASSIGNED = ("ASSIGNED_A", "ASSIGNED_B")
def view_state(kp, kc, kp_conf):
    """Observation state (Facing, Upright) of a view from confident keypoints; None if undefined (missing keypoint or exact tie) -> ineligible, never tie-broken."""
    for i in (5, 6, 11, 12):
        if not (kc[i] >= kp_conf): return None
    x5, x6 = float(kp[5][0]), float(kp[6][0])
    if x5 == x6: return None
    sy, sx = (float(kp[5][1]) + float(kp[6][1])) / 2, (float(kp[5][0]) + float(kp[6][0])) / 2
    hy, hx = (float(kp[11][1]) + float(kp[12][1])) / 2, (float(kp[11][0]) + float(kp[12][0])) / 2
    dy, dx = abs(hy - sy), abs(hx - sx)
    if dy == dx: return None
    return (1 if x5 > x6 else -1, dy > dx)
def independent(s1, s2):
    return s1 is not None and s2 is not None and s1 != s2
def pick_anchor_pair(eligible_desc):
    """eligible_desc: clean, state-defined views of ONE body sorted by frame DESCENDING (each a dict with 'state'). v1 = most recent; v2 = most recent EARLIER view whose state differs.
    -> (pair or None, detail) with detail in OK / NO_CLEAN_VIEW / ONE_CLEAN_VIEW / SAME_STATE."""
    if not eligible_desc: return None, "NO_CLEAN_VIEW"
    if len(eligible_desc) < STRUCT["MIN_VIEWS"]: return None, "ONE_CLEAN_VIEW"
    v1 = eligible_desc[0]
    for v in eligible_desc[1:]:
        if independent(v1["state"], v["state"]): return (v1, v), "OK"
    return None, "SAME_STATE"
def hypotheses(L, n_rivals):
    """Finite set: H_alpha; H_swap(k); H_foreign(j,k) for each drawn landmark j and rival k. Sorted, deterministic."""
    return [("ALPHA",)] + [("SWAP", k) for k in range(n_rivals)] + [("FOREIGN", j, k) for j in sorted(L) for k in range(n_rivals)]
def decide_unique(L, ev, n_rivals):
    """ev[j] = dict(mask_pos, mask_contra, app_pos_vs (list[bool] per rival), app_contra, double). Returns dict(unique, reason, landmarks, margin, n_hyp).
    UNIQUE iff zero contradictions AND every rival hypothesis is excluded by a positive source. Ties withhold; no score, no weight, no margin constant."""
    L = sorted(L)
    if n_rivals < 1: return dict(unique=False, reason="NO_RIVAL_ANCHOR", landmarks=[], margin=None, n_hyp=0)
    hyps = hypotheses(L, n_rivals)
    for reason, key in (("APPEARANCE_CONTRADICTION", "app_contra"), ("MASK_CONTRADICTION", "mask_contra"), ("DOUBLE_CLAIM", "double")):
        bad = [j for j in L if ev[j][key]]
        if bad: return dict(unique=False, reason=reason, landmarks=bad, margin=None, n_hyp=len(hyps))
    def pos_vs(j, k): return bool(ev[j]["mask_pos"] or ev[j]["app_pos_vs"][k])
    unmet = []
    for h in hyps:
        if h[0] == "FOREIGN" and not pos_vs(h[1], h[2]): unmet.append(h)
        elif h[0] == "SWAP" and not any(pos_vs(j, h[1]) for j in L): unmet.append(h)
    if unmet:
        return dict(unique=False, reason="NOT_POSITIVELY_ATTRIBUTED", landmarks=sorted({h[1] for h in unmet if h[0] == "FOREIGN"}), margin=None, n_hyp=len(hyps))
    margin = min(int(bool(ev[j]["mask_pos"])) + int(all(ev[j]["app_pos_vs"])) for j in L)
    return dict(unique=True, reason="", landmarks=[], margin=margin, n_hyp=len(hyps))
def landmark_evidence(L, mask_informative, cls, app_votes, double, n_rivals):
    """Builds ev[j]. cls: {j: OWN_ONLY|CONTESTED|OTHER_ONLY|OUTSIDE}; app_votes: list (per rival) of {region: vote in -1/0/1} or None when appearance is unavailable; double: set of double-claimed landmarks.
    mask-positive: informative mask evidence and OWN_ONLY; mask-contradicted: OTHER_ONLY or CONTESTED (informative or not). appearance-positive vs rival k: some region containing j votes +1 vs k; appearance-contradicted: any region containing j votes -1 vs any rival."""
    ev = {}
    for j in L:
        regs = [r for r, lm in REGION_LANDMARKS.items() if j in lm]
        pos = [False] * n_rivals; contra = False
        if app_votes is not None:
            for k in range(n_rivals):
                vs = [app_votes[k].get(r, 0) for r in regs]
                pos[k] = any(v == 1 for v in vs); contra = contra or any(v == -1 for v in vs)
        c = cls.get(j)
        ev[j] = dict(mask_pos=bool(mask_informative and c == "OWN_ONLY"), mask_contra=c in ("OTHER_ONLY", "CONTESTED"), app_pos_vs=pos, app_contra=contra, double=j in double)
    return ev
def suppress_carry(src_rows, intervals_by_tracklet, stride=STRUCT["STRIDE"]):
    """Drop visualization-only CARRIED rows whose source frame lies inside (or within one stride after) an extended interval of that tracklet, or whose anchor frame lies inside one. Never adds anything."""
    out = []
    for r in src_rows:
        if r.get("pose_status") == "CARRIED":
            bad = False
            for (s, e) in intervals_by_tracklet.get(r["tracklet"], []):
                if s <= r["frame"] <= e + stride - 1 or s <= r.get("anchor_frame", -1) <= e: bad = True; break
            if bad: continue
        out.append(r)
    return out
