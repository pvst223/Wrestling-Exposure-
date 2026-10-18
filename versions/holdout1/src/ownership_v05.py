"""V0.5 person-specific LANDMARK OWNERSHIP evidence from per-person instance masks.

QUESTION ASKED: do the keypoints that would feed the COM of the selected skeleton lie inside ONE person's silhouette, and is that silhouette explained by
this skeleton alone? Evidence comes from a general COCO instance-segmentation model (YOLOv8m-seg, 'person'); it is NOT a wrestling-trained model, NOT validated here.

PER-LANDMARK CLASS (landmark = confident keypoint among nose, shoulders, elbows, wrists, hips, knees, ankles), relative to the OWNER mask
(the instance containing the largest fraction of the skeleton's confident landmarks) and COMPETING masks (other instances that are not near-duplicates of the owner):
  OWN_ONLY    inside the owner mask only
  CONTESTED   inside the owner mask AND inside a competing instance mask (overlap region: ownership cannot be told apart)
  OTHER_ONLY  inside a competing mask but not the owner mask (this landmark is attributed by the masks to a different person)
  OUTSIDE     inside no mask (mask boundaries are imprecise; hands/feet often fall outside)
MASK-LEVEL CUES: opponent pose landmarks inside the owner mask; share of the owner mask NOT explained by the skeleton (UNEXPLAINED: another body may be attached to the
mask); bones whose endpoints sit in different instances (BONE_SPANS_INSTANCES); bones that leave the owner mask.
STATES: SINGLE_BODY_SUPPORTED | MIXED_BODY_SUSPECTED | OWNERSHIP_UNCERTAIN.

WHAT THIS ESTABLISHES: the landmarks lie in one segmented person region, no other segmented region claims them, no other detected person's landmarks lie inside it, and that region
is not much larger than the skeleton accounts for.
WHAT IT DOES NOT ESTABLISH: that the mask is correct (instance masks of touching people can merge or split arbitrarily); that a joint inside a single merged mask belongs to the
person the skeleton claims; correctness of landmark position; identity (identity is appearance evidence and is kept separate). Landmarks of two people inside ONE merged mask that the
skeleton happens to cover are not detectable by this module except through UNEXPLAINED and the geometric/temporal vetoes added in track_v05."""
import numpy as np, cv2
LMS = [0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
BONES = [(5, 6), (11, 12), (5, 11), (6, 12), (5, 7), (7, 9), (6, 8), (8, 10), (11, 13), (13, 15), (12, 14), (14, 16)]
SKEL = BONES + [(0, 5), (0, 6)]
class FrameSeg:
    def __init__(self, sd, W, H, conf_min):
        mh, mw = sd["shape"]; self.mh, self.mw = mh, mw; self.sx, self.sy = mw / W, mh / H; self.W, self.H = W, H
        n = len(sd["conf"]); keep = [i for i in range(n) if sd["conf"][i] >= conf_min]
        if n and keep: self.masks = np.unpackbits(sd["mask"], axis=-1)[..., :mw].astype(bool)[keep]
        else: self.masks = np.zeros((0, mh, mw), bool)
        self.conf = sd["conf"][keep] if n else np.zeros(0); self.box = sd["box"][keep] if n else np.zeros((0, 4)); self.area = self.masks.sum(axis=(1, 2))
        self._dil = {}
    def n(self): return len(self.masks)
    def dilated(self, i, r):
        k = (i, r)
        if k not in self._dil: self._dil[k] = cv2.dilate(self.masks[i].astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))).astype(bool) if r > 0 else self.masks[i]
        return self._dil[k]
    def pts(self, kp, idx):
        x = np.clip(np.round(kp[idx, 0] * self.sx).astype(int), 0, self.mw - 1); y = np.clip(np.round(kp[idx, 1] * self.sy).astype(int), 0, self.mh - 1); return x, y
    def iou(self, a, b):
        i = (self.masks[a] & self.masks[b]).sum(); u = (self.masks[a] | self.masks[b]).sum(); return float(i / u) if u else 0.0
def tol_px(C, fs): return max(0, int(round(C.MASK_TOL_PX * fs.sx)))
def owner_for(fs, kp, kc, kp_conf, C):
    """Instance containing the largest fraction of the skeleton's confident landmarks (ties: higher seg confidence). -> (index|None, cover). Decision-free: also used to cut masked crops."""
    L = [i for i in LMS if kc[i] >= kp_conf]
    if fs.n() == 0 or len(L) < C.MIN_LANDMARKS: return None, 0.0
    r = tol_px(C, fs); x, y = fs.pts(kp, L); best = (None, -1.0, -1.0)
    for m in range(fs.n()):
        cov = float(fs.dilated(m, r)[y, x].mean())
        if cov > best[1] + 1e-9 or (abs(cov - best[1]) <= 1e-9 and fs.conf[m] > best[2]): best = (m, cov, float(fs.conf[m]))
    return (best[0] if best[1] >= C.OWNER_COVER_MIN else None), best[1]
def owner_mask_fullres(fs, m, C):
    """Owner mask (dilated by the tolerance) upsampled to the source frame size (bool H x W)."""
    return cv2.resize(fs.dilated(m, tol_px(C, fs)).astype(np.uint8), (fs.W, fs.H), interpolation=cv2.INTER_NEAREST).astype(bool)
