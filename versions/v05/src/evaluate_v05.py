"""POST-FREEZE EVALUATION (not decision code). Comparison V0.1 / V0.2 / V0.3 / V0.4 / V0.5 on the FROZEN pre-development reference benchmark (read-only), the specification's regression cases and structural metrics.
Reads outputs from disk; writes comparison_metrics_v05.json and regression_cases_v05.csv into the V0.5 output directory. ALL numbers are IN-SAMPLE development numbers: the clip informed the design of every version,
the benchmark is single-reviewer and non-blinded, there is no ground truth. Seed frames are excluded from every benchmark-category count. Dimensions are reported SEPARATELY; no single accuracy number is computed.
Wrestler A is the benchmark target; B has no ground truth."""
import json, hashlib, pickle, sys, os, pandas as pd, numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUTD = os.environ.get("V05_OUT_DIR", os.path.join(ROOT, "v05", "out"))
BP = os.path.join(ROOT, "v02", "benchmark", "benchmark_v0.1_reference.json")
assert hashlib.sha256(open(BP, "rb").read()).hexdigest() == open(os.path.join(ROOT, "v02", "benchmark", "MANIFEST.sha256")).read().split()[0], "BENCHMARK CHANGED"
B = json.load(open(BP)); meta = json.load(open(os.path.join(OUTD, "run_meta_v05.json"))); SEEDS = set(meta["seed_frames"])
rd = lambda *p: pd.read_csv(os.path.join(ROOT, *p))
v1 = rd("out", "tracking_full.csv"); v2 = rd("v02", "out", "tracking_v02.csv")
v3a = rd("v03", "out", "tracking_v03.csv"); v3 = v3a[v3a.target == "A"].reset_index(drop=True); v3b = v3a[v3a.target == "B"].reset_index(drop=True)
v4a = rd("v04", "out", "tracking_v04.csv"); v4 = v4a[v4a.target == "A"].reset_index(drop=True); v4b = v4a[v4a.target == "B"].reset_index(drop=True)
v5a = pd.read_csv(os.path.join(OUTD, "tracking_v05.csv")); v5 = v5a[v5a.target == "A"].reset_index(drop=True); v5b = v5a[v5a.target == "B"].reset_index(drop=True)
ev5 = pd.read_csv(os.path.join(OUTD, "identity_ownership_events_v05.csv")); cand5 = pd.read_csv(os.path.join(OUTD, "candidates_v05.csv")); dets = pickle.load(open(os.path.join(ROOT, "out", "raw_detections.pkl"), "rb"))
EM = ["MEASURED", "PARTIAL"]; ANY = EM + ["PREDICTED"]; ST = ["MEASURED", "PARTIAL", "PREDICTED", "UNRESOLVED"]
def rng(rs): return sorted({f for a, b in rs for f in range(a, b + 1)})
def sub(df, fr): return df[df.frame.isin(fr)]
def cnt(df, fr, sts): return int(sub(df, fr).status.isin(sts).sum())
VERS = {"v01": v1, "v02": v2, "v03": v3, "v04": v4, "v05": v5}
R = {}
def cat(name, frames, sts, want):
    fr = sorted(set(frames) - SEEDS); R[name] = dict(n=len(fr), **{k: cnt(df, fr, sts) for k, df in VERS.items()}, want=want, n_seed_frames_excluded=len(set(frames) & SEEDS))
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
# ---- specification regression cases (frame-by-frame). DIAGNOSTIC ONLY.
REG = {"v01_wrong_person": [376, 386, 392, 753, 772, 1196],
       "contamination": [270] + list(range(275, 280)) + [290, 925, 931, 935, 938, 950, 951, 954, 956, 957, 1075] + list(range(1078, 1085)) + list(range(1088, 1094)),
       "identity_insufficient_closeups": [692, 725, 732, 736], "AB_concern": [1114, 1166, 1179, 1204], "former_false_cut_events": [292, 434, 753, 1062]}
