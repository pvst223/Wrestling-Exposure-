"""V0.5 two-wrestler tracker. FAIL CLOSED. Four SEPARATE states per wrestler: IDENTITY evidence -> LANDMARK OWNERSHIP evidence -> anatomical PLAUSIBILITY -> COM eligibility.
Inputs: video, cached pose detections (V0.1 stage-1 pkl), cached person instance masks (seg_extract.py), camera events json, manual seeds json, cached crop embeddings (embed_crops.py, embed_masked.py). Writes only into out_dir.
Design: docs/V0.5_ARCHITECTURE.md. All behavioural constants are in config/config_v05.json; NO frame-specific exceptions exist in this file.
CORRECT IDENTITY != CORRECT LANDMARK OWNERSHIP: appearance supports identity only; it may VETO ownership, never vouch for it.
IDENTITY STATES (per wrestler, per frame):
  SUPPORTED_INDEPENDENT   appearance evidence (embedding + colour cues, NOT continuity) selects one candidate in a JOINT A/B assignment
  TEMPORAL_CONTINUATION   no independent evidence, but spatial continuity from an independently supported box, within a decaying credit, no contradicting appearance
  AMBIGUOUS               evidence exists but the joint assignment / candidates / A-B separation is not decisive (-> no assignment)
  INSUFFICIENT            candidates exist but appearance evidence is too weak to say
  NOT_IN_VIEW_OR_CONTRA   best candidate is clearly someone else
  NO_CANDIDATE
Temporal continuity is supporting tracking evidence only; it never makes an identity 'verified'."""
import sys, os, json, math, pickle, subprocess, argparse, cv2, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config, appearance as AP, integrity_v05 as IN, reid_v05 as RE, ownership_v05 as OW, render_v05 as RD
from com_model import compute_com, NAMES
IDS = ("A", "B"); OTHER = {"A": "B", "B": "A"}
SEG_LM = {"head": [0, 1, 2, 3, 4], "trunk": [5, 6, 11, 12], "upper_arm_L": [5, 7], "upper_arm_R": [6, 8], "forearm_hand_L": [7, 9], "forearm_hand_R": [8, 10], "thigh_L": [11, 13], "thigh_R": [12, 14], "leg_foot_L": [13, 15], "leg_foot_R": [14, 16]}   # landmarks feeding each com_model segment
def box_iou(a, b):
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]); i = max(0, x2-x1) * max(0, y2-y1)
    u = (a[2]-a[0])*(a[3]-a[1]) + (b[2]-b[0])*(b[3]-b[1]) - i; return i / u if u > 0 else 0.0
def diag(b): return math.hypot(b[2]-b[0], b[3]-b[1])
def ctr(b): return np.array([(b[0]+b[2])/2, (b[1]+b[3])/2])
def thigh_polys(shape, kp, kc, R):
    P = np.zeros(shape, np.uint8); hw = R.THIGH_POLY_HALFWIDTH
    for h, k in ((11, 13), (12, 14)):
        if kc[h] >= R.POLY_KP_CONF and kc[k] >= R.POLY_KP_CONF:
            p, q = kp[h], kp[k]; v = q - p; n = np.array([-v[1], v[0]]) / (np.linalg.norm(v) + 1e-6); w = hw * np.linalg.norm(v)
            cv2.fillConvexPoly(P, np.array([p+n*w, p-n*w, q-n*w, q+n*w]).astype(np.int32), 1)
    return P
def calibrate_denim(frame, kp, kc, R):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV); m = thigh_polys(frame.shape[:2], kp, kc, R)
    px = hsv[m > 0]; assert len(px) > 50, "denim calibration seed has no thigh pixels"
    H = px[:, 0].astype(float); Sa = px[:, 1].astype(float); V = px[:, 2].astype(float); hmed = np.median(H)
    hs = float(np.clip(R.H_SPREAD_MAD_MULT * np.median(np.abs(H - hmed)), R.H_SPREAD_MIN, R.H_SPREAD_MAX))
    return dict(h_lo=hmed-hs, h_hi=hmed+hs, s_lo=max(float(R.S_FLOOR), np.percentile(Sa, R.S_PCT)*R.S_SCALE), v_lo=np.percentile(V, R.V_PCT_LO)*R.V_SCALE_LO, v_hi=min(255., np.percentile(V, R.V_PCT_HI)*R.V_SCALE_HI), n_seed_px=int(len(px)), h_med=float(hmed))
def denim_mask(hsv, r): return (hsv[..., 0] >= r["h_lo"]) & (hsv[..., 0] <= r["h_hi"]) & (hsv[..., 1] >= r["s_lo"]) & (hsv[..., 2] >= r["v_lo"]) & (hsv[..., 2] <= r["v_hi"])
def fuse(cues, present_r, contra_r, contra_s):
    """cues: list of (name, support, reliability). Reliability-weighted mean, equal cue weights. -> S, R(sum), n_present, contra."""
    R = sum(r for _, _, r in cues)
    if R <= 0: return 0.0, 0.0, 0, False
    S = sum(r * s for _, s, r in cues) / R; n = sum(1 for _, _, r in cues if r >= present_r); contra = any(r >= contra_r and s <= contra_s for _, s, r in cues)
    return float(S), float(R), int(n), bool(contra)
class IdState:
    def __init__(s): s.absorbed = None; s.reset_all()   # absorbed: this wrestler is presumed merged inside the OTHER wrestler's detection (persists across cuts; see ownership.MERGE_PERSIST_MAX_FRAMES)
    def reset_all(s): s.reset_spatial(); s.taint = False; s.amb_since_ind = False
    def reset_spatial(s):   # called at confirmed camera cuts: spatial / trajectory continuity is lost; appearance evidence is NOT stored per track (static seed models), so it needs no reset
        s.box = None; s.frame = None; s.S = None; s.lineage_box = None; s.lineage_gap = 999; s.probation = 0; s.prev_emit = None; s.anchor = None; s.vel = np.zeros(2); s.taint = False; s.since_anchor = 999
        s.last_ind = None; s.amb_since_ind = False
