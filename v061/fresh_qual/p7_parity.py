"""Thin P7 parity driver (R3 H-a, reviewer-approved D1). Calls FROZEN functions only; trains nothing new.
Reproduces the DR1 fold head held out for the brock_lesnar component (designation = arithmetic on the frozen DR1 training record: most training episodes, ties lexicographic)
and compares, bit-for-bit, its decision rows (decision code, g, q at the frozen operating point tau_g=0.9, delta=0.10) with the frozen DR1 OOF decision rows of the held-out clip.
Parity failure -> exit 2 (STOP + defect report). Usage: p7_parity.py --frozen_dir D --feat_dir D --oof CSV --dr1 JSON [--save_head PATH] --out JSON"""
import os, sys, json, csv, glob, argparse, collections, hashlib
import numpy as np
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, REPO); sys.path.insert(0, os.path.join(REPO, "v06", "tools"))
from v061.impl import decision_rule as R
from v061.devrun import episodes as EP
from v061.devrun import crossfit_run as CF
def sha(p): return CF.sha(p)
def build_training(frozen, feat_dir, PS, RUN):
    SM = json.load(open(os.path.join(frozen, "SEED_EPISODE_MANIFEST_V2.json"))); labels = {r["tid"]: r for r in csv.DictReader(open(os.path.join(frozen, "labels", "ALL_firstpass.csv")))}
    ex_path = os.path.join(frozen, "EXTRACTION_FRAME_MANIFEST_V1.csv"); exrows = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in csv.DictReader(open(ex_path)): exrows[r["clip"]][r["tid"]].append((int(r["frame"]), int(r["det"]), float(r["box_h"]), int(r["crop_ok"])))
    T = RUN.load_episode_tensors(frozen, feat_dir, CF.BACKBONE, os.path.join(frozen, "SEED_EPISODE_MANIFEST_V2.json"), ex_path); eval_eps = T["train"] + T["dev"] + T["test"]; d_in = eval_eps[0]["cand"].shape[1]
    clip_ids = {c: sorted(cv["named_wrestlers"]) for c, cv in SM["clips"].items()}; comp = CF.components(clip_ids); train_by_clip = {}
    for clip in sorted(clip_ids):
        trs = {t["tid"]: t for t in json.load(open(os.path.join(frozen, "tracklets", f"{clip}.json")))}; lab = {t: labels[t] for t in trs if t in labels and labels[t]["person_class"] != "UNLABELABLE"}
        fp = glob.glob(os.path.join(feat_dir, f"feat_{CF.BACKBONE}_{clip}_*.npz")); assert len(fp) == 1
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
        ref_tids = [tid for tid, l in lab.items() if l["person_class"] == "REFEREE" and l["multi_person_flag"] == "0"]; ref = PS.select_referee_seeds(clip, dets_of(ref_tids)); feat = lambda s: Emb[idx[(s["frame"], s["det"])]]; eps = []
        for k in range(CF.K_RESAMPLES):
            sel = {w: EP.select_seeds(f"{CF.EP_SEED}|{clip}|{w}|target|k{k}", dets_of(elig[w])) for w in wrest}
            if any(sel[w]["status"] != "OK" for w in wrest): continue
            used = {s["tid"] for w in wrest for s in sel[w]["seeds"]} | {s["tid"] for s in ref["seeds"]}; cs = EP.candidate_structure(lab, trs, A, B, used); cand = []; meta = []; y = []
            for c in sorted(cs, key=lambda c: c["tid"]):
                for f, d, h, ok in sorted(exrows[clip][c["tid"]]):
                    if (f, d) in idx: cand.append(Emb[idx[(f, d)]]); meta.append(dict(tid=c["tid"], frame=f, shot=c["shot"], truth=c["truth"])); y.append(c["y"])
            eps.append(dict(id=f"{clip}|{A}|{B}|k{k}", clip=clip, split="train_resample", A=A, B=B, seed_A=np.stack([feat(s) for s in sel[A]["seeds"]]), seed_B=np.stack([feat(s) for s in sel[B]["seeds"]]),
                            seed_N=np.stack([feat(s) for s in ref["seeds"]]) if ref["seeds"] else np.zeros((0, d_in), np.float32), cand=np.stack(cand), y=np.array(y), meta=meta))
        train_by_clip[clip] = eps
    return train_by_clip, eval_eps, comp, d_in
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--frozen_dir", required=True); ap.add_argument("--feat_dir", required=True); ap.add_argument("--oof", required=True); ap.add_argument("--dr1", required=True)
    ap.add_argument("--save_head", default=None); ap.add_argument("--out", required=True); a = ap.parse_args()
    import torch, phase1_run as RUN, phase1_structure as PS
    dr1 = json.load(open(a.dr1)); tl = dr1["training"]
    cand_folds = {k: v for k, v in tl.items() if "n_train_episodes" in v and "final_loss" in v}
    desig = sorted(cand_folds, key=lambda k: (-cand_folds[k]["n_train_episodes"], k))[0]   # outcome-blind arithmetic
    train_by_clip, eval_eps, comp, d_in = build_training(os.path.abspath(a.frozen_dir), os.path.abspath(a.feat_dir), PS, RUN)
    held = {c for c, cc in comp.items() if cc == desig}; tr = [e for c in sorted(train_by_clip) if c not in held for e in train_by_clip[c]]
    head, hist = RUN.train_l1(tr, d_in, seed=0); head.eval()
    rep = dict(designated_fold=desig, heldout_clips=sorted(held), n_train_episodes=len(tr), expected_n_train=tl[desig]["n_train_episodes"], first_loss=hist[0], final_loss=hist[-1], expected_first_loss=tl[desig]["first_loss"], expected_final_loss=tl[desig]["final_loss"])
    rep["loss_bitwise_equal"] = (hist[0] == tl[desig]["first_loss"] and hist[-1] == tl[desig]["final_loss"] and len(tr) == tl[desig]["n_train_episodes"])
    oof = collections.defaultdict(list)
    for r in csv.DictReader(open(a.oof)): oof[r["clip"]].append(r)
    mism = []; n = 0
    for clip in sorted(held):
        got = []
        for e in [x for x in eval_eps if x["clip"] == clip]:
            t = RUN._tt(e); t2 = dict(t)
            if len(t2["seed_N"]) == 0: t2.pop("seed_N")
            with torch.no_grad(): P = torch.softmax(head.logits(t2), 1).numpy().astype(np.float64)
            code, bad, g, q = R.decide(P, 0.9, 0.10)
            for i, m in enumerate(e["meta"]): got.append((m["tid"], m["frame"], R.NAMES[int(code[i])], float(g[i]), float(q[i])))
        exp = oof[clip]
        if len(got) != len(exp): mism.append(dict(clip=clip, issue="row count", got=len(got), expected=len(exp)))
        for (tid, f, dec, g, q), r in zip(got, exp):
            n += 1; eg, eq = float(r["g"]), float(r["q"])
            same = (tid == r["tracklet"] and f == int(r["frame"]) and dec == r["decision"] and ((g == eg) or (np.isnan(g) and np.isnan(eg))) and ((q == eq) or (np.isnan(q) and np.isnan(eq))))
            if not same and len(mism) < 20: mism.append(dict(clip=clip, tid=tid, frame=f, got=[dec, repr(g), repr(q)], expected=[r["decision"], r["g"], r["q"]]))
            elif not same: mism.append(None)
    rep.update(n_rows_compared=n, n_mismatch=len([m for m in mism if True]), mismatch_examples=[m for m in mism if m][:10], parity="PASS" if (not mism and rep["loss_bitwise_equal"] and n > 0) else "FAIL",
               torch=torch.__version__, threads=torch.get_num_threads(), oof_sha256=sha(a.oof), dr1_sha256=sha(a.dr1), operating_point=[0.9, 0.10])
    if rep["parity"] == "PASS" and a.save_head: torch.save(head.state_dict(), a.save_head); rep["head_state_sha256"] = sha(a.save_head)
    json.dump(rep, open(a.out, "w"), indent=1, default=str); print(json.dumps({k: rep[k] for k in ("parity", "n_rows_compared", "n_mismatch", "loss_bitwise_equal", "first_loss", "final_loss")}))
    sys.exit(0 if rep["parity"] == "PASS" else 2)
if __name__ == "__main__": main()