def row(df, f): return df[df.frame == f].iloc[0]
reg_rows = []
for grp, fr in REG.items():
    for f in fr:
        r1, r2, r3, r4, r5, r5b = row(v1, f), row(v2, f), row(v3, f), row(v4, f), row(v5, f), row(v5b, f)
        reg_rows.append(dict(group=grp, frame=f, seed_frame=f in SEEDS, v01=r1.status, v02=r2.status, v03_A=r3.status, v04_A=r4.status, v05_A=r5.status, v05_A_identity_state=r5.identity_state, v05_A_ownership_state=r5.ownership_state,
                             v05_A_ownership_reasons=r5.ownership_reasons if isinstance(r5.ownership_reasons, str) else "", v05_A_unresolved_reason=r5.unresolved_reason if isinstance(r5.unresolved_reason, str) else "",
                             v04_B=row(v4b, f).status, v05_B=r5b.status, v05_B_ownership_state=r5b.ownership_state))
reg = pd.DataFrame(reg_rows); reg.to_csv(os.path.join(OUTD, "regression_cases_v05.csv"), index=False)
reg_sum = {}
for grp in REG:
    g = reg[(reg.group == grp) & ~reg.seed_frame]
    reg_sum[grp] = dict(n=len(g), **{k: int(g[k].isin(EM).sum()) for k in ("v01", "v02", "v03_A", "v04_A", "v05_A")}, v05_A_predicted=int((g.v05_A == "PREDICTED").sum()), v05_B_emits=int(g.v05_B.isin(EM).sum()), v04_B_emits=int(g.v04_B.isin(EM).sum()),
                        v05_A_ownership_states=g.v05_A_ownership_state.value_counts().to_dict())
# ---- identity-level wrong-person check
wp = []
for f in wrong:
    if f in SEEDS: continue
    r1 = row(v1, f)
    if pd.isna(r1.selected_box_x1): wp.append(dict(frame=f, v01_box="none")); continue
    b1 = [r1.selected_box_x1, r1.selected_box_y1, r1.selected_box_x2, r1.selected_box_y2]; d_ = dict(frame=f)
    for nm, df in (("A", v5), ("B", v5b)):
        r = row(df, f); d_[f"v05_{nm}_identity_state"] = r.identity_state; d_[f"v05_{nm}_status"] = r.status
        d_[f"v05_{nm}_identity_box_IoU_with_v01_wrong_box"] = None if (pd.isna(r.selected_det_index) or not r.identity_track_continues) else round(iou(b1, dets[f]["box"][int(r.selected_det_index)]), 2)
    wp.append(d_)
wrong_identity_detail = dict(rows=wp, A_identity_on_v01_wrong_box=[d["frame"] for d in wp if (d.get("v05_A_identity_box_IoU_with_v01_wrong_box") or 0) >= 0.5], B_identity_on_v01_wrong_box=[d["frame"] for d in wp if (d.get("v05_B_identity_box_IoU_with_v01_wrong_box") or 0) >= 0.5],
                             note="a B assignment on V0.1's wrong box is not necessarily an error")
# ---- cuts
tc = set(B["cuts_AUD"]["true_cuts"]); c1 = set(B["cuts_AUD"]["v01_reported"]); cl = lambda *p: {c["frame"] for c in json.load(open(os.path.join(ROOT, *p)))["cuts"]}
c2, c3, c4 = cl("v02", "out", "cuts_v02.json"), cl("v03", "out", "cuts_v03.json"), cl("v04", "out", "cuts_v04.json"); c5 = {c["frame"] for c in json.load(open(os.path.join(OUTD, "cuts_v05.json")))["cuts"]}
def prf(s): tp = len(s & tc); return dict(detected=len(s), true_pos=tp, false_pos=len(s - tc), missed=len(tc - s))
cuts = dict(v01=prf(c1), v02=prf(c2), v03=prf(c3), v04=prf(c4), v05=prf(c5), v05_identical_to_v04=c5 == c4, v05_cut_log_bytes_identical_to_v04=open(os.path.join(OUTD, "cuts_v05.json"), "rb").read() == open(os.path.join(ROOT, "v04", "out", "cuts_v04.json"), "rb").read(), note="IN-SAMPLE")
def dist(df): return {k: int((df.status == k).sum()) for k in ST}
status = dict(v01=dist(v1), v02=dist(v2), v03_A=dist(v3), v04_A=dist(v4), v05_A=dist(v5), v03_B_no_ground_truth=dist(v3b), v04_B_no_ground_truth=dist(v4b), v05_B_no_ground_truth=dist(v5b))
def pred(df, W=640, H=360):
    p = df[df.status == "PREDICTED"]; off = p[(p.COM_x_pixel < 0) | (p.COM_x_pixel > W) | (p.COM_y_pixel < 0) | (p.COM_y_pixel > H)]; return dict(n=len(p), off_image=len(off))
