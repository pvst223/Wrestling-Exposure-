"""Source-rate annotated-video renderer (visualization only; loads no model; computes no scores). Input: decisions CSV (clip, tracklet, frame, truth, decision, reason, g, q) + boxes CSV (tracklet, frame, x1,y1,x2,y2) + source video path.
Writes video at source fps and a sidecar JSON whose frame_status table reconstructs exactly which frames received model evaluation. Footage-derived output must never be committed."""
import csv, hashlib, json, sys, argparse, collections
from .frame_status import tracklet_status, counts, EVALUATED, CARRIED, NOEVAL, MAX_CARRY
RENDER_CONFIG = dict(max_carry=MAX_CARRY, colors_bgr={EVALUATED: (0, 200, 0), CARRIED: (160, 160, 160), NOEVAL: (90, 90, 90)}, font_scale=0.5, dashed_carried=True, interpolation=False)
def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
def read_csv(p): return list(csv.DictReader(open(p, newline="")))
def build_status(decisions, boxes):
    """Returns (frame_status rows, per-(tracklet,frame) draw table). Boxes are held at the last evaluated position (never interpolated)."""
    ev = collections.defaultdict(dict)
    for d in decisions: ev[d["tracklet"]][int(d["frame"])] = d
    bx = collections.defaultdict(dict)
    for b in boxes: bx[b["tracklet"]][int(b["frame"])] = tuple(float(b[k]) for k in ("x1", "y1", "x2", "y2"))
    rows = []
    for t, d in sorted(ev.items()):
        frames = sorted(d); first, last = frames[0], frames[-1] + MAX_CARRY
        for r in tracklet_status(frames, first, last):
            r = dict(r, tracklet=t)
            if r["status"] != NOEVAL: r["box"] = bx[t].get(r["source_eval_frame"]); r["decision"] = d[r["source_eval_frame"]]["decision"]; r["reason"] = d[r["source_eval_frame"]].get("reason", "")
            rows.append(r)
    return rows
def render(video_in, decisions_csv, boxes_csv, video_out, sidecar_out):
    import cv2
    dec, bxs = read_csv(decisions_csv), read_csv(boxes_csv); rows = build_status(dec, bxs)
    by_frame = collections.defaultdict(list)
    for r in rows: by_frame[r["frame"]].append(r)
    cap = cv2.VideoCapture(video_in); fps = cap.get(cv2.CAP_PROP_FPS) or 30.0; W = int(cap.get(3)); H = int(cap.get(4))
    wr = cv2.VideoWriter(video_out, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H)); f = 0; tally = collections.Counter()
    while True:
        ok, img = cap.read()
        if not ok: break
        for r in by_frame.get(f, []):
            if r["status"] == NOEVAL or not r.get("box"): continue
            x1, y1, x2, y2 = (int(v) for v in r["box"]); col = RENDER_CONFIG["colors_bgr"][r["status"]]
            txt = f'{r["decision"]} {r["reason"]}' if r["status"] == EVALUATED else f'carried +{r["age"]}f (visualization only)'
            cv2.rectangle(img, (x1, y1), (x2, y2), col, 2 if r["status"] == EVALUATED else 1); cv2.putText(img, txt, (x1, max(12, y1 - 4)), cv2.FONT_HERSHEY_SIMPLEX, RENDER_CONFIG["font_scale"], col, 1)
        wr.write(img); f += 1
    wr.release(); cap.release()
    side = dict(label="V0.6.1 DEVELOPMENT ONLY - visualization", render_config=RENDER_CONFIG, decisions_sha256=sha256_file(decisions_csv), boxes_sha256=sha256_file(boxes_csv), source_video_sha256=sha256_file(video_in),
                n_source_frames=f, fps=fps, status_counts=dict(counts(rows)), n_unique_evaluated_clip_frames=len({(d.get("clip"), int(d["frame"])) for d in dec}), frame_status=[{k: v for k, v in r.items() if k != "box"} for r in rows])
    json.dump(side, open(sidecar_out, "w"), indent=1, sort_keys=True)
    return side
if __name__ == "__main__":
    a = argparse.ArgumentParser(); [a.add_argument(x) for x in ("video_in", "decisions_csv", "boxes_csv", "video_out", "sidecar_out")]; x = a.parse_args(); render(x.video_in, x.decisions_csv, x.boxes_csv, x.video_out, x.sidecar_out)
