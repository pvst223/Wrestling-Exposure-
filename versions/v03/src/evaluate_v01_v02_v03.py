"""Three-way comparison V0.1 vs V0.2 vs V0.3 on the FROZEN pre-development reference benchmark (read-only) and on structural metrics.
Reads outputs from disk; modifies nothing except out/comparison_metrics_v03.json. Run from the v03 directory.
ALL numbers are IN-SAMPLE / development-clip numbers; the benchmark is single-reviewer, non-blinded, and V0.2 AND V0.3 designs were informed by this clip.
SEED frames (manual identity initialisation) are excluded from every benchmark-category count and are reported separately."""
import json, hashlib, pickle, sys, os, pandas as pd, numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
BP = os.path.join(ROOT, "v02", "benchmark", "benchmark_v0.1_reference.json")
assert hashlib.sha256(open(BP, "rb").read()).hexdigest() == open(os.path.join(ROOT, "v02", "benchmark", "MANIFEST.sha256")).read().split()[0], "BENCHMARK CHANGED"
B = json.load(open(BP)); meta = json.load(open(os.path.join(ROOT, "v03", "out", "run_meta_v03.json"))); SEEDS = set(meta["seed_frames"])
v1 = pd.read_csv(os.path.join(ROOT, "out", "tracking_full.csv")); v2 = pd.read_csv(os.path.join(ROOT, "v02", "out", "tracking_v02.csv")); v3all = pd.read_csv(os.path.join(ROOT, "v03", "out", "tracking_v03.csv"))
v3 = v3all[v3all.target == "A"].reset_index(drop=True); v3b = v3all[v3all.target == "B"].reset_index(drop=True)
dets = pickle.load(open(os.path.join(ROOT, "out", "raw_detections.pkl"), "rb"))
EM = ["MEASURED", "PARTIAL"]; ANY = EM + ["PREDICTED"]; ST = ["MEASURED", "PARTIAL", "PREDICTED", "UNRESOLVED"]
def rng(rs): return sorted({f for a, b in rs for f in range(a, b + 1)})
def sub(df, fr): return df[df.frame.isin(fr)]
def cnt(df, fr, sts): return int(sub(df, fr).status.isin(sts).sum())
R = {}
def cat(name, frames, sts, want):
    fr = sorted(set(frames) - SEEDS); R[name] = dict(n=len(fr), v01=cnt(v1, fr, sts), v02=cnt(v2, fr, sts), v03=cnt(v3, fr, sts), want=want, n_seed_frames_excluded=len(set(frames) & SEEDS))
