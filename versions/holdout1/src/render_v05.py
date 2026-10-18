"""V0.5 annotated-video renderer: the COMPLETE 640x360 source frame on the left (never cropped, no opaque panel over it) + an external QC panel on the right.
On the frame: target skeleton (solid only when a COM is emitted), owner-mask contour, COM marker, compact A/B label. Everything else is in the panel.
Numbers shown are HEURISTIC evidence values (appearance score S in [-1,1], reliability R, mask fractions, visible-mass fraction); none is a probability of correctness.
Status is encoded by text AND shape (not colour alone): MEASURED = filled diamond [M]; PARTIAL = hollow diamond [P]; PREDICTED = circle [~]; UNRESOLVED = no marker [X]."""
import cv2, numpy as np, math
COL = {"A": (0, 200, 0), "B": (255, 0, 255)}; BONE = [(5,6),(5,7),(7,9),(6,8),(8,10),(5,11),(6,12),(11,12),(11,13),(13,15),(12,14),(14,16)]
BADGE = {"MEASURED": "[M]", "PARTIAL": "[P]", "PREDICTED": "[~]", "UNRESOLVED": "[X]"}
WHY = {"LOW_MASS": "low visible mass", "IDENTITY_TIER_ACCEPT": "identity tier ACCEPT (not HIGH)", "PREDICTION_NOT_A_MEASUREMENT": "extrapolated; NOT a measurement"}
def _t(img, s, x, y, scale, col=(235, 235, 235), th=1): cv2.putText(img, s[:66], (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, col, th, cv2.LINE_AA)
def compose(frame, ctx, O, Oc):
    W, H, PW, fs = ctx["W"], ctx["H"], Oc.PANEL_W, Oc.FONT; im = frame.copy(); out = ctx["out"]
    for box, l in ctx["cands"]:
        if l in ("A", "B"): continue
        x1, y1, x2, y2 = box.astype(int); cv2.rectangle(im, (x1, y1), (x2, y2), (130, 130, 130), 1); cv2.putText(im, "N" if l == "NEITHER" else "?", (x1 + 2, y1 + 11), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (190, 190, 190), 1, cv2.LINE_AA)
    for X in ("A", "B"):
        o = out[X]; sel = o["sel"]; col = COL[X]; dim = tuple(int(c * 0.55) for c in col)
        if sel is not None:
            for cn in ctx["contours"].get(X, []): cv2.polylines(im, [cn], True, dim, 1, cv2.LINE_AA)
            x1, y1, x2, y2 = sel["box"].astype(int); em = o["status"] in ("MEASURED", "PARTIAL"); cv2.rectangle(im, (x1, y1), (x2, y2), col if em else dim, 1)
            cv2.putText(im, X + ("" if o["own_state"] == "SINGLE_BODY_SUPPORTED" else "?"), (x1 + 2, y1 + 13), cv2.FONT_HERSHEY_SIMPLEX, 0.5, col, 2, cv2.LINE_AA)
            kp, kc = sel["kp"], sel["kc"]; bd = math.hypot(x2 - x1, y2 - y1)
            for a, b in BONE:
                if kc[a] >= Oc.DISPLAY_KP_CONF and kc[b] >= Oc.DISPLAY_KP_CONF and np.hypot(*(kp[a] - kp[b])) <= Oc.MAX_BONE_FRAC_OF_BOX_DIAG * bd: cv2.line(im, tuple(kp[a].astype(int)), tuple(kp[b].astype(int)), col if em else dim, 1 if em else 1, cv2.LINE_AA)
        if o["com"] is not None:
            cx, cy = int(o["com"][0]), int(o["com"][1])
            if o["status"] == "PREDICTED":
                cv2.circle(im, (cx, cy), 8, col, 1, cv2.LINE_AA)
                if o["unc_px"]: cv2.circle(im, (cx, cy), int(o["unc_px"]), col, 1, cv2.LINE_AA)
            else:
                dia = np.array([[cx, cy - 8], [cx + 8, cy], [cx, cy + 8], [cx - 8, cy]], np.int32)
                if o["status"] == "MEASURED": cv2.fillConvexPoly(im, dia, col); cv2.polylines(im, [dia], True, (0, 0, 0), 1, cv2.LINE_AA)
                else: cv2.polylines(im, [dia], True, col, 2, cv2.LINE_AA)
            cv2.line(im, (cx - 12, cy), (cx + 12, cy), col, 1); cv2.line(im, (cx, cy - 12), (cx, cy + 12), col, 1)
    panel = np.full((H, PW, 3), 28, np.uint8); y = 14
    _t(panel, f"V0.5 QC  frame {ctx['t']}  t={ctx['t']/ctx['fps']:5.2f}s  shot {ctx['seg']}", 6, y, fs + 0.03, (255, 255, 255), 1); y += 14
    cut = f"CAMERA CUT: spatial continuity reset ({ctx['frames_since_cut']} fr ago)" if ctx["banner"] else ("transient event (NOT a cut)" if ctx["transient"] else "camera: no cut in last 8 frames")
    _t(panel, cut, 6, y, fs, (0, 255, 255) if ctx["banner"] else (170, 170, 170)); y += 16
    for X in ("A", "B"):
        o = out[X]; col = COL[X]; cv2.line(panel, (4, y - 9), (PW - 4, y - 9), (70, 70, 70), 1)
        _t(panel, f"{X}  {BADGE[o['status']]} {o['status']}", 6, y + 4, fs + 0.1, col, 2); y += 17
        if o["status"] == "MEASURED": why = f"identity HIGH + single-body supported + mass {o['vm']:.0%}"
        elif o["status"] in ("PARTIAL", "PREDICTED"): why = "; ".join(WHY.get(f, f) for f in o["factors"])
        else: why = o["reason"] or "-"
        _t(panel, "why: " + why, 6, y, fs); y += 14
        _t(panel, f"identity: {o['state']} tier={o['tier'] or '-'}", 6, y, fs); y += 14
        _t(panel, f"  appearance heuristic S={o['S']:+.2f} R={o['R']:.1f} n={o['n']}", 6, y, fs - 0.04, (190, 190, 190)); y += 14
        _t(panel, f"ownership: {o['own_state']}", 6, y, fs, (120, 220, 255) if o["own_state"] == "SINGLE_BODY_SUPPORTED" else ((90, 90, 255) if o["own_state"] == "MIXED_BODY_SUSPECTED" else ((150, 150, 150) if o["own_state"] == "NOT_EVALUATED" else (120, 200, 255)))); y += 14
        om = o["om"]
        if o["own_reasons"]: _t(panel, "  " + (";".join(o["own_reasons"]) if len(";".join(o["own_reasons"])) <= 62 else ";".join(o["own_reasons"])[:60] + "..."), 6, y, fs - 0.06, (190, 190, 190))
        elif om is not None and om["owner"] is not None: _t(panel, f"  own-only {om['own_only_frac']:.0%} contested {om['contested_frac']:.0%} unexplained-mask {om['unexplained_frac']:.0%}", 6, y, fs - 0.06, (190, 190, 190))
        y += 14
        vm = "n/a" if (o["vm"] is None or (isinstance(o["vm"], float) and np.isnan(o["vm"]))) else f"{o['vm']:.0%}"
        _t(panel, f"COM: {o['com_elig']}  visible-mass {vm}", 6, y, fs); y += 14
        if o["status"] == "PREDICTED": _t(panel, f"  predicted {o['since_anchor']} fr after anchor f{o['anchor_frame']}, +/-{o['unc_px']:.0f}px (heuristic)", 6, y, fs - 0.06, (190, 190, 190))
        elif o["status"] == "UNRESOLVED" and o["com_elig"] == "INELIGIBLE": _t(panel, "  identity assigned, COM withheld", 6, y, fs - 0.06, (190, 190, 190))
        y += 18
    yb = H - 40
    for k, s in enumerate(("[M] measured  [P] partial  [~] predicted  [X] unresolved", "A=green B=magenta  '?' = ownership not supported", "Heuristic values, NOT probabilities. Not validated.")): _t(panel, s, 6, yb + 13 * k, fs - 0.06, (150, 150, 150))
    return np.hstack([im, panel])
