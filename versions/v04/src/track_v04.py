"""V0.4 two-wrestler tracker. FAIL CLOSED. Identity state and COM/anatomy eligibility are SEPARATE states.
Inputs: video, cached pose detections (V0.1 stage-1 pkl), camera events json, manual seeds json, cached crop embeddings (embed_crops.py). Writes only into out_dir.
Design: docs/V0.4_ARCHITECTURE.md. All behavioural constants are in config_v04.json; NO frame-specific exceptions exist in this file.
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
import config, appearance as AP, integrity_v04 as IN, reid_v04 as RE
from com_model import compute_com, NAMES
IDS = ("A", "B"); OTHER = {"A": "B", "B": "A"}
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
    def __init__(s): s.reset_all()
    def reset_all(s): s.reset_spatial(); s.taint = False; s.amb_since_ind = False
    def reset_spatial(s):   # called at confirmed camera cuts: spatial / trajectory continuity is lost; appearance evidence is NOT stored per track (static seed models), so it needs no reset
        s.box = None; s.frame = None; s.S = None; s.lineage_box = None; s.lineage_gap = 999; s.probation = 0; s.prev_emit = None; s.anchor = None; s.vel = np.zeros(2); s.taint = False; s.since_anchor = 999
        s.last_ind = None; s.amb_since_ind = False
def run(video, dets_pkl, cuts_json, seeds_json, emb_npz, out_dir, cfg=None, max_frames=None):
    cfg = cfg or config.load(); P, A, DR, F, CT, ST, PR, O = cfg.pose, cfg.appearance, cfg.denim_rule, cfg.fusion, cfg.continuity, cfg.status, cfg.prediction, cfg.output
    ID, RC, AN, CL = cfg.identity, cfg.reid, cfg.anatomy, cfg.collapse
    os.makedirs(out_dir, exist_ok=True); dets = pickle.load(open(dets_pkl, "rb")); cj = json.load(open(cuts_json)); sd = json.load(open(seeds_json))
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
    tmp = os.path.join(out_dir, "annotated_v04.mp4.raw.mp4"); vw = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, Hh))
    rows = []; lm = []; crows = []; events = []; plog = []; seg = 0; last_cut = -999; st = {i: IdState() for i in IDS}
    def ev(t, X, kind, detail=""): events.append(dict(frame=t, target=X, event=kind, detail=detail))
    for t in range(N):
        ok, frame = cap.read()
        if not ok: break
        is_cut = t in cutset
        if is_cut:
            seg += 1; last_cut = t
            for i in IDS: st[i].reset_spatial(); ev(t, i, "CAMERA_CUT_SPATIAL_RESET")
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV); d = dets[t]; q = AP.quantize(frame, A); m = denim_mask(hsv, rule)
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
                    if s_.amb_since_ind and r["tier"] != "HIGH": r.update(sel=None, state="AMBIGUOUS", reason="REACQUISITION_UNCERTAIN", tier="", basis=""); ev(t, X, "REACQUISITION_UNCERTAIN", "independent support after loss following ambiguity; tier not HIGH")
                    else: ev(t, X, "REACQUISITION", f"tier={r['tier']}")
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
            row["denim_cov"] = round(c["den"][2], 3); row["denim_area"] = c["den"][3]; crows.append(row)
        banner = (t - last_cut) < O.BANNER_FRAMES and last_cut >= 0; out = {}
        # ---------------- per-wrestler: anatomy -> COM eligibility -> status; identity track updated independently of COM
        for X in IDS:
            Y = OTHER[X]; s_ = st[X]; dd = dec[X]; sel = dd["sel"]; reason = dd["reason"]; id_state = dd["state"]
            status = "UNRESOLVED"; com = None; integ = None; vm = float("nan"); nlm = 0; emitted = False; factors = []; ov_ = False; mr = False; com_elig = "NOT_EVALUATED"; com_reason = ""; ident_track = False; cred_now = None
            if sel is not None:
                j = sel["j"]; box = sel["box"]; kp = sel["kp"]; kc = sel["kc"]; obs = kc >= P.KP_CONF; ident_track = True
                if s_.lineage_box is not None and s_.lineage_gap <= CT.CONT_MAX_GAP and box_iou(box, s_.lineage_box) >= CT.LINEAGE_IOU_MIN: s_.probation += 1
                else: s_.probation = 1
                s_.lineage_box = box.copy(); s_.lineage_gap = 0
                Yb = st[Y].box; mr = bool(Yb is not None and dec[Y]["sel"] is None and (t - st[Y].frame) <= CT.MERGE_LOOKBACK and (box[0] <= ctr(Yb)[0] <= box[2] and box[1] <= ctr(Yb)[1] <= box[3] or box_iou(Yb, box) >= CT.MERGE_IOU))
                votes = AP.region_votes(sel["desc"], sel["dists"], M, X, Y, A); parts = IN.part_check(sel["reid"], X, AN)
                prev = None if s_.prev_emit is None else dict(s_.prev_emit, frame_gap=t - s_.prev_emit["frame"])
                integ = IN.evaluate(j, d, P.KP_CONF, cfg.integrity, prev, votes, mr, parts); ov_ = integ["overlap_context"]
                s_.box = box.copy(); s_.frame = t
                if integ["S"] is not None: s_.S = integ["S"]
                clean = integ["status"] != "FAIL"
                if id_state == "SUPPORTED_INDEPENDENT" and clean: s_.last_ind = t; s_.amb_since_ind = False
                cred_now = 1.0 if (s_.last_ind == t) else (ID.CRED_DECAY ** (t - s_.last_ind) if s_.last_ind is not None else 0.0)
                if integ["status"] == "FAIL": com_elig = "INELIGIBLE"; com_reason = "ANATOMY_FAIL"
                elif integ["status"] == "UNVERIFIED": com_elig = "INELIGIBLE"; com_reason = "OVERLAP_UNVERIFIED" if ov_ else "MERGE_RISK_UNVERIFIED"
                elif s_.probation < CT.PROBATION_FRAMES: com_elig = "INELIGIBLE"; com_reason = "PROBATION"
                else:
                    r = compute_com(kp, kc, P.KP_CONF); vm = r["visible_mass"]; nlm = r["n_landmarks"]; segs = r["segments"]
                    if r["com"] is None or vm < ST.PARTIAL_MASS: com_elig = "INELIGIBLE"; com_reason = "LOW_ANATOMY_MASS"
                    else:
                        com_elig = "ELIGIBLE"
                        if not (vm >= ST.MEASURED_MASS and segs.get("trunk")): factors.append("LOW_MASS")
                        if id_state != "SUPPORTED_INDEPENDENT": factors.append("IDENTITY_TEMPORAL_ONLY")
                        elif dd["tier"] != "HIGH": factors.append("IDENTITY_TIER_ACCEPT")
                        if integ["tier"] == "TEMPORAL_ONLY": factors.append("ANATOMY_TEMPORAL_ONLY")
                        elif integ["tier"] == "GEOMETRY_ONLY": factors.append("ANATOMY_GEOMETRY_ONLY")
                        status = "MEASURED" if not factors else "PARTIAL"; com = r["com"]; emitted = True; reason = ""
                        s_.vel = (PR.VEL_SMOOTH * s_.vel + (1 - PR.VEL_SMOOTH) * (com - s_.prev_emit["com"])) if (s_.prev_emit is not None and t - s_.prev_emit["frame"] == 1) else np.zeros(2)
                        s_.prev_emit = dict(kp=kp.copy(), obs=obs.copy(), S=integ["S"], frame=t, com=com.copy())
                        if status == "MEASURED": s_.anchor = dict(com=com.copy(), frame=t, box=box.copy()); s_.taint = False; s_.since_anchor = 0
                if not emitted: reason = com_reason
                if com_reason in ("ANATOMY_FAIL", "OVERLAP_UNVERIFIED", "MERGE_RISK_UNVERIFIED"): s_.taint = True; s_.amb_since_ind = True
            else:
                s_.lineage_gap += 1
                if id_state == "AMBIGUOUS": s_.taint = True; s_.amb_since_ind = True
            if s_.anchor is not None and not emitted: s_.since_anchor = t - s_.anchor["frame"]
            plog_row = None
            if status == "UNRESOLVED" and s_.anchor is not None and 0 < s_.since_anchor <= PR.MAX_PRED_GAP + 1:
                k = s_.since_anchor; allowed = (not s_.taint) and reason in ("NO_CANDIDATE", "IDENTITY_INSUFFICIENT_EVIDENCE", "IDENTITY_LOW_SCORE", "IDENTITY_CONTRA_CUE", "LOW_ANATOMY_MASS") and k <= PR.MAX_PRED_GAP
                pc = s_.anchor["com"] + s_.vel * k * PR.DAMP; bb = s_.anchor["box"]; mg = PR.BOX_MARGIN_DIAGS * diag(bb); inside_img = bool(0 <= pc[0] <= W and 0 <= pc[1] <= Hh)
                inside_box = bool((bb[0] - mg <= pc[0] <= bb[2] + mg) and (bb[1] - mg <= pc[1] <= bb[3] + mg))
                plog_row = dict(frame=t, target=X, anchor_frame=s_.anchor["frame"], frames_since_anchor=k, trigger_reason=reason, tainted=bool(s_.taint), pred_x=round(float(pc[0]), 2), pred_y=round(float(pc[1]), 2), inside_image=inside_img, within_anchor_box_bound=inside_box)
                if allowed and inside_img and inside_box:
                    status = "PREDICTED"; com = pc; reason = ""; factors = ["PREDICTION_NOT_A_MEASUREMENT"]; plog_row["decision"] = "PREDICTED"
                else:
                    plog_row["decision"] = "TERMINATED:" + ("TAINT_OR_AMBIGUITY" if (s_.taint or not (reason in ("NO_CANDIDATE", "IDENTITY_INSUFFICIENT_EVIDENCE", "IDENTITY_LOW_SCORE", "IDENTITY_CONTRA_CUE", "LOW_ANATOMY_MASS"))) else ("MAX_GAP" if k > PR.MAX_PRED_GAP else "OUT_OF_BOUNDS"))
                    if allowed and not (inside_img and inside_box): reason = "PREDICTION_OUT_OF_BOUNDS"
                if plog_row["decision"] == "PREDICTED":
                    plog_row["uncertainty_radius_px"] = round(float((PR.UNC_BASE_DIAGS + PR.UNC_PER_FRAME_DIAGS * k) * diag(bb)), 1); plog_row["decay_factor"] = round(PR.DECAY ** k, 4)
                plog.append(plog_row)
            # component fields (kept separate; no single confidence number)
            kmean = float(np.mean(sel["kc"][sel["kc"] >= P.KP_CONF])) if (sel is not None and (sel["kc"] >= P.KP_CONF).any()) else None
            ident_label = f"WRESTLER_{X}" if (id_state in ("SUPPORTED_INDEPENDENT", "TEMPORAL_CONTINUATION")) else f"WRESTLER_{X}_unassigned"
            if status == "PREDICTED": ident_label = f"WRESTLER_{X}(predicted_position_only)"
            out[X] = dict(status=status, com=com, reason=reason, sel=sel, state=id_state)
            nf = integ["temporal"] if integ else None
            rows.append(dict(frame=t, time_s=round(t / fps, 4), camera_segment=seg, camera_cut_confirmed=bool(is_cut), camera_transient_event=bool(t in transient), target=X,
                status=status, unresolved_reason=reason if status == "UNRESOLVED" else "", status_limiting_factors=";".join(factors),
                COM_x_pixel=None if com is None else round(float(com[0]), 2), COM_y_pixel=None if com is None else round(float(com[1]), 2), identity_label=ident_label,
                # --- IDENTITY (separate from COM)
                identity_state=id_state, identity_basis=dd.get("basis", ""), identity_tier=dd["tier"], identity_track_continues=bool(ident_track), identity_reason=dd["reason"] if id_state not in ("SUPPORTED_INDEPENDENT", "TEMPORAL_CONTINUATION") else "",
                ind_S=round(dd["S"], 3), ind_R=round(dd["R"], 3), ind_n_cues=dd["n"], anti_identity_margin_g=None if dd["g"] is None else round(dd["g"], 3), joint_assignment_margin=None if dd["jm"] is None else round(dd["jm"], 3),
                reid_S=None if sel is None else round(sel["fz_reid"][X][0], 3), reid_R=None if sel is None else round(sel["fz_reid"][X][1], 3), colour_S=None if sel is None else round(sel["fz_col"][X][0], 3), colour_R=None if sel is None else round(sel["fz_col"][X][1], 3),
                continuity_S=None if sel is None else round(sel["cont"][X][0], 3), continuity_R=None if sel is None else round(sel["cont"][X][1], 3), pose_consistency_S=None if sel is None else round(sel["pose"][X][0], 3), temporal_credit=None if cred_now is None else round(cred_now, 3),
                frames_since_independent_support=None if s_.last_ind is None else t - s_.last_ind,
                # --- DETECTION quality
                selected_det_index=None if sel is None else sel["j"], n_candidates=len(cands), det_conf=None if sel is None else round(float(d["conf"][sel["j"]]), 3), mean_keypoint_conf_used=None if kmean is None else round(kmean, 3),
                # --- ANATOMY (separate from identity)
                anatomy_status="" if integ is None else integ["status"], anatomy_tier="" if integ is None else integ["tier"], anatomy_reasons="" if integ is None else ";".join(integ["reasons"]),
                anatomy_positive_independent="" if integ is None else ";".join(integ["positive_independent"]), anatomy_positive_temporal="" if integ is None else ";".join(integ["positive_temporal"]), part_detail="" if integ is None else integ["parts"]["detail"],
                colour_region_own_mass=None if integ is None else integ["own_mass"], colour_region_contam_mass=None if integ is None else integ["contam_mass"],
                temporal_rel_median=None if (nf is None or nf["median_rel"] is None) else round(nf["median_rel"], 3), temporal_fail_joints=None if nf is None else nf["fail_joints"],
                overlap_context=bool(ov_), merge_risk=bool(mr), overlap_detail="" if (integ is None or not integ["overlap_info"]) else json.dumps(integ["overlap_info"], default=float),
                # --- COM eligibility (separate from identity)
                com_eligibility=com_elig, com_ineligible_reason=com_reason if com_elig == "INELIGIBLE" else "", visible_mass_fraction=None if np.isnan(vm) else round(vm, 3), visible_landmarks=nlm,
                # --- prediction
                frames_since_anchor=s_.since_anchor if (s_.anchor is not None and s_.since_anchor < 999) else None, prediction_anchor_frame=None if s_.anchor is None else s_.anchor["frame"],
                prediction_uncertainty_px=None if (plog_row is None or plog_row.get("decision") != "PREDICTED") else plog_row["uncertainty_radius_px"],
                bg_denim_fraction=None if np.isnan(bg) else round(bg, 3), colour_cue_valid=bool(cue_valid), probation_count=s_.probation if sel is not None else 0))
            if sel is not None:
                for i in range(17): lm.append(dict(frame=t, target=X, selected_det_index=sel["j"], landmark=NAMES[i], x_pixel=round(float(sel["kp"][i][0]), 2), y_pixel=round(float(sel["kp"][i][1]), 2), keypoint_conf=round(float(sel["kc"][i]), 4), used_for_com=bool(emitted and sel["kc"][i] >= P.KP_CONF), emitted_status=status if emitted else "NOT_EMITTED"))
        # ---------------- annotation
        im = frame.copy(); colid = {"A": (0, 200, 0), "B": (255, 0, 255)}
        for c in cands:
            x1, y1, x2, y2 = c["box"].astype(int); l = lab[c["j"]]
            if l in IDS: continue
            cv2.rectangle(im, (x1, y1), (x2, y2), (150, 150, 150), 1); cv2.putText(im, "N" if l == "NEITHER" else "?", (x1 + 3, y1 + 13), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 200), 1)
        for X in IDS:
            o = out[X]; sel = o["sel"]; col = colid[X]
            if sel is not None:
                x1, y1, x2, y2 = sel["box"].astype(int); cv2.rectangle(im, (x1, y1), (x2, y2), col, 2 if o["status"] in ("MEASURED", "PARTIAL") else 1)
                cv2.putText(im, X + ("" if o["state"] == "SUPPORTED_INDEPENDENT" else "~"), (x1 + 3, y1 + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.55, col, 2)
                if o["status"] in ("MEASURED", "PARTIAL"):
                    kp, kc = sel["kp"], sel["kc"]; bd_ = math.hypot(x2 - x1, y2 - y1)
                    for a, b in [(5,6),(5,7),(7,9),(6,8),(8,10),(5,11),(6,12),(11,12),(11,13),(13,15),(12,14),(14,16)]:
                        if kc[a] >= O.DISPLAY_KP_CONF and kc[b] >= O.DISPLAY_KP_CONF and np.hypot(*(kp[a]-kp[b])) <= O.MAX_BONE_FRAC_OF_BOX_DIAG * bd_: cv2.line(im, tuple(kp[a].astype(int)), tuple(kp[b].astype(int)), col, 1)
            if o["com"] is not None:
                cx, cy = int(o["com"][0]), int(o["com"][1])
                if o["status"] == "PREDICTED": cv2.circle(im, (cx, cy), 10, col, 1)
                else:
                    dia = np.array([[cx, cy-9], [cx+9, cy], [cx, cy+9], [cx-9, cy]], np.int32)
                    if o["status"] == "MEASURED": cv2.fillConvexPoly(im, dia, col)
                    cv2.polylines(im, [dia], True, (0, 0, 0) if o["status"] == "MEASURED" else col, 1 if o["status"] == "MEASURED" else 2)
                cv2.line(im, (cx-15, cy), (cx+15, cy), col, 1); cv2.line(im, (cx, cy-15), (cx, cy+15), col, 1); cv2.putText(im, f"{X} COM", (cx+11, cy-11), cv2.FONT_HERSHEY_SIMPLEX, 0.38, col, 1)
        cv2.rectangle(im, (0, 0), (W, 50), (0, 0, 0), -1); cv2.putText(im, f"V0.4 f{t} {t/fps:5.2f}s seg{seg}  (A=green B=magenta ~=temporal-only N=neither ?=uncertain)", (4, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        for yy, X in ((28, "A"), (44, "B")):
            o = out[X]; cv2.putText(im, f"{X}: {o['status']} {o['reason'][:24] if o['status'] == 'UNRESOLVED' else ''} id={o['state'][:14]}", (4, yy), cv2.FONT_HERSHEY_SIMPLEX, 0.4, colid[X], 1)
        if banner: cv2.putText(im, "CAMERA CUT - spatial continuity reset", (W//2-150, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        elif t in transient: cv2.putText(im, "TRANSIENT (not a cut)", (W//2-100, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 0, 255), 2)
        vw.write(im)
    vw.release(); df = pd.DataFrame(rows); df.to_csv(os.path.join(out_dir, "tracking_v04.csv"), index=False)
    pd.DataFrame(lm).to_csv(os.path.join(out_dir, "tracking_v04_landmarks_raw.csv"), index=False); pd.DataFrame(crows).to_csv(os.path.join(out_dir, "candidates_v04.csv"), index=False)
    pd.DataFrame(events).to_csv(os.path.join(out_dir, "identity_events_v04.csv"), index=False); pd.DataFrame(plog).to_csv(os.path.join(out_dir, "prediction_log_v04.csv"), index=False)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(O.CRF), os.path.join(out_dir, "annotated_v04.mp4")], check=True); os.remove(tmp)
    json.dump(dict(config=json.load(open(config._PATH)), seeds=sd, seed_frames=seed_frames, colour_models=M.summary(), reid_model=RM.summary(), denim_rule=rule, denim_negative_evidence_for_B=denim_neg_for_B, seed_B_denim_coverage=seed_denim, n_frames=N), open(os.path.join(out_dir, "run_meta_v04.json"), "w"), indent=1, default=float)
    return df
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--video", required=True); ap.add_argument("--dets", required=True); ap.add_argument("--cuts", required=True); ap.add_argument("--seeds", required=True); ap.add_argument("--emb", required=True); ap.add_argument("--out_dir", required=True); ap.add_argument("--max_frames", type=int, default=None, help="smoke test only"); a = ap.parse_args()
    df = run(a.video, a.dets, a.cuts, a.seeds, a.emb, a.out_dir, max_frames=a.max_frames)
    for X in IDS: print(X, df[df.target == X].status.value_counts().to_dict(), df[(df.target == X) & (df.status == "UNRESOLVED")].unresolved_reason.value_counts().to_dict(), df[df.target == X].identity_state.value_counts().to_dict())
