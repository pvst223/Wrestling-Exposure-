"""V0.3 two-wrestler tracker: multi-cue identity (A / B / NEITHER / UNCERTAIN) + single-body anatomical verification. FAIL CLOSED.
Inputs: video, cached pose detections (V0.1 stage-1 pkl, read-only), camera events json, manual seeds json. Writes only into out_dir.
See docs/V0.3_ARCHITECTURE_AND_CHANGELOG.md. All behavioural constants are in config_v03.json; NO frame-specific exceptions exist in this file."""
import sys, os, json, math, pickle, subprocess, argparse, cv2, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config, appearance as AP, integrity_v03 as IN
from com_model import compute_com, NAMES
IDS = ("A", "B"); OTHER = {"A": "B", "B": "A"}
def box_iou(a, b):
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]); i = max(0, x2-x1) * max(0, y2-y1)
    u = (a[2]-a[0])*(a[3]-a[1]) + (b[2]-b[0])*(b[3]-b[1]) - i; return i / u if u > 0 else 0.0
def diag(b): return math.hypot(b[2]-b[0], b[3]-b[1])
def ctr(b): return np.array([(b[0]+b[2])/2, (b[1]+b[3])/2])
# ---------------- optional clothing cue (denim), as in V0.2 but now ONE optional cue among several
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
# ---------------- fusion
def fuse(cues, F):
    """cues: list of (name, support in [-1,1], reliability in [0,1]). Reliability-weighted mean (equal cue weights). -> S, R(sum), n_present, contra, cue dict."""
    R = sum(r for _, _, r in cues)
    if R <= 0: return 0.0, 0.0, 0, False
    S = sum(r * s for _, s, r in cues) / R; n = sum(1 for _, _, r in cues if r >= F.CUE_PRESENT_R); contra = any(r >= F.CONTRA_R and s <= F.CONTRA_S for _, s, r in cues)
    return float(S), float(R), int(n), bool(contra)
class IdState:
    def __init__(s): s.reset()
    def reset(s): s.box = None; s.frame = None; s.S = None; s.lineage_box = None; s.lineage_gap = 999; s.probation = 0; s.prev_emit = None; s.anchor = None; s.vel = np.zeros(2); s.taint = False; s.since_anchor = 999
