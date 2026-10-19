"""Builds renderer inputs from the PRIVATE out-of-fold decision table and renders source-rate annotated videos (EVALUATED / CARRIED-FORWARD / NO-EVAL) with the locked renderer semantics.
Footage-derived outputs stay in the private out_dir; they are never committed. Only the sidecar counts and hashes may be recorded."""
import os, sys, csv, json, argparse, collections
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, REPO)
from v061.impl.render import render_video as RV
def build_inputs(oof_csv, tracklets_json, clip, out_dir):
    dec = [r for r in csv.DictReader(open(oof_csv, newline="")) if r["clip"] == clip]
    trs = {t["tid"]: dict(zip(t["frames"], t["boxes"])) for t in json.load(open(tracklets_json))}
    dp = os.path.join(out_dir, f"decisions_{clip}.csv"); bp = os.path.join(out_dir, f"boxes_{clip}.csv")
    with open(dp, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["clip", "tracklet", "frame", "truth", "decision", "reason", "g", "q"])
        for r in dec: w.writerow([clip, r["tracklet"], r["frame"], r["truth"], r["decision"], r["reason"], r["g"], r["q"]])
    with open(bp, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["tracklet", "frame", "x1", "y1", "x2", "y2"])
        for r in dec:
            b = trs[r["tracklet"]][int(r["frame"])]; w.writerow([r["tracklet"], r["frame"], *b])
    return dp, bp, len(dec)
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--frozen_dir", default=os.environ.get("V061_FROZEN_DIR")); ap.add_argument("--out_dir", default=os.environ.get("V061_PRIVATE_DATA_DIR")); a = ap.parse_args()
    frozen, out = os.path.abspath(a.frozen_dir), os.path.abspath(a.out_dir); oof = os.path.join(out, "OOF_DECISIONS_PRIVATE.csv"); summary = {}
    clips = sorted({r["clip"] for r in csv.DictReader(open(oof, newline=""))})
    for clip in clips:
        dp, bp, n = build_inputs(oof, os.path.join(frozen, "tracklets", f"{clip}.json"), clip, out)
        vid = os.path.join(frozen, "norm", f"{clip}.mp4"); vo = os.path.join(out, f"RENDER_{clip}.mp4"); so = os.path.join(out, f"RENDER_{clip}_sidecar.json")
        s = RV.render(vid, dp, bp, vo, so); summary[clip] = dict(n_decision_rows=n, n_source_frames=s["n_source_frames"], fps=s["fps"], status_counts=s["status_counts"], output_video_sha256=RV.sha256_file(vo), sidecar_sha256=RV.sha256_file(so),
                                                                  decisions_sha256=s["decisions_sha256"], source_video_sha256=s["source_video_sha256"])
    json.dump(dict(label="V0.6.1 DEVELOPMENT ONLY - visualization", per_clip=summary), open(os.path.join(out, "RENDER_SUMMARY.json"), "w"), indent=1, sort_keys=True); print(json.dumps(summary, indent=1))
if __name__ == "__main__": main()
