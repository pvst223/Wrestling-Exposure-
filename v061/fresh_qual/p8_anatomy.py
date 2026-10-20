"""Thin P8 driver for the fresh qualitative MP4: runs the FROZEN Anatomical Integration V1 modules unchanged (adapter -> V0.5 ownership -> record classifier -> stride-3 pose -> visualization-only carry -> render_anat.compose).
Stages: preflight | seg (Option W, same wrapper/settings as AR1) | run (rows + MP4 + sidecar). No scoring logic of its own; no parameter changes; no verdicts. Private outputs only."""
import os, sys, json, csv, pickle, subprocess, argparse, hashlib, time
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")); ANAT = os.path.join(REPO, "v061", "anatomical"); sys.path.insert(0, os.path.join(ANAT, "impl"))
import preflight as pf
def sha(p): return pf.sha(p)
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("stage", choices=["preflight", "seg", "run"]); [ap.add_argument(f"--{x}", required=True) for x in ("clip", "work", "pose_w", "seg_w")]; ap.add_argument("--decisions"); a = ap.parse_args()
    pf.check_reused(); pf.check_locked_impl(); pf.check_models(a.pose_w, a.seg_w)
    r = subprocess.run([sys.executable, os.path.join(ANAT, "anat_manifest.py")], capture_output=True, text=True, cwd=REPO)
    if r.returncode != 0: raise SystemExit("anatomical manifest mismatch")
    if a.stage == "preflight": print("PREFLIGHT OK", sha(os.path.join(ANAT, "ANATOMICAL_IMPLEMENTATION_MANIFEST.txt"))); return
    video = os.path.join(a.work, "frozen", "norm", f"{a.clip}.mp4"); dets = pickle.load(open(os.path.join(a.work, "frozen", "dets", f"dets_{a.clip}.pkl"), "rb")); trs = json.load(open(os.path.join(a.work, "frozen", "tracklets", f"{a.clip}.json")))
    segp = os.path.join(a.work, f"SEG_{a.clip}.pkl")
    if a.stage == "seg":
        import seg_posegrid; frames = sorted(int(k) for k in dets); t0 = time.time(); res = seg_posegrid.extract(video, frames, a.seg_w); pickle.dump(res, open(segp + ".tmp", "wb")); os.replace(segp + ".tmp", segp)
        json.dump(dict(clip=a.clip, n_pose_frames=len(frames), n_seg_frames=len(res), seconds=round(time.time() - t0), seg_cache_sha256=sha(segp), seg_weights_sha256=pf.SEG_SHA256), open(os.path.join(a.work, "S1_seg.json"), "w"), indent=1); print("SEG DONE", len(res)); return
    import cv2, pipeline, render_anat
    seg = pickle.load(open(segp, "rb")); dec = list(csv.DictReader(open(a.decisions, newline="")))
    cap = cv2.VideoCapture(video); W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)); fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    starts = sorted({int(t["shot_frames"][0]) for t in trs}); cuts = [s for s in starts if s > 0]
    rows, src = pipeline.run_clip(trs, dets, dec, seg, cuts, W, H); pickle.dump(dict(rows=rows, src=src, cuts=cuts, W=W, H=H), open(os.path.join(a.work, f"ROWS_{a.clip}.pkl"), "wb"))
    by = {}
    for r_ in src: by.setdefault(r_["frame"], []).append(r_)
    vo = os.path.join(a.work, "out", f"ANAT_FRESH_{a.clip}.mp4"); os.makedirs(os.path.dirname(vo), exist_ok=True); wr = None; f = 0
    while True:
        ok, fr = cap.read()
        if not ok: break
        ctx = dict(frame=f, fps=fps, cut_banner=any(cc <= f < cc + 8 for cc in cuts)); im = render_anat.compose(fr, by.get(f, []), ctx)
        if wr is None: wr = cv2.VideoWriter(vo, cv2.VideoWriter_fourcc(*"mp4v"), fps, (im.shape[1], im.shape[0]))
        wr.write(im); f += 1
    cap.release(); wr.release(); h264 = vo.replace(".mp4", "_h264.mp4"); subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vo, "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", h264], check=True)
    cnt = {}
    for r_ in src: cnt[r_["record_class"]] = cnt.get(r_["record_class"], 0) + 1
    sc = os.path.join(a.work, "out", f"ANAT_FRESH_{a.clip}_sidecar.json")
    json.dump(dict(label="FRESH QUALITATIVE ANATOMY V1 INSPECTION - IDENTITY_UNVALIDATED - ANNOTATION-PROVISIONAL - NOT VALIDATION", clip=a.clip, fps=fps, n_source_frames=f, source_video_sha256=sha(video), anat_manifest_sha256=sha(os.path.join(ANAT, "ANATOMICAL_IMPLEMENTATION_MANIFEST.txt")),
                   decisions_sha256=sha(a.decisions), record_class_counts=cnt, rows=render_anat.sidecar_rows(src)), open(sc, "w"), indent=0, sort_keys=True, default=str)
    print(json.dumps(dict(frames=f, mp4v=sha(vo), h264=sha(h264), sidecar=sha(sc), counts=cnt)))
if __name__ == "__main__": main()
