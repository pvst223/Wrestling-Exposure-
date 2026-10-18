"""Comparison V0.1 / V0.2 / V0.3 / V0.4 on the FROZEN pre-development reference benchmark (read-only), the specification's regression cases, and structural metrics.
Reads outputs from disk; writes only v04/out/comparison_metrics_v04.json. ALL numbers are IN-SAMPLE development numbers: the clip informed the design of V0.2, V0.3 AND V0.4, the benchmark is
single-reviewer and non-blinded, there is no ground truth. Seed frames are excluded from every benchmark-category count. V0.4 numbers are for wrestler A (the benchmark target) unless stated."""
import json, hashlib, pickle, sys, os, pandas as pd, numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUTD = os.environ.get("V04_OUT_DIR", os.path.join(ROOT, "v04", "out"))   # default: the frozen run output directory
BP = os.path.join(ROOT, "v02", "benchmark", "benchmark_v0.1_reference.json")
assert hashlib.sha256(open(BP, "rb").read()).hexdigest() == open(os.path.join(ROOT, "v02", "benchmark", "MANIFEST.sha256")).read().split()[0], "BENCHMARK CHANGED"
B = json.load(open(BP)); meta = json.load(open(os.path.join(OUTD, "run_meta_v04.json"))); SEEDS = set(meta["seed_frames"])
v1 = pd.read_csv(os.path.join(ROOT, "out", "tracking_full.csv")); v2 = pd.read_csv(os.path.join(ROOT, "v02", "out", "tracking_v02.csv"))
v3all = pd.read_csv(os.path.join(ROOT, "v03", "out", "tracking_v03.csv")); v3 = v3all[v3all.target == "A"].reset_index(drop=True); v3b = v3all[v3all.target == "B"].reset_index(drop=True)
v4all = pd.read_csv(os.path.join(OUTD, "tracking_v04.csv")); v4 = v4all[v4all.target == "A"].reset_index(drop=True); v4b = v4all[v4all.target == "B"].reset_index(drop=True)
cand4 = pd.read_csv(os.path.join(OUTD, "candidates_v04.csv")); ev4 = pd.read_csv(os.path.join(OUTD, "identity_events_v04.csv")); dets = pickle.load(open(os.path.join(ROOT, "out", "raw_detections.pkl"), "rb"))
EM = ["MEASURED", "PARTIAL"]; ANY = EM + ["PREDICTED"]; ST = ["MEASURED", "PARTIAL", "PREDICTED", "UNRESOLVED"]
def rng(rs): return sorted({f for a, b in rs for f in range(a, b + 1)})
def sub(df, fr): return df[df.frame.isin(fr)]
def cnt(df, fr, sts): return int(sub(df, fr).status.isin(sts).sum())
R = {}
def cat(name, frames, sts, want):
    fr = sorted(set(frames) - SEEDS); R[name] = dict(n=len(fr), v01=cnt(v1, fr, sts), v02=cnt(v2, fr, sts), v03=cnt(v3, fr, sts), v04=cnt(v4, fr, sts), want=want, n_seed_frames_excluded=len(set(frames) & SEEDS))
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
# ---- specification regression cases (frame-by-frame, all versions). DIAGNOSTIC ONLY.
REG = {"v01_wrong_person": [376, 386, 392, 753, 772, 1196], "contamination": [270] + list(range(275, 280)) + [290, 925, 935, 938, 950, 951, 957, 1075, 1078, 1079, 1080, 1081, 1088, 1089, 1092],
       "identity_insufficient_closeups": [692, 725, 732, 736], "AB_concern": [1114, 1166, 1179, 1204], "former_false_cut_events": [292, 434, 753, 1062]}
