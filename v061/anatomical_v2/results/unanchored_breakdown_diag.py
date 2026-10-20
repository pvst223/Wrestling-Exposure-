"""POST-RUN COUNTS-ONLY DIAGNOSTIC (not part of the frozen implementation manifest; changes no rule or constant). Breaks down the C3 cast/anchor failures on the burned clips by sub-cause.
usage: python unanchored_breakdown_diag.py <frozen_dir> <priv_dir> <out.json>"""
import sys, os, pickle, json, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, "..", "impl")]
from c3_scene import Scene
import c3_core as K
fr, pv, out = sys.argv[1:4]; tot = collections.Counter(); per = {}
for clip in ["b1_orton_rollins_wm31", "b2_batch2_clip_condensed", "b2_videoplayback_2", "b2_videoplayback_5"]:
    d = pickle.load(open(f"{pv}/ROWS_{clip}.pkl", "rb")); rows = d["rows"]; dets = pickle.load(open(f"{fr}/dets/dets_{clip}.pkl", "rb")); seg = pickle.load(open(f"{pv}/SEG_{clip}.pkl", "rb")); sc = Scene(rows, dets, seg, d["W"], d["H"]); c = collections.Counter()
    for r in rows:
        if r["record_class"] not in K.ASSIGNED: continue
        iv = sc.interval_of(r)
        if iv is None: continue
        ctx = sc.interval_ctx(iv)
        if ctx["fail"] == "UNANCHORED_PARTICIPANT":
            a1 = sc.analysis(next(x for x in sc.by_tr[iv["tracklet"]] if x["frame"] == iv["first_contact_frame"])); f1 = iv["first_contact_frame"]
            m = bool(a1["unanchored_masks"]); n = any(sc.by_fd.get((f1, o)) is None for o in a1["coloc"])
            c["unanchored:" + ("both" if m and n else "mask_without_detection" if m else "colocated_detection_without_tracklet_row")] += 1
        elif ctx["fail"]: c[ctx["fail"]] += 1
        else: c["cast_and_anchors_ok_row_level"] += 1
    per[clip] = dict(c); tot.update(c)
json.dump(dict(label="post-run counts-only diagnostic on burned clips; ASSIGNED in-interval rows by interval-level failure sub-cause; no correctness labels; no rule/constant changed", pooled=dict(tot), per_clip=per), open(out, "w"), indent=1, sort_keys=True); print(dict(tot))
