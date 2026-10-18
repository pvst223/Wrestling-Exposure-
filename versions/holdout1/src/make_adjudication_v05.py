"""POST-FREEZE analysis tool (not decision code). Builds shuffled, status-blind contact sheets for single-reviewer visual adjudication of V0.5 outputs. Seed 20261014.
Strata: E1 V0.5 A emissions inside known/inferred-bad frames (all); E2 random A emissions outside known-bad (15 MEASURED + 15 PARTIAL); E3 random B emissions (10);
E4 frames V0.4 emitted but V0.5 withheld, outside known-bad (12; the V0.4 skeleton is drawn). Tiles show only the frame, the box and skeleton, the target letter and an index."""
import json, os, sys, pickle, random, cv2, numpy as np, pandas as pd
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "v05", "out"); SC = os.path.join(ROOT, "v05", "scratch", "adj"); os.makedirs(SC, exist_ok=True)
v5 = pd.read_csv(os.path.join(OUT, "tracking_v05.csv")); v4 = pd.read_csv(os.path.join(ROOT, "v04", "out", "tracking_v04.csv")); dets = pickle.load(open(os.path.join(ROOT, "out", "raw_detections.pkl"), "rb"))
cm = json.load(open(os.path.join(OUT, "comparison_metrics_v05.json"))); SEEDS = set(cm["seed_frames_excluded"]); KB = set(cm["known_bad"]["v05_emitting_frames_in_known_bad"])
B = json.load(open(os.path.join(ROOT, "v02", "benchmark", "benchmark_v0.1_reference.json")))
def rng(rs): return {f for a, b in rs for f in range(a, b + 1)}
KBALL = set(B["wrong_identity_frames"]["DEV_viewed"]) | set(B["wrong_identity_frames"]["AUD"]) | set(B["pose_contamination_frames_viewed_DEV"]) | set(B["pose_distorted_frames_viewed_DEV"]) | rng(B["pose_contamination_ranges_inferred_DEV"]) | rng(B["wrong_identity_ranges_inferred_DEV"])
rnd = random.Random(20261014); EM = ["MEASURED", "PARTIAL"]
A5 = v5[v5.target == "A"]; B5 = v5[v5.target == "B"]; A4 = v4[v4.target == "A"]
items = []
for f in sorted(set(A5[A5.status.isin(EM)].frame) & KBALL): items.append(dict(stratum="E1_v05_emit_in_known_bad", frame=int(f), target="A", src="v05"))
for st_, n in (("MEASURED", 15), ("PARTIAL", 15)):
    pool = sorted(set(A5[A5.status == st_].frame) - KBALL - SEEDS); items += [dict(stratum="E2_v05_A_emission", frame=int(f), target="A", src="v05") for f in rnd.sample(pool, n)]
pool = sorted(set(B5[B5.status.isin(EM)].frame) - SEEDS); items += [dict(stratum="E3_v05_B_emission", frame=int(f), target="B", src="v05") for f in rnd.sample(pool, 10)]
pool = sorted(set(A4[A4.status.isin(EM)].frame) - set(A5[A5.status.isin(EM)].frame) - KBALL - SEEDS); items += [dict(stratum="E4_v04_emitted_v05_withheld", frame=int(f), target="A", src="v04") for f in rnd.sample(pool, 12)]
rnd.shuffle(items)
cap = cv2.VideoCapture(os.path.join(ROOT, "input.mp4")); tiles = []
for k, it in enumerate(items, 1):
    it["idx"] = k; cap.set(cv2.CAP_PROP_POS_FRAMES, it["frame"]); ok, im = cap.read(); df = v5 if it["src"] == "v05" else v4; r = df[(df.frame == it["frame"]) & (df.target == it["target"])].iloc[0]
    j = int(r.selected_det_index); d = dets[it["frame"]]; kp, kc = d["kp"][j], d["kpc"][j]; b = d["box"][j].astype(int); col = (0, 220, 0) if it["target"] == "A" else (255, 0, 255)
    cv2.rectangle(im, (b[0], b[1]), (b[2], b[3]), col, 1)
    for a_, b_ in [(5,6),(5,7),(7,9),(6,8),(8,10),(5,11),(6,12),(11,12),(11,13),(13,15),(12,14),(14,16)]:
        if kc[a_] >= 0.5 and kc[b_] >= 0.5: cv2.line(im, tuple(kp[a_].astype(int)), tuple(kp[b_].astype(int)), col, 2)
    big = cv2.resize(im, (800, 450)); cv2.putText(big, f"#{k} target {it['target']}", (8, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2); tiles.append(big)
PER = 6
for s in range(0, len(tiles), PER):
    t = tiles[s:s + PER]; t += [np.zeros_like(tiles[0])] * (PER - len(t)); cv2.imwrite(os.path.join(SC, f"sheet_{s // PER + 1:02d}.jpg"), np.vstack([np.hstack(t[i:i + 2]) for i in range(0, PER, 2)]), [cv2.IMWRITE_JPEG_QUALITY, 90])
json.dump(dict(seed=20261014, n=len(items), items=items), open(os.path.join(SC, "adjudication_key_v05.json"), "w"), indent=1); print(len(items), "items,", (len(items) + PER - 1) // PER, "sheets")