def row(df, f): return df[df.frame == f].iloc[0]
reg_rows = []
for grp, fr in REG.items():
    for f in fr:
        r1, r2, r3, r4, r4b = row(v1, f), row(v2, f), row(v3, f), row(v4, f), row(v4b, f); b3 = row(v3b, f)
        reg_rows.append(dict(group=grp, frame=f, seed_frame=f in SEEDS, v01=r1.status, v02=r2.status, v03_A=r3.status, v03_A_reason=r3.unresolved_reason if isinstance(r3.unresolved_reason, str) else "", v04_A=r4.status, v04_A_identity_state=r4.identity_state, v04_A_reason=r4.unresolved_reason if isinstance(r4.unresolved_reason, str) else "",
                             v04_A_anatomy=f"{r4.anatomy_status}/{r4.anatomy_tier}", v04_A_anatomy_reasons=r4.anatomy_reasons if isinstance(r4.anatomy_reasons, str) else "", v03_B=b3.status, v04_B=r4b.status, v04_B_identity_state=r4b.identity_state, v04_B_reason=r4b.unresolved_reason if isinstance(r4b.unresolved_reason, str) else ""))
reg = pd.DataFrame(reg_rows); reg.to_csv(os.path.join(OUTD, "regression_cases_v04.csv"), index=False)
reg_sum = {}
for grp in REG:
    g = reg[(reg.group == grp) & ~reg.seed_frame]
    reg_sum[grp] = dict(n=len(g), **{k: int(g[k].isin(EM).sum()) for k in ("v01", "v02", "v03_A", "v04_A")}, v04_A_predicted=int((g.v04_A == "PREDICTED").sum()), v04_B_emits=int(g.v04_B.isin(EM).sum()), v03_B_emits=int(g.v03_B.isin(EM).sum()))
# ---- identity-level wrong-person check: does V0.4 assign A/B IDENTITY (independent of COM status) to the box V0.1 wrongly selected?
wp = []
for f in wrong:
    if f in SEEDS: continue
    r1 = row(v1, f)
    if pd.isna(r1.selected_box_x1): wp.append(dict(frame=f, v01_box="none")); continue
    b1 = [r1.selected_box_x1, r1.selected_box_y1, r1.selected_box_x2, r1.selected_box_y2]; d_ = dict(frame=f)
    for nm, df in (("A", v4), ("B", v4b)):
        r = row(df, f); d_[f"v04_{nm}_identity_state"] = r.identity_state; d_[f"v04_{nm}_status"] = r.status
        d_[f"v04_{nm}_identity_box_IoU_with_v01_wrong_box"] = None if (pd.isna(r.selected_det_index) or not r.identity_track_continues) else round(iou(b1, dets[f]["box"][int(r.selected_det_index)]), 2)
    wp.append(d_)
wrong_identity_detail = dict(rows=wp, A_identity_on_v01_wrong_box=[d["frame"] for d in wp if (d.get("v04_A_identity_box_IoU_with_v01_wrong_box") or 0) >= 0.5], B_identity_on_v01_wrong_box=[d["frame"] for d in wp if (d.get("v04_B_identity_box_IoU_with_v01_wrong_box") or 0) >= 0.5],
                       note="a B assignment on V0.1's wrong box is not necessarily an error (V0.1's wrong box may be the real B)")