def metrics(fs, kp, kc, others, S, kp_conf, C):
    """Raw ownership numbers (no decision). others: list of (kp, kc) of OTHER detected people (non-duplicates of this skeleton)."""
    L = [i for i in LMS if kc[i] >= kp_conf]; M = dict(n_landmarks=len(L), owner=None, cover=0.0, cls={}, n_inst=fs.n())
    own, cover = owner_for(fs, kp, kc, kp_conf, C); M["owner"], M["cover"] = own, cover
    if own is None: return M
    r = tol_px(C, fs); x, y = fs.pts(kp, L); own_in = fs.dilated(own, r)[y, x]
    comp = np.zeros(len(L), bool); comp_ids = []
    for m in range(fs.n()):
        if m == own or fs.iou(own, m) >= C.SEG_DUP_IOU: continue
        ins = fs.dilated(m, r)[y, x]
        if ins.any(): comp |= ins; comp_ids.append(m)
    cls = {}
    for k, i in enumerate(L): cls[i] = "CONTESTED" if (own_in[k] and comp[k]) else ("OWN_ONLY" if own_in[k] else ("OTHER_ONLY" if comp[k] else "OUTSIDE"))
    n = len(L); cnt = lambda c: sum(1 for v in cls.values() if v == c)
    M.update(cls=cls, own_only_n=cnt("OWN_ONLY"), contested_n=cnt("CONTESTED"), other_only_n=cnt("OTHER_ONLY"), outside_n=cnt("OUTSIDE"), competing=comp_ids)
    for k in ("own_only", "contested", "other_only", "outside"): M[k + "_frac"] = M[k + "_n"] / n
    # opponent landmarks inside the owner mask
    opp = 0.0; opp_n = 0
    for okp, okc in others:
        Lo = [i for i in LMS if okc[i] >= kp_conf]
        if len(Lo) < C.OPP_MIN_N: continue
        xo, yo = fs.pts(okp, Lo); f = float(fs.dilated(own, r)[yo, xo].mean())
        if f > opp: opp, opp_n = f, len(Lo)
    M["opp_inside_frac"] = opp; M["opp_n"] = opp_n
    # share of the owner mask not explained by this skeleton
    mask = fs.masks[own]; area = int(mask.sum()); M["mask_area_px"] = area
    if S is None or area == 0: M["unexplained_frac"] = 1.0
    else:
        D = max(1.0, C.UNEXPL_DIST_S * S * fs.sx); sk = np.zeros((fs.mh, fs.mw), np.uint8); pk = (kc >= C.SKEL_KP_CONF)
        for a, b in SKEL:
            if pk[a] and pk[b]: cv2.line(sk, (int(kp[a][0] * fs.sx), int(kp[a][1] * fs.sy)), (int(kp[b][0] * fs.sx), int(kp[b][1] * fs.sy)), 1, max(1, int(round(2 * D))))
        for i in range(17):
            if pk[i]: cv2.circle(sk, (int(kp[i][0] * fs.sx), int(kp[i][1] * fs.sy)), int(round(D)), 1, -1)
        M["unexplained_frac"] = float((mask & (sk == 0)).sum() / area)
    # bones
    out = 0; span = 0; nb = 0; dm = fs.dilated(own, r)
    for a, b in BONES:
        if kc[a] >= kp_conf and kc[b] >= kp_conf:
            nb += 1; ts = np.linspace(0, 1, C.BONE_SAMPLES); pts = kp[a][None] * (1 - ts[:, None]) + kp[b][None] * ts[:, None]; xs = np.clip(np.round(pts[:, 0] * fs.sx).astype(int), 0, fs.mw - 1); ys = np.clip(np.round(pts[:, 1] * fs.sy).astype(int), 0, fs.mh - 1)
            if dm[ys, xs].mean() < C.BONE_INSIDE_MIN: out += 1
            if {cls.get(a), cls.get(b)} == {"OWN_ONLY", "OTHER_ONLY"}: span += 1
    M.update(n_bones=nb, bones_outside=out, bones_span=span); return M
def decide(M, C, strict=1.0):
    """-> (state, reasons[]). strict < 1 tightens the contested / unexplained limits (used when the opponent's last position is unaccounted for)."""
    if M["owner"] is None: return "OWNERSHIP_UNCERTAIN", ["NO_OWNER_MASK" if M["n_landmarks"] >= C.MIN_LANDMARKS else "FEW_LANDMARKS"]
    mixed = []; unc = []
    if M["bones_span"] >= 1: mixed.append("BONE_SPANS_INSTANCES")
    if M["other_only_n"] >= C.MIX_OTHER_MIN_N and M["other_only_frac"] >= C.MIX_OTHER_MIN_FRAC: mixed.append("LANDMARKS_IN_OTHER_INSTANCE")
    if mixed: return "MIXED_BODY_SUSPECTED", mixed
    if M["other_only_n"] > 0: unc.append("SOME_LANDMARK_IN_OTHER_INSTANCE")
    if M["contested_frac"] > C.CONTESTED_MAX * strict: unc.append("CONTESTED_LANDMARKS")
    if M["opp_inside_frac"] >= C.OPP_INSIDE_FRAC_MAX and M["opp_n"] >= C.OPP_MIN_N: unc.append("OPPONENT_LANDMARKS_IN_MASK")
    if M["unexplained_frac"] > C.UNEXPL_MAX * strict: unc.append("MASK_NOT_EXPLAINED_BY_SKELETON")
    if M["own_only_frac"] < C.SINGLE_OWN_ONLY_MIN: unc.append("TOO_FEW_OWN_ONLY_LANDMARKS")
    if M["bones_outside"] > C.BONES_OUTSIDE_MAX: unc.append("BONES_LEAVE_MASK")
    return ("OWNERSHIP_UNCERTAIN", unc) if unc else ("SINGLE_BODY_SUPPORTED", [])