prediction = dict(v01=pred(v1), v02=pred(v2), v03_A=pred(v3), v04_A=pred(v4), v05_A=pred(v5), v05_B=pred(v5b))
KB = set(wrong) | set(B["pose_contamination_frames_viewed_DEV"]) | set(B["pose_distorted_frames_viewed_DEV"]) | set(rng(B["pose_contamination_ranges_inferred_DEV"])) | set(rng(B["wrong_identity_ranges_inferred_DEV"]))
KBe = sorted(KB - SEEDS)
kb = dict(n_known_or_inferred_bad_frames=len(KBe), **{f"{k}_emits": cnt(df, KBe, EM) for k, df in VERS.items()}, v05_emits_incl_predicted=cnt(v5, KBe, ANY),
          v05_emitting_frames_in_known_bad=sorted(sub(v5, KBe)[sub(v5, KBe).status.isin(EM)].frame.tolist()), v05_predicted_frames_in_known_bad=sorted(sub(v5, KBe)[sub(v5, KBe).status == "PREDICTED"].frame.tolist()),
          note="known-bad includes INFERRED ranges containing never-viewed frames")
# ---- recovery / loss relative to V0.3 and V0.4
m = v1[["frame", "status"]].rename(columns={"status": "s1"}).merge(v2[["frame", "status"]].rename(columns={"status": "s2"}), on="frame").merge(v3[["frame", "status", "unresolved_reason"]].rename(columns={"status": "s3", "unresolved_reason": "r3"}), on="frame")
m = m.merge(v4[["frame", "status", "unresolved_reason", "identity_state"]].rename(columns={"status": "s4", "unresolved_reason": "r4", "identity_state": "i4"}), on="frame").merge(v5[["frame", "status", "unresolved_reason", "identity_state", "ownership_state"]].rename(columns={"status": "s5", "unresolved_reason": "r5", "identity_state": "i5", "ownership_state": "o5"}), on="frame")
ins = m[(m.r3 == "IDENTITY_INSUFFICIENT_EVIDENCE") & ~m.frame.isin(SEEDS)]
rec = dict(v03_identity_insufficient_frames=len(ins), recovered_by_v05_emitted=int(ins.s5.isin(EM).sum()), recovered_in_known_bad=int((ins.s5.isin(EM) & ins.frame.isin(KB)).sum()), v05_identity_state_of_these=ins.i5.value_counts().to_dict())
reacq = m[(m.r4 == "REACQUISITION_UNCERTAIN") & ~m.frame.isin(SEEDS)]
rec_reacq = dict(v04_reacquisition_uncertain_frames=len(reacq), v05_now_emitted=int(reacq.s5.isin(EM).sum()), v05_now_emitted_in_known_bad=int((reacq.s5.isin(EM) & reacq.frame.isin(KB)).sum()), v05_state=reacq.s5.value_counts().to_dict(), v05_reason=reacq[~reacq.s5.isin(ANY)].r5.value_counts().to_dict())
nb = m[m.s1.isin(EM) & ~m.frame.isin(KB) & ~m.frame.isin(SEEDS)]
emit = dict(v05_emits_where_v04_did_not=int((m.s5.isin(EM) & ~m.s4.isin(EM)).sum()), v04_emits_where_v05_does_not=int((m.s4.isin(EM) & ~m.s5.isin(EM)).sum()), v05_emits_where_v03_did_not=int((m.s5.isin(EM) & ~m.s3.isin(EM)).sum()), v05_emits_where_v01_did_not=int((m.s5.isin(EM) & ~m.s1.isin(EM)).sum()),
            v05_new_vs_v04_in_known_bad=int((m.s5.isin(EM) & ~m.s4.isin(EM) & m.frame.isin(KB)).sum()), v05_dropped_vs_v04_in_known_bad=int((m.s4.isin(EM) & ~m.s5.isin(EM) & m.frame.isin(KB)).sum()),
            v01_tracked_not_known_bad=len(nb), **{f"{k}_kept": int(nb[s].isin(EM).sum()) for k, s in (("v02", "s2"), ("v03", "s3"), ("v04", "s4"), ("v05", "s5"))})
