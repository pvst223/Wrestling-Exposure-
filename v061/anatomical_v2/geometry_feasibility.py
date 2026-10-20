#!/usr/bin/env python3
"""Geometry-only feasibility COUNTS for the implemented Anatomy V2 (C3) candidate on the four burned development clips. No correctness labels, review keys, owner notes or contact flags are read; the output is aggregate counts only and cannot change any rule or constant.
usage: python geometry_feasibility.py --frozen <v06 frozen dir (dets/, tracklets/, norm/)> --priv <private dir with V1 ROWS_<clip>.pkl and SEG_<clip>.pkl> --clips c1 c2 ... --out results/GEOMETRY_FEASIBILITY_BURNED_V1.json"""
import argparse, os, sys, json, pickle, hashlib, collections, statistics
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, "impl")]
from c3_scene import Scene, APP, load_cfg
from c3_apply import apply_c3
import c3_core as K
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
def quantised_frames(video, frames, A):
    want = set(int(f) for f in frames); out = {}; cap = cv2.VideoCapture(video); i = 0
    while True:
        ok, fr = cap.read()
        if not ok: break
        if i in want: out[i] = APP.quantize(fr, A)
        i += 1
    cap.release(); return out
def summ(xs):
    return None if not xs else dict(n=len(xs), min=min(xs), median=statistics.median(xs), max=max(xs))
def one_clip(frozen, priv, clip):
    d = pickle.load(open(os.path.join(priv, f"ROWS_{clip}.pkl"), "rb")); rows, cuts, W, H = d["rows"], d["cuts"], d["W"], d["H"]
    dets = pickle.load(open(os.path.join(frozen, "dets", f"dets_{clip}.pkl"), "rb")); seg = pickle.load(open(os.path.join(priv, f"SEG_{clip}.pkl"), "rb"))
    cfg = load_cfg(); qs = quantised_frames(os.path.join(frozen, "norm", f"{clip}.mp4"), dets.keys(), cfg.appearance)
    sc = Scene(rows, dets, seg, W, H, cfg=cfg, frame_q=lambda f: qs.get(f)); res = apply_c3(sc, rows, cuts); st = res["stats"]
    assigned_tr = sorted({r["tracklet"] for r in rows if r["record_class"] in K.ASSIGNED})
    comp = collections.Counter(); ivn = 0; fail = collections.Counter(); cast = collections.Counter(); detail = collections.Counter(); pooled = 0; full = 0; age = []; gate_any = 0; gate_n = 0; types = collections.Counter()
    for t in assigned_tr:
        for r in sc.by_tr.get(t, []):
            if r["record_class"] not in K.ASSIGNED: continue
            a = sc.analysis(r)
            for k in ("overlap_a", "shared", "cannot_eval", "mask_touch", "contested", "other_only", "opp_inside"): comp[k] += bool(a[k])
            comp["contact_any"] += bool(a["contact"])
        for iv in sc.intervals(t):
            if not any(r["record_class"] in K.ASSIGNED and iv["start_frame"] <= r["frame"] <= iv["end_frame"] for r in sc.by_tr[t]): continue
            ivn += 1; ctx = sc.interval_ctx(iv); fail[ctx["fail"] or "CAST_AND_ANCHORS_OK"] += 1
            if len(ctx["cast"]) > 0 and ctx["detail"]: cast[len(ctx["cast"])] += 1
            for tt, dd in ctx["detail"].items(): detail[dd] += 1
            if ctx["detail"] and all(v != "NO_CLEAN_VIEW" for v in ctx["detail"].values()) and any(v == "OK" for v in ctx["detail"].values()): pooled += 1
            if ctx["fail"] is None and ctx["anchors"]:
                full += 1; age.append(iv["start_frame"] - ctx["anchors"][t][0]["frame"])
                if ctx["models"] is not None:
                    gate_n += 1; ok = all(any(g >= cfg.appearance.D_SEP_MIN for g in M.gap.values()) for M in ctx["models"]); gate_any += ok
                    for M in ctx["models"]:
                        for ty, g in M.gap.items(): types[ty] += g >= cfg.appearance.D_SEP_MIN
    n_in = st["in_interval"]; Y = (st["supported"] / n_in) if n_in else None
    return dict(clip=clip, n_rows=st["n_rows"], n_assigned_v1=st["n_assigned_v1"], tracklets_with_assigned=len(assigned_tr), assigned_contact_components=dict(comp), intervals_with_assigned_rows=ivn,
                interval_outcome=dict(fail), cast_size_when_formed={str(k): v for k, v in sorted(cast.items())}, anchor_detail_per_body=dict(detail), intervals_pooled_minimum_pair_reported_only=pooled,
                intervals_with_full_per_body_anchors=full, anchor_age_source_frames_target=summ(age), appearance_gate_intervals_evaluated=gate_n, appearance_gate_any_usable_type_for_every_rival=gate_any,
                appearance_types_usable_counts=dict(types), in_interval_assigned_rows=n_in, pass_through_assigned_rows=st["pass_through"], c3_retained=st["supported"], c3_withheld=st["withheld"], withhold_reasons=st["reasons"],
                margin_distribution=st["margins"], c0_withheld_assigned_rows=st["c0_withheld"], partition=st["partition"], yield_Y=Y,
                carried_rows_v1=sum(1 for r in d["src"] if r.get("pose_status") == "CARRIED"), carried_rows_v2=sum(1 for r in res["src"] if r.get("pose_status") == "CARRIED"))
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--frozen", required=True); ap.add_argument("--priv", required=True); ap.add_argument("--clips", nargs="+", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
    per = [one_clip(a.frozen, a.priv, c) for c in a.clips]
    tot = collections.Counter(); part = collections.Counter(); reasons = collections.Counter()
    for p in per:
        for k in ("n_assigned_v1", "in_interval_assigned_rows", "pass_through_assigned_rows", "c3_retained", "c3_withheld", "c0_withheld_assigned_rows", "intervals_with_assigned_rows", "intervals_with_full_per_body_anchors", "intervals_pooled_minimum_pair_reported_only"): tot[k] += p[k]
        part.update(p["partition"]); reasons.update(p["withhold_reasons"])
    pooled = dict(tot); pooled["partition"] = dict(part); pooled["withhold_reasons"] = dict(reasons); pooled["yield_Y"] = (tot["c3_retained"] / tot["in_interval_assigned_rows"]) if tot["in_interval_assigned_rows"] else None
    out = dict(label="GEOMETRY-ONLY FEASIBILITY COUNTS, burned development clips, counts only; no correctness labels/review keys/owner notes/contact flags read; cannot change any rule or constant; NOT an evaluation",
               pooled=pooled, per_clip=per, inputs_sha256={c: dict(rows=sha(os.path.join(a.priv, f"ROWS_{c}.pkl")), seg=sha(os.path.join(a.priv, f"SEG_{c}.pkl")), dets=sha(os.path.join(a.frozen, "dets", f"dets_{c}.pkl")), video=sha(os.path.join(a.frozen, "norm", f"{c}.mp4"))) for c in a.clips})
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); json.dump(out, open(a.out, "w"), indent=1, sort_keys=True, default=str); print(json.dumps(pooled, sort_keys=True, default=str)); print("out sha256", sha(a.out))
if __name__ == "__main__": main()
