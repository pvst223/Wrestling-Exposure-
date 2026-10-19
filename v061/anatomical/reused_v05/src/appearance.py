"""V0.3 appearance descriptors and identity models.

WHAT THIS IS: colour-histogram descriptors of body regions located by the pose keypoints, compared with Bhattacharyya distance
against per-identity models built ONLY from manually seeded frames (static; no online model update, see docs for why).
WHAT THIS IS NOT: a learned re-identification embedding (no pretrained re-ID weights could be obtained in this environment),
not validated on any wrestler other than the two in this clip, and not robust to lighting changes between shots (a lighting change
is expected to lower support / raise UNRESOLVED, not to be compensated).

Descriptor: HSV pixels are quantised into 3 + 2*NBINS_H bins: DARK (V<V_DARK), GRAY_MID, GRAY_LIGHT (S<S_GRAY), and
NBINS_H hue bins x 2 value levels for coloured pixels. Chosen so that black clothing, white/stripes and hue-bearing clothing/skin are
separable without relying on hue where it is meaningless (low V or low S)."""
import numpy as np, cv2

SIDES_REGIONS = ["torso", "thigh_L", "thigh_R", "shank_L", "shank_R", "arm_L", "arm_R", "head"]
REGION_MASS = {"torso": 0.497, "thigh_L": 0.100, "thigh_R": 0.100, "shank_L": 0.061, "shank_R": 0.061, "arm_L": 0.028, "arm_R": 0.028, "head": 0.081}  # Dempster/Winter masses as in com_model.py (shank=leg+foot, arm=upper arm)
TYPES = ["torso", "thigh", "shank", "arm", "head"]
def rtype(r): return r.split("_")[0]

def nbins(A): return 3 + 2 * A.NBINS_H

