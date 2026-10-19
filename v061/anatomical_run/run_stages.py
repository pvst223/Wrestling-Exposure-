#!/usr/bin/env python3
"""Anatomical integration execution runner (stages S0-S6). Authorized by reviewer (OGR18). Uses ONLY the hashed candidate modules in v061/anatomical (impl, reused_v05); contains no scoring logic of its own.
Write-once outputs; any exception stops the sequence (genuine defects are recorded, never silently repaired). Private outputs (seg caches, rows, sheets, MP4s, sidecars) live under --priv and are never committed."""
import argparse, csv, hashlib, json, os, pickle, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
ANAT = os.path.join(REPO, "v061", "anatomical"); sys.path.insert(0, os.path.join(ANAT, "impl"))
import preflight as pf, adapter, pipeline, metrics, render_anat, ownership_stage
SEED = int("cff3dcc4", 16) % 2 ** 31
def sha(p): return pf.sha(p)
def wo(path):
    if os.path.exists(path): raise pf.Blocked(f"write-once violated: {path}")
    return path
def dump_json(path, obj): json.dump(obj, open(wo(path), "w"), indent=1, sort_keys=True, default=str)
def clip_paths(frozen, clip): return dict(dets=os.path.join(frozen, "dets", f"dets_{clip}.pkl"), tracklets=os.path.join(frozen, "tracklets", f"{clip}.json"), video=os.path.join(frozen, "norm", f"{clip}.mp4"))
def load_clip(frozen, clip):
    p = clip_paths(frozen, clip); return pickle.load(open(p["dets"], "rb")), json.load(open(p["tracklets"])), p["video"]
def s0(a):
    pf.check_reused(); pf.check_locked_impl(); pf.check_clips(a.clips); pf.check_authorization(a.auth, a.ledger); pf.check_models(a.pose_w, a.seg_w); pf.check_exactly_once(a.result)
    r = subprocess.run([sys.executable, os.path.join(ANAT, "anat_manifest.py")], capture_output=True, text=True, cwd=REPO)
    if r.returncode != 0: raise pf.Blocked("anatomical manifest mismatch")
    info = dict(anat_manifest_sha256=sha(os.path.join(ANAT, "ANATOMICAL_IMPLEMENTATION_MANIFEST.txt")), runner_sha256=sha(__file__), auth_sha256=sha(a.auth), pose_w=sha(a.pose_w), seg_w=sha(a.seg_w), per_clip={})
    for c in a.clips:
        p = clip_paths(a.frozen, c); info["per_clip"][c] = {k: sha(v) for k, v in p.items()}
    # blinded OOF decision copy (decision columns only)
    rows = [r for r in csv.DictReader(open(a.oof, newline=""))]; blind = adapter.blind_rows(rows)
    out = wo(os.path.join(a.priv, "OOF_BLINDED.csv"))
    with open(out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["clip"] + list(adapter.ALLOWED_COLS)); [w.writerow([r["clip"]] + [b[c] for c in adapter.ALLOWED_COLS]) for r, b in zip(rows, blind)]
    info["oof_private_sha256"] = sha(a.oof); info["oof_blinded_sha256"] = sha(out); dump_json(os.path.join(a.priv, "S0_PREFLIGHT.json"), info); return info
def s1(a, clip):
    import seg_posegrid
    dets, _, video = load_clip(a.frozen, clip); frames = sorted(int(k) for k in dets)
    t0 = time.time(); res = seg_posegrid.extract(video, frames, a.seg_w); out = wo(os.path.join(a.priv, f"SEG_{clip}.pkl"))
    pickle.dump(res, open(out + ".tmp", "wb")); os.replace(out + ".tmp", out)
    dump_json(os.path.join(a.priv, f"S1_{clip}.json"), dict(clip=clip, n_pose_frames=len(frames), n_seg_frames=len(res), missing=[f for f in frames if f not in res][:20], seconds=round(time.time() - t0), seg_cache_sha256=sha(out), seg_weights_sha256=pf.SEG_SHA256))
