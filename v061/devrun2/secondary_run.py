"""Seeds 1-3 variance + descriptive ablations A (old rule + new training), B (new rule + old single-episode head), C (drop relaxed-seed training episodes) on the V0.6.1 cross-fitted development pool.
SECONDARY / DEVELOPMENT ONLY. The locked rule, grids, selection procedure, metrics, backbone, loss and architecture are used unchanged. No final head is trained. Single execution; clarifications in SECONDARY_CLARIFICATIONS.md (ledger DR2)."""
import os, sys, json, csv, glob, hashlib, argparse, collections, subprocess
import numpy as np
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, REPO); sys.path.insert(0, os.path.join(REPO, "v06", "tools"))
from v061.impl import decision_rule as R, selection as S, evaluate as E, units as U
from v061.devrun import episodes as EP
from v061.devrun import crossfit_run as C1     # constants + helpers only (file unchanged since DR1)
LABEL = "V0.6.1 SECONDARY DEVELOPMENT ANALYSIS (seed variance / descriptive ablations; development-exposed; exploratory; NOT validation)"
FIXED_PARAM = (0.9, 0.1)       # the DR1 seed-0 selected L1 operating point; used UNCHANGED for the fixed-point view
OLD_FLOOR_GRID = (0.4, 0.5, 0.6, 0.7, 0.8)   # frozen V0.6 L1 floor grid (old 3-class rule), margin 0.0
def manifest_sha(dirname):
    d = os.path.join(REPO, "v061", dirname); items = []
    for dp, dn, fs in os.walk(d):
        dn[:] = [x for x in dn if x != "__pycache__"]
        for f in fs:
            if f.endswith(".pyc") or f.endswith("MANIFEST.txt"): continue
            p = os.path.join(dp, f); items.append((os.path.relpath(p, REPO).replace(os.sep, "/"), C1.sha(p)))
    items.sort(); return hashlib.sha256("".join(f"{h}  {f}\n" for f, h in items).encode()).hexdigest(), items
def preflight(frozen, result_path):
    r = subprocess.run([sys.executable, os.path.join(REPO, "v061", "tooling", "impl_manifest.py")], capture_output=True, text=True)
    if r.returncode != 0 or C1.sha(os.path.join(REPO, "v061", "impl", "IMPLEMENTATION_MANIFEST.txt")) != C1.LOCKED_IMPL_MANIFEST_SHA256: raise SystemExit("locked implementation check FAILED")
    ms, _ = manifest_sha("devrun2"); led = [json.loads(l) for l in open(os.path.join(frozen, "AUDIT_LEDGER.jsonl"))]
    dr2 = [e for e in led if e.get("id") in ("DR2", "DR2R")]
    if not dr2 or dr2[-1].get("devrun2_code_manifest_sha256") != ms: raise SystemExit("ledger DR2 missing or devrun2 code hash differs")
    if any(e.get("id") == "DR3" for e in led) or os.path.exists(result_path): raise SystemExit("EXECUTED ALREADY (exactly-once rule)")
    return ms
