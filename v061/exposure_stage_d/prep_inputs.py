#!/usr/bin/env python3
"""Stage-D input preparation + no-label preflight. Deterministic, model-free. Applies ONLY the frozen PREPROC_V1 shot rule
(ffmpeg scene>0.3 on the ORIGINAL file; events closer than 0.25 s merged; frames = round(t*30)) and the frozen splits.
Assigns NO labels. Writes private manifests/sources.json under --out (never committed) and a public report (hashes/counts)."""
import argparse, csv, hashlib, json, os, re, subprocess, sys
import labeller_core as C

FPS = 30
BURNED = {   # source_id -> (original file, frozen cuts file, frame limit or None)
    "b1_orton_rollins_wm31": ("batch1/raw/orton_rollins_wm31.mp4", "batch1/sheets/orton_rollins_wm31.cuts.txt", None),
    "b2_batch2_clip_condensed": ("batch2/raw/b2_batch2_clip_condensed.mp4", "batch2/sheets/b2_batch2_clip_condensed.cuts.txt", None),
    "b2_videoplayback_2": ("batch2/raw/b2_videoplayback_2.mp4", "batch2/sheets/b2_videoplayback_2.cuts.txt", 1934),
    "b2_videoplayback_5": ("batch2/raw/b2_videoplayback_5.mp4", "batch2/sheets/b2_videoplayback_5.cuts.txt", None),
}
MATCH_ID = "rr_balor_full"
SPLITS_S = {"seen_end": 150.0, "build_end": 450.0}


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def merge_times(times):
    d = []
    for x in sorted(times):
        if not d or x - d[-1] >= 0.25: d.append(x)
    return d


def shots_from_times(times, nframes, limit=None):
    """Identical to frozen build_tracklets.shots(): boundaries [0]+round(t*30)+[limit]; shots are consecutive pairs."""
    lim = min(nframes, limit if limit else nframes)
    b = [0] + [int(round(x * FPS)) for x in merge_times(times) if int(round(x * FPS)) < lim] + [lim]
    return [(b[i], b[i + 1]) for i in range(len(b) - 1)]


def parse_ffmpeg_scene_log(path):
    t = open(path, errors="ignore").read().replace("\r", "\n")
    times = [float(m.group(1)) for m in re.finditer(r"pts_time:([0-9.]+)", t)]
    fr = [int(m.group(1)) for m in re.finditer(r"frame=\s*(\d+)", t)]
    return times, (max(fr) if fr else None)


def count_frames(p):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                                   "stream=nb_read_frames", "-of", "csv=p=0", p]).decode().strip()
    return int(out)


