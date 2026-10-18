"""V0.2 single-target tracker. FAIL CLOSED: a COM is emitted only when identity evidence (multi-condition), body integrity and probation all pass.
Reads V0.1's cached pose detections (raw_detections.pkl, read-only) and V0.2's own cut events. V0.1 files are never modified."""
import sys, os, json, math, pickle, subprocess, cv2, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config, integrity
from com_model import compute_com, NAMES
def box_iou(a, b):
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]); i = max(0, x2-x1) * max(0, y2-y1)
    u = (a[2]-a[0])*(a[3]-a[1]) + (b[2]-b[0])*(b[3]-b[1]) - i; return i / u if u > 0 else 0.0
def diag(b): return math.hypot(b[2]-b[0], b[3]-b[1])
def ctr(b): return np.array([(b[0]+b[2])/2, (b[1]+b[3])/2])
def calibrate_denim(frame, kp, kc, cfg):
    S, R = cfg.seed, cfg.denim_rule
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV); m = np.zeros(frame.shape[:2], np.uint8)
    for h, k in ((11, 13), (12, 14)):
        if kc[h] > S.KP_CONF and kc[k] > S.KP_CONF:
            p, q = kp[h], kp[k]; v = q - p; n = np.array([-v[1], v[0]]) / (np.linalg.norm(v) + 1e-6); w = R.THIGH_POLY_HALFWIDTH * np.linalg.norm(v)
            cv2.fillConvexPoly(m, np.array([p+n*w, p-n*w, q-n*w, q+n*w]).astype(np.int32), 1)
    px = hsv[m > 0]; assert len(px) > S.MIN_PIXELS
    H = px[:, 0].astype(float); Sa = px[:, 1].astype(float); V = px[:, 2].astype(float); hmed = np.median(H)
    hs = float(np.clip(R.H_SPREAD_MAD_MULT * np.median(np.abs(H - hmed)), R.H_SPREAD_MIN, R.H_SPREAD_MAX))
    return dict(h_lo=hmed-hs, h_hi=hmed+hs, s_lo=max(float(R.S_FLOOR), np.percentile(Sa, R.S_PCT)*R.S_SCALE), v_lo=np.percentile(V, R.V_PCT_LO)*R.V_SCALE_LO, v_hi=min(255., np.percentile(V, R.V_PCT_HI)*R.V_SCALE_HI), n_seed_px=int(len(px)), h_med=float(hmed))
def denim_mask(hsv, r): return (hsv[..., 0] >= r["h_lo"]) & (hsv[..., 0] <= r["h_hi"]) & (hsv[..., 1] >= r["s_lo"]) & (hsv[..., 2] >= r["v_lo"]) & (hsv[..., 2] <= r["v_hi"])
def thigh_polys(shape, kp, kc, cfg):
    P = np.zeros(shape, np.uint8); hw = cfg.denim_rule.THIGH_POLY_HALFWIDTH
    for h, k in ((11, 13), (12, 14)):
        if kc[h] >= cfg.identity.POLY_KP_CONF and kc[k] >= cfg.identity.POLY_KP_CONF:
            p, q = kp[h], kp[k]; v = q - p; n = np.array([-v[1], v[0]]) / (np.linalg.norm(v) + 1e-6); w = hw * np.linalg.norm(v)
            cv2.fillConvexPoly(P, np.array([p+n*w, p-n*w, q-n*w, q+n*w]).astype(np.int32), 1)
    return P