def build_data(frozen, feat_dir):
    """Identical construction to crossfit_run.main (DR1): frozen strict evaluation episodes + K=5 resampled training episodes per clip."""
    import phase1_run as RUN, phase1_structure as PS
    sm_path = os.path.join(frozen, "SEED_EPISODE_MANIFEST_V2.json"); ex_path = os.path.join(frozen, "EXTRACTION_FRAME_MANIFEST_V1.csv"); SM = json.load(open(sm_path))
    labels = {r["tid"]: r for r in csv.DictReader(open(os.path.join(frozen, "labels", "ALL_firstpass.csv")))}
    exrows = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in csv.DictReader(open(ex_path)): exrows[r["clip"]][r["tid"]].append((int(r["frame"]), int(r["det"]), float(r["box_h"]), int(r["crop_ok"])))
    T = RUN.load_episode_tensors(frozen, feat_dir, C1.BACKBONE, sm_path, ex_path); eval_eps = T["train"] + T["dev"] + T["test"]; d_in = eval_eps[0]["cand"].shape[1]
    clip_ids = {c: sorted(cv["named_wrestlers"]) for c, cv in SM["clips"].items()}; comp = C1.components(clip_ids); train_by_clip = {}; relaxed_clips = set()
    for clip in sorted(clip_ids):
        trs = {t["tid"]: t for t in json.load(open(os.path.join(frozen, "tracklets", f"{clip}.json")))}; lab = {t: labels[t] for t in trs if t in labels and labels[t]["person_class"] != "UNLABELABLE"}
        fp = glob.glob(os.path.join(feat_dir, f"feat_{C1.BACKBONE}_{clip}_*.npz")); assert len(fp) == 1
        z = np.load(fp[0]); idx = {(int(f), int(d)): i for i, (f, d) in enumerate(zip(z["frame"], z["det"]))}; Emb = z["emb"]; detmap = {(tid, f): d for tid, rows in exrows[clip].items() for (f, d, h, ok) in rows}
        def dets_of(tids):
            out = []
            for tid in tids:
                t = trs[tid]
                for f, b in zip(t["frames"], t["boxes"]):
                    if (tid, f) in detmap and (f, detmap[(tid, f)]) in idx: out.append(dict(frame=f, det=detmap[(tid, f)], tid=tid, shot=t["shot"], box_h=float(b[3] - b[1])))
            return out
        wrest = clip_ids[clip]; A, B = wrest
        elig = {w: [tid for tid, l in lab.items() if l["person_class"] == "WRESTLER" and l["wrestler_id"] == w and l["multi_person_flag"] == "0"] for w in wrest}
        ref = PS.select_referee_seeds(clip, dets_of([tid for tid, l in lab.items() if l["person_class"] == "REFEREE" and l["multi_person_flag"] == "0"])); feat = lambda s: Emb[idx[(s["frame"], s["det"])]]; eps = []
        for k in range(C1.K_RESAMPLES):
            sel = {w: EP.select_seeds(f"{C1.EP_SEED}|{clip}|{w}|target|k{k}", dets_of(elig[w])) for w in wrest}
            if any(sel[w]["status"] != "OK" for w in wrest): continue
            if any(sel[w]["rule"] != "STRICT_4" for w in wrest): relaxed_clips.add(clip)
            used = {s["tid"] for w in wrest for s in sel[w]["seeds"]} | {s["tid"] for s in ref["seeds"]}; cs = EP.candidate_structure(lab, trs, A, B, used); cand = []; meta = []; y = []
            for c in sorted(cs, key=lambda c: c["tid"]):
                for f, d, h, ok in sorted(exrows[clip][c["tid"]]):
                    if (f, d) in idx: cand.append(Emb[idx[(f, d)]]); meta.append(dict(tid=c["tid"], frame=f, shot=c["shot"], truth=c["truth"])); y.append(c["y"])
            eps.append(dict(id=f"{clip}|{A}|{B}|k{k}", clip=clip, split="train_resample", A=A, B=B, seed_A=np.stack([feat(s) for s in sel[A]["seeds"]]), seed_B=np.stack([feat(s) for s in sel[B]["seeds"]]),
                            seed_N=np.stack([feat(s) for s in ref["seeds"]]) if ref["seeds"] else np.zeros((0, d_in), np.float32), cand=np.stack(cand), y=np.array(y), meta=meta))
        train_by_clip[clip] = eps
    return dict(eval_eps=eval_eps, train_by_clip=train_by_clip, comp=comp, d_in=d_in, relaxed_clips=sorted(relaxed_clips))
def softmax_np(head, e):
    import torch, phase1_run as RUN
    t = RUN._tt(e); t2 = dict(t)
    if len(t2["seed_N"]) == 0: t2.pop("seed_N")
    with torch.no_grad(): return torch.softmax(head.logits(t2), 1).numpy().astype(np.float64)
def crossfit(D, seed, exclude_clips=(), want_insample=False):
    import phase1_run as RUN
    folds = collections.defaultdict(list)
    for e in D["eval_eps"]: folds[D["comp"][e["clip"]]].append(e)
    probs = {}; ins = []
    for fn in sorted(folds):
        held = {c for c, cc in D["comp"].items() if cc == fn}; tr = [e for c in sorted(D["train_by_clip"]) if c not in held and c not in exclude_clips for e in D["train_by_clip"][c]]
        head, hist = RUN.train_l1(tr, D["d_in"], seed=seed); head.eval()
        for e in folds[fn]: probs[e["id"]] = softmax_np(head, e)
        if want_insample:
            for e in tr: ins.append(dict(ep=e, P=softmax_np(head, e)))
    return probs, ins