# ---- cuts
tc = set(B["cuts_AUD"]["true_cuts"]); c1 = set(B["cuts_AUD"]["v01_reported"]); c2 = {c["frame"] for c in json.load(open(os.path.join(ROOT, "v02", "out", "cuts_v02.json")))["cuts"]}; c3 = {c["frame"] for c in json.load(open(os.path.join(ROOT, "v03", "out", "cuts_v03.json")))["cuts"]}; c4 = {c["frame"] for c in json.load(open(os.path.join(OUTD, "cuts_v04.json")))["cuts"]}
def prf(s): tp = len(s & tc); return dict(detected=len(s), true_pos=tp, false_pos=len(s - tc), missed=len(tc - s))
cuts = dict(v01=prf(c1), v02=prf(c2), v03=prf(c3), v04=prf(c4), v04_identical_to_v03=c3 == c4, v04_cut_log_bytes_identical_to_v03=open(os.path.join(OUTD, "cuts_v04.json"), "rb").read() == open(os.path.join(ROOT, "v03", "out", "cuts_v03.json"), "rb").read(), note="IN-SAMPLE")
def dist(df): return {k: int((df.status == k).sum()) for k in ST}
status = dict(v01=dist(v1), v02=dist(v2), v03_A=dist(v3), v04_A=dist(v4), v03_B_no_ground_truth=dist(v3b), v04_B_no_ground_truth=dist(v4b))
def pred(df, W=640, H=360):
    p = df[df.status == "PREDICTED"]; off = p[(p.COM_x_pixel < 0) | (p.COM_x_pixel > W) | (p.COM_y_pixel < 0) | (p.COM_y_pixel > H)]; return dict(n=len(p), off_image=len(off))
prediction = dict(v01=pred(v1), v02=pred(v2), v03_A=pred(v3), v04_A=pred(v4), v04_B=pred(v4b))
KB = set(wrong) | set(B["pose_contamination_frames_viewed_DEV"]) | set(B["pose_distorted_frames_viewed_DEV"]) | set(rng(B["pose_contamination_ranges_inferred_DEV"])) | set(rng(B["wrong_identity_ranges_inferred_DEV"]))
KBe = sorted(KB - SEEDS)
kb = dict(n_known_or_inferred_bad_frames=len(KBe), v01_emits=cnt(v1, KBe, EM), v02_emits=cnt(v2, KBe, EM), v03_A_emits=cnt(v3, KBe, EM), v04_A_emits=cnt(v4, KBe, EM), v04_A_emits_incl_predicted=cnt(v4, KBe, ANY),
          v04_A_emitting_frames_in_known_bad=sorted(sub(v4, KBe)[sub(v4, KBe).status.isin(ANY)].frame.tolist()), note="known-bad includes INFERRED ranges containing never-viewed frames")
# ---- recovery of V0.3 missingness
m = v1[["frame", "status"]].rename(columns={"status": "s1"}).merge(v2[["frame", "status"]].rename(columns={"status": "s2"}), on="frame").merge(v3[["frame", "status", "unresolved_reason"]].rename(columns={"status": "s3", "unresolved_reason": "r3"}), on="frame").merge(v4[["frame", "status", "unresolved_reason", "identity_state", "status_limiting_factors"]].rename(columns={"status": "s4", "unresolved_reason": "r4"}), on="frame")
ins = m[(m.r3 == "IDENTITY_INSUFFICIENT_EVIDENCE") & ~m.frame.isin(SEEDS)]
rec_ins = dict(v03_identity_insufficient_frames=len(ins), of_which_v01_tracked=int(ins.s1.isin(EM).sum()), recovered_by_v04_emitted=int(ins.s4.isin(EM).sum()), recovered_in_known_bad=int((ins.s4.isin(EM) & ins.frame.isin(KB)).sum()), recovered_frames_outside_known_bad=int((ins.s4.isin(EM) & ~ins.frame.isin(KB)).sum()),
               v04_identity_state_of_these=ins.identity_state.value_counts().to_dict(), v04_reason_of_these=ins[~ins.s4.isin(ANY)].r4.value_counts().to_dict())
