"""ANALYSIS ONLY (not part of the measurement pipeline). Reads the frozen V0.1 outputs and builds:
  out/tracking_full.csv                       superset of tracking.csv (original columns unchanged, extra columns appended)
  out/frames_without_landmarks_accounting.csv per-frame reason for the frames with no selected-Cena landmarks
  out/accounting_summary.json                 numbers used by the diagnostic report
Nothing here feeds back into tracking, COM, identity, status or confidence."""
import sys, json, pickle, numpy as np, pandas as pd, cv2
sys.path.insert(0, "src")
import track
from com_model import NAMES

CFG = track.CONFIG
df = pd.read_csv("out/tracking.csv")
lm = pd.read_csv("out/tracking_landmarks_raw.csv")
dets = pickle.load(open("out/raw_detections.pkl", "rb"))
rule = json.load(open("out/run_meta.json"))["denim_rule"]
manual = pd.read_csv("out/failure_frames_manual.csv")
N = len(df); TRACKED = ["MEASURED", "PARTIAL"]

# ---- 1. per-frame raw-detection statistics (re-using the frozen denim function on the original video frames)
cap = cv2.VideoCapture("input.mp4")
raw_n, gated_n, max_h, max_den, big_n = [], [], [], [], []
for t in range(N):
    ok, frame = cap.read(); assert ok
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV); d = dets[t]
    raw_n.append(int(len(d["conf"]))); g = [j for j in range(len(d["conf"]))
        if d["conf"][j] >= CFG["DET_CONF"] and (d["box"][j][3] - d["box"][j][1]) >= CFG["MIN_BOX_H"]]
    gated_n.append(len(g))
    max_h.append(max([float(d["box"][j][3] - d["box"][j][1]) for j in g], default=np.nan))
    max_den.append(max([track.denim_frac(hsv, d["box"][j], rule) for j in g], default=np.nan))
    big_n.append(sum(1 for j in g if (d["box"][j][3] - d["box"][j][1]) >= 300))
df["n_raw_person_detections"] = raw_n
df["n_gated_person_detections"] = gated_n
df["max_gated_box_height_px"] = np.round(max_h, 1)
df["max_gated_denim_fraction"] = np.round(max_den, 3)

# ---- 2. selected person / landmark quality (selected detection exists only when a candidate was accepted)
sel = lm.groupby("frame").agg(selected_det_index=("selected_det_index", "first"),
        n_landmarks_ge_0p5=("used_for_status_com", "sum"), n_landmarks_ge_0p7=("drawn_in_overlay", "sum"),
        mean_kp_conf_all17=("keypoint_conf", "mean")).reset_index()
obs = lm[lm.used_for_status_com].groupby("frame").keypoint_conf.mean().rename("mean_kp_conf_observed").reset_index()
df = df.merge(sel, on="frame", how="left").merge(obs, on="frame", how="left")
for c in ["mean_kp_conf_all17", "mean_kp_conf_observed"]: df[c] = df[c].round(3)
sx = {}
for t, j in zip(sel.frame, sel.selected_det_index):
    b = dets[t]["box"][int(j)]; sx[t] = (round(float(b[0]), 1), round(float(b[1]), 1), round(float(b[2]), 1), round(float(b[3]), 1))
for k, name in enumerate(["selected_box_x1", "selected_box_y1", "selected_box_x2", "selected_box_y2"]):
    df[name] = [sx[t][k] if t in sx else np.nan for t in df.frame]
df["has_selected_landmarks"] = df.frame.isin(lm.frame.unique())

# ---- 3. why a frame has no selected-Cena landmarks
def reason(r):
    if r.has_selected_landmarks:
        return "LANDMARKS_PRESENT_INSUFFICIENT_ANATOMY" if r.status == "UNRESOLVED" else "LANDMARKS_PRESENT_TRACKED"
    pre = "PREDICTED_" if r.status == "PREDICTED" else "UNRESOLVED_"
    if r.n_gated_person_detections == 0:
        return pre + ("NO_PERSON_DETECTION_RAW" if r.n_raw_person_detections == 0 else "NO_PERSON_DETECTION_PASSING_GATES")
    if r.max_gated_box_height_px >= 300: return pre + "PERSON_BOX_PRESENT_CLOSEUP_SCALE_NOT_ACCEPTED_AS_CENA"
    return pre + "PERSON_BOX_PRESENT_NOT_ACCEPTED_AS_CENA"
df["landmark_absence_reason"] = df.apply(reason, axis=1)

# ---- 4. derived loss / reacquisition state (computed from statuses AFTER the run; the tracker itself keeps no such state)
state, since_last, loss_len, shot_lat = [], [], [], []
for seg, g in df.groupby("camera_segment"):
    start = int(g.frame.min()); seen = False; last = None; run = 0
    for _, r in g.iterrows():
        trk = r.status in TRACKED
        if trk:
            if not seen: st = "ACQUIRED_FIRST_IN_SHOT"; seen = True
            elif run > 0: st = "REACQUIRED_AFTER_LOSS"
            else: st = "TRACKED"
            ll = run; run = 0; last = int(r.frame); sl = 0
        else:
            if not seen: st = "NOT_YET_ACQUIRED"; ll = 0; sl = np.nan
            else:
                run += 1; ll = run; sl = int(r.frame) - last
                st = "LOST_PREDICTED" if r.status == "PREDICTED" else "LOST_UNRESOLVED"
        state.append((int(r.frame), st, sl, ll, int(r.frame) - start))
s = pd.DataFrame(state, columns=["frame", "derived_track_state", "frames_since_last_tracked_in_shot",
                                 "loss_run_length_so_far_or_prior", "frames_since_shot_start"])
df = df.merge(s, on="frame", how="left")

# ---- 5. audit annotations (my manual audit; NOT tracker output; clearly prefixed audit_)
cat = {t: [] for t in range(N)}
for _, r in manual.iterrows():
    for t in range(int(r.frame_start), int(r.frame_end) + 1): cat[t].append(r.category)
df["audit_categories"] = ["|".join(sorted(set(cat[t]))) for t in df.frame]
wrong = set(df[(df.camera_segment == 8) & (df.frame >= 386) & (df.identity != "unassigned")].frame) | {473, 474, 615, 617, 618, 628}
df["audit_identity_on_wrong_target_confirmed_or_inferred"] = df.frame.isin(wrong)

# ---- 6. write; the original columns must be bit-identical to tracking.csv
orig = pd.read_csv("out/tracking.csv")
out = df[list(orig.columns) + [c for c in df.columns if c not in orig.columns]]
assert out[list(orig.columns)].fillna("NA").astype(str).equals(orig.fillna("NA").astype(str)), "original columns changed!"
out.to_csv("out/tracking_full.csv", index=False)
acc = out[~out.has_selected_landmarks][["frame", "time_s", "camera_segment", "status", "n_raw_person_detections",
        "n_gated_person_detections", "max_gated_box_height_px", "max_gated_denim_fraction", "landmark_absence_reason", "audit_categories"]]
acc.to_csv("out/frames_without_landmarks_accounting.csv", index=False)
summ = dict(total=N, with_landmarks=int(out.has_selected_landmarks.sum()), without=int((~out.has_selected_landmarks).sum()),
            reasons=out.landmark_absence_reason.value_counts().to_dict(),
            wrong_target=sorted(int(x) for x in wrong))
json.dump(summ, open("out/accounting_summary.json", "w"), indent=1)
print(json.dumps(summ, indent=1)); print("columns:", len(out.columns)); print("original columns verified identical to tracking.csv")