# ---- identity
def idsum(df): return dict(identity_state=df.identity_state.value_counts().to_dict(), identity_track_continues=int(df.identity_track_continues.sum()), emitted_independent=int((df.status.isin(EM) & (df.identity_state == "SUPPORTED_INDEPENDENT")).sum()),
                         emitted_temporal_only=int((df.status.isin(EM) & (df.identity_state == "TEMPORAL_CONTINUATION")).sum()), identity_supported_com_withheld=int((df.identity_state.isin(["SUPPORTED_INDEPENDENT"]) & ~df.status.isin(ANY)).sum()),
                         identity_reasons=df[df.identity_reason.notna()].identity_reason.value_counts().to_dict())
identity = dict(A=idsum(v5), B=idsum(v5b), events=ev5.event.value_counts().to_dict(), events_by_wrestler=ev5.groupby(["event", "target"]).size().to_dict().__repr__(),
                A_and_B_both_have_identity_on_same_detection=int(((v5.selected_det_index == v5b.selected_det_index) & v5.selected_det_index.notna() & v5.identity_track_continues & v5b.identity_track_continues).sum()), frames_both_emit=int((v5.status.isin(EM) & v5b.status.isin(EM)).sum()))
# ---- appearance-dependence of emissions (identity evidence beyond colour/thigh and the masked-box cue)
c = cand5.merge(v5[["frame", "selected_det_index", "identity_state", "status", "colour_R", "masked_box_R"]].rename(columns={"selected_det_index": "det"}), on=["frame", "det"], how="inner")
c = c[(c.identity_state == "SUPPORTED_INDEPENDENT") & (c.label == "A")]; e_ = c[c.status.isin(EM)]
contrib = dict(n_A_independent_supported_frames=int(len(c)), emitted=int(len(e_)), emitted_with_colour_R_below_0p8_embedding_necessary=int((e_.colour_R < 0.8).sum()), emitted_with_masked_box_cue_present=int((e_.masked_box_R.fillna(0) > 0).sum()),
               emitted_embedding_necessary_and_in_known_bad=int(((e_.colour_R < 0.8) & e_.frame.isin(KB)).sum()), emitted_embedding_necessary_and_v04_emitted=int(((e_.colour_R < 0.8) & e_.frame.isin(v4[v4.status.isin(EM)].frame)).sum()))
# ---- ownership / anatomy
def owsum(df):
    e = df[df.ownership_state != "NOT_EVALUATED"]
    return dict(ownership_state=e.ownership_state.value_counts().to_dict(), ownership_state_all_frames=df.ownership_state.value_counts().to_dict(),
                reasons=pd.Series([r for x in e.ownership_reasons.dropna() for r in str(x).split(";") if r]).value_counts().to_dict(), anatomy_plausibility=e.anatomy_plausibility.value_counts().to_dict(),
                com_ineligible=df[df.com_eligibility == "INELIGIBLE"].com_ineligible_reason.value_counts().to_dict(), emitted_ownership_states=df[df.status.isin(EM)].ownership_state.value_counts().to_dict())
