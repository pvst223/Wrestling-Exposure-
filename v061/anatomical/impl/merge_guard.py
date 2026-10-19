"""DIAGNOSTIC-ONLY merge guard (reviewer ruling Q2). Logs merge_guard_would_trigger / reason / timing.
It must not alter ownership state, record class, landmark emission, carry or metrics: nothing in the pipeline consumes its output except the log/sidecar.
Heuristic (a priori, uncalibrated; V0.5 config constants): earlier (within LOOKBACK source frames) >=2 non-duplicate boxes that touch each other; now exactly one box overlapping their union at IoU>=MERGE_IOU;
persists until >=2 separate boxes reappear or PERSIST frames elapse."""
LOOKBACK, MERGE_IOU, PERSIST, DUP_IOU = 10, 0.3, 150, 0.5
def _iou(a, b):
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]); i = max(0, x2 - x1) * max(0, y2 - y1)
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i
    return i / u if u > 0 else 0.0
def _union(a, b): return (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))
def _touching_pair(boxes):
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if _iou(a, b) < DUP_IOU and (min(a[2], b[2]) > max(a[0], b[0])) and (min(a[3], b[3]) > max(a[1], b[1])): return (a, b)
    return None
def log_shot(frame_boxes):
    """frame_boxes: {source_frame: [box,...]} for ONE shot (a cut starts a new call). -> {frame: dict(merge_guard_would_trigger, merge_guard_reason, merge_guard_since_frame)}."""
    out = {}; pair = None; pair_frame = None; since = None
    for f in sorted(frame_boxes):
        boxes = frame_boxes[f]; tp = _touching_pair(boxes)
        if tp is not None: pair, pair_frame = tp, f
        if since is not None and (f - since > PERSIST or len(boxes) >= 2): since = None
        if since is None and tp is None and len(boxes) == 1 and pair is not None and 0 < f - pair_frame <= LOOKBACK:
            if _iou(boxes[0], _union(*pair)) >= MERGE_IOU: since = f
        out[f] = dict(merge_guard_would_trigger=since is not None, merge_guard_reason="TWO_TO_ONE_BOX_MERGE" if since is not None else "", merge_guard_since_frame=since)
    return out
