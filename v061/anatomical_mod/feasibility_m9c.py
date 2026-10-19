#!/usr/bin/env python3
"""M9C feasibility COUNT only (no sampling, no images, no verdicts): how many released-PARTIAL frames survive the burned-frame and +-30-source-frame exclusions, per clip, and how many can be picked >=30 frames apart (greedy count)."""
import csv, json, os, pickle, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__)); V = os.path.dirname(HERE); sys.path[:0] = [os.path.join(V, "anatomical", "impl"), os.path.join(HERE, "impl")]
import ownership_stage, partial_release as PR
P = "/home/claude/proj/v061_anat_private"; FZ = "/home/claude/proj/v06_phase1/frozen"
CLIPS = ["b1_orton_rollins_wm31", "b2_batch2_clip_condensed", "b2_videoplayback_2", "b2_videoplayback_5"]
rev = collections.defaultdict(set)
for nm in ("M9_HIDDEN_KEY.csv", "M9B_HIDDEN_KEY.csv"):
    for r in csv.DictReader(open(os.path.join(P, nm), newline="")): rev[r["clip"]].add(int(r["frame"]))
own = ownership_stage._mods()[0]; cfg = ownership_stage.load_cfg(); out = {}
for c in CLIPS:
    dets = pickle.load(open(os.path.join(FZ, "dets", f"dets_{c}.pkl"), "rb")); seg = pickle.load(open(os.path.join(P, f"SEG_{c}.pkl"), "rb")); D = pickle.load(open(os.path.join(P, f"ROWS_{c}.pkl"), "rb")); fsc = {}; rel = []
    for r in D["rows"]:
        if not PR.eligible(r) or r.get("own_summary") is None: continue
        f = r["frame"]
        if f not in fsc: fsc[f] = own.FrameSeg(seg[f], D["W"], D["H"], cfg.seg.SEG_CONF_MIN) if f in seg else None
        cls = PR.landmark_classes(r["det"], dets[f], fsc[f], cfg)[0]
        if PR.apply_release(r, cls)["record_class"].startswith("RELEASED_PARTIAL"): rel.append((f, r["shot"], r["tracklet"]))
    keep = [x for x in rel if all(abs(x[0] - g) > 30 for g in rev[c])]; frames = sorted({x[0] for x in keep})
    def greedy(fr, gap):
        sel = []
        for f in fr:
            if not sel or f - sel[-1] >= gap: sel.append(f)
        return len(sel)
    alt = {}
    for rad in (30, 15, 0):
        fr = sorted({x[0] for x in rel if all(abs(x[0] - g) > rad for g in rev[c])}); alt[f"excl_radius_{rad}"] = dict(unique_frames=len(fr), greedy_gap30=greedy(fr, 30), greedy_gap15=greedy(fr, 15), greedy_gap0=len(fr))
    out[c] = dict(released=len(rel), unique_frames_released=len({x[0] for x in rel}), after_exclusion_rows=len(keep), after_exclusion_unique_frames=len(frames), max_greedy_30_apart=greedy(frames, 30), shots=len({x[1] for x in keep}), alternatives=alt)
tot = {k: sum(v[k] for v in out.values()) for k in ("released", "after_exclusion_rows", "after_exclusion_unique_frames", "max_greedy_30_apart")}
tot["alternatives"] = {a: {k: sum(v["alternatives"][a][k] for v in out.values()) for k in ("unique_frames", "greedy_gap30", "greedy_gap15", "greedy_gap0")} for a in ("excl_radius_30", "excl_radius_15", "excl_radius_0")}
json.dump(dict(per_clip=out, totals=tot, label="COUNTS ONLY; no sampling performed"), open(sys.argv[1], "w"), indent=1, sort_keys=True); print(json.dumps(out, indent=0)); print(tot)