anat = dict(A=owsum(v5), B=owsum(v5b)); em5 = v5[v5.status.isin(EM)]
tiers = dict(identity_tier=em5.identity_tier.value_counts().to_dict(), limiting_factors=em5.status_limiting_factors.fillna("").value_counts().to_dict(), overlap_context_diagnostic=int(em5.overlap_context_diagnostic.sum()), merge_risk=int(em5.merge_risk.sum()),
             contested_frac_mean=float(em5.contested_frac.mean()), unexplained_frac_mean=float(em5.mask_unexplained_frac.mean()), landmarks_used_own_only_total=int(em5.com_landmarks_own_only.sum()), landmarks_used_contested_total=int(em5.com_landmarks_contested.sum()), landmarks_used_outside_total=int(em5.com_landmarks_outside_mask.sum()))
reasons = dict(v03_A=v3[v3.status == "UNRESOLVED"].unresolved_reason.value_counts().to_dict(), v04_A=v4[v4.status == "UNRESOLVED"].unresolved_reason.value_counts().to_dict(), v05_A=v5[v5.status == "UNRESOLVED"].unresolved_reason.value_counts().to_dict(), v05_B=v5b[v5b.status == "UNRESOLVED"].unresolved_reason.value_counts().to_dict())
def boxes_det(df): return {int(r.frame): dets[int(r.frame)]["box"][int(r.selected_det_index)] for r in df.itertuples() if r.status in EM and not pd.isna(r.selected_det_index)}
bx5, bx5b = boxes_det(v5), boxes_det(v5b); coincide = []
for f in sorted(set(bx5) & set(bx5b)):
    ra, rb = v5[v5.frame == f].iloc[0], v5b[v5b.frame == f].iloc[0]; d_ = float(np.hypot(ra.COM_x_pixel - rb.COM_x_pixel, ra.COM_y_pixel - rb.COM_y_pixel)); dg = min(np.hypot(bx5[f][2]-bx5[f][0], bx5[f][3]-bx5[f][1]), np.hypot(bx5b[f][2]-bx5b[f][0], bx5b[f][3]-bx5b[f][1]))
    if d_ / dg < 0.15: coincide.append((f, round(d_ / dg, 3)))
ab = dict(frames_both_emit=int(len(set(bx5) & set(bx5b))), coms_closer_than_0p15_diag=coincide)
shots = []
for s, g in v5.groupby("camera_segment"):
    e = g[g.status.isin(EM)]; shots.append(dict(seg=int(s), n=len(g), emitted=len(e), first_emission_latency=None if len(e) == 0 else int(e.frame.iloc[0] - g.frame.iloc[0])))
pl = pd.read_csv(os.path.join(OUTD, "prediction_log_v05.csv")) if os.path.getsize(os.path.join(OUTD, "prediction_log_v05.csv")) > 5 else pd.DataFrame()
plsum = {} if pl.empty else dict(n_rows=len(pl), decisions=pl.decision.value_counts().to_dict(), predicted_outside_image=int(((pl.decision == "PREDICTED") & ~pl.inside_image).sum()), contra_terminations=int((pl.decision == "TERMINATED:CONTRA_CUE").sum()))
lat = [s["first_emission_latency"] for s in shots if s["first_emission_latency"] is not None]
out = dict(categories=R, wrong_person_identity_detail=wrong_identity_detail, regression_cases_summary=reg_sum, cuts=cuts, status_counts=status, prediction=prediction, prediction_log=plsum, known_bad=kb, recovery_of_v03_identity_insufficient=rec, recovery_of_v04_reacquisition_uncertain=rec_reacq,
           emissions=emit, identity=identity, appearance_dependence=contrib, ownership_and_anatomy=anat, v05_emission_tiers=tiers, unresolved_reasons=reasons, AB=ab, shots=dict(n_shots=len(shots), shots_with_emission=sum(1 for s in shots if s["emitted"] > 0), median_latency=float(np.median(lat)) if lat else None, per_shot=shots),
           seed_frames_excluded=sorted(SEEDS))
json.dump(out, open(os.path.join(OUTD, "comparison_metrics_v05.json"), "w"), indent=1, default=int); print(json.dumps({k: out[k] for k in out if k not in ("shots", "wrong_person_identity_detail")}, indent=1, default=int))