nb = m[m.s1.isin(EM) & ~m.frame.isin(KB) & ~m.frame.isin(SEEDS)]
emit = dict(v04_emits_where_v03_did_not=int((m.s4.isin(EM) & ~m.s3.isin(EM)).sum()), v03_emits_where_v04_does_not=int((m.s3.isin(EM) & ~m.s4.isin(EM)).sum()), v04_emits_where_v02_did_not=int((m.s4.isin(EM) & ~m.s2.isin(EM)).sum()), v04_emits_where_v01_did_not=int((m.s4.isin(EM) & ~m.s1.isin(EM)).sum()),
            v04_new_vs_v03_in_known_bad=int((m.s4.isin(EM) & ~m.s3.isin(EM) & m.frame.isin(KB)).sum()), v04_dropped_vs_v03_in_known_bad=int((m.s3.isin(EM) & ~m.s4.isin(EM) & m.frame.isin(KB)).sum()),
            v01_tracked_not_known_bad=len(nb), v02_kept=int(nb.s2.isin(EM).sum()), v03_kept=int(nb.s3.isin(EM).sum()), v04_kept=int(nb.s4.isin(EM).sum()))
# ---- identity (A and B)
def idsum(df): return dict(identity_state=df.identity_state.value_counts().to_dict(), identity_track_continues=int(df.identity_track_continues.sum()), emitted_temporal_only=int(((df.status.isin(EM)) & (df.identity_state == "TEMPORAL_CONTINUATION")).sum()),
                         emitted_independent=int(((df.status.isin(EM)) & (df.identity_state == "SUPPORTED_INDEPENDENT")).sum()), identity_known_but_com_unresolved=int(((df.identity_state.isin(["SUPPORTED_INDEPENDENT", "TEMPORAL_CONTINUATION"])) & (~df.status.isin(EM))).sum()),
                         identity_reasons=df[df.identity_reason.notna()].identity_reason.value_counts().to_dict())
identity = dict(A=idsum(v4), B=idsum(v4b), events=ev4.event.value_counts().to_dict(), events_by_wrestler=ev4.groupby(["event", "target"]).size().to_dict().__repr__(),
                A_and_B_both_have_identity_on_same_detection=int(((v4.selected_det_index == v4b.selected_det_index) & v4.selected_det_index.notna() & v4.identity_track_continues & v4b.identity_track_continues).sum()),
                frames_both_emit=int((v4.status.isin(EM) & v4b.status.isin(EM)).sum()))
# ---- did the embedding contribute beyond thigh/colour? (candidates of SELECTED A with independent support)
c = cand4.merge(v4[["frame", "selected_det_index", "identity_state", "status", "colour_R", "reid_R"]].rename(columns={"selected_det_index": "det"}), on=["frame", "det"], how="inner")
c = c[(c.identity_state == "SUPPORTED_INDEPENDENT") & (c.label == "A")]
contrib = dict(n_A_independent_supported_frames=int(len(c)), colour_R_below_R_MIN_APP=int((c.colour_R < 0.8).sum()), thigh_polygon_area_below_600=int((c.denim_area < 600).sum()),
               emitted_without_adequate_colour_evidence=int(((c.colour_R < 0.8) & c.status.isin(EM)).sum()), emitted_without_thigh_polygon=int(((c.denim_area < 600) & c.status.isin(EM)).sum()),
               of_those_emitted_without_colour_evidence_v03_also_emitted=int(((c.colour_R < 0.8) & c.status.isin(EM) & c.frame.isin(v3[v3.status.isin(EM)].frame)).sum()),
               in_known_bad=int(((c.colour_R < 0.8) & c.status.isin(EM) & c.frame.isin(KB)).sum()), note="colour_R = summed reliability of legacy colour+denim cues; the selection needs R_ind >= 0.8, so colour_R < 0.8 means the embedding was NECESSARY for the independent-support threshold")
# ---- anatomy
def ansum(df):
    e = df[df.anatomy_status != ""].dropna(subset=["anatomy_status"])
    return dict(anatomy_status=e.anatomy_status.value_counts().to_dict(), anatomy_tier=e.anatomy_tier.fillna("").value_counts().to_dict(), fail_reasons=pd.Series([r for x in e.anatomy_reasons.dropna() for r in str(x).split(";") if r]).value_counts().to_dict(),
                positive_independent=e.anatomy_positive_independent.fillna("none").replace("", "none").value_counts().to_dict(), com_ineligible=df[df.com_eligibility == "INELIGIBLE"].com_ineligible_reason.value_counts().to_dict())
