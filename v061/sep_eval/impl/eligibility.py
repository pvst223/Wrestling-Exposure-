"""SEPARATED-BODY ELIGIBILITY V1 (frozen parameters; reviewer ruling D3). Pure geometry on person-class detection boxes, frame size and cut positions.
Deliberately has NO input for skeletons, ownership state/reasons, merge guard, identity scores/labels, or any verdict. No tuning: parameters are constants."""
import numpy as np
PARAMS = dict(margin=0.15, conf_floor=0.10, other_min_height_frac=0.25, border_frac=0.02, target_min_height_frac=0.15, stability_stride=3, cut_window=3)
def _expand(b, m):
    w, h = b[2] - b[0], b[3] - b[1]; return (b[0] - m * w, b[1] - m * h, b[2] + m * w, b[3] + m * h)
def _intersects(a, b):
    """Strict positive-area overlap (touching edges do not count)."""
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])
def _inside_frac(o, t):
    """Fraction of box o's area inside box t (DESCRIPTIVE VARIANT ONLY; the frozen criterion never passes ignore_contained)."""
    iw = max(0.0, min(o[2], t[2]) - max(o[0], t[0])); ih = max(0.0, min(o[3], t[3]) - max(o[1], t[1])); a = (o[2] - o[0]) * (o[3] - o[1]); return iw * ih / a if a > 0 else 0.0
def frame_ok(boxes, conf, t_idx, W, H, p=PARAMS, margin=None, ignore_contained=None):
    """Criteria 1-3 for one frame. boxes: (N,4) xyxy, conf: (N,), t_idx: index of the assigned/target detection. Returns (ok, reason)."""
    m = p["margin"] if margin is None else margin; boxes = np.asarray(boxes, float).reshape(-1, 4); conf = np.asarray(conf, float).reshape(-1)
    if t_idx is None or not (0 <= t_idx < len(boxes)): return False, "NO_TARGET_BOX"
    t = boxes[t_idx]; th = t[3] - t[1]; tw = t[2] - t[0]
    if th <= 0 or tw <= 0: return False, "DEGENERATE_BOX"
    bx, by = p["border_frac"] * W, p["border_frac"] * H
    if t[0] < bx or t[1] < by or t[2] > W - bx or t[3] > H - by: return False, "TARGET_NEAR_BORDER"
    if th < p["target_min_height_frac"] * H: return False, "TARGET_TOO_SMALL"
    ex = _expand(t, m)
    for i in range(len(boxes)):
        if i == t_idx or conf[i] < p["conf_floor"]: continue
        o = boxes[i]
        if (o[3] - o[1]) < p["other_min_height_frac"] * th: continue
        if ignore_contained is not None and _inside_frac(o, t) >= ignore_contained: continue
        if _intersects(ex, o): return False, "OTHER_PERSON_WITHIN_MARGIN"
    return True, "OK"
def eligible(frame, dets_at, tbox_at, shot_of, W, H, p=PARAMS, margin=None, ignore_contained=None):
    """Full criterion for assigned detection at source frame `frame`. dets_at(f)->(boxes,conf) or None; tbox_at(f)->target (tracklet) detection index at f or None (stride-3 neighbour);
    shot_of(f)->shot index. Neighbour frames f-3 and f+3 must exist, belong to the same shot, and satisfy criteria 1-3; no cut within +-3 frames (same shot index over the window)."""
    s = p["stability_stride"]; shot0 = shot_of(frame)
    for f in (frame - s, frame, frame + s):
        d = dets_at(f)
        if d is None: return False, "NEIGHBOUR_MISSING"
        if shot_of(f) != shot0: return False, "CUT_WITHIN_WINDOW"
        ok, why = frame_ok(d[0], d[1], tbox_at(f), W, H, p, margin, ignore_contained)
        if not ok: return False, (why if f == frame else "NEIGHBOUR_" + why)
    for f in range(frame - p["cut_window"], frame + p["cut_window"] + 1):
        if shot_of(f) != shot0: return False, "CUT_WITHIN_WINDOW"
    return True, "OK"