def l1_eps(eps, probs): return [dict(id=e["id"], targets=(e["A"], e["B"]), clip=e["clip"], rows=[dict(clip=e["clip"], shot=m["shot"], truth=m["truth"]) for m in e["meta"]], P=probs[e["id"]]) for e in eps]
def groups_of(eps, comp):
    g = collections.OrderedDict()
    for e in eps: g.setdefault(comp[e["clip"]], []).append(e)
    return list(g.values())
def grid_pts(eps_list, groups, rows_fn, grid):
    out = []
    for prm in grid:
        tab = U.table_metrics(U.unit_table([(e["targets"], rows_fn(e, *prm)) for e in eps_list])); tab["param"] = prm
        tab["fold_coverages"] = [U.table_metrics(U.unit_table([(e["targets"], rows_fn(e, *prm)) for e in g]))["coverage"] for g in groups]; out.append(tab)
    return out
def b0_pts(eval_eps, comp):
    import heads
    def rows(e, tau, mg):
        labs, _ = heads.NonLearnedBaseline(tau, mg).decide(e); ident = {"A": e["A"], "B": e["B"]}
        return [dict(clip=e["clip"], shot=m["shot"], truth=m["truth"], accepted=ident.get(l, "")) for m, l in zip(e["meta"], labs)]
    pe = [dict(targets=(e["A"], e["B"]), **e) for e in eval_eps]
    return grid_pts(pe, groups_of(pe, comp), rows, R.GRID_B0)
def old_rule_rows(e, tau):
    P = e["P"]; k = P.argmax(1); A, B = e["targets"]; ok = np.isfinite(P).all(1) & (P.max(1) >= tau)
    return [dict(clip=r["clip"], shot=r["shot"], truth=r["truth"], accepted=(A if kk == 0 else B if kk == 1 else "") if o else "") for r, kk, o in zip(e["rows"], k, ok)]
def compact(d):
    return dict(param=d["param"], n_units=d["unit_metrics"]["n_units"], fa_units=d["unit_metrics"]["fa_units"], fta=d["unit_metrics"]["fta"], fta_ci95_exact=d["fta_ci95_exact"], coverage=d["coverage"], strata=d["unit_metrics"]["strata"],
                gate_auroc=d["target_gate"]["auroc"], gate_ci95=d["target_gate"]["ci95"], target_rejected=d["target_gate"]["target_candidates_rejected"], target_candidates=d["target_gate"]["target_candidates"],
                ab_auroc=d["ab_assignment"]["auroc"], ab_ci95=d["ab_assignment"]["ci95"], abstained=d["ab_assignment"]["target_candidates_abstained"], accepted_target=d["ab_assignment"]["accepted_target_candidates"], wrong_wrestler=d["ab_assignment"]["accepted_as_wrong_target"],
                nontarget_accepted=d["false_target_acceptance"]["nontarget_candidates_accepted"], numeric_failures=d["n_numeric_failures"])
def analyse(eps_L1, comp, B0pts, seed, fixed=FIXED_PARAM, B=2000):
    """Locked two-stage rule: fixed-point view (DR1 point, unchanged) and the V0.6-precedent re-selection view (same deterministic procedure at the joint c*)."""
    groups = groups_of(eps_L1, comp); gL1 = grid_pts(eps_L1, groups, E.rows_for, R.GRID_L1); cstar = S.joint_cstar({"L1": gL1, "B0": B0pts}); out = dict(grid=gL1, cstar=cstar)
    out["fixed_point"] = compact(E.diagnostics(eps_L1, *fixed, seed=seed, B=B))
    if cstar is not None:
        pl = S.select_point(gL1, cstar); out["reselected_point"] = compact(E.diagnostics(eps_L1, *pl["param"], seed=seed, B=B)) if pl else None
    return out
