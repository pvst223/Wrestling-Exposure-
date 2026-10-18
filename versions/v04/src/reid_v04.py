"""V0.4 embedding-based identity evidence (decomposed). Uses the cached MobileCLIP-B embeddings (see docs/V0.4_REID_MODEL_SELECTION.md).
THIS IS NOT PERSON RE-IDENTIFICATION: it is a general image embedding compared with the 10 manually seeded exemplars. Cosine similarity is an UNCALIBRATED
heuristic similarity, not a probability.
Per crop type k (box / upper / lower) and identity I in {A, B, NEITHER}: sim_I = mean cosine similarity to I's seed embeddings of type k.
Evidence that the candidate is X (X = A or B): margin_X = sim_X - max(sim of the other identities)  [i.e. 'is X' AND 'is not the other wrestler / not the referee' in ONE number];
support s_X = clip(margin_X / scale_k, -1, 1).  scale_k = mean |leave-one-out margin| over the seeds of that crop type (derived from the seeds only).
reliability r_k = max(0, 2*acc_k - 1) * q, acc_k = seed leave-one-out 3-class accuracy of crop type k, q = min(1, min crop side / REID_FULL_PX). A crop type with acc_k <= ACC_MIN gets r = 0."""
import numpy as np
import embed_crops as EC
IDS3 = ("A", "B", "NEITHER")
class EmbCache:
    def __init__(self, path):
        z = np.load(path); self.d = {(int(f), int(j), int(c)): e for f, j, c, e in zip(z["frame"], z["det"], z["ctype"], z["emb"])}
    def get(self, t, j, k): return self.d.get((t, j, EC.CT[k]))
def crop_min_side(kp, kc, box, k, shape):
    if k == "box": b = list(box)
    else:
        b = EC.part_box(kp, kc, k)
        if b is None: return 0.0
    x1, y1, x2, y2 = b; x1 = max(0, x1); y1 = max(0, y1); x2 = min(shape[1], x2); y2 = min(shape[0], y2); return float(max(0.0, min(x2 - x1, y2 - y1)))
class ReidModel:
    def __init__(self, cache, seeds, dets, R):
        self.R = R; self.ref = {k: {i: [] for i in IDS3} for k in R.CROP_TYPES}; self.n_seed_crops = {k: {i: 0 for i in IDS3} for k in R.CROP_TYPES}
        for si, s in enumerate(seeds):
            for k in R.CROP_TYPES:
                e = cache.get(s["frame"], s["det"], k)
                if e is not None: self.ref[k][s["identity"]].append((si, e)); self.n_seed_crops[k][s["identity"]] += 1
        self.scale = {}; self.acc = {}; self.loo = {}
        for k in R.CROP_TYPES:
            right = 0; tot = 0; mags = []
            for i in IDS3:
                for si, e in self.ref[k][i]:
                    sims = {}
                    for I in IDS3:
                        refs = [x for (sj, x) in self.ref[k][I] if sj != si]
                        if refs: sims[I] = float(np.mean([e @ x for x in refs]))
                    if i not in sims or len(sims) < 2: continue
                    tot += 1; best = max(sims, key=sims.get); right += best == i; mags.append(abs(sims[i] - max(v for I, v in sims.items() if I != i)))
            self.acc[k] = right / tot if tot else 0.0; self.scale[k] = max(R.SCALE_MIN, float(np.mean(mags))) if mags else R.SCALE_MIN; self.loo[k] = dict(correct=right, total=tot)
        self.rel_cap = {k: max(0.0, 2 * self.acc[k] - 1) if self.acc[k] > R.ACC_MIN else 0.0 for k in R.CROP_TYPES}
    def summary(self):
        return dict(n_seed_crops=self.n_seed_crops, loo=self.loo, acc={k: round(v, 3) for k, v in self.acc.items()}, scale={k: round(v, 4) for k, v in self.scale.items()}, reliability_cap={k: round(v, 3) for k, v in self.rel_cap.items()})
    def cues(self, cache, t, j, kp, kc, box, shape):
        """-> dict k -> dict(sim={A,B,N}, s={A,B,NEITHER}, r) for crop types with an embedding and usable references."""
        out = {}
        for k in self.R.CROP_TYPES:
            e = cache.get(t, j, k)
            if e is None: continue
            sims = {I: float(np.mean([e @ x for (_, x) in self.ref[k][I]])) for I in IDS3 if self.ref[k][I]}
            if len(sims) < 2: continue
            q = min(1.0, crop_min_side(kp, kc, box, k, shape) / self.R.REID_FULL_PX)
            s = {I: float(np.clip((sims[I] - max(v for J, v in sims.items() if J != I)) / self.scale[k], -1, 1)) for I in sims}
            out[k] = dict(sim=sims, s=s, r=self.rel_cap[k] * q)
        return out
