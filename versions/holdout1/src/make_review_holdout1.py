"""POST-FREEZE analysis tool for Holdout #1 (not decision code). Builds shuffled STATUS-BLIND contact sheets for single-reviewer visual judgment. Seed 20261017.
Tiles show only the frame (original 720p), the tracker's assigned detection box+skeleton (drawn whether or not COM was emitted), the target letter and an index. No status, ownership state, scores or reasons.
Strata (sample rules fixed here, before the tracker was run): R1 random A emissions (up to 15 MEASURED + 15 PARTIAL), R2 random B emissions (up to 10), R3 SYSTEMATIC: every 15th frame (frame%15==0) where the tracker assigned a
detection to A with identity SUPPORTED_INDEPENDENT, regardless of whether COM was emitted (A), and every 30th frame for B; R4 PLAIN frames every 30th frame (no overlay) for coverage ground truth (is the wrestler clearly visible?).
Seed frames excluded from R1-R3. Items shared between strata appear once."""
import json, os, sys, random, cv2, numpy as np, pandas as pd, pickle
H = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); OUT = os.path.join(H, "out"); SC = os.path.join(H, "review"); os.makedirs(SC, exist_ok=True)
tr = pd.read_csv(os.path.join(OUT, "tracking_v05.csv")); dets = pickle.load(open(os.path.join(H, "cache", "raw_detections_holdout1.pkl"), "rb"))
SEEDS = {s["frame"] for s in json.load(open(os.path.join(H, "config", "seeds_holdout1.json")))["seeds"]}; EM = ["MEASURED", "PARTIAL"]; rnd = random.Random(20261017)
A = tr[tr.target == "A"]; B = tr[tr.target == "B"]; items = {}
def add(f, t, strat, plain=False):
    k = (int(f), t, plain); items.setdefault(k, dict(frame=int(f), target=t, plain=plain, strata=[])); items[k]["strata"].append(strat)
for st_, n in (("MEASURED", 15), ("PARTIAL", 15)):
    pool = sorted(set(A[A.status == st_].frame) - SEEDS)
    for f in rnd.sample(pool, min(n, len(pool))): add(f, "A", "R1_A_emission")
pool = sorted(set(B[B.status.isin(EM)].frame) - SEEDS)
for f in rnd.sample(pool, min(10, len(pool))): add(f, "B", "R2_B_emission")
def assigned(df, f):
    r = df[df.frame == f]
    if r.empty: return False
    r = r.iloc[0]; return pd.notna(r.selected_det_index) and int(r.selected_det_index) >= 0 and r.identity_state == "SUPPORTED_INDEPENDENT"
for f in range(0, len(tr.frame.unique()), 15):
    if f not in SEEDS and assigned(A, f): add(f, "A", "R3_A_systematic")
for f in range(0, len(tr.frame.unique()), 30):
    if f not in SEEDS and assigned(B, f): add(f, "B", "R3_B_systematic")
for f in range(0, len(tr.frame.unique()), 30): add(f, "-", "R4_plain", plain=True)
L = list(items.values()); rnd.shuffle(L)
cap = cv2.VideoCapture(os.path.join(H, "raw", "hardy_original_720p.mp4")); tiles = []
for k, it in enumerate(L, 1):
    it["idx"] = k; cap.set(cv2.CAP_PROP_POS_FRAMES, it["frame"]); ok, im = cap.read()
    if not it["plain"]:
        df = A if it["target"] == "A" else B; r = df[df.frame == it["frame"]].iloc[0]; j = int(r.selected_det_index); d = dets[it["frame"]]; kp, kc = d["kp"][j] * 2, d["kpc"][j]; b = (d["box"][j] * 2).astype(int)
        col = (0, 220, 0) if it["target"] == "A" else (255, 0, 255); cv2.rectangle(im, (b[0], b[1]), (b[2], b[3]), col, 2)
        for a_, b_ in [(5,6),(5,7),(7,9),(6,8),(8,10),(5,11),(6,12),(11,12),(11,13),(13,15),(12,14),(14,16)]:
            if kc[a_] >= 0.5 and kc[b_] >= 0.5: cv2.line(im, tuple(kp[a_].astype(int)), tuple(kp[b_].astype(int)), col, 3)
    big = cv2.resize(im, (800, 450)); cv2.putText(big, f"#{k} " + ("plain" if it["plain"] else f"target {it['target']}"), (8, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2); tiles.append(big)
PER = 6
for s in range(0, len(tiles), PER):
    t = tiles[s:s + PER]; t += [np.zeros_like(tiles[0])] * (PER - len(t)); cv2.imwrite(os.path.join(SC, f"sheet_{s // PER + 1:02d}.jpg"), np.vstack([np.hstack(t[i:i + 2]) for i in range(0, PER, 2)]), [cv2.IMWRITE_JPEG_QUALITY, 90])
json.dump(dict(seed=20261017, n=len(L), items=L), open(os.path.join(SC, "review_key_holdout1.json"), "w"), indent=1); print(len(L), "items,", (len(L) + PER - 1) // PER, "sheets")
