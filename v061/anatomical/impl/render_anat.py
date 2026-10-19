"""Anatomical diagnostic renderer. Full source frame left (uncropped) + 420 px panel. Encoding by text + shape + line style (not colour alone).
No COM, no distance/speed/impact overlay. Every record class has its own glyph; legend always on the panel."""
import cv2, numpy as np, json, hashlib
BONES = [(5, 6), (5, 7), (7, 9), (6, 8), (8, 10), (5, 11), (6, 12), (11, 12), (11, 13), (13, 15), (12, 14), (14, 16)]
COL = {"A": (0, 200, 0), "B": (255, 0, 255), "N": (200, 200, 200), "W": (255, 255, 255), "Y": (0, 220, 255), "R": (0, 0, 255), "O": (0, 140, 255)}
PANEL_W, DISPLAY_KP_CONF, MAX_BONE_FRAC = 420, 0.7, 0.75
LEGEND = [("ASSIGNED_A/B", "solid skeleton, [M]"), ("UNASSIGNED_IDENTITY_AMBIGUOUS", "dashed white, A|B ?"), ("NONTARGET", "grey box NT"), ("INVALID_NUMERIC", "yellow box NUM-FAIL"),
          ("WITHHELD_MIXED_BODY", "red box X MIXED"), ("WITHHELD_OWNERSHIP_*", "orange box OWN ?"), ("CARRIED_*", "dotted, viz only"), ("NO_POSE", "nothing drawn")]
def _t(im, s, x, y, sc=0.42, col=(235, 235, 235), th=1): cv2.putText(im, s[:62], (x, y), cv2.FONT_HERSHEY_SIMPLEX, sc, col, th, cv2.LINE_AA)
def _skel(im, r, col, style):
    kp = np.asarray(r["kp"]); kc = np.asarray(r["kpc"]); x1, y1, x2, y2 = r["box"]; bd = float(np.hypot(x2 - x1, y2 - y1))
    for a, b in BONES:
        if kc[a] >= DISPLAY_KP_CONF and kc[b] >= DISPLAY_KP_CONF and np.hypot(*(kp[a] - kp[b])) <= MAX_BONE_FRAC * bd:
            p, q = kp[a], kp[b]
            if style == "solid": cv2.line(im, tuple(int(v) for v in p), tuple(int(v) for v in q), col, 2, cv2.LINE_AA)
            else:
                n = 7 if style == "dashed" else 14; ts = np.linspace(0, 1, n)
                for i in range(0, n - 1, 2 if style == "dashed" else 1):
                    if style == "dotted": cv2.circle(im, tuple(int(v) for v in (p + (q - p) * ts[i])), 1, col, -1)
                    else: cv2.line(im, tuple(int(v) for v in (p + (q - p) * ts[i])), tuple(int(v) for v in (p + (q - p) * ts[i + 1])), col, 2)
def _box(im, r, col, text, thick=1):
    x1, y1, x2, y2 = [int(v) for v in r["box"]]; cv2.rectangle(im, (x1, y1), (x2, y2), col, thick); _t(im, text, x1 + 2, max(12, y1 + 13), 0.45, col, 1)
def draw_record(im, r):
    c = r["record_class"]
    if c in ("ASSIGNED_A", "ASSIGNED_B"):
        k = c[-1]; _skel(im, r, COL[k], "solid"); _box(im, r, COL[k], f"{k} [M]")
    elif c == "UNASSIGNED_IDENTITY_AMBIGUOUS": _skel(im, r, COL["W"], "dashed"); _box(im, r, COL["W"], "A|B ?")
    elif c == "NONTARGET": _box(im, r, COL["N"], "NT")
    elif c == "NO_IDENTITY_EVAL": _box(im, r, (120, 120, 120), "no id")
    elif c == "INVALID_NUMERIC": _box(im, r, COL["Y"], "NUM-FAIL", 2)
    elif c == "WITHHELD_MIXED_BODY":
        x1, y1, x2, y2 = [int(v) for v in r["box"]]; _box(im, r, COL["R"], "MIXED - withheld", 2); cv2.line(im, (x1, y1), (x2, y2), COL["R"], 1); cv2.line(im, (x1, y2), (x2, y1), COL["R"], 1)
    elif c in ("WITHHELD_OWNERSHIP_UNCERTAIN", "WITHHELD_OWNERSHIP_NOT_EVALUATED"): _box(im, r, COL["O"], "OWN ?" if c.endswith("UNCERTAIN") else "OWN n/e", 1)
    elif c.startswith("CARRIED_"):
        k = c[-1]; _skel(im, r, tuple(int(v * 0.6) for v in COL[k]), "dotted"); _box(im, r, tuple(int(v * 0.6) for v in COL[k]), f"{k} carried")
    return im
def compose(frame, rows, ctx):
    """rows: source-rate rows for this frame. ctx: dict(frame, fps, shot, cut_banner(bool))."""
    H, W = frame.shape[:2]; im = frame.copy()
    for r in rows:
        if r["record_class"] != "NO_POSE" and r.get("box") is not None: draw_record(im, r)
    pan = np.full((H, PANEL_W, 3), 28, np.uint8); y = 14
    _t(pan, f"ANATOMICAL DIAGNOSTIC (dev only) frame {ctx['frame']} t={ctx['frame']/ctx['fps']:5.2f}s", 6, y, 0.42, (255, 255, 255)); y += 14
    _t(pan, "IDENTITY UNVALIDATED (MODIFY); ownership != identity", 6, y, 0.38, (0, 220, 255)); y += 14
    _t(pan, "CAMERA CUT: all anchors reset" if ctx.get("cut_banner") else "no cut in last 8 frames", 6, y, 0.4, (255, 255, 0) if ctx.get("cut_banner") else (150, 150, 150)); y += 16
    for r in rows:
        if y > H - 20 * len(LEGEND) - 10: break
        q = "" if r.get("q") is None else f" q={r['q']:.2f}"; _t(pan, f"{r['tracklet'].split(':')[-1]} {r['record_class']}{q} [{r['pose_status']}]", 6, y); y += 12
        if r.get("merge_guard_would_trigger"): _t(pan, "  merge-guard (diagnostic only) would trigger", 6, y, 0.36, (180, 180, 255)); y += 12
    y = H - 12 * len(LEGEND) - 6
    for a, b in LEGEND: _t(pan, f"{a}: {b}", 6, y, 0.34, (170, 170, 170)); y += 12
    return np.hstack([im, pan])
def sidecar_rows(source_rows):
    keep = ("clip", "shot", "tracklet", "frame", "record_class", "pose_status", "identity_state_passthrough", "ownership_state_passthrough", "numeric_failure", "q", "g", "carry_age", "merge_guard_would_trigger", "merge_guard_reason")
    return [{k: r.get(k) for k in keep} | {"own_reasons": list(r.get("own_reasons") or [])} for r in sorted(source_rows, key=lambda r: (r["frame"], r["tracklet"]))]
def sha256_bytes(b): return hashlib.sha256(b).hexdigest()
