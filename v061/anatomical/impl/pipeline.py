"""Pure pipeline: identity rows + pose dets + (optional) seg data + cuts -> measured rows -> source-rate rows. No file/video I/O; no model inference here (seg data are injected)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import adapter, ownership_stage, merge_guard, carry
from record_class import classify
def run_clip(tracklets, dets, decision_rows, seg_by_frame, cut_frames, W, H, cfg=None):
    """seg_by_frame: {frame: sd dict (shape, conf, box, mask packed)} or {} / missing frames -> OWNERSHIP_NOT_EVALUATED."""
    own, *_ = ownership_stage._mods(); cfg = cfg or ownership_stage.load_cfg()
    arows = adapter.build(tracklets, dets, decision_rows); prev = {}; out = []; fs_cache = {}
    shot_boxes = {}
    for r in arows:   # guard input = ALL non-duplicate pose detections in the frame (not only the tracked one)
        d = dets.get(r["frame"])
        if d is None or r["frame"] in shot_boxes.get((r["clip"], r["shot"]), {}): continue
        bx = []
        for b in d["box"]:
            b = tuple(map(float, b))
            if not any(merge_guard._iou(b, c) >= merge_guard.DUP_IOU for c in bx): bx.append(b)
        shot_boxes.setdefault((r["clip"], r["shot"]), {})[r["frame"]] = bx
    guard = {k: merge_guard.log_shot(v) for k, v in shot_boxes.items()}
    for r in sorted(arows, key=lambda x: (x["tracklet"], x["frame"])):
        d = dets.get(r["frame"]); rec = dict(r)
        if d is None or r["det"] is None:
            rec.update(ownership_state="OWNERSHIP_NOT_EVALUATED", own_reasons=["NO_POSE_DETECTION"], pose_status="NONE", n_landmarks=0, S=None, temporal=None)
        else:
            f = r["frame"]
            if f not in fs_cache:
                sd = seg_by_frame.get(f); fs_cache[f] = own.FrameSeg(sd, W, H, cfg.seg.SEG_CONF_MIN) if sd is not None else None
            p = prev.get(r["tracklet"])
            kp_prev = None
            if p is not None and f - p["frame"] <= cfg.integrity.TEMPORAL_MAX_GAP: kp_prev = dict(kp=p["kp"], obs=p["obs"], S=p["S"], frame_gap=f - p["frame"])
            ev = ownership_stage.evaluate(r["det"], d, fs_cache[f], cfg, kp_prev)
            rec.update(ownership_state=ev["ownership_state"], own_reasons=ev["reasons"], pose_status="MEASURED", n_landmarks=ev["n_landmarks"], S=ev["S"], temporal=ev["temporal"], own_summary=ev.get("own_summary"))
            if ev["S"]: prev[r["tracklet"]] = dict(frame=f, kp=d["kp"][r["det"]], obs=d["kpc"][r["det"]] >= cfg.pose.KP_CONF, S=ev["S"])
            rec.update(box=[float(x) for x in d["box"][r["det"]]], kp=d["kp"][r["det"]].tolist(), kpc=d["kpc"][r["det"]].tolist())
        c = classify(r["identity_code"], r["numeric_failure"], rec["ownership_state"], rec["pose_status"]); rec.update(c)
        g = guard.get((r["clip"], r["shot"]), {}).get(r["frame"], dict(merge_guard_would_trigger=False, merge_guard_reason="", merge_guard_since_frame=None))
        rec.update(g)   # logged only; classify() above never saw it
        out.append(rec)
    return out, carry.source_rate(out, cut_frames)