anat = dict(A=ansum(v4), B=ansum(v4b)); em4 = v4[v4.status.isin(EM)]
tiers = dict(identity_tier=em4.identity_tier.value_counts().to_dict(), identity_state=em4.identity_state.value_counts().to_dict(), anatomy_tier=em4.anatomy_tier.value_counts().to_dict(), limiting_factors=em4.status_limiting_factors.fillna("").value_counts().to_dict(), overlap_context=int(em4.overlap_context.sum()), merge_risk=int(em4.merge_risk.sum()))
reasons = dict(v03_A=v3[v3.status == "UNRESOLVED"].unresolved_reason.value_counts().to_dict(), v04_A=v4[v4.status == "UNRESOLVED"].unresolved_reason.value_counts().to_dict(), v04_B=v4b[v4b.status == "UNRESOLVED"].unresolved_reason.value_counts().to_dict())
# ---- A/B structural
def boxes_det(df): return {int(r.frame): dets[int(r.frame)]["box"][int(r.selected_det_index)] for r in df.itertuples() if r.status in EM and not pd.isna(r.selected_det_index)}
bx4, bx4b = boxes_det(v4), boxes_det(v4b); coincide = []
for f in sorted(set(bx4) & set(bx4b)):
    ra, rb = v4[v4.frame == f].iloc[0], v4b[v4b.frame == f].iloc[0]; d_ = float(np.hypot(ra.COM_x_pixel - rb.COM_x_pixel, ra.COM_y_pixel - rb.COM_y_pixel)); dg = min(np.hypot(bx4[f][2]-bx4[f][0], bx4[f][3]-bx4[f][1]), np.hypot(bx4b[f][2]-bx4b[f][0], bx4b[f][3]-bx4b[f][1]))
    if d_ / dg < 0.15: coincide.append((f, round(d_ / dg, 3)))
ab = dict(frames_both_emit=int(len(set(bx4) & set(bx4b))), coms_closer_than_0p15_diag=coincide)
shots = []
for s, g in v4.groupby("camera_segment"):
    e_ = g[g.status.isin(EM)]; shots.append(dict(seg=int(s), n=len(g), emitted=len(e_), first_emission_latency=None if len(e_) == 0 else int(e_.frame.iloc[0] - g.frame.iloc[0])))
pl = pd.read_csv(os.path.join(OUTD, "prediction_log_v04.csv")) if os.path.getsize(os.path.join(OUTD, "prediction_log_v04.csv")) > 5 else pd.DataFrame()
plsum = {} if pl.empty else dict(n_rows=len(pl), decisions=pl.decision.value_counts().to_dict(), predicted_outside_image=int(((pl.decision == "PREDICTED") & ~pl.inside_image).sum()))
out = dict(categories=R, wrong_person_identity_detail=wrong_identity_detail, regression_cases_summary=reg_sum, cuts=cuts, status_counts=status, prediction=prediction, prediction_log=plsum, known_bad=kb, recovery_of_v03_identity_insufficient=rec_ins, emissions=emit, identity=identity, embedding_contribution_beyond_colour=contrib,
           anatomy=anat, v04_emission_tiers=tiers, unresolved_reasons=reasons, AB=ab, shots=dict(n_shots=len(shots), shots_with_emission=sum(1 for s in shots if s["emitted"] > 0), median_latency=float(np.median([s["first_emission_latency"] for s in shots if s["first_emission_latency"] is not None])), per_shot=shots), seed_frames_excluded=sorted(SEEDS))
json.dump(out, open(os.path.join(OUTD, "comparison_metrics_v04.json"), "w"), indent=1, default=int); print(json.dumps({k: out[k] for k in out if k not in ("shots",)}, indent=1, default=int))
