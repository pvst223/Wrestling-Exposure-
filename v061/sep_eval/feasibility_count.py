#!/usr/bin/env python3
"""FEASIBILITY COUNT (counts only; no skeletons viewed, no verdicts, no images). Counts frozen ASSIGNED_A/B measured rows and how many satisfy the frozen eligibility criterion (and the 10%/25% margin sensitivities), per clip and shot.
Input per clip: frozen dets pickle {frame: {box, conf}} and a rows pickle {rows, cuts, W, H} with fields tracklet, frame, det, record_class, shot. Writes aggregate counts only.
When run on already-burned clips the output is INDICATIVE YIELD ONLY and cannot support KEEP."""
import argparse, collections, json, os, pickle, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "impl"))
import eligibility as E
from drawn import drawn_landmarks
def clip_counts(dets, D, with_rows=False):
    rows, W, H = D["rows"], D["W"], D["H"]; cuts = sorted(D["cuts"]); byt = collections.defaultdict(dict)
    for r in rows:
        if r.get("det") is not None and r.get("pose_status") == "MEASURED": byt[r["tracklet"]][r["frame"]] = r["det"]
    import bisect
    shot_of = lambda f: bisect.bisect_right(cuts, f)
    out = collections.Counter(); per_shot = collections.defaultdict(lambda: collections.Counter()); why = collections.Counter(); keep = []
    for r in rows:
        if r["record_class"] not in ("ASSIGNED_A", "ASSIGNED_B") or r.get("det") is None: continue
        t = byt[r["tracklet"]]; f = r["frame"]
        dets_at = lambda g: ((dets[g]["box"], dets[g]["conf"]) if g in dets else None); tbox_at = lambda g: t.get(g)
        out["assigned_measured"] += 1; ok, w = E.eligible(f, dets_at, tbox_at, shot_of, W, H); why[w] += 1
        ok10, _ = E.eligible(f, dets_at, tbox_at, shot_of, W, H, margin=0.10); ok25, _ = E.eligible(f, dets_at, tbox_at, shot_of, W, H, margin=0.25)
        okc, _ = E.eligible(f, dets_at, tbox_at, shot_of, W, H, ignore_contained=0.8); out["DESCRIPTIVE_VARIANT_ignore_boxes_80pct_inside_target_NOT_ADOPTED"] += okc
        out["eligible"] += ok; out["eligible_margin10"] += ok10; out["eligible_margin25"] += ok25; per_shot[(r["shot"])]["assigned"] += 1; per_shot[r["shot"]]["eligible"] += ok
        if with_rows: keep.append(dict(tracklet=r["tracklet"], frame=f, shot=r["shot"], record_class=r["record_class"], assigned_label=r.get("assigned_label"), det=int(r["det"]), box=[float(v) for v in r["box"]], n_drawn=len(drawn_landmarks(r["box"], r["kp"], r["kpc"])), eligible=bool(ok), eligible10=bool(ok10), eligible25=bool(ok25)))
    return dict(out), {str(k): dict(v) for k, v in sorted(per_shot.items())}, dict(why), keep
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dets-dir", required=True); ap.add_argument("--rows-dir", required=True); ap.add_argument("--clips", nargs="+", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
    res = dict(label="FEASIBILITY COUNT ONLY (counts; no verdicts, images or skeletons viewed). Burned clips => indicative yield only, cannot support KEEP.", clips={}, params=E.PARAMS)
    for c in a.clips:
        dets = pickle.load(open(os.path.join(a.dets_dir, f"dets_{c}.pkl"), "rb")); D = pickle.load(open(os.path.join(a.rows_dir, f"ROWS_{c}.pkl"), "rb"))
        cnt, shots, why, _ = clip_counts(dets, D); res["clips"][c] = dict(counts=cnt, n_shots_with_eligible=sum(1 for v in shots.values() if v.get("eligible", 0) > 0), n_shots_with_assigned=len(shots), reasons=why)
    tot = collections.Counter()
    for v in res["clips"].values(): tot.update(v["counts"])
    res["totals"] = dict(tot); json.dump(res, open(a.out, "w"), indent=1, sort_keys=True); print(json.dumps(res["totals"], indent=1))
if __name__ == "__main__": main()