wrong = sorted(set(B["wrong_identity_frames"]["DEV_viewed"]) | set(B["wrong_identity_frames"]["AUD"]))
cat("wrong-person frames (viewed+auditor): COM emitted MEASURED/PARTIAL", wrong, EM, "0")
cat("wrong-person frames: any COM incl PREDICTED", wrong, ANY, "0")
cat("AUDITOR wrong-person frames: MEASURED/PARTIAL", B["wrong_identity_frames"]["AUD"], EM, "0")
cat("viewed multi-body (POSE-MIX) frames: MEASURED/PARTIAL", B["pose_contamination_frames_viewed_DEV"], EM, "0")
cat("viewed distorted-pose frames: MEASURED/PARTIAL", B["pose_distorted_frames_viewed_DEV"], EM, "0")
cat("no-target (crowd) frames: any COM", B["no_target_frames_viewed_DEV"], ANY, "0")
cat("viewed CLEAN target frames: retained MEASURED/PARTIAL", B["clean_target_frames_viewed_DEV"], EM, "high")
cat("viewed overlap-but-correct frames: retained", B["overlap_target_correct_frames_viewed_DEV"], EM, "either")
cat("inferred contamination ranges: MEASURED/PARTIAL (inferred extents, includes frames never viewed)", rng(B["pose_contamination_ranges_inferred_DEV"]), EM, "0")
cat("inferred wrong-ID ranges: MEASURED/PARTIAL (inferred extents)", rng(B["wrong_identity_ranges_inferred_DEV"]), EM, "0")
def iou(a, b):
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]); i = max(0, x2-x1)*max(0, y2-y1); u = (a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-i; return i/u if u > 0 else 0
# ---- wrong-person detail: does V0.3 emit A on the box V0.1 wrongly selected? is that box instead assigned to B?
det_rows = []
for f in wrong:
    if f in SEEDS: continue
    r1 = v1[v1.frame == f].iloc[0]; r3 = v3[v3.frame == f].iloc[0]; rb = v3b[v3b.frame == f].iloc[0]
    if pd.isna(r1.selected_box_x1): det_rows.append(dict(frame=f, v01_box="none", v03_A_status=r3.status, v03_B_status=rb.status)); continue
    b1 = [r1.selected_box_x1, r1.selected_box_y1, r1.selected_box_x2, r1.selected_box_y2]
    ia = None if pd.isna(r3.selected_det_index) else iou(b1, dets[f]["box"][int(r3.selected_det_index)]); ib = None if pd.isna(rb.selected_det_index) else iou(b1, dets[f]["box"][int(rb.selected_det_index)])
    det_rows.append(dict(frame=f, v03_A_status=r3.status, v03_A_reason=r3.unresolved_reason, v03_A_selected_IoU_with_v01_wrong_box=None if ia is None else round(ia, 2), v03_B_status=rb.status, v03_B_selected_IoU_with_v01_wrong_box=None if ib is None else round(ib, 2)))
wrong_detail = dict(rows=det_rows, A_emits_on_v01_wrong_box=[d["frame"] for d in det_rows if d.get("v03_A_status") in ANY and (d.get("v03_A_selected_IoU_with_v01_wrong_box") or 0) >= 0.5],
                    A_emits_on_other_box_needs_visual_check=[d["frame"] for d in det_rows if d.get("v03_A_status") in ANY and (d.get("v03_A_selected_IoU_with_v01_wrong_box") or 0) < 0.5],
                    v01_wrong_box_assigned_to_B=[d["frame"] for d in det_rows if d.get("v03_B_status") in ANY and (d.get("v03_B_selected_IoU_with_v01_wrong_box") or 0) >= 0.5])
# ---- cuts
tc = set(B["cuts_AUD"]["true_cuts"]); c1 = set(B["cuts_AUD"]["v01_reported"]); c2 = {c["frame"] for c in json.load(open(os.path.join(ROOT, "v02", "out", "cuts_v02.json")))["cuts"]}; c3 = {c["frame"] for c in json.load(open(os.path.join(ROOT, "v03", "out", "cuts_v03.json")))["cuts"]}
def prf(s): tp = len(s & tc); return dict(detected=len(s), true_pos=tp, false_pos=len(s - tc), missed=len(tc - s))
cuts = dict(v01=prf(c1), v02=prf(c2), v03=prf(c3), v03_identical_to_v02=c2 == c3, note="IN-SAMPLE: the persistence rule was designed after examining these events; auditor labels = one reviewer")
# ---- status counts
def dist(df): return {k: int((df.status == k).sum()) for k in ST}
status = dict(v01=dist(v1), v02=dist(v2), v03_A=dist(v3), v03_B_no_ground_truth=dist(v3b))
# ---- prediction
def pred(df, W=640, H=360):
    p = df[df.status == "PREDICTED"]; off = p[(p.COM_x_pixel < 0) | (p.COM_x_pixel > W) | (p.COM_y_pixel < 0) | (p.COM_y_pixel > H)]; return dict(n=len(p), off_image=len(off))
prediction = dict(v01=pred(v1), v02=pred(v2), v03_A=pred(v3), v03_B=pred(v3b))
# ---- known-bad frame sets (viewed + auditor + inferred extents) and V0.3 emissions inside them
KB = set(wrong) | set(B["pose_contamination_frames_viewed_DEV"]) | set(B["pose_distorted_frames_viewed_DEV"]) | set(rng(B["pose_contamination_ranges_inferred_DEV"])) | set(rng(B["wrong_identity_ranges_inferred_DEV"]))
KBe = sorted(KB - SEEDS)
kb = dict(n_known_or_inferred_bad_frames=len(KBe), v01_emits=cnt(v1, KBe, EM), v02_emits=cnt(v2, KBe, EM), v03_A_emits=cnt(v3, KBe, EM), v03_A_emits_incl_predicted=cnt(v3, KBe, ANY),
          note="known-bad = viewed wrong-person + auditor + viewed contaminated/distorted + INFERRED ranges (the inferred ranges contain frames that were never individually viewed and may include some clean frames)")
kb["v03_A_emitting_frames_in_known_bad"] = sorted(sub(v3, KBe)[sub(v3, KBe).status.isin(ANY)].frame.tolist())
# ---- recovery of V0.2 rejections
m = v1[["frame", "status"]].rename(columns={"status": "s1"}).merge(v2[["frame", "status"]].rename(columns={"status": "s2"}), on="frame").merge(v3[["frame", "status", "unresolved_reason"]].rename(columns={"status": "s3", "unresolved_reason": "r3"}), on="frame")
nb = m[m.s1.isin(EM) & ~m.frame.isin(KB) & ~m.frame.isin(SEEDS)]
rec = dict(v01_tracked_not_known_bad=len(nb), v02_kept=int(nb.s2.isin(EM).sum()), v02_dropped=int((~nb.s2.isin(ANY)).sum()), v03_kept=int(nb.s3.isin(EM).sum()), v03_dropped=int((~nb.s3.isin(ANY)).sum()),
           v02_dropped_but_v03_emits=int(((~nb.s2.isin(ANY)) & nb.s3.isin(EM)).sum()), v02_kept_but_v03_drops=int((nb.s2.isin(EM) & ~nb.s3.isin(ANY)).sum()))
emit = dict(v03_emits_where_v02_did_not=int((m.s3.isin(EM) & ~m.s2.isin(EM)).sum()), v02_emits_where_v03_does_not=int((m.s2.isin(EM) & ~m.s3.isin(EM)).sum()), v03_emits_where_v01_did_not=int((m.s3.isin(EM) & ~m.s1.isin(EM)).sum()), v03_emits_where_neither_v01_nor_v02_did=int((m.s3.isin(EM) & ~m.s1.isin(EM) & ~m.s2.isin(EM)).sum()))
both = v2.merge(v3, on="frame", suffixes=("_2", "_3")); e = both[both.status_2.isin(EM) & both.status_3.isin(EM)]; d = np.hypot(e.COM_x_pixel_2 - e.COM_x_pixel_3, e.COM_y_pixel_2 - e.COM_y_pixel_3)
agree = dict(n=len(e), median_px=round(float(d.median()), 3) if len(e) else None, max_px=round(float(d.max()), 3) if len(e) else None, n_diff_box=int(((e.selected_det_index_2 != e.selected_det_index_3)).sum()))
# ---- reasons
reasons = dict(v02=v2[v2.status == "UNRESOLVED"].unresolved_reason.value_counts().to_dict(), v03_A=v3[v3.status == "UNRESOLVED"].unresolved_reason.value_counts().to_dict(), v03_B=v3b[v3b.status == "UNRESOLVED"].unresolved_reason.value_counts().to_dict())
# ---- anatomy / identity tiers of emissions
em3 = v3[v3.status.isin(EM)]; tiers = dict(identity_tier=em3.identity_tier.value_counts().to_dict(), anatomy_tier=em3.anatomy_tier.value_counts().to_dict(), limiting_factors=em3.status_limiting_factors.fillna("").value_counts().to_dict(), positive_coherence=em3.positive_coherence.fillna("none").value_counts().to_dict())
# ---- identity-switch evidence: box-centre jumps between consecutive EMITTED frames within a shot (gap <= 2) in units of box diagonal; and A/B box swaps
def boxes_v1(df): return {int(r.frame): [r.selected_box_x1, r.selected_box_y1, r.selected_box_x2, r.selected_box_y2] for r in df.itertuples() if r.status in EM and not pd.isna(r.selected_box_x1)}
def boxes_det(df): return {int(r.frame): dets[int(r.frame)]["box"][int(r.selected_det_index)] for r in df.itertuples() if r.status in EM and not pd.isna(r.selected_det_index)}
def jumps(bx, df, thr=1.0):
    seg = dict(zip(df.frame, df.camera_segment)); fr = sorted(bx); out = []
    for a, b in zip(fr, fr[1:]):
        if b - a <= 2 and seg[a] == seg[b]:
            ca = np.array([(bx[a][0]+bx[a][2])/2, (bx[a][1]+bx[a][3])/2]); cb = np.array([(bx[b][0]+bx[b][2])/2, (bx[b][1]+bx[b][3])/2]); dg = np.hypot(bx[a][2]-bx[a][0], bx[a][3]-bx[a][1])
            if np.linalg.norm(cb - ca) / dg > thr: out.append((a, b))
    return out
bx1, bx2, bx3, bx3b = boxes_v1(v1), boxes_det(v2), boxes_det(v3), boxes_det(v3b)
seg1 = v1[["frame", "camera_segment"]]
sw = []
for t in sorted(bx3):   # A at t has the box that B had at t-1 (or t-2) and not A's own previous box
    for g in (1, 2):
        if (t - g) in bx3b and (t - g) in bx3 and iou(bx3[t], bx3b[t - g]) >= 0.5 and iou(bx3[t], bx3[t - g]) < 0.3 and v3.loc[v3.frame == t, "camera_segment"].iloc[0] == v3.loc[v3.frame == t - g, "camera_segment"].iloc[0]: sw.append((t - g, t)); break
switch = dict(v01_emitted_box_jumps_gt1diag_gap_le2=len(jumps(bx1, v1)), v02=len(jumps(bx2, v2)), v03_A=len(jumps(bx3, v3)), v03_B=len(jumps(bx3b, v3b)), v03_A_jump_frames=jumps(bx3, v3), v03_A_takes_B_previous_box=sw,
              A_and_B_same_detection_frames=int(((v3.selected_det_index == v3b.selected_det_index) & v3.selected_det_index.notna()).sum()),
              note="box-jump = centre displacement > 1 box diagonal between consecutive emitted frames <= 2 frames apart in the same shot; a lower bound on switches (a switch between two near-by people is not a jump)")
# ---- shots
shots = []
for s, g in v3.groupby("camera_segment"):
    e_ = g[g.status.isin(EM)]; shots.append(dict(seg=int(s), n=len(g), emitted=len(e_), first_emission_latency=None if len(e_) == 0 else int(e_.frame.iloc[0] - g.frame.iloc[0])))
out = dict(categories=R, wrong_person_detail=wrong_detail, cuts=cuts, status_counts=status, prediction=prediction, known_bad=kb, recovery=rec, emissions=emit, agreement_v02_v03=agree, unresolved_reasons=reasons, v03_emission_tiers=tiers, identity_switch_evidence=switch,
           shots=dict(n_shots_v03=len(shots), shots_with_emission=sum(1 for s in shots if s["emitted"] > 0), median_latency=float(np.median([s["first_emission_latency"] for s in shots if s["first_emission_latency"] is not None])), per_shot=shots), seed_frames_excluded=sorted(SEEDS))
json.dump(out, open(os.path.join(ROOT, "v03", "out", "comparison_metrics_v03.json"), "w"), indent=1, default=int); print(json.dumps({k: out[k] for k in out if k not in ("shots",)}, indent=1, default=int))