def run(video, dets_pkl, cuts_json, out_csv, out_mp4, out_meta, cfg=None):
    cfg = cfg or config.load(); P, I, ST, PR, O = cfg.pose, cfg.identity, cfg.status, cfg.prediction, cfg.output
    dets = pickle.load(open(dets_pkl, "rb")); cj = json.load(open(cuts_json))
    cutset = {c["frame"] for c in cj["cuts"]}; transient = set(cj["transient_frames"])
    cap = cv2.VideoCapture(video); fps = cap.get(cv2.CAP_PROP_FPS); W = int(cap.get(3)); Hh = int(cap.get(4)); N = len(dets)
    cap.set(cv2.CAP_PROP_POS_FRAMES, cfg.seed.FRAME); ok, sf = cap.read(); d0 = dets[cfg.seed.FRAME]; sj = cfg.seed.DET_INDEX
    rule = calibrate_denim(sf, d0["kp"][sj], d0["kpc"][sj], cfg); cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    tmp = out_mp4 + ".raw.mp4"; vw = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, Hh))
    rows = []; lm = []; seg = 0; last_cut = -999
    # shot-level state
    chain_box = None; chain_gap = 999; lineage_box = None; lineage_gap = 999; probation = 0
    prev_emit = None   # dict(kp,obs,S,frame_gap) of last emitted skeleton
    anchor = None      # dict(com,frame,box,eq,vel) of last emitted MEASURED
    vel = np.zeros(2); taint = False; since_anchor = 999
    for t in range(N):
        ok, frame = cap.read()
        if not ok: break
        is_cut = t in cutset
        if is_cut:
            seg += 1; last_cut = t; chain_box = None; chain_gap = 999; lineage_box = None; lineage_gap = 999; probation = 0; prev_emit = None; anchor = None; vel = np.zeros(2); taint = False; since_anchor = 999
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV); d = dets[t]; m = denim_mask(hsv, rule)
        occ = np.zeros(m.shape, bool)
        for o in range(len(d["conf"])):
            if d["conf"][o] >= P.RAW_OTHER_CONF:
                x1, y1, x2, y2 = [int(v) for v in d["box"][o]]; occ[max(0, y1):max(0, y2), max(0, x1):max(0, x2)] = True
        bg = float(m[~occ].mean()) if (~occ).sum() > 0 else float("nan")
        cue_valid = (not (bg > I.BG_DENIM_MAX)) and (t not in transient)
        # ---- candidates
        cands = []
        for j in range(len(d["conf"])):
            b = d["box"][j]
            if d["conf"][j] < P.DET_CONF_GATE or (b[3]-b[1]) < P.MIN_BOX_H: continue
            poly = thigh_polys(m.shape, d["kp"][j], d["kpc"][j], cfg); area = int(poly.sum()); cov = float(m[poly > 0].mean()) if area > 0 else 0.0
            alive = chain_box is not None and chain_gap <= I.CONT_MAX_GAP
            cont_ok = False; veto = False
            if alive:
                lim = min(I.JUMP_CAP_DIAGS, I.JUMP_BASE_DIAGS + I.JUMP_PER_GAP_DIAGS * chain_gap)
                disp = float(np.linalg.norm(ctr(b) - ctr(chain_box))) / max(diag(chain_box), 1e-6); sr = (b[3]-b[1]) / max(chain_box[3]-chain_box[1], 1e-6)
                scale_ok = I.CONT_SCALE_MIN <= sr <= I.CONT_SCALE_MAX
                cont_ok = scale_ok and (box_iou(b, chain_box) >= I.CONT_IOU_MIN or disp <= lim); veto = not cont_ok
            app_ok = cue_valid and area >= I.POLY_MIN_AREA_PX and cov >= I.APP_COV_MIN
            cands.append(dict(j=j, cov=cov, area=area, cont=cont_ok, veto=veto, app=app_ok, passes=app_ok and not veto, score=cov + I.CONT_BONUS * cont_ok))
        passers = sorted([c for c in cands if c["passes"]], key=lambda c: -c["score"])
        reason = ""; sel = None
        if passers:
            sel = passers[0]
            if len(passers) > 1 and passers[0]["score"] - passers[1]["score"] < I.AMBIG_MARGIN and not (passers[0]["cont"] and not passers[1]["cont"]): reason = "IDENTITY_AMBIGUOUS"; sel = None
        else:
            if not cands: reason = "NO_CANDIDATE"
            elif not cue_valid: reason = "COLOUR_CUE_INVALID_PHOTOMETRIC"
            elif all(c["veto"] and c["app"] for c in cands): reason = "IDENTITY_JUMP_VETO"
            elif any(c["app"] and c["veto"] for c in cands): reason = "IDENTITY_JUMP_VETO"
            else: reason = "IDENTITY_NOT_MATCHED"
        status = "UNRESOLVED"; com = None; eq = 0.0; integ = dict(status="", reasons=[], overlap_context=False, overlap_info=[]); vm = float("nan"); nlm = 0; segs = {}; emitted = False; id_basis = "none"; ident = "unassigned"
        idev = 0.0
        if sel is not None:
            j = sel["j"]; box = d["box"][j]; kp = d["kp"][j]; kc = d["kpc"][j]
            # lineage / probation (identity-passing frames only)
            if lineage_box is not None and lineage_gap <= I.CONT_MAX_GAP and box_iou(box, lineage_box) >= I.LINEAGE_IOU_MIN: probation += 1
            else: probation = 1
            lineage_box = box.copy(); lineage_gap = 0
            id_basis = "appearance+continuity" if sel["cont"] else "appearance_only"; ident = "Cena(candidate)"
            idev = min(1.0, sel["cov"] / I.APP_COV_REF) * (1.0 if sel["cont"] or probation >= I.PROBATION_FRAMES else I.CONT_WEAK_FACTOR)
            obs = kc >= P.KP_CONF
            integ = integrity.evaluate(j, d, P.KP_CONF, cfg.integrity, prev_emit if prev_emit is None else dict(prev_emit, frame_gap=t - prev_emit["frame"]))
            chain_box = box.copy(); chain_gap = 0      # chain updated on identity pass (integrity only gates EMISSION)
            if integ["status"] == "FAIL": reason = "INTEGRITY_FAIL"
            elif integ["status"] == "OVERLAP_UNVERIFIED": reason = "OVERLAP_UNVERIFIED"
            elif probation < I.PROBATION_FRAMES: reason = "PROBATION"
            else:
                r = compute_com(kp, kc, P.KP_CONF); vm = r["visible_mass"]; nlm = r["n_landmarks"]; segs = r["segments"]
                if r["com"] is None or vm < ST.PARTIAL_MASS: reason = "LOW_ANATOMY_MASS"
                else:
                    status = "MEASURED" if (vm >= ST.MEASURED_MASS and segs.get("trunk")) else "PARTIAL"; com = r["com"]; emitted = True; ident = "Cena"
                    mk = float(np.mean(kc[obs])) if obs.any() else 0.0; eq = float(min(idev, mk, min(1.0, vm))); reason = ""
                    vel = (PR.VEL_SMOOTH * vel + (1 - PR.VEL_SMOOTH) * (com - prev_emit["com"])) if (prev_emit is not None and t - prev_emit["frame"] == 1) else np.zeros(2)   # velocity only from CONSECUTIVE emitted frames (fixes V0.1 multi-frame-gap quirk)
                    prev_emit = dict(kp=kp.copy(), obs=obs.copy(), S=integ["S"], frame=t, com=com.copy())
                    if status == "MEASURED": anchor = dict(com=com.copy(), frame=t, box=box.copy(), eq=eq); taint = False; since_anchor = 0
            if reason in ("INTEGRITY_FAIL", "OVERLAP_UNVERIFIED", "IDENTITY_AMBIGUOUS"): taint = True
        else:
            chain_gap += 1; lineage_gap += 1
            if reason in ("IDENTITY_AMBIGUOUS", "IDENTITY_JUMP_VETO"): taint = True
        if anchor is not None and not emitted: since_anchor = t - anchor["frame"]
        # ---- prediction (explicit, bounded, never off-image)
        if status == "UNRESOLVED" and anchor is not None and not taint and reason in ("NO_CANDIDATE", "IDENTITY_NOT_MATCHED", "LOW_ANATOMY_MASS") and 0 < since_anchor <= PR.MAX_PRED_GAP:
            k = since_anchor; pc = anchor["com"] + vel * k * PR.DAMP
            inside_img = 0 <= pc[0] <= W and 0 <= pc[1] <= Hh; bb = anchor["box"]; mg = PR.BOX_MARGIN_DIAGS * diag(bb)
            inside_box = (bb[0] - mg <= pc[0] <= bb[2] + mg) and (bb[1] - mg <= pc[1] <= bb[3] + mg)
            if inside_img and inside_box: status = "PREDICTED"; com = pc; eq = anchor["eq"] * (PR.DECAY ** k); ident = "Cena(predicted)"; id_basis = "prediction"; reason = ""
            else: reason = "PREDICTION_OUT_OF_BOUNDS"
        if status == "UNRESOLVED" and ident == "unassigned" and sel is not None: ident = "Cena(candidate_unverified)"
        banner = (t - last_cut) < O.BANNER_FRAMES and last_cut >= 0
        rows.append(dict(frame=t, time_s=round(t / fps, 4), camera_segment=seg, camera_cut_confirmed=bool(is_cut), camera_transient_event=bool(t in transient),
            identity=ident, identity_basis=id_basis, status=status, unresolved_reason=reason if status == "UNRESOLVED" else "",
            COM_x_pixel=None if com is None else round(float(com[0]), 2), COM_y_pixel=None if com is None else round(float(com[1]), 2),
            evidence_quality_ordinal=round(eq, 4), identity_evidence=round(idev, 3), visible_mass_fraction=None if np.isnan(vm) else round(vm, 3), visible_landmarks=nlm,
            selected_det_index=None if sel is None else sel["j"], thigh_poly_denim_coverage=None if sel is None else round(sel["cov"], 3), thigh_poly_area_px=None if sel is None else sel["area"],
            bg_denim_fraction=None if np.isnan(bg) else round(bg, 3), colour_cue_valid=bool(cue_valid), n_candidates=len(cands), n_identity_passers=len(passers), max_cand_coverage=None if not cands else round(max(c['cov'] for c in cands),3), max_cand_poly_area=None if not cands else max(c['area'] for c in cands), n_cands_jump_veto=sum(1 for c in cands if c['veto']),
            continuity_ok=None if sel is None else bool(sel["cont"]), probation_count=probation if sel is not None else 0,
            integrity_status=integ["status"], integrity_reasons=";".join(integ["reasons"]), overlap_context=bool(integ["overlap_context"]),
            overlap_detail=json.dumps(integ["overlap_info"], default=float) if integ["overlap_info"] else "", frames_since_anchor=since_anchor if (anchor is not None and since_anchor < 999) else None,
            prediction_anchor_frame=None if anchor is None else anchor["frame"]))
        if sel is not None:
            for i in range(17): lm.append(dict(frame=t, selected_det_index=sel["j"], landmark=NAMES[i], x_pixel=round(float(d["kp"][sel["j"]][i][0]), 2), y_pixel=round(float(d["kp"][sel["j"]][i][1]), 2), keypoint_conf=round(float(d["kpc"][sel["j"]][i]), 4), used_for_com=bool(emitted and d["kpc"][sel["j"]][i] >= P.KP_CONF), emitted_status=status if emitted else "NOT_EMITTED"))
        # ---- annotation
        im = frame.copy(); col = dict(MEASURED=(0, 200, 0), PARTIAL=(0, 215, 255), PREDICTED=(0, 140, 255), UNRESOLVED=(0, 0, 230))
        for o in range(len(d["conf"])):
            if d["conf"][o] >= P.DET_CONF_GATE and (d["box"][o][3]-d["box"][o][1]) >= P.MIN_BOX_H and (sel is None or o != sel["j"]):
                x1, y1, x2, y2 = d["box"][o].astype(int); cv2.rectangle(im, (x1, y1), (x2, y2), (150, 150, 150), 1)
        if sel is not None:
            x1, y1, x2, y2 = d["box"][sel["j"]].astype(int); cv2.rectangle(im, (x1, y1), (x2, y2), col[status], 1)
            if emitted:
                kp = d["kp"][sel["j"]]; kc = d["kpc"][sel["j"]]; bd_ = math.hypot(x2-x1, y2-y1)
                for a, b in [(5,6),(5,7),(7,9),(6,8),(8,10),(5,11),(6,12),(11,12),(11,13),(13,15),(12,14),(14,16)]:
                    if kc[a] >= O.DISPLAY_KP_CONF and kc[b] >= O.DISPLAY_KP_CONF and np.hypot(*(kp[a]-kp[b])) <= O.MAX_BONE_FRAC_OF_BOX_DIAG * bd_: cv2.line(im, tuple(kp[a].astype(int)), tuple(kp[b].astype(int)), (255, 200, 0), 1)
                for i in range(17):
                    if kc[i] >= O.DISPLAY_KP_CONF: cv2.circle(im, tuple(kp[i].astype(int)), 2, (255, 255, 0), -1)
        if com is not None:
            cx, cy = int(com[0]), int(com[1]); c_ = col[status]
            if status == "PREDICTED": cv2.circle(im, (cx, cy), 10, c_, 1)
            else:
                dia = np.array([[cx, cy-9], [cx+9, cy], [cx, cy+9], [cx-9, cy]], np.int32); cv2.fillConvexPoly(im, dia, c_); cv2.polylines(im, [dia], True, (0, 0, 0), 1)
            cv2.line(im, (cx-15, cy), (cx+15, cy), c_, 1); cv2.line(im, (cx, cy-15), (cx, cy+15), c_, 1); cv2.putText(im, "COM", (cx+11, cy-11), cv2.FONT_HERSHEY_SIMPLEX, 0.38, c_, 1)
        cv2.rectangle(im, (0, 0), (W, 38), (0, 0, 0), -1)
        cv2.putText(im, f"V0.2 f{t} {t/fps:5.2f}s seg{seg}", (4, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)
        cv2.putText(im, f"{(reason if status=='UNRESOLVED' else id_basis)[:34]} eq {eq:.2f}", (4, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)
        cv2.putText(im, status, (W-120, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, col[status], 2)
        if banner: cv2.putText(im, "CAMERA CUT - track reset", (W//2-110, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        elif t in transient: cv2.putText(im, "TRANSIENT (not a cut)", (W//2-100, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 0, 255), 2)
        vw.write(im)
    vw.release(); df = pd.DataFrame(rows); df.to_csv(out_csv, index=False); pd.DataFrame(lm).to_csv(out_csv.replace(".csv", "_landmarks_raw.csv"), index=False)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(O.CRF), out_mp4], check=True); os.remove(tmp)
    json.dump(dict(config=json.load(open(config._PATH)), denim_rule=rule, n_frames=N), open(out_meta, "w"), indent=1)
    return df
if __name__ == "__main__":
    a = sys.argv[1:]; df = run(*a); print(df.status.value_counts()); print(df.unresolved_reason.value_counts())
