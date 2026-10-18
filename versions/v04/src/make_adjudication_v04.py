"""Builds shuffled visual-adjudication sheets for the FROZEN V0.4 outputs (analysis only; modifies nothing else). Single reviewer, NOT independent. Tiles are drawn from the ORIGINAL video with
only the claimed box / skeleton / COM and an index number: no status text, order shuffled (seed 20261014) to reduce (not remove) the reviewer's knowledge of the stratum."""
import json, pickle, random, os, cv2, numpy as np, pandas as pd
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "v04", "scratch", "adj"); B = json.load(open(os.path.join(ROOT, "v02", "benchmark", "benchmark_v0.1_reference.json"))); meta = json.load(open(os.path.join(ROOT, "v04", "out", "run_meta_v04.json"))); SEEDS = set(meta["seed_frames"])
v1 = pd.read_csv(os.path.join(ROOT, "out", "tracking_full.csv")); v3all = pd.read_csv(os.path.join(ROOT, "v03", "out", "tracking_v03.csv")); v3 = v3all[v3all.target == "A"].set_index("frame")
t4 = pd.read_csv(os.path.join(ROOT, "v04", "out", "tracking_v04.csv")); A4 = t4[t4.target == "A"].set_index("frame"); B4 = t4[t4.target == "B"].set_index("frame"); cand = pd.read_csv(os.path.join(ROOT, "v04", "out", "candidates_v04.csv"))
lm = pd.read_csv(os.path.join(ROOT, "v04", "out", "tracking_v04_landmarks_raw.csv")); dets = pickle.load(open(os.path.join(ROOT, "out", "raw_detections.pkl"), "rb"))
def rng(rs): return {f for a, b in rs for f in range(a, b + 1)}
wrong = set(B["wrong_identity_frames"]["DEV_viewed"]) | set(B["wrong_identity_frames"]["AUD"])
KB = (wrong | set(B["pose_contamination_frames_viewed_DEV"]) | set(B["pose_distorted_frames_viewed_DEV"]) | rng(B["pose_contamination_ranges_inferred_DEV"]) | rng(B["wrong_identity_ranges_inferred_DEV"])) - SEEDS
EM = ("MEASURED", "PARTIAL"); R = random.Random(20261014); items = []
def add(stratum, frame, target, kind): items.append(dict(stratum=stratum, frame=int(frame), target=target, kind=kind))
s1 = sorted(f for f in A4.index if A4.loc[f].status in EM and f in KB); [add("S1_emit_in_known_bad", f, "A", "emission") for f in s1]
nov = [f for f in A4.index if A4.loc[f].status in EM and f not in KB and f not in SEEDS and v3.loc[f].status not in EM]
cn = cand.merge(A4.reset_index()[["frame", "selected_det_index", "status", "colour_R", "identity_state"]].rename(columns={"selected_det_index": "det"}), on=["frame", "det"]); necessary = set(cn[(cn.label == "A") & (cn.colour_R < 0.8) & cn.status.isin(EM)].frame)
s2a = sorted(f for f in nov if f in necessary); s2b = sorted(f for f in nov if f not in necessary)
[add("S2_new_vs_v03_embedding_necessary", f, "A", "emission") for f in R.sample(s2a, min(12, len(s2a)))]; [add("S2_new_vs_v03_other", f, "A", "emission") for f in R.sample(s2b, min(8, len(s2b)))]
s4 = sorted(f for f in B4.index if B4.loc[f].status in EM and f not in SEEDS); [add("S4_B_emission", f, "B", "emission") for f in R.sample(s4, min(9, len(s4)))]
s5 = sorted(f for f in A4.index if A4.loc[f].identity_state == "SUPPORTED_INDEPENDENT" and A4.loc[f].status == "UNRESOLVED" and A4.loc[f].unresolved_reason == "LOW_ANATOMY_MASS" and f not in SEEDS); [add("S5_identity_only_low_mass", f, "A", "identity_only") for f in R.sample(s5, min(9, len(s5)))]
s6 = sorted(f for f in A4.index if A4.loc[f].status == "UNRESOLVED" and A4.loc[f].unresolved_reason in ("IDENTITY_LOW_SCORE", "IDENTITY_CONTRA_CUE") and v1.set_index("frame").loc[f].status in EM and f not in KB and f not in SEEDS); [add("S6_v04_rejects_v01_tracked_not_bad", f, "A", "v01_box") for f in R.sample(s6, min(9, len(s6)))]
s7 = sorted(f for f in A4.index if v3.loc[f].status in EM and A4.loc[f].status not in EM and f not in KB and f not in SEEDS); [add("S7_v03_emitted_v04_not", f, "A", "v03_emission") for f in R.sample(s7, min(9, len(s7)))]
R.shuffle(items)
for i, it in enumerate(items): it["idx"] = i + 1
cap = cv2.VideoCapture(os.path.join(ROOT, "input.mp4")); COL = {"A": (0, 200, 0), "B": (255, 0, 255)}; BONES = [(5,6),(5,7),(7,9),(6,8),(8,10),(5,11),(6,12),(11,12),(11,13),(13,15),(12,14),(14,16)]
tiles = []
for it in items:
    f, X = it["frame"], it["target"]; cap.set(cv2.CAP_PROP_POS_FRAMES, f); ok, im = cap.read(); d = dets[f]; col = COL[X]; df = A4 if X == "A" else B4; r = df.loc[f]
    if it["kind"] in ("emission", "identity_only") and not np.isnan(r.selected_det_index):
        j = int(r.selected_det_index); x1, y1, x2, y2 = d["box"][j].astype(int); cv2.rectangle(im, (x1, y1), (x2, y2), col, 2)
        if it["kind"] == "emission":
            g = lm[(lm.frame == f) & (lm.target == X)]; kp = g[["x_pixel", "y_pixel"]].values; kc = g.keypoint_conf.values
            for a, b in BONES:
                if kc[a] >= 0.5 and kc[b] >= 0.5: cv2.line(im, tuple(kp[a].astype(int)), tuple(kp[b].astype(int)), col, 1)
            cx, cy = int(r.COM_x_pixel), int(r.COM_y_pixel); cv2.line(im, (cx-14, cy), (cx+14, cy), col, 2); cv2.line(im, (cx, cy-14), (cx, cy+14), col, 2)
    elif it["kind"] == "v01_box":
        q = v1.set_index("frame").loc[f]; cv2.rectangle(im, (int(q.selected_box_x1), int(q.selected_box_y1)), (int(q.selected_box_x2), int(q.selected_box_y2)), (0, 255, 255), 2)
    elif it["kind"] == "v03_emission":
        q = v3.loc[f]; j = int(q.selected_det_index); x1, y1, x2, y2 = d["box"][j].astype(int); cv2.rectangle(im, (x1, y1), (x2, y2), (255, 255, 255), 2); cx, cy = int(q.COM_x_pixel), int(q.COM_y_pixel); cv2.line(im, (cx-14, cy), (cx+14, cy), (255, 255, 255), 2); cv2.line(im, (cx, cy-14), (cx, cy+14), (255, 255, 255), 2)
        kp = d["kp"][j]; kc = d["kpc"][j]
        for a, b in BONES:
            if kc[a] >= 0.5 and kc[b] >= 0.5: cv2.line(im, tuple(kp[a].astype(int)), tuple(kp[b].astype(int)), (255, 255, 255), 1)
    cv2.rectangle(im, (0, 0), (150, 26), (0, 0, 0), -1); cv2.putText(im, f"#{it['idx']}", (4, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2); tiles.append(im)
while len(tiles) % 9: tiles.append(np.zeros_like(tiles[0]))
for s in range(0, len(tiles), 9): cv2.imwrite(os.path.join(OUT, f"sheet_{s//9+1:02d}.jpg"), np.vstack([np.hstack(tiles[s+r*3:s+r*3+3]) for r in range(3)]), [cv2.IMWRITE_JPEG_QUALITY, 88])
json.dump(dict(items=items, seed=20261014, note="idx -> stratum key; kept separate from the sheets", n_pop=dict(S1=len(s1), S2_necessary=len(s2a), S2_other=len(s2b), S4=len(s4), S5=len(s5), S6=len(s6), S7=len(s7))), open(os.path.join(OUT, "adjudication_key_v04.json"), "w"), indent=1)
print(len(items), "items;", len(tiles)//9, "sheets"); print({k: v for k, v in json.load(open(os.path.join(OUT, "adjudication_key_v04.json")))["n_pop"].items()})