def quantize(frame_bgr, A):
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV); h = hsv[..., 0].astype(np.int32); s = hsv[..., 1]; v = hsv[..., 2]
    idx = (h * A.NBINS_H // 180) * 2 + (v >= A.V_SPLIT).astype(np.int32) + 3
    idx = np.where(v < A.V_DARK, 0, np.where(s < A.S_GRAY, np.where(v >= A.V_GRAY_LIGHT, 2, 1), idx))
    return idx.astype(np.uint8)

def _seg_poly(p, q, hw):
    v = q - p; n = np.array([-v[1], v[0]]) / (np.linalg.norm(v) + 1e-6); w = hw * np.linalg.norm(v)
    return np.array([p + n * w, p - n * w, q - n * w, q + n * w])

def region_masks(shape, kp, kc, A):
    """dict region -> uint8 mask (only for regions whose defining keypoints have conf >= A.KP_CONF)."""
    ok = kc >= A.KP_CONF; out = {}
    def fill(poly):
        m = np.zeros(shape, np.uint8); cv2.fillConvexPoly(m, np.round(poly).astype(np.int32), 1); return m
    if ok[5] and ok[6] and ok[11] and ok[12]:
        quad = kp[[5, 6, 12, 11]].astype(float); c = quad.mean(0); out["torso"] = fill(c + (quad - c) * (1 - A.TORSO_SHRINK))
    for name, (a, b), hw in (("thigh_L", (11, 13), A.THIGH_HW), ("thigh_R", (12, 14), A.THIGH_HW), ("shank_L", (13, 15), A.SHANK_HW), ("shank_R", (14, 16), A.SHANK_HW), ("arm_L", (5, 7), A.ARM_HW), ("arm_R", (6, 8), A.ARM_HW)):
        if ok[a] and ok[b]: out[name] = fill(_seg_poly(kp[a].astype(float), kp[b].astype(float), hw))
    hd = [i for i in range(5) if ok[i]]
    if len(hd) >= 2:
        pts = kp[hd].astype(float); c = pts.mean(0); dmax = max(float(np.linalg.norm(pts[i] - pts[j])) for i in range(len(pts)) for j in range(i + 1, len(pts)))
        m = np.zeros(shape, np.uint8); cv2.circle(m, (int(round(c[0])), int(round(c[1]))), int(max(A.HEAD_MIN_R, A.HEAD_R_FRAC * dmax)), 1, -1); out["head"] = m
    return out

def whole_mask(shape, box, A):
    x1, y1, x2, y2 = box; cx = (x1 + x2) / 2; hw = A.WHOLE_COL_FRAC * (x2 - x1) / 2; m = np.zeros(shape, np.uint8)
    m[max(0, int(y1)):max(0, int(y2)), max(0, int(cx - hw)):max(0, int(cx + hw))] = 1; return m

def counts(q, mask, A):
    n = int(mask.sum())
    if n < A.REGION_MIN_PIX: return None
    return np.bincount(q[mask > 0], minlength=nbins(A)).astype(np.float64)

def bd(p, q):  # Bhattacharyya distance between two L1-normalised histograms (same definition as cv2.HISTCMP_BHATTACHARYYA)
    return float(np.sqrt(max(0.0, 1.0 - np.sum(np.sqrt(p * q)))))

def descriptors(q, kp, kc, box, A):
    """-> dict region -> (hist (L1-normalised), n_pixels); includes 'whole'."""
    out = {}
    for r, m in region_masks(q.shape, kp, kc, A).items():
        c = counts(q, m, A)
        if c is not None: out[r] = (c / c.sum(), int(c.sum()))
    c = counts(q, whole_mask(q.shape, box, A), A)
    if c is not None: out["whole"] = (c / c.sum(), int(c.sum()))
    return out

class Models:
    """Static per-identity appearance models (pooled L/R per type) built from the manual seed frames, plus SEED-DERIVED scale references:
      dsep[t]   BD(A_t, B_t)             between-wrestler separation of region type t
      noise[t]  MEAN of all BDs between pairs of SEED VIEWS of the same wrestler (A and B pooled): typical cross-view within-person variation; a type for which
                no wrestler has two views has UNKNOWN noise and is not used (weight 0)
      gap[t]    dsep[t] - noise[t]       the usable signal; <= 0 means the type does not separate the wrestlers beyond within-person variation."""
    def __init__(self, A): self.A = A; self.acc = {}; self.views = {}   # identity -> type -> counts ; identity -> list of {type: hist}
    def add(self, identity, q, kp, kc, box):
        a = self.acc.setdefault(identity, {}); v = {}
        for r, m in region_masks(q.shape, kp, kc, self.A).items():
            c = counts(q, m, self.A)
            if c is not None: a[rtype(r)] = a.get(rtype(r), 0) + c; v[rtype(r)] = v.get(rtype(r), 0) + c
        c = counts(q, whole_mask(q.shape, box, self.A), self.A)
        if c is not None: a["whole"] = a.get("whole", 0) + c; v["whole"] = c
        self.views.setdefault(identity, []).append({t: x / x.sum() for t, x in v.items() if x.sum() >= self.A.MODEL_MIN_PIX})
    def finalize(self):
        A = self.A; self.model = {}
        for i, a in self.acc.items(): self.model[i] = {t: c / c.sum() for t, c in a.items() if c.sum() >= A.MODEL_MIN_PIX}
        self.dsep = {}; self.noise = {}; self.gap = {}
        for t in TYPES + ["whole"]:
            if t in self.model.get("A", {}) and t in self.model.get("B", {}): self.dsep[t] = bd(self.model["A"][t], self.model["B"][t])
            w = []
            for i in ("A", "B"):
                vs = [v[t] for v in self.views.get(i, []) if t in v]
                w += [bd(vs[a_], vs[b_]) for a_ in range(len(vs)) for b_ in range(a_ + 1, len(vs))]
            if w: self.noise[t] = float(np.mean(w))
            if t in self.dsep and t in self.noise: self.gap[t] = self.dsep[t] - self.noise[t]
        self.dsep_n = {}   # NEITHER exemplar: mean distance of its model to the A and B models
        if "NEITHER" in self.model:
            for t in TYPES + ["whole"]:
                if t in self.model["NEITHER"] and t in self.model.get("A", {}) and t in self.model.get("B", {}):
                    self.dsep_n[t] = 0.5 * (bd(self.model["NEITHER"][t], self.model["A"][t]) + bd(self.model["NEITHER"][t], self.model["B"][t]))
    def summary(self):
        return dict(n_views={i: len(v) for i, v in self.views.items()}, model_types={i: sorted(m.keys()) for i, m in self.model.items()}, dsep={k: round(v, 4) for k, v in self.dsep.items()}, noise={k: round(v, 4) for k, v in self.noise.items()}, gap={k: round(v, 4) for k, v in self.gap.items()}, dsep_neither={k: round(v, 4) for k, v in self.dsep_n.items()})

def appearance_cues(desc, M, A):
    """For one candidate. Returns (dict identity -> dict(reg=(s,r), whole=(s,r)) for A,B,NEITHER, per-region distances).
    support s = clip(1 - 2*(d - noise_t)/gap_t, -1, 1): +1 = as close as a second view of the same wrestler typically is; 0 = midway between that and the
    other wrestler's model; -1 = at least as far as the other wrestler. reliability = pixel factor x min(1, gap_t/D_SEP_MIN) (a region type that does not
    separate the wrestlers beyond within-person variation gets zero weight)."""
    out = {}; dists = {}
    for ident in ("A", "B", "NEITHER"):
        if ident not in M.model: continue
        num = 0.0; den = 0.0
        def ref(t):
            if t not in M.noise: return None
            g = (M.gap.get(t) if ident in ("A", "B") else (M.dsep_n[t] - M.noise[t] if t in M.dsep_n else None))
            return None if g is None or g <= 0 else g
        for r, (h, n) in desc.items():
            if r == "whole": continue
            t = rtype(r); g = ref(t)
            if t not in M.model[ident] or g is None: continue
            d = bd(h, M.model[ident][t]); dists[(ident, r)] = d
            w = REGION_MASS[r] * min(1.0, n / A.PIX_FULL) * min(1.0, g / A.D_SEP_MIN)
            num += w * float(np.clip(1.0 - 2.0 * (d - M.noise[t]) / g, -1.0, 1.0)); den += w
        reg = (num / den, min(1.0, den / A.W_FULL)) if den > 0 else (0.0, 0.0)
        wh = (0.0, 0.0); g = ref("whole")
        if "whole" in desc and "whole" in M.model[ident] and g is not None:
            d = bd(desc["whole"][0], M.model[ident]["whole"]); dists[(ident, "whole")] = d
            wh = (float(np.clip(1.0 - 2.0 * (d - M.noise["whole"]) / g, -1.0, 1.0)), A.WHOLE_R_CAP * min(1.0, g / A.D_SEP_MIN))
        out[ident] = dict(reg=reg, whole=wh)
    return out, dists

def region_votes(desc, dists, M, own, other, A):
    """Per-region vote for single-body verification: +1 region looks like `own`, -1 looks like `other`, 0 neutral/unavailable.
    A region type votes only if it separates the wrestlers beyond within-person variation (gap >= D_SEP_MIN), and the distance difference must exceed
    max(VOTE_DELTA * d_sep, noise_t): i.e. larger than the typical difference between two views of the SAME wrestler."""
    v = {}
    for r in desc:
        if r == "whole": continue
        t = rtype(r)
        if (own, r) not in dists or (other, r) not in dists or M.gap.get(t, 0) < A.D_SEP_MIN: continue
        diff = dists[(other, r)] - dists[(own, r)]; thr = max(A.VOTE_DELTA * M.dsep[t], M.noise[t])
        v[r] = 1 if diff >= thr else (-1 if diff <= -thr else 0)
    return v