def _cv2(): import cv2; return cv2
def s2_s4(a):
    cv2 = _cv2(); allrows, allsrc, m7, perclip = [], [], {}, {}
    blind = {}
    for r in csv.DictReader(open(os.path.join(a.priv, "OOF_BLINDED.csv"), newline="")): blind.setdefault(r["clip"], []).append(r)
    ownership_stage._mods(); import cuts_events
    for c in a.clips:
        dets, trs, video = load_clip(a.frozen, c); seg = pickle.load(open(os.path.join(a.priv, f"SEG_{c}.pkl"), "rb"))
        cap = cv2.VideoCapture(video); W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)); cap.release()
        starts = sorted({int(t["shot_frames"][0]) for t in trs}); cuts = [s for s in starts if s > 0]
        rows, src = pipeline.run_clip(trs, dets, blind.get(c, []), seg, cuts, W, H)
        allrows += rows; allsrc += src
        ev = cuts_events.detect(video); m7[c] = metrics.m7_cut_crosscheck(starts, [e["frame"] for e in ev if e["cls"] == "CUT"]); m7[c]["classifier_events"] = [(e["frame"], e["cls"]) for e in ev]
        perclip[c] = dict(W=W, H=H, n_rows=len(rows), n_source_rows=len(src), cuts=cuts, merge_guard_flagged_rows=sum(1 for r in rows if r["merge_guard_would_trigger"]),
                          classes={k: sum(1 for r in rows if r["record_class"] == k) for k in sorted({r["record_class"] for r in rows})})
        pickle.dump(dict(rows=rows, src=src, cuts=cuts, W=W, H=H), open(wo(os.path.join(a.priv, f"ROWS_{c}.pkl")), "wb"))
    rep, sheet, key = metrics.report(allrows, allsrc, [], [], SEED); rep["M7"] = m7
    for nm, d in (("M9_REVIEW_SHEET_BLIND.csv", sheet), ("M9_HIDDEN_KEY.csv", key)):
        with open(wo(os.path.join(a.priv, nm)), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(d[0]) if d else ["none"]); w.writeheader(); [w.writerow(x) for x in d]
    dump_json(os.path.join(a.priv, "S4_METRICS.json"), dict(metrics=rep, per_clip=perclip, m9_sheet_sha256=sha(os.path.join(a.priv, "M9_REVIEW_SHEET_BLIND.csv")), m9_key_sha256=sha(os.path.join(a.priv, "M9_HIDDEN_KEY.csv")), seed=SEED))
def s5(a):
    cv2 = _cv2(); out = {}
    for c in a.clips:
        d = pickle.load(open(os.path.join(a.priv, f"ROWS_{c}.pkl"), "rb")); src, cuts = d["src"], d["cuts"]; by = {}
        for r in src: by.setdefault(r["frame"], []).append(r)
        _, _, video = load_clip(a.frozen, c); cap = cv2.VideoCapture(video); fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        vo = wo(os.path.join(a.priv, f"ANAT_{c}.mp4")); wr = None; f = 0; n = 0
        while True:
            ok, fr = cap.read()
            if not ok: break
            ctx = dict(frame=f, fps=fps, cut_banner=any(cc <= f < cc + 8 for cc in cuts)); im = render_anat.compose(fr, by.get(f, []), ctx)
            if wr is None: wr = cv2.VideoWriter(vo, cv2.VideoWriter_fourcc(*"mp4v"), fps, (im.shape[1], im.shape[0]))
            wr.write(im); f += 1; n += 1
        cap.release(); wr.release(); h264 = wo(os.path.join(a.priv, f"ANAT_{c}_h264.mp4"))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vo, "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", h264], check=True)
        sc = wo(os.path.join(a.priv, f"ANAT_{c}_sidecar.json"))
        cnt = {}
        for r in src: cnt[r["record_class"]] = cnt.get(r["record_class"], 0) + 1
        json.dump(dict(label="V0.6.1 ANATOMICAL DIAGNOSTIC - DEVELOPMENT ONLY - IDENTITY UNVALIDATED", clip=c, fps=fps, n_source_frames=n, source_video_sha256=sha(video), anat_manifest_sha256=sha(os.path.join(ANAT, "ANATOMICAL_IMPLEMENTATION_MANIFEST.txt")),
                       record_class_counts=cnt, rows=render_anat.sidecar_rows(src)), open(sc, "w"), indent=0, sort_keys=True, default=str)
        out[c] = dict(n_source_frames=n, fps=fps, mp4v_sha256=sha(vo), h264_sha256=sha(h264), sidecar_sha256=sha(sc), record_class_counts=cnt)
    dump_json(os.path.join(a.priv, "S5_RENDER.json"), out)
def main():
    ap = argparse.ArgumentParser()
    for k, v in (("frozen", "/home/claude/proj/v06_phase1/frozen"), ("priv", "/home/claude/proj/v061_anat_private"), ("pose_w", "/home/claude/proj/models/yolov8m-pose.pt"), ("seg_w", "/home/claude/proj/v05/models/yolov8m-seg.pt"),
                 ("auth", os.path.join(HERE, "AUTHORIZATION_RECORD.json")), ("ledger", os.path.join(REPO, "v06", "frozen", "AUDIT_LEDGER.jsonl")), ("oof", "/home/claude/proj/v061_devrun_private/OOF_DECISIONS_PRIVATE.csv"), ("result", os.path.join(HERE, "ANATOMICAL_RESULT_V1.json"))):
        ap.add_argument("--" + k.replace("_", "-"), dest=k, default=v)
    ap.add_argument("stage", choices=["s0", "s1", "s2s4", "s5"]); ap.add_argument("--clip"); a = ap.parse_args(); a.clips = list(pf.CLIPS); os.makedirs(a.priv, exist_ok=True)
    if a.stage == "s0": print(json.dumps(s0(a), indent=1))
    elif a.stage == "s1": s1(a, a.clip)
    elif a.stage == "s2s4": s2_s4(a)
    elif a.stage == "s5": s5(a)
if __name__ == "__main__": main()
