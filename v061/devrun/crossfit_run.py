"""V0.6.1 development cross-fit (spec_v4 02 section 2.3 + 03 section 3). DEVELOPMENT ONLY; exploratory; not validation. MobileCLIP-B only.
Uses ONLY the six existing development-pool clips (frozen features/labels/tracklets); no Holdout #2; old V0.6 TEST clips are development data here per spec 02 section 2.2/2.3 (every number exploratory).
Paths come from args/env (V061_FROZEN_DIR, V061_FEATURE_DIR, V061_PRIVATE_DATA_DIR). Frozen V0.6 code is imported read-only from v06/tools.
Refuses to run unless: locked implementation manifest hash matches, ledger holds DR0 with this code's manifest hash, and no result file exists."""
import os, sys, json, csv, hashlib, argparse, collections, subprocess
import numpy as np
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, REPO); sys.path.insert(0, os.path.join(REPO, "v06", "tools"))
from v061.impl import decision_rule as R, selection as S, evaluate as E, units as U
from v061.devrun import episodes as EP
LOCKED_IMPL_MANIFEST_SHA256 = "eb99beb359ee28dca883d7976ede4385f8dafb2e739d729f89a3358cd3ea073d"
SPEC_V4_MANIFEST_SHA256 = "efb2a797c358cdcad73bc933ccc5a80d95979610179240daf6229b4ba86c88af"
LABEL = "V0.6.1 DEVELOPMENT ONLY (cross-fitted, development-exposed data; exploratory; NOT validation)"
BACKBONE = "mobileclip_b"; K_RESAMPLES = 5
EP_SEED = int(SPEC_V4_MANIFEST_SHA256[:8], 16) % 2**31          # spec 01 'Determinism and seeds' (precedent: EXR2 used the first 8 hex of the manifest hash)
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
def devrun_manifest_sha():
    d = os.path.join(REPO, "v061", "devrun"); items = []
    for dp, dn, fs in os.walk(d):
        dn[:] = [x for x in dn if x != "__pycache__"]
        for f in fs:
            if f.endswith(".pyc") or f == "DEVRUN_MANIFEST.txt": continue
            p = os.path.join(dp, f); items.append((os.path.relpath(p, REPO).replace(os.sep, "/"), sha(p)))
    items.sort(); return hashlib.sha256("".join(f"{h}  {f}\n" for f, h in items).encode()).hexdigest(), items
def components(clip_ids):
    par = {}
    def f(x):
        par.setdefault(x, x)
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for ids in clip_ids.values():
        for i in ids[1:]: par[f(i)] = f(ids[0])
    comp = {}
    for c, ids in clip_ids.items(): comp[c] = f(ids[0])
    return comp