def run(video, dets_pkl, seg_pkl, cuts_json, seeds_json, emb_npz, out_dir, cfg=None, max_frames=None):
    cfg = cfg or config.load(); P, A, DR, F, CT, ST, PR, O = cfg.pose, cfg.appearance, cfg.denim_rule, cfg.fusion, cfg.continuity, cfg.status, cfg.prediction, cfg.output
    ID, RC, AN, CL, OWc, SG = cfg.identity, cfg.reid, cfg.anatomy, cfg.collapse, cfg.ownership, cfg.seg
    os.makedirs(out_dir, exist_ok=True); dets = pickle.load(open(dets_pkl, "rb")); segs_all = pickle.load(open(seg_pkl, "rb")); cj = json.load(open(cuts_json)); sd = json.load(open(seeds_json))
    cutset = {c["frame"] for c in cj["cuts"]}; transient = set(cj["transient_frames"])
    cap = cv2.VideoCapture(video); fps = cap.get(cv2.CAP_PROP_FPS); W = int(cap.get(3)); Hh = int(cap.get(4)); N = len(dets) if max_frames is None else min(len(dets), max_frames)   # max_frames: SMOKE-TEST ONLY
    cache = RE.EmbCache(emb_npz); RM = RE.ReidModel(cache, sd["seeds"], dets, RC)
    M = AP.Models(A); rule = None; seed_denim = {}
    for si, s in enumerate(sd["seeds"]):
        cap.set(cv2.CAP_PROP_POS_FRAMES, s["frame"]); ok, im = cap.read(); assert ok
        d0 = dets[s["frame"]]; kp0, kc0, b0 = d0["kp"][s["det"]], d0["kpc"][s["det"]], d0["box"][s["det"]]
        M.add(s["identity"], AP.quantize(im, A), kp0, kc0, b0)
        if si == sd["denim_calibration_seed_index"]: assert s["identity"] == "A"; rule = calibrate_denim(im, kp0, kc0, DR)
    M.finalize(); seed_frames = sorted({s["frame"] for s in sd["seeds"]})
    for si, s in enumerate(sd["seeds"]):
        if s["identity"] != "B": continue
        cap.set(cv2.CAP_PROP_POS_FRAMES, s["frame"]); ok, im = cap.read(); d0 = dets[s["frame"]]; pm = thigh_polys(im.shape[:2], d0["kp"][s["det"]], d0["kpc"][s["det"]], DR)
        if pm.sum() > 0: seed_denim[si] = float(denim_mask(cv2.cvtColor(im, cv2.COLOR_BGR2HSV), rule)[pm > 0].mean())
    denim_neg_for_B = bool(seed_denim) and max(seed_denim.values()) < DR.COV_LO
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    tmp = os.path.join(out_dir, "annotated_v05.mp4.raw.mp4"); vw = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W + O.PANEL_W, Hh))
    rows = []; lm = []; crows = []; events = []; plog = []; seg = 0; last_cut = -999; st = {i: IdState() for i in IDS}; own_prev = {i: None for i in IDS}; refst = dict(box=None, frame=None, seg=None, absorbed=None)   # referee/third-person memory (last NEITHER-labelled candidate)
    def ev(t, X, kind, detail=""): events.append(dict(frame=t, target=X, event=kind, detail=detail))
    for t in range(N):
        ok, frame = cap.read()
        if not ok: break
        is_cut = t in cutset
        if is_cut:
            seg += 1; last_cut = t
            for i in IDS: st[i].reset_spatial(); ev(t, i, "CAMERA_CUT_SPATIAL_RESET")
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV); d = dets[t]; fs = OW.FrameSeg(segs_all[t], W, Hh, SG.SEG_CONF_MIN); q = AP.quantize(frame, A); m = denim_mask(hsv, rule)
        occ = np.zeros(m.shape, bool)
        for o in range(len(d["conf"])):
            if d["conf"][o] >= P.RAW_OTHER_CONF:
                x1, y1, x2, y2 = [int(v) for v in d["box"][o]]; occ[max(0, y1):max(0, y2), max(0, x1):max(0, x2)] = True
        bg = float(m[~occ].mean()) if (~occ).sum() > 0 else float("nan")
        cue_valid = (not (bg > DR.BG_DENIM_MAX)) and (t not in transient)
        # ---------------- candidates: DECOMPOSED evidence
        cands = []
        for j in range(len(d["conf"])):
            b = d["box"][j]
            if d["conf"][j] < P.DET_CONF_GATE or (b[3]-b[1]) < P.MIN_BOX_H: continue
            kp, kc = d["kp"][j], d["kpc"][j]; desc = AP.descriptors(q, kp, kc, b, A); app, dists = AP.appearance_cues(desc, M, A)
            poly = thigh_polys(m.shape, kp, kc, DR); area = int(poly.sum()); cov = float(m[poly > 0].mean()) if area > 0 else 0.0
            den_ok = cue_valid and area >= DR.POLY_MIN_AREA_PX; den_s = float(np.clip(2 * (cov - DR.COV_LO) / (DR.COV_HI - DR.COV_LO) - 1, -1, 1)); den_r = min(1.0, area / (2 * DR.POLY_MIN_AREA_PX)) if den_ok else 0.0
            S_c = IN.body_scale(kp, kc >= P.KP_CONF, cfg.integrity); rid = RM.cues(cache, t, j, kp, kc, b, frame.shape)
            c = dict(j=j, box=b, kp=kp, kc=kc, desc=desc, dists=dists, app=app, den=(den_s, den_r, cov, area), S=S_c, reid=rid)
            fz = lambda cl: fuse(cl, F.CUE_PRESENT_R, ID.CONTRA_R, ID.CONTRA_S)
            reid_cl = {X: [(f"reid_{k}", v["s"].get(X, 0.0), v["r"] if X in v["s"] else 0.0) for k, v in rid.items()] for X in ("A", "B", "NEITHER")}
            col_cl = {}
            for X in ("A", "B"):
                cl = []
                if X in app: cl += [("app_reg",) + app[X]["reg"], ("app_whole",) + app[X]["whole"]]
                cl.append(("denim", den_s if X == "A" else (-den_s if denim_neg_for_B else 0.0), den_r if (X == "A" or denim_neg_for_B) else 0.0)); col_cl[X] = cl
            col_cl["NEITHER"] = [("app_reg",) + app["NEITHER"]["reg"], ("app_whole",) + app["NEITHER"]["whole"]] if "NEITHER" in app else []
            c["fz_reid"] = {X: fz(reid_cl[X]) for X in reid_cl}; c["fz_col"] = {X: fz(col_cl[X]) for X in col_cl}
            c["fz_ind"] = {X: fz(reid_cl[X] + col_cl[X]) for X in reid_cl}                     # INDEPENDENT appearance evidence (no continuity)
            c["cont"] = {}; c["pose"] = {}
            for X in IDS:
                s_ = st[X]; gap = None if s_.box is None else t - s_.frame; c["cont"][X] = (0.0, 0.0); c["pose"][X] = (0.0, 0.0)
                if s_.box is not None and gap <= CT.CONT_MAX_GAP:
                    lim = min(CT.JUMP_CAP_DIAGS, CT.JUMP_BASE_DIAGS + CT.JUMP_PER_GAP_DIAGS * gap); disp = float(np.linalg.norm(ctr(b) - ctr(s_.box))) / max(diag(s_.box), 1e-6)
                    sr = (b[3]-b[1]) / max(s_.box[3]-s_.box[1], 1e-6); iou = box_iou(b, s_.box)
                    sc = -1.0 if not (CT.CONT_SCALE_MIN <= sr <= CT.CONT_SCALE_MAX) else 1.0 - 2.0 * min(1.0, disp / lim)
                    if sc > -1.0 and iou >= CT.CONT_IOU_MIN: sc = max(sc, CT.CONT_IOU_SUPPORT)
                    rc = max(0.0, 1.0 - gap / (CT.CONT_MAX_GAP + 1)); c["cont"][X] = (sc, rc)
                    if S_c is not None and s_.S is not None: c["pose"][X] = (1.0 - 2.0 * min(1.0, abs(math.log(S_c / s_.S)) / math.log(F.POSE_SCALE_RANGE)), F.POSE_R_CAP * rc)
            # anti-identity-aware margin g: evidence it IS X minus evidence it is the competitor (other wrestler / referee) when that competitor evidence is reliable
            c["g"] = {}
            for X in IDS:
                Y = OTHER[X]; alts = [c["fz_ind"][I][0] for I in (Y, "NEITHER") if c["fz_ind"][I][1] >= ID.RELAXED_R_FRAC * ID.R_MIN_APP]
                c["g"][X] = c["fz_ind"][X][0] - (max(alts) if alts else 0.0)
            cands.append(c)
        # ---------------- mask-based LANDMARK OWNERSHIP metrics per candidate (decision-free numbers + default-strictness state)
        for c in cands:
            others = []
            for c2 in cands:
                if c2 is c: continue
                oa_, ob_ = c["kc"] >= P.KP_CONF, c2["kc"] >= P.KP_CONF; dg = diag(c["box"])
                shared = int(sum(1 for i in range(17) if oa_[i] and ob_[i] and np.linalg.norm(c["kp"][i] - c2["kp"][i]) < cfg.integrity.SHARE_DIST_FRAC * dg)); iou2 = box_iou(c["box"], c2["box"])
                if shared >= cfg.integrity.SHARE_MIN_JOINTS and iou2 >= cfg.integrity.DUP_IOU: continue
                others.append((c2["kp"], c2["kc"]))
            c["om"] = OW.metrics(fs, c["kp"], c["kc"], others, c["S"], P.KP_CONF, OWc); c["os"], c["or_"] = OW.decide(c["om"], OWc)
        # ---------------- JOINT A/B independent-identity assignment
        def eligible(c, X): S0, R0, n0, contra0 = c["fz_ind"][X]; return R0 >= ID.R_MIN_APP and n0 >= ID.N_APP_MIN and (not contra0) and S0 >= ID.S_MIN and c["g"][X] >= ID.JOINT_MARGIN
        def plausible(c, X): S0, R0, n0, contra0 = c["fz_ind"][X]; return R0 >= ID.RELAXED_R_FRAC * ID.R_MIN_APP and (not contra0) and S0 >= ID.S_MIN and c["g"][X] > 0
        PL = {X: [c for c in cands if plausible(c, X)] for X in IDS}; EL = {X: [c for c in cands if eligible(c, X)] for X in IDS}
        LA = [None] + PL["A"]; LB = [None] + PL["B"]; best = (-1e9, None, None); allsc = []
        for ca in LA:
            for cb in LB:
                if ca is not None and cb is not None and ca is cb: continue
                sc_ = (ca["g"]["A"] if ca else 0.0) + (cb["g"]["B"] if cb else 0.0); allsc.append((sc_, ca, cb))
                if sc_ > best[0] + 1e-12: best = (sc_, ca, cb)
        sA, sB = best[1], best[2]; jm = {"A": None, "B": None}
        for X, sx in (("A", sA), ("B", sB)):
            idx = 1 if X == "A" else 2; alt = [s_ for s_ in allsc if s_[idx] is not sx]
            jm[X] = best[0] - max((s_[0] for s_ in alt), default=-1e9) if sx is not None else None
        indA = max(EL["A"], key=lambda c: c["g"]["A"], default=None); indB = max(EL["B"], key=lambda c: c["g"]["B"], default=None)
        same_det = indA is not None and indB is not None and indA is indB
        if same_det:
            ev(t, "AB", "SAME_DETECTION_CONFLICT", f"det={indA['j']} gA={indA['g']['A']:.2f} gB={indA['g']['B']:.2f}")
        for X, ind_, sx_ in (("A", indA, sA), ("B", indB, sB)):   # DIAGNOSTIC ONLY (no decision depends on it): joint solution differs from the independent per-wrestler best
            if ind_ is not None and sx_ is not ind_: ev(t, X, "ASSIGNMENT_COLLISION", f"independent best det={ind_['j']} but joint assignment chose {'none' if sx_ is None else 'det=' + str(sx_['j'])}")
        dec = {}
        for X in IDS:
            Y = OTHER[X]; sx = (sA if X == "A" else sB); r = dict(sel=None, reason="", state="", tier="", S=0.0, R=0.0, n=0, g=None, jm=None, basis="")
            if not cands: r["reason"] = "NO_CANDIDATE"; r["state"] = "NO_CANDIDATE"
            else:
                order = sorted(cands, key=lambda c: -c["fz_ind"][X][0]); c0 = order[0]; S0, R0, n0, contra0 = c0["fz_ind"][X]; r.update(S=S0, R=R0, n=n0, g=c0["g"][X])
                if sx is not None and eligible(sx, X) and jm[X] is not None and jm[X] >= ID.JOINT_MARGIN:
                    S1, R1, n1, _ = sx["fz_ind"][X]; r.update(sel=sx, state="SUPPORTED_INDEPENDENT", jm=jm[X], S=S1, R=R1, n=n1, g=sx["g"][X], basis="appearance"); r["tier"] = "HIGH" if (S1 >= ID.S_HIGH and R1 >= ID.R_HIGH and n1 >= ID.N_HIGH) else "ACCEPT"
                elif sx is not None and eligible(sx, X):
                    r["reason"] = "IDENTITY_AMBIGUOUS_JOINT"; r["state"] = "AMBIGUOUS"; r["jm"] = jm[X]
                elif R0 < ID.R_MIN_APP or n0 < ID.N_APP_MIN: r["reason"] = "IDENTITY_INSUFFICIENT_EVIDENCE"; r["state"] = "INSUFFICIENT"
                elif contra0: r["reason"] = "IDENTITY_CONTRA_CUE"; r["state"] = "NOT_IN_VIEW_OR_CONTRA"
                elif S0 < ID.S_MIN: r["reason"] = "IDENTITY_LOW_SCORE"; r["state"] = "NOT_IN_VIEW_OR_CONTRA"
                elif c0["g"][X] < ID.JOINT_MARGIN: r["reason"] = "IDENTITY_AMBIGUOUS_COMPETITOR"; r["state"] = "AMBIGUOUS"
                else: r["reason"] = "IDENTITY_AMBIGUOUS_JOINT"; r["state"] = "AMBIGUOUS"
            if r["state"] == "AMBIGUOUS" and r["reason"] in ("IDENTITY_AMBIGUOUS_JOINT", "IDENTITY_AMBIGUOUS_COMPETITOR"): ev(t, X, "AB_AMBIGUOUS", f"{r['reason']} joint_margin={None if r['jm'] is None else round(r['jm'], 3)}")   # DIAGNOSTIC ONLY
            dec[X] = r
        # ---------------- temporal continuation (supporting evidence only; decaying credit; never for ambiguous/contra; never when the other wrestler is merge-risk)
        for X in IDS:
            Y = OTHER[X]; s_ = st[X]; r = dec[X]
            if r["sel"] is not None or r["state"] not in ("INSUFFICIENT",) or not cands or s_.box is None or s_.last_ind is None or s_.taint: continue
            cred = ID.CRED_DECAY ** (t - s_.last_ind)
            if cred < ID.CRED_MIN or (t - s_.frame) > CT.CONT_MAX_GAP: continue
            claimed = {id(dec[Y]["sel"])} if dec[Y]["sel"] is not None else set()
            pool = [c for c in cands if id(c) not in claimed and c["cont"][X][0] >= ID.CONT_S_MIN and c["cont"][X][1] >= ID.CONT_R_MIN and not c["fz_ind"][X][3] and (c["fz_ind"][X][1] < ID.RELAXED_R_FRAC * ID.R_MIN_APP or c["fz_ind"][X][0] >= ID.CONT_IND_FLOOR)]
            if not pool: continue
            pool.sort(key=lambda c: -c["cont"][X][0]); others = [c for c in cands if c is not pool[0] and id(c) not in claimed]
            rival = max((c["cont"][X][0] for c in others), default=-1.0)
            Yb = st[Y].box; box0 = pool[0]["box"]; mr0 = bool(Yb is not None and dec[Y]["sel"] is None and (t - st[Y].frame) <= CT.MERGE_LOOKBACK and (box0[0] <= ctr(Yb)[0] <= box0[2] and box0[1] <= ctr(Yb)[1] <= box0[3] or box_iou(Yb, box0) >= CT.MERGE_IOU))
            if pool[0]["cont"][X][0] - rival < ID.CONT_UNIQUE_MARGIN or mr0: continue
            r.update(sel=pool[0], state="TEMPORAL_CONTINUATION", reason="", tier="", basis="continuity", cred=cred, S=pool[0]["fz_ind"][X][0], R=pool[0]["fz_ind"][X][1], n=pool[0]["fz_ind"][X][2], g=pool[0]["g"][X])
        # ---------------- A/B collapse check on the two SELECTED skeletons
        collapse = False
        if dec["A"]["sel"] is not None and dec["B"]["sel"] is not None:
            ca, cb = dec["A"]["sel"], dec["B"]["sel"]
            if ca is cb: collapse = True; why = "same_detection"
            else:
                def torso_c(c):
                    ok_ = c["kc"] >= P.KP_CONF; tj = [i for i in (5, 6, 11, 12) if ok_[i]]; return c["kp"][tj].mean(0) if len(tj) >= 3 else ctr(c["box"])
                dist = float(np.linalg.norm(torso_c(ca) - torso_c(cb))); mind = min(diag(ca["box"]), diag(cb["box"])); oa, ob = ca["kc"] >= P.KP_CONF, cb["kc"] >= P.KP_CONF
                shared = int(sum(1 for i in range(17) if oa[i] and ob[i] and np.linalg.norm(ca["kp"][i] - cb["kp"][i]) < cfg.integrity.SHARE_DIST_FRAC * mind))
                collapse = dist < CL.COM_DIST_DIAG_FRAC * mind or shared >= cfg.integrity.SHARE_MIN_JOINTS; why = f"torso_centre_dist={dist/mind:.3f}diag shared_joints={shared}"
            if collapse:
                ev(t, "AB", "AB_COLLAPSE_SUSPECTED", why)
                for X in IDS: dec[X].update(sel=None, state="AMBIGUOUS", reason="AB_COLLAPSE_SUSPECTED", tier="", basis=""); st[X].taint = True; st[X].amb_since_ind = True
        # ---------------- reacquisition (independent support after loss / cut); stricter after ambiguity
        for X in IDS:
            r = dec[X]; s_ = st[X]
            if r["sel"] is not None and r["state"] == "SUPPORTED_INDEPENDENT":
                lost = s_.box is None or (t - s_.frame) > CT.CONT_MAX_GAP
                if lost:
                    mb = r["sel"]["reid"].get("mbox"); mb_ok = mb is not None and mb["s"].get(X, -1) >= ID.REACQ_MBOX_S_MIN and mb["r"] >= ID.REACQ_MBOX_R_MIN
                    strong = r["tier"] == "HIGH" or (r["sel"]["os"] == "SINGLE_BODY_SUPPORTED" and mb_ok)    # V0.5: stronger evidence = (tier HIGH) OR (mask-based single-body ownership AND masked-box appearance support); NOT a lowered threshold
                    if s_.amb_since_ind and not strong: ev(t, X, "REACQUISITION_UNCERTAIN", f"independent support after loss following ambiguity; tier={r['tier']} ownership={r['sel']['os']} masked_box_support={'yes' if mb_ok else 'no'}"); r.update(sel=None, state="AMBIGUOUS", reason="REACQUISITION_UNCERTAIN", tier="", basis="")
                    else: ev(t, X, "REACQUISITION", f"tier={r['tier']} ownership={r['sel']['os']} masked_box_support={'yes' if mb_ok else 'no'}" + (" (after ambiguity: strong evidence)" if s_.amb_since_ind else ""))
        # ---------------- labels / candidate log
        lab = {}
        for c in cands:
            if dec["A"]["sel"] is c: lab[c["j"]] = "A"
            elif dec["B"]["sel"] is c: lab[c["j"]] = "B"
            else:
                sN, rN, nN, _ = c["fz_ind"]["NEITHER"]; sA_, rA_, _, _ = c["fz_ind"]["A"]; sB_, rB_, _, _ = c["fz_ind"]["B"]
                lab[c["j"]] = "NEITHER" if (rN >= ID.R_MIN_APP and sN >= ID.S_MIN and sN - max(sA_, sB_) >= ID.JOINT_MARGIN) else "UNCERTAIN"
            row = dict(frame=t, det=c["j"], det_conf=round(float(d["conf"][c["j"]]), 3), x1=round(float(c["box"][0]), 1), y1=round(float(c["box"][1]), 1), x2=round(float(c["box"][2]), 1), y2=round(float(c["box"][3]), 1), label=lab[c["j"]])
            for k in RC.CROP_TYPES:
                v = c["reid"].get(k)
                for I in ("A", "B", "N"): row[f"reid_{k}_sim_{I}"] = None if v is None else round(v["sim"].get("NEITHER" if I == "N" else I, float("nan")), 4)
                for I in ("A", "B"): row[f"reid_{k}_s_{I}"] = None if v is None else round(v["s"][I], 3)
                row[f"reid_{k}_r"] = None if v is None else round(v["r"], 3)
            for I in ("A", "B", "NEITHER"):
                row[f"reid_S_{I}"], row[f"reid_R_{I}"] = round(c["fz_reid"][I][0], 3), round(c["fz_reid"][I][1], 3)
                row[f"colour_S_{I}"], row[f"colour_R_{I}"] = round(c["fz_col"][I][0], 3), round(c["fz_col"][I][1], 3)
                row[f"ind_S_{I}"], row[f"ind_R_{I}"], row[f"ind_n_{I}"] = round(c["fz_ind"][I][0], 3), round(c["fz_ind"][I][1], 3), c["fz_ind"][I][2]
            for X in IDS:
                row[f"g_{X}"] = round(c["g"][X], 3); row[f"cont_s_{X}"], row[f"cont_r_{X}"] = round(c["cont"][X][0], 3), round(c["cont"][X][1], 3); row[f"pose_s_{X}"], row[f"pose_r_{X}"] = round(c["pose"][X][0], 3), round(c["pose"][X][1], 3)
            row["denim_cov"] = round(c["den"][2], 3); row["denim_area"] = c["den"][3]
            om_ = c["om"]; row.update(own_n_instances=om_["n_inst"], own_owner_idx=om_["owner"], own_owner_cover=round(om_["cover"], 3), own_state_mask_only=c["os"], own_mask_reasons=";".join(c["or_"]))
            for k_ in ("own_only", "contested", "other_only", "outside"): row[f"own_{k_}_frac"] = None if om_["owner"] is None else round(om_[k_ + "_frac"], 3)
            for k_ in ("opp_inside_frac", "unexplained_frac"): row[f"own_{k_}"] = None if om_["owner"] is None else round(om_[k_], 3)
            row["own_bones_span"] = None if om_["owner"] is None else om_["bones_span"]; row["own_bones_outside"] = None if om_["owner"] is None else om_["bones_outside"]
            crows.append(row)
        neis = [c for c in cands if lab[c["j"]] == "NEITHER"]
        if refst["absorbed"] is not None:
            ab = refst["absorbed"]
            if any(c is not dec[ab["host"]]["sel"] for c in neis): refst["absorbed"] = None; ev(t, "N", "ABSORPTION_CLEARED", f"a referee/third-person candidate is visible again on a separate detection after {t - ab['since']} frames")
            elif t - ab["since"] > OWc.MERGE_PERSIST_MAX_FRAMES: refst["absorbed"] = None; ev(t, "N", "ABSORPTION_CLEARED", f"timeout after {t - ab['since']} frames (presumption lapsed, NOT separation evidence)")
        # ---------------- persistent OPPONENT-PRESUMED-ABSORBED state (V0.5): Y was last seen touching host X's detection and has not been independently supported on a DIFFERENT detection since
        for Yw in IDS:
            ab = st[Yw].absorbed
            if ab is None: continue
            h = ab["host"]
            if dec[Yw]["state"] == "SUPPORTED_INDEPENDENT" and dec[Yw]["sel"] is not None and dec[Yw]["sel"] is not dec[h]["sel"]: st[Yw].absorbed = None; ev(t, Yw, "ABSORPTION_CLEARED", f"independent support on a separate detection (host {h}) after {t - ab['since']} frames")
            elif t - ab["since"] > OWc.MERGE_PERSIST_MAX_FRAMES: st[Yw].absorbed = None; ev(t, Yw, "ABSORPTION_CLEARED", f"timeout after {t - ab['since']} frames (presumption lapsed, NOT separation evidence)")
        banner = (t - last_cut) < O.BANNER_FRAMES and last_cut >= 0; out = {}
        # ---------------- per-wrestler: ownership -> plausibility -> COM eligibility -> status; identity track updated independently of COM
        for X in IDS:
            Y = OTHER[X]; s_ = st[X]; dd = dec[X]; sel = dd["sel"]; reason = dd["reason"]; id_state = dd["state"]
            status = "UNRESOLVED"; com = None; integ = None; vm = float("nan"); nlm = 0; emitted = False; factors = []; ov_ = False; mr = False; com_elig = "NOT_EVALUATED"; com_reason = ""; ident_track = False; cred_now = None
            own_state = "NOT_EVALUATED"; own_reasons = []; om = None; used_segs = []; used_lms = []
            if sel is not None:
                j = sel["j"]; box = sel["box"]; kp = sel["kp"]; kc = sel["kc"]; obs = kc >= P.KP_CONF; ident_track = True
                if s_.lineage_box is not None and s_.lineage_gap <= CT.CONT_MAX_GAP and box_iou(box, s_.lineage_box) >= CT.LINEAGE_IOU_MIN: s_.probation += 1
                else: s_.probation = 1
                s_.lineage_box = box.copy(); s_.lineage_gap = 0
                Yb = st[Y].box; mr = bool(Yb is not None and dec[Y]["sel"] is None and (t - st[Y].frame) <= CT.MERGE_LOOKBACK and (box[0] <= ctr(Yb)[0] <= box[2] and box[1] <= ctr(Yb)[1] <= box[3] or box_iou(Yb, box) >= CT.MERGE_IOU))
                if mr and st[Y].absorbed is None: st[Y].absorbed = dict(host=X, since=t); ev(t, Y, "OPPONENT_PRESUMED_ABSORBED", f"last seen inside {X}'s detection; not independently supported elsewhere")
                mr_ref = bool(refst["box"] is not None and refst["seg"] == seg and (t - refst["frame"]) <= CT.MERGE_LOOKBACK and not neis and (box[0] <= ctr(refst["box"])[0] <= box[2] and box[1] <= ctr(refst["box"])[1] <= box[3] or box_iou(refst["box"], box) >= CT.MERGE_IOU))
                if mr_ref and refst["absorbed"] is None: refst["absorbed"] = dict(host=X, since=t); ev(t, "N", "THIRD_PERSON_PRESUMED_ABSORBED", f"referee/third person last seen inside {X}'s detection; no such candidate visible now")
                absorbed_tag = "OPPONENT_PRESUMED_ABSORBED" if (st[Y].absorbed is not None and st[Y].absorbed["host"] == X) else ("THIRD_PERSON_PRESUMED_ABSORBED" if (refst["absorbed"] is not None and refst["absorbed"]["host"] == X) else None)
                votes = AP.region_votes(sel["desc"], sel["dists"], M, X, Y, A); parts = IN.part_check(sel["reid"], X, AN)
                prev = None if s_.prev_emit is None else dict(s_.prev_emit, frame_gap=t - s_.prev_emit["frame"])
                integ = IN.evaluate(j, d, P.KP_CONF, cfg.integrity, prev, votes, parts); ov_ = integ["overlap_context"]
                om = sel["om"]; ms_, mrs_ = OW.decide(om, OWc, OWc.MERGE_STRICT if mr else 1.0)      # stricter mask limits when the opponent's last position is unaccounted for (merge risk)
                if integ["cross_body"]: own_state, own_reasons = "MIXED_BODY_SUSPECTED", integ["cross_body"] + mrs_
                elif absorbed_tag: own_state, own_reasons = "OWNERSHIP_UNCERTAIN", [absorbed_tag] + mrs_
                else: own_state, own_reasons = ms_, mrs_
                s_.box = box.copy(); s_.frame = t
                if integ["S"] is not None: s_.S = integ["S"]
                clean = integ["status"] == "PASS" and own_state == "SINGLE_BODY_SUPPORTED"
                if id_state == "SUPPORTED_INDEPENDENT" and clean: s_.last_ind = t; s_.amb_since_ind = False
                cred_now = 1.0 if (s_.last_ind == t) else (ID.CRED_DECAY ** (t - s_.last_ind) if s_.last_ind is not None else 0.0)
                if id_state != "SUPPORTED_INDEPENDENT": com_elig = "INELIGIBLE"; com_reason = "IDENTITY_TEMPORAL_ONLY"
                elif own_state == "MIXED_BODY_SUSPECTED": com_elig = "INELIGIBLE"; com_reason = "OWNERSHIP_MIXED_BODY_SUSPECTED"
                elif integ["status"] == "FAIL": com_elig = "INELIGIBLE"; com_reason = "ANATOMY_FAIL"
                elif own_state != "SINGLE_BODY_SUPPORTED": com_elig = "INELIGIBLE"; com_reason = absorbed_tag if absorbed_tag else "OWNERSHIP_UNCERTAIN"
                elif s_.probation < CT.PROBATION_FRAMES: com_elig = "INELIGIBLE"; com_reason = "PROBATION"
                else:
                    r = compute_com(kp, kc, P.KP_CONF); vm = r["visible_mass"]; nlm = r["n_landmarks"]; segs = r["segments"]
                    if r["com"] is None or vm < ST.PARTIAL_MASS: com_elig = "INELIGIBLE"; com_reason = "LOW_ANATOMY_MASS"
                    else:
                        com_elig = "ELIGIBLE"
                        if not (vm >= ST.MEASURED_MASS and segs.get("trunk")): factors.append("LOW_MASS")
                        if dd["tier"] != "HIGH": factors.append("IDENTITY_TIER_ACCEPT")
                        status = "MEASURED" if not factors else "PARTIAL"; com = r["com"]; emitted = True; reason = ""
                        used_segs = [k for k, v in segs.items() if v]; used_lms = sorted({i for k in used_segs for i in SEG_LM[k] if obs[i]})
                        s_.vel = (PR.VEL_SMOOTH * s_.vel + (1 - PR.VEL_SMOOTH) * (com - s_.prev_emit["com"])) if (s_.prev_emit is not None and t - s_.prev_emit["frame"] == 1) else np.zeros(2)
                        s_.prev_emit = dict(kp=kp.copy(), obs=obs.copy(), S=integ["S"], frame=t, com=com.copy())
                        if status == "MEASURED": s_.anchor = dict(com=com.copy(), frame=t, box=box.copy()); s_.taint = False; s_.since_anchor = 0
                if not emitted: reason = com_reason
                if com_reason in ("ANATOMY_FAIL", "OWNERSHIP_MIXED_BODY_SUSPECTED", "OWNERSHIP_UNCERTAIN", "OPPONENT_PRESUMED_ABSORBED", "THIRD_PERSON_PRESUMED_ABSORBED"): s_.taint = True; s_.amb_since_ind = True
            else:
                s_.lineage_gap += 1
                if id_state == "AMBIGUOUS": s_.taint = True; s_.amb_since_ind = True
            if own_state != own_prev[X]:
                ev(t, X, "OWNERSHIP_STATE", f"{own_prev[X]}->{own_state}" + (f" [{';'.join(own_reasons)}]" if own_reasons else "")); own_prev[X] = own_state
            if s_.anchor is not None and not emitted: s_.since_anchor = t - s_.anchor["frame"]
            plog_row = None
            if status == "UNRESOLVED" and s_.anchor is not None and 0 < s_.since_anchor <= PR.MAX_PRED_GAP + 1:
                k = s_.since_anchor; reason_ok = reason in PR.ALLOWED_REASONS; unc_diags = PR.UNC_BASE_DIAGS + PR.UNC_PER_FRAME_DIAGS * k
                allowed = (not s_.taint) and reason_ok and k <= PR.MAX_PRED_GAP and unc_diags <= PR.UNC_MAX_DIAGS
                pc = s_.anchor["com"] + s_.vel * k * PR.DAMP; bb = s_.anchor["box"]; mg = PR.BOX_MARGIN_DIAGS * diag(bb); inside_img = bool(0 <= pc[0] <= W and 0 <= pc[1] <= Hh)
                inside_box = bool((bb[0] - mg <= pc[0] <= bb[2] + mg) and (bb[1] - mg <= pc[1] <= bb[3] + mg))
                plog_row = dict(frame=t, target=X, anchor_frame=s_.anchor["frame"], frames_since_anchor=k, trigger_reason=reason, tainted=bool(s_.taint), pred_x=round(float(pc[0]), 2), pred_y=round(float(pc[1]), 2), inside_image=inside_img, within_anchor_box_bound=inside_box)
                if allowed and inside_img and inside_box:
                    status = "PREDICTED"; com = pc; reason = ""; factors = ["PREDICTION_NOT_A_MEASUREMENT"]; plog_row["decision"] = "PREDICTED"
                else:
                    why_ = ("CONTRA_CUE" if reason == "IDENTITY_CONTRA_CUE" else "TAINT_OR_AMBIGUITY") if (s_.taint or not reason_ok) else ("MAX_GAP" if k > PR.MAX_PRED_GAP else ("UNCERTAINTY_LIMIT" if unc_diags > PR.UNC_MAX_DIAGS else "OUT_OF_BOUNDS"))
                    plog_row["decision"] = "TERMINATED:" + why_
                    if why_ == "OUT_OF_BOUNDS": reason = "PREDICTION_OUT_OF_BOUNDS"
                if plog_row["decision"] == "PREDICTED":
                    plog_row["uncertainty_radius_px"] = round(float(unc_diags * diag(bb)), 1); plog_row["decay_factor"] = round(PR.DECAY ** k, 4)
                plog.append(plog_row)
            kmean = float(np.mean(sel["kc"][sel["kc"] >= P.KP_CONF])) if (sel is not None and (sel["kc"] >= P.KP_CONF).any()) else None
            ident_label = f"WRESTLER_{X}" if (id_state in ("SUPPORTED_INDEPENDENT", "TEMPORAL_CONTINUATION")) else f"WRESTLER_{X}_unassigned"
            if status == "PREDICTED": ident_label = f"WRESTLER_{X}(predicted_position_only)"
            unc_px = None if (plog_row is None or plog_row.get("decision") != "PREDICTED") else plog_row["uncertainty_radius_px"]
            out[X] = dict(status=status, com=com, reason=reason, sel=sel, state=id_state, tier=dd["tier"], S=dd["S"], R=dd["R"], n=dd["n"], factors=factors, own_state=own_state, own_reasons=own_reasons, om=om, com_elig=com_elig, vm=vm,
                          integ=integ, unc_px=unc_px, since_anchor=s_.since_anchor if (s_.anchor is not None and s_.since_anchor < 999) else None, anchor_frame=None if s_.anchor is None else s_.anchor["frame"], used_segs=used_segs, mr=mr, jm=dd["jm"])
            nf = integ["temporal"] if integ else None
            f_ = lambda v, n=3: None if v is None else round(float(v), n)
            rows.append(dict(frame=t, time_s=round(t / fps, 4), camera_segment=seg, camera_cut_confirmed=bool(is_cut), camera_transient_event=bool(t in transient), target=X,
                status=status, unresolved_reason=reason if status == "UNRESOLVED" else "", status_limiting_factors=";".join(factors),
                COM_x_pixel=None if com is None else round(float(com[0]), 2), COM_y_pixel=None if com is None else round(float(com[1]), 2), identity_label=ident_label,
                # --- IDENTITY EVIDENCE (appearance + separately logged continuity/pose; heuristic, not probabilities)
                identity_state=id_state, identity_basis=dd.get("basis", ""), identity_tier=dd["tier"], identity_track_continues=bool(ident_track), identity_reason=dd["reason"] if id_state not in ("SUPPORTED_INDEPENDENT", "TEMPORAL_CONTINUATION") else "",
                ind_S=round(dd["S"], 3), ind_R=round(dd["R"], 3), ind_n_cues=dd["n"], anti_identity_margin_g=f_(dd["g"]), joint_assignment_margin=f_(dd["jm"]),
                reid_S=None if sel is None else f_(sel["fz_reid"][X][0]), reid_R=None if sel is None else f_(sel["fz_reid"][X][1]), colour_S=None if sel is None else f_(sel["fz_col"][X][0]), colour_R=None if sel is None else f_(sel["fz_col"][X][1]),
                masked_box_S=None if (sel is None or "mbox" not in sel["reid"]) else f_(sel["reid"]["mbox"]["s"].get(X)), masked_box_R=None if (sel is None or "mbox" not in sel["reid"]) else f_(sel["reid"]["mbox"]["r"]),
                continuity_S=None if sel is None else f_(sel["cont"][X][0]), continuity_R=None if sel is None else f_(sel["cont"][X][1]), pose_consistency_S=None if sel is None else f_(sel["pose"][X][0]), temporal_credit=f_(cred_now),
                frames_since_independent_support=None if s_.last_ind is None else t - s_.last_ind,
                selected_det_index=None if sel is None else sel["j"], n_candidates=len(cands), det_conf=None if sel is None else f_(d["conf"][sel["j"]]), mean_keypoint_conf_used=f_(kmean),
                # --- LANDMARK OWNERSHIP EVIDENCE (mask-based; separate from identity)
                ownership_state=own_state, ownership_reasons=";".join(own_reasons), ownership_mask_only_state="" if sel is None else sel["os"], n_seg_instances=fs.n(),
                owner_mask_idx=None if om is None else om["owner"], owner_cover=None if om is None else f_(om["cover"]),
                own_only_frac=None if (om is None or om["owner"] is None) else f_(om["own_only_frac"]), contested_frac=None if (om is None or om["owner"] is None) else f_(om["contested_frac"]),
                other_only_frac=None if (om is None or om["owner"] is None) else f_(om["other_only_frac"]), outside_frac=None if (om is None or om["owner"] is None) else f_(om["outside_frac"]),
                opponent_landmarks_inside_mask_frac=None if (om is None or om["owner"] is None) else f_(om["opp_inside_frac"]), mask_unexplained_frac=None if (om is None or om["owner"] is None) else f_(om["unexplained_frac"]),
                bones_spanning_instances=None if (om is None or om["owner"] is None) else om["bones_span"], bones_leaving_mask=None if (om is None or om["owner"] is None) else om["bones_outside"],
                # --- ANATOMICAL PLAUSIBILITY (separate; cross-body cues listed apart)
                anatomy_plausibility="" if integ is None else integ["status"], anatomy_reasons="" if integ is None else ";".join(integ["plain"]), cross_body_cues="" if integ is None else ";".join(integ["cross_body"]), part_detail="" if integ is None else integ["parts"]["detail"],
                part_appearance_coherent_diagnostic_only=None if integ is None else bool(integ["parts"]["coherent"]),
                colour_region_own_mass=None if integ is None else integ["own_mass"], colour_region_contam_mass=None if integ is None else integ["contam_mass"],
                temporal_rel_median=None if (nf is None or nf["median_rel"] is None) else f_(nf["median_rel"]), temporal_fail_joints=None if nf is None else nf["fail_joints"],
                overlap_context_diagnostic=bool(ov_), merge_risk=bool(mr), overlap_detail="" if (integ is None or not integ["overlap_info"]) else json.dumps(integ["overlap_info"], default=float),
                # --- COM eligibility / support (separate)
                com_eligibility=com_elig, com_ineligible_reason=com_reason if com_elig == "INELIGIBLE" else "", visible_mass_fraction=None if np.isnan(vm) else round(vm, 3), visible_landmarks=nlm,
                com_segments_used=";".join(used_segs), com_landmarks_used=";".join(NAMES[i] for i in used_lms),
                com_landmarks_own_only=sum(1 for i in used_lms if om and om["cls"].get(i) == "OWN_ONLY"), com_landmarks_contested=sum(1 for i in used_lms if om and om["cls"].get(i) == "CONTESTED"), com_landmarks_outside_mask=sum(1 for i in used_lms if om and om["cls"].get(i) == "OUTSIDE"),
                # --- prediction
                frames_since_anchor=s_.since_anchor if (s_.anchor is not None and s_.since_anchor < 999) else None, prediction_anchor_frame=None if s_.anchor is None else s_.anchor["frame"], prediction_uncertainty_px=unc_px,
                bg_denim_fraction=None if np.isnan(bg) else round(bg, 3), colour_cue_valid=bool(cue_valid), probation_count=s_.probation if sel is not None else 0))
            if sel is not None:
                cls_ = {} if om is None else om["cls"]
                for i in range(17): lm.append(dict(frame=t, target=X, selected_det_index=sel["j"], landmark=NAMES[i], x_pixel=round(float(sel["kp"][i][0]), 2), y_pixel=round(float(sel["kp"][i][1]), 2), keypoint_conf=round(float(sel["kc"][i]), 4), ownership_class=cls_.get(i, ""), used_for_com=bool(emitted and i in used_lms), emitted_status=status if emitted else "NOT_EMITTED"))
        if neis: bb_ = max(neis, key=lambda c: (c["box"][2] - c["box"][0]) * (c["box"][3] - c["box"][1])); refst.update(box=bb_["box"].copy(), frame=t, seg=seg)
        # ---------------- annotation: FULL 640x360 source frame + external QC panel
        contours = {}
        for X in IDS:
            om = out[X]["om"]
            if om is not None and om["owner"] is not None:
                cs, _ = cv2.findContours(fs.masks[om["owner"]].astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); contours[X] = [(c_.reshape(-1, 2) / np.array([fs.sx, fs.sy])).astype(np.int32) for c_ in cs]
        vw.write(RD.compose(frame, dict(t=t, fps=fps, seg=seg, banner=banner, frames_since_cut=t - last_cut if last_cut >= 0 else None, transient=(t in transient), out=out, cands=[(c["box"], lab[c["j"]]) for c in cands], contours=contours, W=W, H=Hh), O, cfg.output))
    vw.release(); df = pd.DataFrame(rows); df.to_csv(os.path.join(out_dir, "tracking_v05.csv"), index=False)
    pd.DataFrame(lm).to_csv(os.path.join(out_dir, "tracking_v05_landmarks_raw.csv"), index=False); pd.DataFrame(crows).to_csv(os.path.join(out_dir, "candidates_v05.csv"), index=False)
    pd.DataFrame(events).to_csv(os.path.join(out_dir, "identity_ownership_events_v05.csv"), index=False); pd.DataFrame(plog).to_csv(os.path.join(out_dir, "prediction_log_v05.csv"), index=False)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(O.CRF), os.path.join(out_dir, "annotated_v05.mp4")], check=True); os.remove(tmp)
    json.dump(dict(config=json.load(open(config._PATH)), seeds=sd, seed_frames=seed_frames, colour_models=M.summary(), reid_model=RM.summary(), denim_rule=rule, denim_negative_evidence_for_B=denim_neg_for_B, seed_B_denim_coverage=seed_denim, n_frames=N), open(os.path.join(out_dir, "run_meta_v05.json"), "w"), indent=1, default=float)
    return df
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--video", required=True); ap.add_argument("--dets", required=True); ap.add_argument("--seg", required=True); ap.add_argument("--cuts", required=True); ap.add_argument("--seeds", required=True); ap.add_argument("--emb", required=True); ap.add_argument("--out_dir", required=True); ap.add_argument("--max_frames", type=int, default=None, help="smoke test only"); a = ap.parse_args()
    df = run(a.video, a.dets, a.seg, a.cuts, a.seeds, a.emb, a.out_dir, max_frames=a.max_frames)
    for X in IDS: print(X, df[df.target == X].status.value_counts().to_dict(), df[(df.target == X) & (df.status == "UNRESOLVED")].unresolved_reason.value_counts().to_dict(), df[df.target == X].ownership_state.value_counts().to_dict())
