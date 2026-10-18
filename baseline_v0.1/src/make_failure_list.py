"""ANALYSIS ONLY. Builds out/FAILURE_AND_DO_NOT_TRUST_LIST.md from failure_frames_manual.csv + tracking_full.csv."""
import pandas as pd
m = pd.read_csv("out/failure_frames_manual.csv"); t = pd.read_csv("out/tracking_full.csv")
L = ["# V0.1 failure / ambiguity / do-not-trust list", "",
"Frame numbers are 0-based; time = frame/29.97 s. Evidence levels: 'viewed' = I looked at the frame(s) (single non-blinded reviewer, ~75 of 1,501 frames); 'inferred' = extent extrapolated from sampled frames; 'automatic' = tracker flag or geometry check only. **This list is a lower bound.** A frame absent from it is NOT known to be good.", "",
"## A. Ranges from manual audit + automatic flags (`failure_frames_manual.csv`)", "",
"| Frames | Time (s) | Category | Frames with status MEASURED/PARTIAL/PRED/UNRES | Evidence | Notes |", "|---|---|---|---|---|---|"]
for _, r in m.iterrows():
    s = t[(t.frame >= r.frame_start) & (t.frame <= r.frame_end)].status.value_counts()
    c = "/".join(str(int(s.get(k, 0))) for k in ["MEASURED", "PARTIAL", "PREDICTED", "UNRESOLVED"])
    L.append(f"| {r.frame_start}-{r.frame_end} | {r.time_start_s}-{r.time_end_s} | {r.category} | {c} | {r.evidence} | {r.notes} |")
L += ["", "## B. Do-not-trust summary by consequence", "",
"* **Identity wrong (output follows another person):** f386-404, 473-474, 615, 617-618, 628 (wrong-target frames confirmed or inferred: 25, of which 21 tracked).",
"* **Skeleton/COM merges several bodies yet labelled MEASURED/PARTIAL:** f245-279, f918-957, f1062-1214, f775.",
"* **Distorted pose from out-of-frame legs:** f440-444.",
"* **PREDICTED markers anchored to wrong/noisy observation:** f445-459, f474-488.",
"* **Cena visible but not tracked (identity cue failed):** 336 close-up frames (shorts out of view); f150, f650.",
"* **COM values on both sides of a camera cut are not comparable:** cuts at f80, 156, 203, 328, 708, 753, 763, 1070, 1144 (jumps up to 728 px).",
"* **Geometry warnings (limb length, coincident joints, landmarks outside box):** 30 frames, notably f936-942.",
"* **Cut detections not human-validated;** least certain f434, f1062, f1070.",
"* **Every PREDICTED frame (76)** is an extrapolation, not an observation.",
"* **Whole dataset:** no ground truth; tracking_confidence is uncalibrated; MEASURED means model-confident segments, not verified anatomy.", ""]
open("out/FAILURE_AND_DO_NOT_TRUST_LIST.md", "w").write("\n".join(L))
print(len(L))
