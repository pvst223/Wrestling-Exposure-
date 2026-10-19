"""Identity -> detection adapter. Metadata only: reads ONLY decision/g/q/tracklet/frame from the out-of-fold decision rows (never truth / b0_decision / reason).
Maps each (tracklet, frame) to a skeleton detection index by box match against the frozen pose detections (stride-3 frames)."""
import math
ALLOWED_COLS = ("tracklet", "frame", "decision", "g", "q")
FORBIDDEN_COLS = ("truth", "b0_decision", "label", "y")
IOU_MATCH_MIN = 0.95
def _iou(a, b):
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]); i = max(0, x2 - x1) * max(0, y2 - y1)
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i
    return i / u if u > 0 else 0.0
def blind_rows(decision_rows):
    """Drop every column except ALLOWED_COLS. Raises if the input would leak nothing but also lacks required ones."""
    out = []
    for r in decision_rows:
        for c in ALLOWED_COLS:
            if c not in r: raise KeyError(f"decision row lacks {c}")
        out.append({c: r[c] for c in ALLOWED_COLS})
    return out
def numeric_failure(g, q):
    try: g = float(g); q = float(q)
    except (TypeError, ValueError): return True
    return not (math.isfinite(g) and math.isfinite(q))
def build(tracklets, dets, decision_rows):
    """tracklets: list of frozen tracklet dicts (tid, clip, shot, frames, boxes). dets: {frame: {box, conf, kp, kpc, ...}}.
    -> list of rows: tracklet, clip, shot, frame, det (index|None), match_iou, identity_code, numeric_failure, g, q. Missing identity row -> NO_IDENTITY_EVAL; unmatched det -> det None."""
    dec = {(r["tracklet"], int(r["frame"])): r for r in blind_rows(decision_rows)}
    rows = []
    for t in tracklets:
        for f, b in zip(t["frames"], t["boxes"]):
            d = dets.get(int(f)); j, best = None, 0.0
            if d is not None:
                for k in range(len(d["conf"])):
                    v = _iou(b, d["box"][k])
                    if v > best: j, best = k, v
                if best < IOU_MATCH_MIN: j = None
            r = dec.get((t["tid"], int(f)))
            if r is None: code, nf, g, q = "NO_IDENTITY_EVAL", False, None, None
            else:
                nf = numeric_failure(r["g"], r["q"]); code = "REJECT_NONTARGET" if nf else r["decision"]
                g = None if nf else float(r["g"]); q = None if nf else float(r["q"])
            rows.append(dict(tracklet=t["tid"], clip=t["clip"], shot=t["shot"], frame=int(f), det=j, match_iou=round(best, 4), identity_code=code, numeric_failure=nf, g=g, q=q))
    return rows