def ab_breakdown(eps_L1, param):
    """Per clip and per true identity: where A/B assignment fails (prespecified per-clip / per-identity breakdowns). Aggregate counts only."""
    out = {}
    for e in eps_L1:
        code, bad, g, q = R.decide(e["P"], *param); A, Bn = e["targets"]; c = collections.Counter()
        for r, cc in zip(e["rows"], code):
            t = U.norm_truth(r["truth"])
            if t not in (A, Bn): continue
            tag = {R.ACCEPT_A: f"accepted_as_{A}", R.ACCEPT_B: f"accepted_as_{Bn}", R.REJECT_NONTARGET: "rejected_at_gate", R.ABSTAIN_AMBIGUOUS: "abstained"}[int(cc)]; c[f"true_{t}->{tag}"] += 1
        d = E.diagnostics([e], *param, seed=1, B=500); out[e["id"]] = dict(confusion=dict(c), ab_auroc=d["ab_assignment"]["auroc"], ab_ci95=d["ab_assignment"]["ci95"], gate_auroc=d["target_gate"]["auroc"], n_units=d["unit_metrics"]["n_units"], fta=d["unit_metrics"]["fta"], coverage=d["coverage"])
    return out
def dist_summary(v): v = np.asarray(v, float); v = v[np.isfinite(v)]; return dict(n=int(len(v)), q10=float(np.quantile(v, .1)), median=float(np.median(v)), q90=float(np.quantile(v, .9))) if len(v) else None
def calibration_transfer(ins, eps_L1):
    """Descriptive adaptation of the 03 section 4 calibration-transfer metric: training-episode (in-sample) vs out-of-fold distributions of g and |q-0.5| for target candidates, and A/B AUROC in-sample vs OOF."""
    def collect(items):
        g = []; dq = []; qa = []; qb = []
        for P, y in items:
            m = np.isin(y, (0, 1)); gg = P[:, 0] + P[:, 1]; q = P[:, 0] / np.maximum(gg, 1e-12)
            g += list(gg[m]); dq += list(np.abs(q[m] - .5)); qa += list(q[y == 0]); qb += list(q[y == 1])
        return dict(g=dist_summary(g), abs_q_minus_half=dist_summary(dq), ab_auroc=U.auroc(qa, qb))
    tr = collect([(x["P"], x["ep"]["y"]) for x in ins]); oof = collect([(e["P"], np.array([0 if U.norm_truth(r["truth"]) == e["targets"][0] else 1 if U.norm_truth(r["truth"]) == e["targets"][1] else 2 for r in e["rows"]])) for e in eps_L1])
    return dict(training_episodes_in_sample=tr, out_of_fold=oof)
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--frozen_dir", default=os.environ.get("V061_FROZEN_DIR")); ap.add_argument("--feat_dir", default=os.environ.get("V061_FEATURE_DIR")); ap.add_argument("--dr1_result", required=True); ap.add_argument("--result", required=True); a = ap.parse_args()
    frozen, feat_dir = os.path.abspath(a.frozen_dir), os.path.abspath(a.feat_dir); ms = preflight(frozen, a.result)
    import torch, phase1_run as RUN, heads; dr1 = json.load(open(a.dr1_result)); D = build_data(frozen, feat_dir); comp = D["comp"]; eps = D["eval_eps"]; B0 = b0_pts(eps, comp); seed = C1.EP_SEED
    res = dict(label=LABEL, locked_impl_manifest_sha256=C1.LOCKED_IMPL_MANIFEST_SHA256, devrun2_code_manifest_sha256=ms, dr1_result_sha256=C1.sha(a.dr1_result), ep_seed=seed, fixed_param=FIXED_PARAM, relaxed_clips=D["relaxed_clips"],
               note="Secondary, descriptive. No outcome class; no scientific change; final head not trained; old-TEST check not rerun; Holdout #2 untouched.")
    # ---- seeds 0..3 (seed 0 = integrity reproduction of DR1) ----
    res["seed_variance"] = {}; cache = {}
    for s in (0, 1, 2, 3):
        probs, ins = crossfit(D, s, want_insample=(s == 0)); cache[s] = probs; L = l1_eps(eps, probs); res["seed_variance"][str(s)] = analyse(L, comp, B0, seed)
        if s == 0:
            same = all(abs(p["fta"] - q["fta"]) < 1e-12 and abs(p["coverage"] - q["coverage"]) < 1e-12 for p, q in zip(res["seed_variance"]["0"]["grid"], dr1["grids"]["L1"]))
            res["dr1_reproduction_check"] = dict(l1_grid_identical_to_dr1=bool(same))
            if not same: json.dump(res, open(a.result + ".ABORTED", "w"), indent=1, default=str); raise SystemExit("seed-0 reproduction does NOT match DR1; aborted, recorded as defect")
            res["breakdown_seed0_fixed_point"] = ab_breakdown(L, FIXED_PARAM); res["calibration_transfer_seed0_descriptive"] = calibration_transfer(ins, L); L0 = L
    res["seed_variance_note"] = "Heads differ only by training/initialisation seed; data and K=5 seed draws fixed. Fixed-point = DR1 point (0.9, 0.10); reselected = same deterministic procedure at the joint c* (V0.6 variance precedent)."
    # ---- Ablation A: old 3-class floor rule + new (seed-0) cross-fitted head ----
    gA = grid_pts(L0, groups_of(L0, comp), lambda e, tau: old_rule_rows(e, tau), [(t,) for t in OLD_FLOOR_GRID]); cA = S.joint_cstar({"L1old": gA, "B0": B0}); ab = dict(grid=gA, cstar=cA)
    if cA is not None:
        pa = S.select_point(gA, cA); ab["selected"] = dict(param=pa["param"], fta=pa["fta"], coverage=pa["coverage"], fa_units=pa["fa_units"], n_units=pa["n_units"], strata=pa["strata"], fold_coverages=pa["fold_coverages"])
        wrong = 0; accT = 0; nt = 0
        for e in L0:
            for r, row in zip(e["rows"], old_rule_rows(e, pa["param"][0])):
                t = U.norm_truth(r["truth"]); tg = t in e["targets"]
                if row["accepted"]:
                    if tg: accT += 1; wrong += int(row["accepted"] != t)
                    else: nt += 1
        ab["selected"].update(accepted_target_candidates=accT, accepted_as_wrong_target=wrong, nontarget_candidates_accepted=nt)
    res["ablation_A_old_rule_new_head_seed0"] = ab
    # ---- Ablation B: new rule + frozen old single-episode head, on episodes it did not train on ----
    old = heads.LearnedHead(D["d_in"]); old.load_state_dict(torch.load(os.path.join(frozen, "phase1_results", "L1_seed0_mobileclip_b.pt"))); old.eval()
    sub = [e for e in eps if e["clip"] != "b1_orton_rollins_wm31"]; subB0 = b0_pts(sub, comp)
    Lold = l1_eps(sub, {e["id"]: softmax_np(old, e) for e in sub}); Lnew = [x for x in L0 if x["clip"] != "b1_orton_rollins_wm31"]
    res["ablation_B_new_rule_old_head"] = dict(episodes=[e["id"] for e in sub], old_head_sha256=C1.sha(os.path.join(frozen, "phase1_results", "L1_seed0_mobileclip_b.pt")),
                                              note="Old head was trained on the Orton/Rollins episode, so that episode is excluded; comparison head = seed-0 cross-fitted head on the same 3 episodes.",
                                              old_head=analyse(Lold, comp, subB0, seed), new_head_same_episodes=analyse(Lnew, comp, subB0, seed))
    # ---- Ablation C: drop relaxed-seed training episodes (HBK, Rock contribute nothing), seeds 0..3 ----
    res["ablation_C_drop_relaxed_episodes"] = dict(dropped_clips=D["relaxed_clips"], by_seed={})
    for s in (0, 1, 2, 3):
        probs, _ = crossfit(D, s, exclude_clips=set(D["relaxed_clips"])); res["ablation_C_drop_relaxed_episodes"]["by_seed"][str(s)] = analyse(l1_eps(eps, probs), comp, B0, seed)
    res["input_sha256"] = dr1["input_sha256"]; json.dump(res, open(a.result, "w"), indent=1, sort_keys=True, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)); os.chmod(a.result, 0o444); print("result sha256", C1.sha(a.result))
if __name__ == "__main__": main()
