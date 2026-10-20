"""Anatomy V2 (C3) scene analysis over frozen V1 output. Calls ONLY frozen functions (integrity_v05.evaluate, ownership_v05.owner_for/metrics/FrameSeg, appearance.*) and the pure logic in c3_core.
Subtract-only: reads V1 rows; never writes a coordinate. Inputs: V1 rows, all pose detections per pose frame, cached instance masks, an optional quantised-frame provider. No identity names, no review keys, no correctness data."""
import os, sys, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ANAT_IMPL = os.path.join(HERE, "..", "..", "anatomical", "impl")
sys.path.insert(0, ANAT_IMPL); sys.path.insert(0, HERE)
import ownership_stage
own, integ, _i3, _cfgm = ownership_stage._mods()
import appearance as APP        # frozen V0.3/V0.5 appearance machinery (path set by ownership_stage._mods)
import c3_core as K
def load_cfg(): return ownership_stage.load_cfg()
class Scene:
    def __init__(self, rows, dets, seg, W, H, cfg=None, frame_q=None):
        self.cfg = cfg or load_cfg(); self.dets = dets; self.seg = seg or {}; self.W, self.H = W, H; self.frame_q = frame_q
        self.rows = rows; self.kpc_min = self.cfg.pose.KP_CONF
        self._fs = {}; self._an = {}; self._owner_of = {}; self._iv = {}; self._ictx = {}
        self.meas = [r for r in rows if r.get("pose_status") == "MEASURED" and r.get("det") is not None]
        self.by_tr = {}
        for r in self.meas: self.by_tr.setdefault(r["tracklet"], []).append(r)
        for t in self.by_tr: self.by_tr[t].sort(key=lambda r: r["frame"])
        self.by_fd = {(r["frame"], r["det"]): r for r in self.meas}
    # ---------- frozen-function wrappers ----------
    def fs(self, f):
        if f not in self._fs:
            sd = self.seg.get(f); self._fs[f] = own.FrameSeg(sd, self.W, self.H, self.cfg.seg.SEG_CONF_MIN) if sd is not None else None
        return self._fs[f]
    def owner_idx(self, f, o):
        k = (f, o)
        if k not in self._owner_of:
            fs = self.fs(f); d = self.dets[f]
            self._owner_of[k] = own.owner_for(fs, d["kp"][o], d["kpc"][o], self.kpc_min, self.cfg.ownership)[0] if fs is not None else None
        return self._owner_of[k]
    def analysis(self, row):
        """Contact predicate pieces for the detection of a row (identity-free, correctness-label-free)."""
        key = (row["frame"], row["det"])
        if key in self._an: return self._an[key]
        f, j = key; d = self.dets[f]; C = self.cfg; kp = np.asarray(d["kp"][j]); kc = np.asarray(d["kpc"][j])
        ev = integ.evaluate(j, d, self.kpc_min, C.integrity, None, {}, {"conflict": False})
        dup = {o["det"] for o in ev["overlap_info"] if o["kind"] == "duplicate_ignored"}
        others = [o for o in range(len(d["conf"])) if o != j and o not in dup]
        coloc = {o["det"] for o in ev["overlap_info"] if o["kind"] in ("overlap", "shared_joints")}
        res = dict(overlap_a=bool(ev["overlap_context"]), shared=("SHARED_JOINT_CONFLICT" in ev["reasons"]), S=ev["S"], others=others, coloc=coloc, touching=[], unanchored_masks=[],
                   M=None, owner=None, cannot_eval=False, contested=False, other_only=False, opp_inside=False, mask_touch=False)
        fs = self.fs(f)
        if fs is None: res["cannot_eval"] = True
        else:
            M = own.metrics(fs, kp, kc, [(d["kp"][o], d["kpc"][o]) for o in others], ev["S"], self.kpc_min, C.ownership); res["M"] = M; res["owner"] = M["owner"]
            if M["owner"] is None: res["cannot_eval"] = True
            else:
                r = own.tol_px(C.ownership, fs); dm = fs.dilated(M["owner"], r)
                for m in range(fs.n()):
                    if m == M["owner"] or fs.iou(M["owner"], m) >= C.ownership.SEG_DUP_IOU: continue
                    if (dm & fs.masks[m]).any(): res["touching"].append(m)
                res["mask_touch"] = bool(res["touching"])
                om = {o: self.owner_idx(f, o) for o in others}
                for o in others:
                    if om[o] is not None and om[o] in res["touching"]: coloc.add(o)
                    Lo = [i for i in own.LMS if d["kpc"][o][i] >= self.kpc_min]
                    if len(Lo) >= C.ownership.OPP_MIN_N:
                        xo, yo = fs.pts(np.asarray(d["kp"][o]), Lo)
                        if float(dm[yo, xo].mean()) > 0: coloc.add(o)
                known = {m for m in om.values() if m is not None}
                res["unanchored_masks"] = [m for m in res["touching"] if m not in known]
                res["contested"] = M["contested_n"] > 0; res["other_only"] = M["other_only_n"] > 0; res["opp_inside"] = M["opp_inside_frac"] > 0
        res["contact"] = bool(res["overlap_a"] or res["shared"] or res["cannot_eval"] or res["mask_touch"] or res["contested"] or res["other_only"] or res["opp_inside"])
        res["coloc"] = coloc; self._an[key] = res; return res
    # ---------- intervals ----------
    def intervals(self, tid):
        if tid in self._iv: return self._iv[tid]
        rs = self.by_tr.get(tid, []); st = K.STRUCT["STRIDE"]; runs = []; cur = []
        for i, r in enumerate(rs):
            if self.analysis(r)["contact"]:
                if cur and cur[-1] == i - 1 and r["frame"] - rs[i - 1]["frame"] <= st: cur.append(i)
                else:
                    if cur: runs.append(cur)
                    cur = [i]
        if cur: runs.append(cur)
        ext = []
        for run in runs:
            a, b = run[0], run[-1]
            if a > 0 and rs[a]["frame"] - rs[a - 1]["frame"] <= st: a -= K.STRUCT["EXT_FRAMES"]
            if b < len(rs) - 1 and rs[b + 1]["frame"] - rs[b]["frame"] <= st: b += K.STRUCT["EXT_FRAMES"]
            ext.append([a, b, rs[run[0]]["frame"]])
        ivs = []
        for a, b, fc in ext:
            if ivs and a <= ivs[-1]["end_idx"] + 1: ivs[-1]["end_idx"] = max(ivs[-1]["end_idx"], b)
            else: ivs.append(dict(tracklet=tid, start_idx=a, end_idx=b, first_contact_frame=fc))
        for iv in ivs: iv["start_frame"] = rs[iv["start_idx"]]["frame"]; iv["end_frame"] = rs[iv["end_idx"]]["frame"]
        self._iv[tid] = ivs; return ivs
    def interval_of(self, row):
        for iv in self.intervals(row["tracklet"]):
            if iv["start_frame"] <= row["frame"] <= iv["end_frame"]: return iv
        return None
    def interval_spans(self):
        return {t: [(iv["start_frame"], iv["end_frame"]) for iv in self.intervals(t)] for t in self.by_tr}
    # ---------- views and anchors ----------
    def _enough_joints(self, row):
        kc = np.asarray(row["kpc"]); obs = kc >= self.kpc_min; I = self.cfg.integrity
        return int(sum(obs[i] for i in (5, 6, 11, 12))) >= I.REL_MIN_TORSO_JOINTS and int(obs.sum()) >= I.REL_MIN_JOINTS
    def _desc(self, row):
        if self.frame_q is None: return None
        q = self.frame_q(row["frame"])
        if q is None: return None
        return APP.descriptors(q, np.asarray(row["kp"]), np.asarray(row["kpc"]), row["box"], self.cfg.appearance)
    def clean_views(self, tid, lo, hi):
        """Eligible anchor views of tracklet tid with lo < frame < hi, sorted by frame DESCENDING."""
        out = []
        for r in self.by_tr.get(tid, []):
            if not (lo < r["frame"] < hi): continue
            if self.analysis(r)["contact"] or r["ownership_state"] != "SINGLE_BODY_SUPPORTED" or not self._enough_joints(r): continue
            s = K.view_state(np.asarray(r["kp"]), np.asarray(r["kpc"]), self.kpc_min)
            if s is None: continue
            if self.frame_q is not None:
                dsc = self._desc(r)
                if dsc is None or not any(k != "whole" for k in dsc): continue
            out.append(dict(row=r, frame=r["frame"], state=s))
        out.sort(key=lambda v: -v["frame"]); return out
    def anchor_for(self, tid, iv_cur):
        prev_end = max([iv["end_frame"] for iv in self.intervals(tid) if iv["start_frame"] < iv_cur["start_frame"]] or [-1])
        return K.pick_anchor_pair(self.clean_views(tid, prev_end, iv_cur["start_frame"]))
    # ---------- per-interval context (cast, anchors, appearance models) ----------
    def interval_ctx(self, iv):
        key = (iv["tracklet"], iv["start_frame"])
        if key in self._ictx: return self._ictx[key]
        ctx = dict(fail=None, cast=[iv["tracklet"]], anchors={}, models=None, detail={})
        rows = self.by_tr[iv["tracklet"]]; f1 = iv["first_contact_frame"]
        r1 = next(r for r in rows if r["frame"] == f1); a1 = self.analysis(r1)
        if a1["cannot_eval"]: ctx["fail"] = "CANNOT_EVALUATE"
        elif a1["unanchored_masks"]: ctx["fail"] = "UNANCHORED_PARTICIPANT"
        else:
            riv = []
            for o in sorted(a1["coloc"]):
                rr = self.by_fd.get((f1, o))
                if rr is None: ctx["fail"] = "UNANCHORED_PARTICIPANT"; break
                if rr["tracklet"] != iv["tracklet"] and rr["tracklet"] not in riv: riv.append(rr["tracklet"])
            if ctx["fail"] is None:
                if not riv: ctx["fail"] = "NO_RIVAL_ANCHOR"
                else:
                    ctx["cast"] = [iv["tracklet"]] + sorted(riv)
                    if len(ctx["cast"]) > K.STRUCT["MAX_CAST"]: ctx["fail"] = "CAST_TOO_LARGE"
        if ctx["fail"] is None:
            for t in ctx["cast"]:
                pair, det = self.anchor_for(t, iv); ctx["anchors"][t] = pair; ctx["detail"][t] = det
                if pair is None and ctx["fail"] is None: ctx["fail"] = "NO_INDEPENDENT_ANCHOR_VIEWS"
        if ctx["fail"] is None and self.frame_q is not None:
            A = self.cfg.appearance; ms = []
            for t in ctx["cast"][1:]:
                M = APP.Models(A)
                for tag, tt in (("A", ctx["cast"][0]), ("B", t)):
                    for v in ctx["anchors"][tt]:
                        r = v["row"]; M.add(tag, self.frame_q(r["frame"]), np.asarray(r["kp"]), np.asarray(r["kpc"]), r["box"])
                M.finalize(); ms.append(M)
            ctx["models"] = ms
        self._ictx[key] = ctx; return ctx
    # ---------- per-row decision ----------
    def _votes(self, row, M, own_tag, other_tag, kp=None, kc=None, box=None):
        q = self.frame_q(row["frame"]) if self.frame_q is not None else None
        if q is None: return None
        A = self.cfg.appearance; kp = np.asarray(row["kp"]) if kp is None else kp; kc = np.asarray(row["kpc"]) if kc is None else kc; box = row["box"] if box is None else box
        desc = APP.descriptors(q, kp, kc, box, A); _, dists = APP.appearance_cues(desc, M, A)
        return APP.region_votes(desc, dists, M, own_tag, other_tag, A)
    def decide_row(self, row, iv):
        """-> dict(status SUPPORTED_UNIQUE|WITHHELD_C3, reason, margin, ...). Only called for V1 ASSIGNED rows inside an interval."""
        ctx = self.interval_ctx(iv); out = dict(status="WITHHELD_C3", reason="", margin=None, landmarks=[], cast=len(ctx["cast"]))
        def w(reason, **kw): out.update(reason=reason, **kw); return out
        if ctx["fail"]: return w(ctx["fail"])
        a = self.analysis(row)
        if a["cannot_eval"]: return w("CANNOT_EVALUATE")
        if a["unanchored_masks"]: return w("UNANCHORED_PARTICIPANT")
        f = row["frame"]; d = self.dets[f]; C = self.cfg; kp = np.asarray(row["kp"]); kc = np.asarray(row["kpc"]); cast = ctx["cast"]; nr = len(cast) - 1
        rival_of = {}
        for o in sorted(a["coloc"]):
            rr = self.by_fd.get((f, o))
            if rr is None or rr["tracklet"] not in cast or rr["tracklet"] == cast[0]: return w("UNANCHORED_PARTICIPANT")
            rival_of[o] = cast.index(rr["tracklet"]) - 1
        L = [i for i in own.LMS if kc[i] >= self.kpc_min]
        if len(L) < C.ownership.MIN_LANDMARKS: return w("FEW_LANDMARKS")
        M = a["M"]
        # mask informativeness: distinct owner masks for every co-located detection, no opponent landmark inside the owner mask, unexplained share within the frozen limit
        fs = self.fs(f); om = [self.owner_idx(f, o) for o in sorted(a["coloc"])]; ids = [a["owner"]] + om
        distinct = all(m is not None for m in ids) and len(set(ids)) == len(ids) and all(fs.iou(ids[x], ids[y]) < C.ownership.SEG_DUP_IOU for x in range(len(ids)) for y in range(x + 1, len(ids)))
        informative = bool(distinct and M["opp_inside_frac"] == 0 and M["unexplained_frac"] <= C.ownership.UNEXPL_MAX)
        # double claim (frozen shared-joint rule, per landmark)
        bx = row["box"]; diag = math.hypot(bx[2] - bx[0], bx[3] - bx[1]); dbl = set()
        for o in a["others"]:
            for j in L:
                if d["kpc"][o][j] >= self.kpc_min and float(np.linalg.norm(kp[j] - np.asarray(d["kp"][o][j]))) < C.integrity.SHARE_DIST_FRAC * diag: dbl.add(j)
        votes = None
        if ctx["models"] is not None:
            votes = [self._votes(row, ctx["models"][k], "A", "B") for k in range(nr)]
            if any(v is None for v in votes): votes = None
            else:
                for o, k in rival_of.items():
                    vo = self._votes(row, ctx["models"][k], "B", "A", kp=np.asarray(d["kp"][o]), kc=np.asarray(d["kpc"][o]), box=d["box"][o])
                    if vo is not None and any(v == -1 for v in vo.values()): return w("RIVAL_APPEARANCE_CONFLICT")
        ev = K.landmark_evidence(L, informative, M["cls"], votes, dbl, nr); dec = K.decide_unique(L, ev, nr)
        out.update(informative_masks=informative, appearance_available=votes is not None, n_landmarks=len(L))
        if dec["unique"]: out.update(status="SUPPORTED_UNIQUE", reason="", margin=dec["margin"]); return out
        return w(dec["reason"], landmarks=dec["landmarks"])