def run(video, dets_pkl, cuts_json, seeds_json, out_dir, cfg=None, max_frames=None):
    cfg = cfg or config.load(); P, A, DR, F, CT, ST, PR, O = cfg.pose, cfg.appearance, cfg.denim_rule, cfg.fusion, cfg.continuity, cfg.status, cfg.prediction, cfg.output
    os.makedirs(out_dir, exist_ok=True); dets = pickle.load(open(dets_pkl, "rb")); cj = json.load(open(cuts_json)); sd = json.load(open(seeds_json))
    cutset = {c["frame"] for c in cj["cuts"]}; transient = set(cj["transient_frames"])
    cap = cv2.VideoCapture(video); fps = cap.get(cv2.CAP_PROP_FPS); W = int(cap.get(3)); Hh = int(cap.get(4)); N = len(dets) if max_frames is None else min(len(dets), max_frames)   # max_frames: SMOKE-TEST ONLY
    # ---- manual seeds -> static appearance models (A, B, NEITHER) and the optional denim rule
    M = AP.Models(A); rule = None; seed_denim = {}
    for si, s in enumerate(sd["seeds"]):
        cap.set(cv2.CAP_PROP_POS_FRAMES, s["frame"]); ok, im = cap.read(); assert ok
        d0 = dets[s["frame"]]; kp0, kc0, b0 = d0["kp"][s["det"]], d0["kpc"][s["det"]], d0["box"][s["det"]]
        M.add(s["identity"], AP.quantize(im, A), kp0, kc0, b0)
        if si == sd["denim_calibration_seed_index"]: assert s["identity"] == "A"; rule = calibrate_denim(im, kp0, kc0, DR)
    M.finalize(); seed_frames = sorted({s["frame"] for s in sd["seeds"]})
    # does the denim rule also fire on B's seed thighs? if so, 'denim thighs' is NOT evidence against B (checked, not assumed)
    for si, s in enumerate(sd["seeds"]):
        if s["identity"] != "B": continue
        cap.set(cv2.CAP_PROP_POS_FRAMES, s["frame"]); ok, im = cap.read(); d0 = dets[s["frame"]]; pm = thigh_polys(im.shape[:2], d0["kp"][s["det"]], d0["kpc"][s["det"]], DR)
        if pm.sum() > 0: seed_denim[si] = float(denim_mask(cv2.cvtColor(im, cv2.COLOR_BGR2HSV), rule)[pm > 0].mean())
    denim_neg_for_B = bool(seed_denim) and max(seed_denim.values()) < DR.COV_LO
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    tmp = os.path.join(out_dir, "annotated_v03.mp4.raw.mp4"); vw = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, Hh))
    rows = []; lm = []; crows = []; seg = 0; last_cut = -999; st = {i: IdState() for i in IDS}
    for t in range(N):
        ok, frame = cap.read()
        if not ok: break
        is_cut = t in cutset
        if is_cut:
            seg += 1; last_cut = t
            for i in IDS: st[i].reset()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV); d = dets[t]; q = AP.quantize(frame, A); m = denim_mask(hsv, rule)
        occ = np.zeros(m.shape, bool)
        for o in range(len(d["conf"])):
            if d["conf"][o] >= P.RAW_OTHER_CONF:
                x1, y1, x2, y2 = [int(v) for v in d["box"][o]]; occ[max(0, y1):max(0, y2), max(0, x1):max(0, x2)] = True
        bg = float(m[~occ].mean()) if (~occ).sum() > 0 else float("nan")
        cue_valid = (not (bg > DR.BG_DENIM_MAX)) and (t not in transient)
        # ---------------- candidates and their cues
        cands = []
        for j in range(len(d["conf"])):
            b = d["box"][j]
            if d["conf"][j] < P.DET_CONF_GATE or (b[3]-b[1]) < P.MIN_BOX_H: continue
            kp, kc = d["kp"][j], d["kpc"][j]; desc = AP.descriptors(q, kp, kc, b, A); app, dists = AP.appearance_cues(desc, M, A)
            poly = thigh_polys(m.shape, kp, kc, DR); area = int(poly.sum()); cov = float(m[poly > 0].mean()) if area > 0 else 0.0
            den_ok = cue_valid and area >= DR.POLY_MIN_AREA_PX; den_s = float(np.clip(2 * (cov - DR.COV_LO) / (DR.COV_HI - DR.COV_LO) - 1, -1, 1)); den_r = min(1.0, area / (2 * DR.POLY_MIN_AREA_PX)) if den_ok else 0.0
            S_c = IN.body_scale(kp, kc >= P.KP_CONF, cfg.integrity)
            c = dict(j=j, box=b, kp=kp, kc=kc, desc=desc, dists=dists, app=app, den=(den_s, den_r, cov, area), S=S_c); cues = {}
            for X in IDS:
                cl = []
                if X in app: cl += [("app_reg",) + app[X]["reg"], ("app_whole",) + app[X]["whole"]]
                cl.append(("denim", den_s if X == "A" else (-den_s if denim_neg_for_B else 0.0), den_r if (X == "A" or denim_neg_for_B) else 0.0))
                s_ = st[X]; gap = None if s_.box is None else t - s_.frame
                if s_.box is not None and gap <= CT.CONT_MAX_GAP:
                    lim = min(CT.JUMP_CAP_DIAGS, CT.JUMP_BASE_DIAGS + CT.JUMP_PER_GAP_DIAGS * gap); disp = float(np.linalg.norm(ctr(b) - ctr(s_.box))) / max(diag(s_.box), 1e-6)
                    sr = (b[3]-b[1]) / max(s_.box[3]-s_.box[1], 1e-6); iou = box_iou(b, s_.box)
                    sc = -1.0 if not (CT.CONT_SCALE_MIN <= sr <= CT.CONT_SCALE_MAX) else 1.0 - 2.0 * min(1.0, disp / lim)
                    if sc > -1.0 and iou >= CT.CONT_IOU_MIN: sc = max(sc, CT.CONT_IOU_SUPPORT)
                    rc = max(0.0, 1.0 - gap / (CT.CONT_MAX_GAP + 1)); cl.append(("cont", sc, rc))
                    if S_c is not None and s_.S is not None:
                        sp = 1.0 - 2.0 * min(1.0, abs(math.log(S_c / s_.S)) / math.log(F.POSE_SCALE_RANGE)); cl.append(("pose", sp, F.POSE_R_CAP * rc))
                cues[X] = cl
            c["cues"] = cues; c["fused"] = {X: fuse(cues[X], F) for X in IDS}
            if "NEITHER" in app: c["fused_N"] = fuse([("app_reg",) + app["NEITHER"]["reg"], ("app_whole",) + app["NEITHER"]["whole"]], F)
            else: c["fused_N"] = (-1.0, 0.0, 0, False)
            cands.append(c)
        # ---------------- identity decision per wrestler (relative evidence: other candidates, other wrestler, NEITHER)
        dec = {}
        for X in IDS:
            Y = OTHER[X]; r = dict(sel=None, reason="", tier="", S=0.0, R=0.0, n=0, m_c=None, m_x=None)
            if not cands: r["reason"] = "NO_CANDIDATE"
            else:
                order = sorted(cands, key=lambda c: -c["fused"][X][0]); c0 = order[0]; S0, R0, n0, contra0 = c0["fused"][X]
                r.update(S=S0, R=R0, n=n0); s2 = order[1]["fused"][X][0] if len(order) > 1 else -1.0; alt = max(c0["fused"][Y][0], c0["fused_N"][0])
                r["m_c"] = S0 - s2; r["m_x"] = S0 - alt
                if R0 < F.R_MIN or n0 < F.N_CUES_MIN: r["reason"] = "IDENTITY_INSUFFICIENT_EVIDENCE"
                elif contra0: r["reason"] = "IDENTITY_CONTRA_CUE"
                elif S0 < F.S_MIN: r["reason"] = "IDENTITY_LOW_SCORE"
                elif r["m_c"] < F.MARGIN: r["reason"] = "IDENTITY_AMBIGUOUS_CANDIDATES"
                elif r["m_x"] < F.MARGIN: r["reason"] = "IDENTITY_AMBIGUOUS_COMPETITOR"
                else: r["sel"] = c0; r["tier"] = "HIGH" if (S0 >= F.S_HIGH and R0 >= F.R_HIGH and n0 >= F.N_HIGH) else "ACCEPT"
            dec[X] = r
        lab = {}
        for c in cands:
            if dec["A"]["sel"] is c: lab[c["j"]] = "A"
            elif dec["B"]["sel"] is c: lab[c["j"]] = "B"
            else:
                sA, rA, _, _ = c["fused"]["A"]; sB, rB, _, _ = c["fused"]["B"]; sN, rN, _, _ = c["fused_N"]
                if rN >= F.R_MIN and sN >= F.S_MIN and sN - max(sA, sB) >= F.MARGIN: lab[c["j"]] = "NEITHER"
                elif min(rA, rB) >= F.R_MIN and max(sA, sB) <= F.NEITHER_FIT_MAX: lab[c["j"]] = "NEITHER"
                else: lab[c["j"]] = "UNCERTAIN"
            c_ = c; fa, fb = c["fused"]["A"], c["fused"]["B"]
            crows.append(dict(frame=t, det=c["j"], det_conf=round(float(d["conf"][c["j"]]), 3), x1=round(float(c["box"][0]), 1), y1=round(float(c["box"][1]), 1), x2=round(float(c["box"][2]), 1), y2=round(float(c["box"][3]), 1),
                S_A=round(fa[0], 3), R_A=round(fa[1], 3), nA=fa[2], S_B=round(fb[0], 3), R_B=round(fb[1], 3), nB=fb[2], S_N=round(c["fused_N"][0], 3), R_N=round(c["fused_N"][1], 3), label=lab[c["j"]],
                **{f"{X}_{k}_s": round(s, 3) for X in IDS for (k, s, r) in c["cues"][X]}, **{f"{X}_{k}_r": round(r, 3) for X in IDS for (k, s, r) in c["cues"][X]}))
        banner = (t - last_cut) < O.BANNER_FRAMES and last_cut >= 0; out = {}
        for X in IDS:
            Y = OTHER[X]; s_ = st[X]; dd = dec[X]; sel = dd["sel"]; reason = dd["reason"]
            status = "UNRESOLVED"; com = None; eq = 0.0; integ = None; vm = float("nan"); nlm = 0; emitted = False; id_basis = "none"; ident = f"WRESTLER_{X}_unassigned"; factors = []; ov_ = False; mr = False; ants = ""
            if sel is not None:
                j = sel["j"]; box = sel["box"]; kp = sel["kp"]; kc = sel["kc"]; obs = kc >= P.KP_CONF
                if s_.lineage_box is not None and s_.lineage_gap <= CT.CONT_MAX_GAP and box_iou(box, s_.lineage_box) >= CT.LINEAGE_IOU_MIN: s_.probation += 1
                else: s_.probation = 1
                s_.lineage_box = box.copy(); s_.lineage_gap = 0
                cont_used = any(k == "cont" and r >= F.CUE_PRESENT_R for (k, s, r) in sel["cues"][X]); id_basis = "multi_cue+continuity" if cont_used else "multi_cue_no_continuity"; ident = f"WRESTLER_{X}"
                Yb = st[Y].box; mr = bool(Yb is not None and dec[Y]["sel"] is None and (t - st[Y].frame) <= CT.MERGE_LOOKBACK and (box[0] <= ctr(Yb)[0] <= box[2] and box[1] <= ctr(Yb)[1] <= box[3] or box_iou(Yb, box) >= CT.MERGE_IOU))
                votes = AP.region_votes(sel["desc"], sel["dists"], M, X, Y, A)
                prev = None if s_.prev_emit is None else dict(s_.prev_emit, frame_gap=t - s_.prev_emit["frame"])
                integ = IN.evaluate(j, d, P.KP_CONF, cfg.integrity, prev, votes, mr); ov_ = integ["overlap_context"]
                s_.box = box.copy(); s_.frame = t
                if integ["S"] is not None: s_.S = integ["S"]
                if integ["status"] == "FAIL": reason = "ANATOMY_FAIL"
                elif integ["status"] == "UNVERIFIED": reason = "OVERLAP_UNVERIFIED" if ov_ else "MERGE_RISK_UNVERIFIED"
                elif s_.probation < CT.PROBATION_FRAMES: reason = "PROBATION"
                else:
                    r = compute_com(kp, kc, P.KP_CONF); vm = r["visible_mass"]; nlm = r["n_landmarks"]; segs = r["segments"]
                    if r["com"] is None or vm < ST.PARTIAL_MASS: reason = "LOW_ANATOMY_MASS"
                    else:
                        if not (vm >= ST.MEASURED_MASS and segs.get("trunk")): factors.append("LOW_MASS")
                        if dd["tier"] != "HIGH": factors.append("IDENTITY_TIER_ACCEPT")
                        if integ["tier"] != "VERIFIED": factors.append("ANATOMY_GEOMETRY_ONLY")
                        status = "MEASURED" if not factors else "PARTIAL"; com = r["com"]; emitted = True; reason = ""
                        mk = float(np.mean(kc[obs])) if obs.any() else 0.0; aq = 1.0 if integ["tier"] == "VERIFIED" else ST.ANATOMY_GEOMETRY_ONLY_QUALITY
                        eq = float(min(max(0.0, dd["S"]), aq, mk, min(1.0, vm)))
                        s_.vel = (PR.VEL_SMOOTH * s_.vel + (1 - PR.VEL_SMOOTH) * (com - s_.prev_emit["com"])) if (s_.prev_emit is not None and t - s_.prev_emit["frame"] == 1) else np.zeros(2)
                        s_.prev_emit = dict(kp=kp.copy(), obs=obs.copy(), S=integ["S"], frame=t, com=com.copy())
                        if status == "MEASURED": s_.anchor = dict(com=com.copy(), frame=t, box=box.copy(), eq=eq); s_.taint = False; s_.since_anchor = 0
                if reason in ("ANATOMY_FAIL", "OVERLAP_UNVERIFIED", "MERGE_RISK_UNVERIFIED"): s_.taint = True
            else:
                s_.lineage_gap += 1
                if reason in ("IDENTITY_AMBIGUOUS_CANDIDATES", "IDENTITY_AMBIGUOUS_COMPETITOR"): s_.taint = True   # CONTRA/LOW_SCORE = best candidate is clearly someone else: not a corruption risk
            if s_.anchor is not None and not emitted: s_.since_anchor = t - s_.anchor["frame"]
            if status == "UNRESOLVED" and s_.anchor is not None and not s_.taint and reason in ("NO_CANDIDATE", "IDENTITY_INSUFFICIENT_EVIDENCE", "IDENTITY_LOW_SCORE", "IDENTITY_CONTRA_CUE", "LOW_ANATOMY_MASS") and 0 < s_.since_anchor <= PR.MAX_PRED_GAP:
                k = s_.since_anchor; pc = s_.anchor["com"] + s_.vel * k * PR.DAMP; inside_img = 0 <= pc[0] <= W and 0 <= pc[1] <= Hh; bb = s_.anchor["box"]; mg = PR.BOX_MARGIN_DIAGS * diag(bb)
                inside_box = (bb[0] - mg <= pc[0] <= bb[2] + mg) and (bb[1] - mg <= pc[1] <= bb[3] + mg)
                if inside_img and inside_box: status = "PREDICTED"; com = pc; eq = s_.anchor["eq"] * (PR.DECAY ** k); ident = f"WRESTLER_{X}(predicted)"; id_basis = "prediction"; reason = ""; factors = ["PREDICTION_NOT_A_MEASUREMENT"]
                else: reason = "PREDICTION_OUT_OF_BOUNDS"
            if status == "UNRESOLVED" and sel is not None and ident == f"WRESTLER_{X}": ident = f"WRESTLER_{X}(candidate_unverified)"
            out[X] = dict(status=status, com=com, reason=reason, sel=sel)
            nf = integ["temporal"] if integ else None
            rows.append(dict(frame=t, time_s=round(t / fps, 4), camera_segment=seg, camera_cut_confirmed=bool(is_cut), camera_transient_event=bool(t in transient), target=X, identity=ident, identity_basis=id_basis, status=status,
                unresolved_reason=reason if status == "UNRESOLVED" else "", status_limiting_factors=";".join(factors),
                COM_x_pixel=None if com is None else round(float(com[0]), 2), COM_y_pixel=None if com is None else round(float(com[1]), 2), evidence_quality_ordinal=round(eq, 4),
                identity_S=round(dd["S"], 3), identity_R=round(dd["R"], 3), identity_n_cues=dd["n"], identity_tier=dd["tier"], margin_vs_other_candidates=None if dd["m_c"] is None else round(dd["m_c"], 3), margin_vs_competitor=None if dd["m_x"] is None else round(dd["m_x"], 3),
                selected_det_index=None if sel is None else sel["j"], n_candidates=len(cands), probation_count=s_.probation if sel is not None else 0,
                anatomy_tier="" if integ is None else (integ["tier"] if integ["status"] != "UNVERIFIED" else "UNVERIFIED"), integrity_status="" if integ is None else integ["status"], integrity_reasons="" if integ is None else ";".join(integ["reasons"]),
                positive_coherence="" if integ is None else ";".join(integ["positive"]), appearance_own_mass=None if integ is None else integ["own_mass"], appearance_contam_mass=None if integ is None else integ["contam_mass"],
                temporal_rel_median=None if (nf is None or nf["median_rel"] is None) else round(nf["median_rel"], 3), temporal_fail_joints=None if nf is None else nf["fail_joints"],
                overlap_context=bool(ov_), merge_risk=bool(mr), overlap_detail="" if (integ is None or not integ["overlap_info"]) else json.dumps(integ["overlap_info"], default=float),
                visible_mass_fraction=None if np.isnan(vm) else round(vm, 3), visible_landmarks=nlm, bg_denim_fraction=None if np.isnan(bg) else round(bg, 3), colour_cue_valid=bool(cue_valid),
                frames_since_anchor=s_.since_anchor if (s_.anchor is not None and s_.since_anchor < 999) else None, prediction_anchor_frame=None if s_.anchor is None else s_.anchor["frame"]))
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
                x1, y1, x2, y2 = sel["box"].astype(int); cv2.rectangle(im, (x1, y1), (x2, y2), col, 2 if o["status"] in ("MEASURED", "PARTIAL") else 1); cv2.putText(im, X, (x1 + 3, y1 + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.55, col, 2)
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
        cv2.rectangle(im, (0, 0), (W, 50), (0, 0, 0), -1); cv2.putText(im, f"V0.3 f{t} {t/fps:5.2f}s seg{seg}  (A=green B=magenta N=neither ?=uncertain)", (4, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        for yy, X in ((28, "A"), (44, "B")):
            o = out[X]; cv2.putText(im, f"{X}: {o['status']} {o['reason'][:30] if o['status'] == 'UNRESOLVED' else ''}", (4, yy), cv2.FONT_HERSHEY_SIMPLEX, 0.42, colid[X], 1)
        if banner: cv2.putText(im, "CAMERA CUT - tracks reset", (W//2-110, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        elif t in transient: cv2.putText(im, "TRANSIENT (not a cut)", (W//2-100, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 0, 255), 2)
        vw.write(im)
    vw.release(); df = pd.DataFrame(rows); df.to_csv(os.path.join(out_dir, "tracking_v03.csv"), index=False)
    pd.DataFrame(lm).to_csv(os.path.join(out_dir, "tracking_v03_landmarks_raw.csv"), index=False); pd.DataFrame(crows).to_csv(os.path.join(out_dir, "candidates_v03.csv"), index=False)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(O.CRF), os.path.join(out_dir, "annotated_v03.mp4")], check=True); os.remove(tmp)
    json.dump(dict(config=json.load(open(config._PATH)), seeds=sd, seed_frames=seed_frames, appearance_models=M.summary(), denim_rule=rule, denim_negative_evidence_for_B=denim_neg_for_B, seed_B_denim_coverage=seed_denim, n_frames=N), open(os.path.join(out_dir, "run_meta_v03.json"), "w"), indent=1, default=float)
    return df
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--video", required=True); ap.add_argument("--dets", required=True); ap.add_argument("--cuts", required=True); ap.add_argument("--seeds", required=True); ap.add_argument("--out_dir", required=True); ap.add_argument("--max_frames", type=int, default=None, help="smoke test only"); a = ap.parse_args()
    df = run(a.video, a.dets, a.cuts, a.seeds, a.out_dir, max_frames=a.max_frames)
    for X in IDS: print(X, df[df.target == X].status.value_counts().to_dict(), df[(df.target == X) & (df.status == "UNRESOLVED")].unresolved_reason.value_counts().to_dict())
