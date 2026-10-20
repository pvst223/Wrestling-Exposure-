"""Thin P7 inference driver: loads the parity-passed frozen fold head (saved state), scores the fresh clip's candidate detections, applies the frozen two-stage decision rule at the frozen operating point (tau_g=0.9, delta=0.10).
Uses the V2 owner-approved episode (seeds) only; no labels (y) enter scoring. Output: decisions CSV (clip,tracklet,frame,shot,decision,g,q) in the frozen OOF decision format (no truth column)."""
import os, sys, json, csv, glob, argparse, collections
import numpy as np
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, REPO); sys.path.insert(0, os.path.join(REPO, "v06", "tools"))
import torch, heads
from v061.impl import decision_rule as R
def main():
    ap = argparse.ArgumentParser(); [ap.add_argument(f"--{x}", required=True) for x in ("clip", "seed_json", "feat", "manifest", "head", "out")]; a = ap.parse_args()
    ep = json.load(open(a.seed_json))["episodes"][0]; assert ep["status"] == "OK" and ep["clip"] == a.clip
    z = np.load(a.feat); idx = {(int(f), int(d)): i for i, (f, d) in enumerate(zip(z["frame"], z["det"]))}; E = z["emb"]; feat = lambda s: E[idx[(s["frame"], s["det"])]]
    rows = collections.defaultdict(list)
    for r in csv.DictReader(open(a.manifest)): rows[r["tid"]].append((int(r["frame"]), int(r["det"])))
    sa = np.stack([feat(s) for s in ep["seed_A"]]); sb = np.stack([feat(s) for s in ep["seed_B"]]); sn = np.stack([feat(s) for s in ep["seed_N"]]) if ep["seed_N"] else np.zeros((0, E.shape[1]), np.float32)
    cand = []; meta = []
    for c in sorted(ep["candidate_tracklets"], key=lambda c: c["tid"]):
        for f, d in sorted(rows[c["tid"]]):
            if (f, d) in idx: cand.append(E[idx[(f, d)]]); meta.append(dict(tid=c["tid"], frame=f, shot=c["shot"]))
    t = dict(seed_A=torch.as_tensor(sa, dtype=torch.float32), seed_B=torch.as_tensor(sb, dtype=torch.float32), cand=torch.as_tensor(np.stack(cand), dtype=torch.float32))
    if len(sn): t["seed_N"] = torch.as_tensor(sn, dtype=torch.float32)
    head = heads.LearnedHead(E.shape[1], 128, seed=0); head.load_state_dict(torch.load(a.head, map_location="cpu", weights_only=True)); head.eval()
    with torch.no_grad(): P = torch.softmax(head.logits(t), 1).numpy().astype(np.float64)
    code, bad, g, q = R.decide(P, 0.9, 0.10)
    with open(a.out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["clip", "tracklet", "frame", "shot", "decision", "g", "q"])
        for i, m in enumerate(meta): w.writerow([a.clip, m["tid"], m["frame"], m["shot"], R.NAMES[int(code[i])], float(g[i]), float(q[i])])
    cnt = collections.Counter(R.NAMES[int(c)] for c in code); print(json.dumps(dict(n_rows=len(meta), counts=cnt, A=ep["A"], B=ep["B"], numeric_failures=int(bad.sum()))))
if __name__ == "__main__": main()