def tstr(frames): return f"{frames / FPS:.4f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase1", required=True); ap.add_argument("--match", required=True)
    ap.add_argument("--match_scene_log", required=True); ap.add_argument("--seg150_cuts", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--report", required=True)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    verify = C.verify_protocol()
    build, check, frames_rows, src_map, src_hash, notes = [], [], [], {}, {}, {}
    # --- burned development clips (frozen shot lists, unchanged) ---
    for sid, (raw, cuts, lim) in BURNED.items():
        p = os.path.join(a.phase1, raw); n = count_frames(p)
        times = [float(x) for x in open(os.path.join(a.phase1, cuts)).read().split()]
        for i, (s, e) in enumerate(shots_from_times(times, n, lim)):
            build.append([f"{sid}_s{i:03d}", sid, "build", tstr(s), tstr(e)]); frames_rows.append([f"{sid}_s{i:03d}", s, e])
        src_map[sid] = os.path.abspath(p); src_hash[sid] = sha_file(p); notes[sid] = {"frames": n, "limit": lim, "n_cuts_raw": len(times)}
    # --- match: frozen rule on the full original file ---
    times, last_frame = parse_ffmpeg_scene_log(a.match_scene_log)
    n_match = count_frames(a.match)
    seg_cuts = [float(x) for x in open(a.seg150_cuts).read().split()]
    first150 = [t for t in times if t < 150.0]
    consistency = {"full_file_cuts_in_first_150s": len(first150), "seg150_cuts_raw": len(seg_cuts),
                   "max_abs_time_diff_s": (max(abs(x - y) for x, y in zip(first150, seg_cuts)) if len(first150) == len(seg_cuts) else None),
                   "identical_count": len(first150) == len(seg_cuts)}
    shots = shots_from_times(times, n_match)
    f_seen, f_build = int(round(SPLITS_S["seen_end"] * FPS)), int(round(SPLITS_S["build_end"] * FPS))
    straddle = [(i, s, e) for i, (s, e) in enumerate(shots) if s < f_seen < e or s < f_build < e]
    for i, (s, e) in enumerate(shots):
        row_id = f"{MATCH_ID}_s{i:04d}"
        if s >= f_build: check.append([row_id, MATCH_ID, "check", tstr(s), tstr(e)]); frames_rows.append([row_id, s, e])
        elif s >= f_seen and e <= f_build: build.append([row_id, MATCH_ID, "build", tstr(s), tstr(e)]); frames_rows.append([row_id, s, e])
    src_map[MATCH_ID] = os.path.abspath(a.match); src_hash[MATCH_ID] = sha_file(a.match)
    for name, rows in (("manifest_build.csv", build), ("manifest_check.csv", check)):
        with open(os.path.join(a.out, name), "w", newline="") as f:
            w = csv.writer(f, lineterminator="\n"); w.writerow(C.MANIFEST_COLUMNS); w.writerows(rows)
    with open(os.path.join(a.out, "shot_frames_private.csv"), "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n"); w.writerow(["shot_id", "frame_start", "frame_end"]); w.writerows(frames_rows)
    json.dump(src_map, open(os.path.join(a.out, "sources.json"), "w"), indent=1)
    # --- no-label preflight ---
    with open(os.path.join(a.out, "manifest_build.csv")) as f: bm = list(csv.DictReader(f))
    with open(os.path.join(a.out, "manifest_check.csv")) as f: cm = list(csv.DictReader(f))
    ids_b, ids_c = {r["shot_id"] for r in bm}, {r["shot_id"] for r in cm}
    ws = C.Workspace(os.path.join(a.out, "_preflight_ws"))
    ev_b = ws.open_set("build", os.path.join(a.out, "manifest_build.csv")); ev_c = ws.open_set("check", os.path.join(a.out, "manifest_check.csv"))
    ctx = {}
    for s_ in ("build", "check"):
        rows = ws.manifest(s_); rep = rows[len(rows) // 2]; v = ws.view(s_, rep["shot_id"])
        out = os.path.join(a.out, "_preflight_ctx", v["shot_id"] + ".mp4"); os.makedirs(os.path.dirname(out), exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(v["context_start_s"]), "-to", str(v["context_end_s"]), "-i",
                        src_map[v["source_id"]], "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "30", out], check=True)
        d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out]))
        ctx[s_] = {"clip_opens": True, "context_duration_s": round(d, 2), "expected_s": round(v["context_end_s"] - v["context_start_s"], 2)}
    mb, mc = [os.path.join(a.out, "manifest_build.csv"), os.path.join(a.out, "manifest_check.csv")]
    dur = lambda rows: round(sum(float(r["t_end_s"]) - float(r["t_start_s"]) for r in rows), 3)
    by_src = lambda rows: {k: sum(1 for r in rows if r["source_id"] == k) for k in sorted({r["source_id"] for r in rows})}
    mrow = lambda rows, s, e: [r for r in rows if r["source_id"] == MATCH_ID]
    rep = {"protocol_v1_1_sha256": verify, "protocol_hash_matches_frozen": verify == C.PROTOCOL_SHA256,
           "manifest_columns": list(C.MANIFEST_COLUMNS), "manifest_build_sha256": sha_file(mb), "manifest_check_sha256": sha_file(mc),
           "n_build_shots": len(bm), "n_check_shots": len(cm), "build_shots_by_source": by_src(bm), "check_shots_by_source": by_src(cm),
           "build_total_duration_s": dur(bm), "check_total_duration_s": dur(cm), "build_check_shot_id_overlap": len(ids_b & ids_c),
           "match_shot_count_full_file": len(shots), "match_frames_full_file": n_match, "match_duration_s": round(n_match / FPS, 3),
           "match_build_range_s": [min(float(r["t_start_s"]) for r in bm if r["source_id"] == MATCH_ID), max(float(r["t_end_s"]) for r in bm if r["source_id"] == MATCH_ID)],
           "match_check_range_s": [min(float(r["t_start_s"]) for r in cm), max(float(r["t_end_s"]) for r in cm)],
           "match_shots_straddling_split_points": [{"shot_index": i, "t_start_s": s / FPS, "t_end_s": e / FPS} for i, s, e in straddle],
           "sources_hashes_sha256": src_hash, "source_notes": notes, "all_source_ids_resolve": all(os.path.exists(v) for v in src_map.values()),
           "boundary_valid": all(float(r["t_end_s"]) > float(r["t_start_s"]) >= 0 for r in bm + cm),
           "shot_rule_consistency_first_150s_vs_earlier_segment_cuts": consistency, "context_clip_checks": ctx,
           "events_set_open_hashes": {"build": ev_b["data"]["manifest_sha256"], "check": ev_c["data"]["manifest_sha256"]},
           "labels_present": {"build": len(ws._label_rows("build")), "check": len(ws._label_rows("check"))},
           "classifier_implemented": False}
    json.dump(rep, open(a.report, "w"), indent=1, sort_keys=True); print(json.dumps(rep, indent=1, sort_keys=True))


if __name__ == "__main__": main()
