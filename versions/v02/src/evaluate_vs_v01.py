"""Compares V0.1 and V0.2 on the FROZEN pre-development reference benchmark (read-only). Both outputs read from disk; nothing is modified."""
import json, hashlib, sys, pandas as pd, numpy as np
B = json.load(open("benchmark/benchmark_v0.1_reference.json"))
assert hashlib.sha256(open("benchmark/benchmark_v0.1_reference.json", "rb").read()).hexdigest() == open("benchmark/MANIFEST.sha256").read().split()[0], "BENCHMARK CHANGED"
v1 = pd.read_csv("../out/tracking_full.csv"); v2 = pd.read_csv("out/tracking_v02.csv")
EM = ["MEASURED", "PARTIAL"]; ANY = ["MEASURED", "PARTIAL", "PREDICTED"]
def sub(df, fr): return df[df.frame.isin(fr)]
def rate(df, fr, sts): s = sub(df, fr); return int(s.status.isin(sts).sum()), len(s)
R = {}
def cat(name, fr, sts, want):
    a1, n = rate(v1, fr, sts); a2, _ = rate(v2, fr, sts); R[name] = dict(n=n, v01=a1, v02=a2, want=want)
wrong = sorted(set(B["wrong_identity_frames"]["DEV_viewed"]) | set(B["wrong_identity_frames"]["AUD"]))
cat("wrong-person frames: COM emitted (MEASURED/PARTIAL)", wrong, EM, "0")
cat("wrong-person frames: any COM incl. PREDICTED", wrong, ANY, "0")
cat("AUDITOR wrong-person frames: MEASURED/PARTIAL", B["wrong_identity_frames"]["AUD"], EM, "0")
cat("viewed multi-body (POSE-MIX) frames: MEASURED/PARTIAL", B["pose_contamination_frames_viewed_DEV"], EM, "0")
cat("viewed distorted-pose frames: MEASURED/PARTIAL", B["pose_distorted_frames_viewed_DEV"], EM, "0")
cat("no-target (crowd) frames: any COM", B["no_target_frames_viewed_DEV"], ANY, "0")
cat("viewed CLEAN target frames: retained (MEASURED/PARTIAL)", B["clean_target_frames_viewed_DEV"], EM, "high (missingness cost if low)")
cat("viewed overlap-but-correct frames: retained", B["overlap_target_correct_frames_viewed_DEV"], EM, "(either; fail-closed expected)")
def rng(rs): return sorted({f for a, b in rs for f in range(a, b + 1)})
cat("inferred contamination ranges (developer ranges): MEASURED/PARTIAL", rng(B["pose_contamination_ranges_inferred_DEV"]), EM, "0 (inferred extents, includes frames not viewed)")
cat("inferred wrong-ID ranges: MEASURED/PARTIAL", rng(B["wrong_identity_ranges_inferred_DEV"]), EM, "0 (inferred extents)")
import pickle
dets = pickle.load(open("../out/raw_detections.pkl", "rb"))
def _iou(a, b):
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]); i = max(0, x2-x1)*max(0, y2-y1); u = (a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-i; return i/u if u > 0 else 0
same, diff = [], []
for f in wrong:
    r1 = v1[v1.frame == f].iloc[0]; r2 = v2[v2.frame == f].iloc[0]
    if r2.status not in ANY or pd.isna(r2.selected_det_index) or pd.isna(r1.selected_box_x1): continue
    b2 = dets[f]["box"][int(r2.selected_det_index)]; b1 = [r1.selected_box_x1, r1.selected_box_y1, r1.selected_box_x2, r1.selected_box_y2]
    (same if _iou(b1, b2) >= 0.5 else diff).append(f)
out = dict(categories=R)
out["wrong_person_detail"] = dict(v02_emits_on_SAME_box_as_v01_wrong_selection=same, v02_emits_on_DIFFERENT_box_needs_visual_check=diff, n_labelled=len(wrong))
# cuts
c1 = set(B["cuts_AUD"]["v01_reported"]); fp = set(B["cuts_AUD"]["false_positive"]); tc = set(B["cuts_AUD"]["true_cuts"])
cuts2 = set(json.load(open("out/cuts_v02.json"))["cuts"][i]["frame"] for i in range(len(json.load(open("out/cuts_v02.json"))["cuts"])))
def prf(det): tp = len(det & tc); return dict(detected=len(det), true_pos=tp, false_pos=len(det - tc), missed=len(tc - det), precision=round(tp / len(det), 3) if det else None, recall=round(tp / len(tc), 3))
out["cuts"] = dict(v01=prf(c1), v02=prf(cuts2), v02_false_positive_frames=sorted(cuts2 - tc), v02_missed=sorted(tc - cuts2), note="IN-SAMPLE: V0.2 cut thresholds were chosen after examining these events; auditor labels come from one reviewer")
# overall status
def dist(df): return {k: int((df.status == k).sum()) for k in ["MEASURED", "PARTIAL", "PREDICTED", "UNRESOLVED"]}
out["status_counts"] = dict(v01=dist(v1), v02=dist(v2))
# prediction behaviour
def pred_stats(df, W=640, H=360):
    p = df[df.status == "PREDICTED"]; off = p[(p.COM_x_pixel < 0) | (p.COM_x_pixel > W) | (p.COM_y_pixel < 0) | (p.COM_y_pixel > H)]
    return dict(n=len(p), off_image=len(off), off_frames=off.frame.tolist())
out["prediction"] = dict(v01=pred_stats(v1), v02=pred_stats(v2))
# on frames where both emit COM: agreement
both = v1.merge(v2, on="frame", suffixes=("_1", "_2")); e = both[both.status_1.isin(EM) & both.status_2.isin(EM)]
d = np.hypot(e.COM_x_pixel_1 - e.COM_x_pixel_2, e.COM_y_pixel_1 - e.COM_y_pixel_2)
out["agreement_when_both_emit"] = dict(n=len(e), median_px=round(float(d.median()), 3), max_px=round(float(d.max()), 3))
out["v01_tracked_frames_dropped_by_v02"] = int((v1.status.isin(EM) & ~v2.status.isin(ANY)).sum()); out["v01_tracked_frames_kept_by_v02"] = int((v1.status.isin(EM) & v2.status.isin(EM)).sum())
out["v02_emits_where_v01_did_not"] = int((~v1.status.isin(EM) & v2.status.isin(EM)).sum())
out["v02_unresolved_reasons"] = v2[v2.status == "UNRESOLVED"].unresolved_reason.value_counts().to_dict()
json.dump(out, open("out/comparison_metrics.json", "w"), indent=1, default=int); print(json.dumps(out, indent=1, default=int))
