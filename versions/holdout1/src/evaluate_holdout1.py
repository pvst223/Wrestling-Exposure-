"""POST-RUN analysis (not decision code). Joins the BLIND verdicts to the tracker output and reports dimensions separately. Writes out/holdout1_metrics.json."""
import json, os, pandas as pd, numpy as np
H = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); O = os.path.join(H, "out")
tr = pd.read_csv(os.path.join(O, "tracking_v05.csv")); V = json.load(open(os.path.join(H, "review", "review_verdicts_holdout1_BLIND.json")))["verdicts"]; K = json.load(open(os.path.join(H, "review", "review_key_holdout1.json")))["items"]
cuts = json.load(open(os.path.join(H, "cache", "cuts_holdout1.json"))); EM = ("MEASURED", "PARTIAL"); M = {}
kmap = {i["idx"]: i for i in K}
for X in ("A", "B"):
    d = tr[tr.target == X]; M[f"status_{X}"] = d.status.value_counts().to_dict(); M[f"unresolved_reasons_{X}"] = d[d.status == "UNRESOLVED"].unresolved_reason.value_counts().to_dict()
    M[f"identity_state_{X}"] = d.identity_state.value_counts().to_dict(); M[f"ownership_state_{X}"] = d.ownership_state.value_counts().to_dict()
    M[f"emitted_{X}"] = int(d.status.isin(EM).sum()); M[f"limiting_factors_{X}"] = d[d.status.isin(EM)].status_limiting_factors.fillna("").value_counts().to_dict()
    M[f"emitted_identity_basis_{X}"] = d[d.status.isin(EM)].identity_basis.value_counts().to_dict(); M[f"emitted_identity_tier_{X}"] = d[d.status.isin(EM)].identity_tier.value_counts().to_dict()
# shots
cf = sorted(e["frame"] for e in cuts["cuts"]); edges = [0] + cf + [len(tr.frame.unique())]; shots = []
for k in range(len(edges) - 1):
    a, b = edges[k], edges[k + 1]; row = dict(shot=k, start=a, end=b - 1, n=b - a)
    for X in ("A", "B"):
        d = tr[(tr.target == X) & (tr.frame >= a) & (tr.frame < b)]; e = d[d.status.isin(EM)]; row[f"emitted_{X}"] = int(len(e)); row[f"first_{X}_latency"] = int(e.frame.min() - a) if len(e) else None
    shots.append(row)
M["shots"] = shots; M["n_shots"] = len(shots); M["shots_with_A_emission"] = sum(1 for s in shots if s["emitted_A"] > 0); M["shots_with_B_emission"] = sum(1 for s in shots if s["emitted_B"] > 0)
# review join
rows = []
for v in V:
    it = kmap[v["idx"]]
    if v["kind"] == "overlay":
        r = tr[(tr.frame == v["frame"]) & (tr.target == v["target"])].iloc[0]
        rows.append(dict(idx=v["idx"], frame=v["frame"], target=v["target"], strata="|".join(it["strata"]), verdict=v["verdict"], status=r.status, emitted=r.status in EM, identity_state=r.identity_state, ownership_state=r.ownership_state, unresolved_reason=r.unresolved_reason, tier=r.identity_tier))
J = pd.DataFrame(rows); J.to_csv(os.path.join(O, "holdout1_review_join.csv"), index=False)
def tab(df): return {v: dict(n=int(len(g)), emitted=int(g.emitted.sum()), withheld=int((~g.emitted).sum())) for v, g in df.groupby("verdict")}
M["review_overall"] = tab(J)
for X in ("A", "B"): M[f"review_{X}"] = tab(J[J.target == X])
M["review_R1_R2_emission_samples"] = tab(J[J.strata.str.contains("R1|R2")])
M["review_R3_systematic_assigned"] = tab(J[J.strata.str.contains("R3")])
bad = J[J.verdict.isin(["MIXED_BODIES", "WRONG_PERSON_NOT_A_WRESTLER"])]; M["bad_frames_detail"] = bad[["idx", "frame", "target", "verdict", "status", "identity_state", "ownership_state", "unresolved_reason"]].to_dict("records")
# coverage ground truth from plain frames
pl = [v for v in V if v["kind"] == "plain"]; cov = {}
for X, key in (("A", "A_clearly_visible"), ("B", "B_clearly_visible")):
    vis = [v for v in pl if v[key] == "Y"]; em = [v for v in vis if tr[(tr.frame == v["frame"]) & (tr.target == X)].iloc[0].status in EM]
    cov[X] = dict(plain_frames_target_visible=len(vis), of_which_emitted=len(em), frames_visible_not_emitted=[v["frame"] for v in vis if v not in em])
    ov = [v for v in vis if v["A_B_overlapping"] == "Y"]; cov[X]["overlap_visible"] = len(ov); cov[X]["overlap_emitted"] = sum(1 for v in ov if v in em)
M["coverage_ground_truth_plain_every30"] = cov
# prediction
pr = pd.read_csv(os.path.join(O, "prediction_log_v05.csv")); M["prediction_log_rows"] = int(len(pr)); M["prediction_decisions"] = pr.iloc[:, :].astype(str).apply(lambda c: c.value_counts().to_dict()).to_dict() if False else None
pdf = tr[tr.status == "PREDICTED"]; M["predicted_frames"] = {X: pdf[pdf.target == X].frame.tolist() for X in ("A", "B")}
W, Hh = 640, 360; off = pdf[(pdf.COM_x_pixel < 0) | (pdf.COM_x_pixel > W) | (pdf.COM_y_pixel < 0) | (pdf.COM_y_pixel > Hh)]; M["predicted_off_image"] = int(len(off))
ev = pd.read_csv(os.path.join(O, "identity_ownership_events_v05.csv")); M["event_log_rows"] = int(len(ev)); M["event_types"] = ev.iloc[:, 1].astype(str).value_counts().to_dict() if ev.shape[1] > 1 else {}
M["cuts_detected"] = cf; M["cut_events_total"] = len(cuts["events"]); M["non_cut_transients"] = cuts["transient_frames"]
# A and B emitted same frame / COM proximity
a = tr[(tr.target == "A") & tr.status.isin(EM)].set_index("frame"); b = tr[(tr.target == "B") & tr.status.isin(EM)].set_index("frame"); both = a.index.intersection(b.index); M["frames_both_emit"] = int(len(both))
if len(both): dd = np.hypot(a.loc[both].COM_x_pixel - b.loc[both].COM_x_pixel, a.loc[both].COM_y_pixel - b.loc[both].COM_y_pixel); M["both_emit_COM_dist_px_min"] = float(dd.min()); M["both_emit_COM_closer_than_30px"] = int((dd < 30).sum())
json.dump(M, open(os.path.join(O, "holdout1_metrics.json"), "w"), indent=1, default=str); print(json.dumps({k: v for k, v in M.items() if k not in ("shots", "unresolved_reasons_A", "unresolved_reasons_B", "bad_frames_detail", "prediction_decisions")}, indent=0, default=str)[:6000])