def preflight(frozen, out_dir, result_path):
    r = subprocess.run([sys.executable, os.path.join(REPO, "v061", "tooling", "impl_manifest.py")], capture_output=True, text=True)
    if r.returncode != 0: raise SystemExit("locked implementation manifest check FAILED: " + r.stdout)
    if sha(os.path.join(REPO, "v061", "impl", "IMPLEMENTATION_MANIFEST.txt")) != LOCKED_IMPL_MANIFEST_SHA256: raise SystemExit("implementation manifest hash != locked reference")
    ms, _ = devrun_manifest_sha(); led = [json.loads(l) for l in open(os.path.join(frozen, "AUDIT_LEDGER.jsonl"))]
    dr0 = [e for e in led if e.get("id") == "DR0"]
    if not dr0 or dr0[-1].get("devrun_code_manifest_sha256") != ms: raise SystemExit("ledger DR0 missing or devrun code hash differs")
    if any(e.get("id") == "DR1" for e in led) or os.path.exists(result_path): raise SystemExit("EXECUTED ALREADY: exactly-once rule (re-execution only after a recorded defect)")
    return ms
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frozen_dir", default=os.environ.get("V061_FROZEN_DIR")); ap.add_argument("--feat_dir", default=os.environ.get("V061_FEATURE_DIR"))
    ap.add_argument("--out_dir", default=os.environ.get("V061_PRIVATE_DATA_DIR")); ap.add_argument("--result", required=True)
    ap.add_argument("--dry_structure", action="store_true", help="build and count training episodes only; no training, no scoring")
    a = ap.parse_args()
    if not (a.frozen_dir and a.feat_dir and a.out_dir): raise SystemExit("--frozen_dir, --feat_dir, --out_dir (or env) required")
    frozen, feat_dir, out_dir = (os.path.abspath(x) for x in (a.frozen_dir, a.feat_dir, a.out_dir)); os.makedirs(out_dir, exist_ok=True)
    codeh = None if a.dry_structure else preflight(frozen, out_dir, a.result)
    import torch, phase1_run as RUN, phase1_structure as PS, heads, phase1_metrics as M
    sm_path = os.path.join(frozen, "SEED_EPISODE_MANIFEST_V2.json"); ex_path = os.path.join(frozen, "EXTRACTION_FRAME_MANIFEST_V1.csv")
    SM = json.load(open(sm_path)); sp = {r["clip_id"]: r["split"] for r in csv.DictReader(open(os.path.join(frozen, "splits_v1.csv")))}
    labels = {r["tid"]: r for r in csv.DictReader(open(os.path.join(frozen, "labels", "ALL_firstpass.csv")))}
    exrows = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in csv.DictReader(open(ex_path)): exrows[r["clip"]][r["tid"]].append((int(r["frame"]), int(r["det"]), float(r["box_h"]), int(r["crop_ok"])))
    # ---- evaluation episodes: frozen strict episodes, unchanged ----
    T = RUN.load_episode_tensors(frozen, feat_dir, BACKBONE, sm_path, ex_path); eval_eps = T["train"] + T["dev"] + T["test"]
    d_in = eval_eps[0]["cand"].shape[1]
    # ---- training structure per clip (pair = the two named wrestlers) ----
    clip_ids = {c: sorted(cv["named_wrestlers"]) for c, cv in SM["clips"].items()}; comp = components(clip_ids)
    import glob
    train_by_clip = {}; draw_log = []
    for clip in sorted(clip_ids):
        trs = {t["tid"]: t for t in json.load(open(os.path.join(frozen, "tracklets", f"{clip}.json")))}
        lab = {t: labels[t] for t in trs if t in labels and labels[t]["person_class"] != "UNLABELABLE"}
        fp = glob.glob(os.path.join(feat_dir, f"feat_{BACKBONE}_{clip}_*.npz")); assert len(fp) == 1
        z = np.load(fp[0]); idx = {(int(f), int(d)): i for i, (f, d) in enumerate(zip(z["frame"], z["det"]))}; Emb = z["emb"]
        detmap = {(tid, f): d for tid, rows in exrows[clip].items() for (f, d, h, ok) in rows}
        def dets_of(tids):
            out = []
            for tid in tids:
                t = trs[tid]
                for f, b in zip(t["frames"], t["boxes"]):
                    if (tid, f) in detmap and (f, detmap[(tid, f)]) in idx: out.append(dict(frame=f, det=detmap[(tid, f)], tid=tid, shot=t["shot"], box_h=float(b[3] - b[1])))
            return out
        wrest = clip_ids[clip]; A, B = wrest
        elig = {w: [tid for tid, l in lab.items() if l["person_class"] == "WRESTLER" and l["wrestler_id"] == w and l["multi_person_flag"] == "0"] for w in wrest}
        ref_tids = [tid for tid, l in lab.items() if l["person_class"] == "REFEREE" and l["multi_person_flag"] == "0"]
        ref = PS.select_referee_seeds(clip, dets_of(ref_tids)); feat = lambda s: Emb[idx[(s["frame"], s["det"])]]
        eps = []
        for k in range(K_RESAMPLES):
            sel = {w: EP.select_seeds(f"{EP_SEED}|{clip}|{w}|target|k{k}", dets_of(elig[w])) for w in wrest}
            draw_log.append(dict(clip=clip, k=k, **{w: dict(status=sel[w]["status"], rule=sel[w]["rule"], n_seeds=len(sel[w]["seeds"])) for w in wrest}))
            if any(sel[w]["status"] != "OK" for w in wrest): continue
            used = {s["tid"] for w in wrest for s in sel[w]["seeds"]} | {s["tid"] for s in ref["seeds"]}
            cs = EP.candidate_structure(lab, trs, A, B, used); cand = []; meta = []; y = []
            for c in sorted(cs, key=lambda c: c["tid"]):
                for f, d, h, ok in sorted(exrows[clip][c["tid"]]):
                    if (f, d) in idx: cand.append(Emb[idx[(f, d)]]); meta.append(dict(tid=c["tid"], frame=f, shot=c["shot"], truth=c["truth"])); y.append(c["y"])
            eps.append(dict(id=f"{clip}|{A}|{B}|k{k}", clip=clip, split="train_resample", A=A, B=B, seed_A=np.stack([feat(s) for s in sel[A]["seeds"]]), seed_B=np.stack([feat(s) for s in sel[B]["seeds"]]),
                            seed_N=np.stack([feat(s) for s in ref["seeds"]]) if ref["seeds"] else np.zeros((0, d_in), np.float32), cand=np.stack(cand), y=np.array(y), meta=meta))
        train_by_clip[clip] = eps
    struct = dict(label=LABEL, n_training_episodes_per_clip={c: len(v) for c, v in train_by_clip.items()}, draw_log=draw_log, components=comp, ep_seed=EP_SEED,
                  n_eval_episodes=len(eval_eps), eval_episode_ids=[e["id"] for e in eval_eps])
    if a.dry_structure:
        print(json.dumps(struct, indent=1, default=str)); return
    # ---- cross-fit ----
    folds = collections.defaultdict(list)
    for e in eval_eps: folds[comp[e["clip"]]].append(e)
    all_fold_names = sorted(set(comp.values())); probs = {}; train_log = {}
    for fn in all_fold_names:
        held = {c for c, cc in comp.items() if cc == fn}; tr = [e for c in sorted(train_by_clip) if c not in held for e in train_by_clip[c]]
        if not folds.get(fn): train_log[fn] = dict(heldout_clips=sorted(held), n_train_episodes=len(tr), note="no strictly evaluable episode; contributes training data only"); continue
        head, hist = RUN.train_l1(tr, d_in, seed=0); head.eval(); train_log[fn] = dict(heldout_clips=sorted(held), n_train_episodes=len(tr), final_loss=hist[-1], first_loss=hist[0])
        for e in folds[fn]:
            t = RUN._tt(e); t2 = dict(t)
            if len(t2["seed_N"]) == 0: t2.pop("seed_N")
            with torch.no_grad(): probs[e["id"]] = torch.softmax(head.logits(t2), 1).numpy().astype(np.float64)
    def to_ep(e): return dict(id=e["id"], targets=(e["A"], e["B"]), clip=e["clip"], rows=[dict(clip=e["clip"], shot=m["shot"], truth=m["truth"]) for m in e["meta"]], P=probs[e["id"]])
    L1eps = {fn: [to_ep(e) for e in folds[fn]] for fn in folds}; allL1 = [x for fn in sorted(L1eps) for x in L1eps[fn]]
    def b0_rows(e, tau, mg):
        labs, _ = heads.NonLearnedBaseline(tau, mg).decide(e); ident = {"A": e["A"], "B": e["B"]}
        return [dict(clip=e["clip"], shot=m["shot"], truth=m["truth"], accepted=ident.get(l, "")) for m, l in zip(e["meta"], labs)]
    def pts(rows_fn, grid):
        out = []
        for prm in grid:
            tab = U.table_metrics(U.unit_table([(rows_fn.targets(e), rows_fn(e, *prm)) for e in rows_fn.eps])); tab["param"] = prm
            tab["fold_coverages"] = [U.table_metrics(U.unit_table([(rows_fn.targets(e), rows_fn(e, *prm)) for e in grp]))["coverage"] for grp in rows_fn.groups]; out.append(tab)
        return out
    class L1Fn:
        eps = allL1; groups = [L1eps[fn] for fn in sorted(L1eps)]; targets = staticmethod(lambda e: e["targets"])
        def __call__(self, e, tg, dl): return E.rows_for(e, tg, dl)
    class B0Fn:
        eps = [e for fn in sorted(folds) for e in folds[fn]]; groups = [folds[fn] for fn in sorted(folds)]; targets = staticmethod(lambda e: (e["A"], e["B"]))
        def __call__(self, e, tau, mg): return b0_rows(e, tau, mg)
    gL1 = pts(L1Fn(), R.GRID_L1); gB0 = pts(B0Fn(), R.GRID_B0)
    cstar = S.joint_cstar({"L1": gL1, "B0": gB0}); res = dict(label=LABEL, locked_impl_manifest_sha256=LOCKED_IMPL_MANIFEST_SHA256, devrun_code_manifest_sha256=codeh, spec_v4_manifest_sha256=SPEC_V4_MANIFEST_SHA256, ep_seed=EP_SEED,
                                                                    backbone=BACKBONE, k_resamples=K_RESAMPLES, structure=struct, training=train_log, grids=dict(L1=gL1, B0=gB0), cstar=cstar,
                                                                    note="No outcome class (KEEP/KILL/MODIFY) is assigned; all numbers are development-exposed and exploratory.")
    if cstar is None: res["status"] = "no feasible operating point"
    else:
        pl = S.select_point(gL1, cstar); pb = S.select_point(gB0, cstar); res.update(status="OK", selected_L1=pl, selected_B0=pb)
        TL = U.unit_table([(e["targets"], E.rows_for(e, *pl["param"])) for e in allL1]); TB = U.unit_table([(B0Fn.targets(e), b0_rows(e, *pb["param"])) for e in B0Fn.eps])
        res["pooled_oof_L1"] = U.table_metrics(TL); res["pooled_oof_B0"] = U.table_metrics(TB); res["paired_sign_exploratory"] = U.paired_sign(TB, TL)
        for nm in ("pooled_oof_L1", "pooled_oof_B0"):
            m = res[nm]; m["fta_ci95_exact"] = list(U.clopper_pearson(m["fa_units"], m["n_units"]))
        seed = EP_SEED; d = E.diagnostics(allL1, *pl["param"], seed=seed); d["label"] = LABEL; res["diagnostics_L1"] = d
        # candidate-level private table for the renderer (NOT committed)
        rows = []
        for e in B0Fn.eps:
            P = probs[e["id"]]; code, bad, g, q = R.decide(P, *pl["param"]); labs, _ = heads.NonLearnedBaseline(*pb["param"]).decide(e)
            for i, m in enumerate(e["meta"]):
                tn = M._norm_truth(m["truth"]); tgt = tn in (e["A"], e["B"]); c = int(code[i]); acc = e["A"] if c == R.ACCEPT_A else (e["B"] if c == R.ACCEPT_B else "")
                tag = ("OK" if acc == tn else "SWAP-FA") if (acc and tgt) else ("FA" if acc else ("MISS" if (tgt and c == R.REJECT_NONTARGET) else ("ABSTAIN" if c == R.ABSTAIN_AMBIGUOUS else "rej")))
                if tgt and c == R.ABSTAIN_AMBIGUOUS: tag = "ABSTAIN"
                rows.append(dict(clip=e["clip"], tracklet=m["tid"], frame=m["frame"], shot=m["shot"], truth=tn, decision=R.NAMES[c], reason=tag, g=float(g[i]), q=float(q[i]), b0_decision=labs[i]))
        with open(os.path.join(out_dir, "OOF_DECISIONS_PRIVATE.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        res["private_oof_decisions_sha256"] = sha(os.path.join(out_dir, "OOF_DECISIONS_PRIVATE.csv")); res["n_oof_candidate_rows"] = len(rows)
    res["input_sha256"] = dict(seed_manifest=sha(sm_path), extraction_manifest=sha(ex_path), splits=sha(os.path.join(frozen, "splits_v1.csv")), labels=sha(os.path.join(frozen, "labels", "ALL_firstpass.csv")),
                               features={os.path.basename(p): sha(p) for p in sorted(glob.glob(os.path.join(feat_dir, f"feat_{BACKBONE}_*.npz")))})
    json.dump(res, open(a.result, "w"), indent=1, sort_keys=True, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)); os.chmod(a.result, 0o444)
    print(json.dumps({k: res.get(k) for k in ("status", "cstar")}), "result sha256", sha(a.result))
if __name__ == "__main__": main()
