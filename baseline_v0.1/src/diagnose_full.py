"""ANALYSIS ONLY. Builds out/diagnostic_report_full.md from the frozen V0.1 outputs.
Requires out/tracking_full.csv (build_full_outputs.py), out/tracking_landmarks_raw.csv, out/cuts.json,
out/raw_detections.pkl, out/tracking_with_overlap.csv, out/diagnostic_report.md."""
import json, pickle, hashlib, numpy as np, pandas as pd
from collections import Counter
df = pd.read_csv("out/tracking_full.csv"); lm = pd.read_csv("out/tracking_landmarks_raw.csv")
ov = pd.read_csv("out/tracking_with_overlap.csv")[["frame", "max_overlap_iou"]]; df = df.merge(ov, on="frame")
cuts = json.load(open("out/cuts.json")); dets = pickle.load(open("out/raw_detections.pkl", "rb"))
N = len(df); fps = 30000 / 1001; T = lambda f: f"{f / fps:.2f}s"; TR = ["MEASURED", "PARTIAL"]
L = []; add = L.append
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
def pct(n, d=N): return f"{n} ({100 * n / d:.1f}%)"
def runs(mask, minlen=1):
    r = []; s = None
    for i, v in enumerate(mask):
        if v and s is None: s = i
        if s is not None and (not v or i == len(mask) - 1):
            e = i if v else i - 1
            if e - s + 1 >= minlen: r.append((s, e))
            s = None
    return r

add("# V0.1 Complete Diagnostic Report (frozen baseline)\n")
add("**Provisional, pose-derived, unvalidated.** No ground truth exists for this clip. Numbers marked *(pipeline)* are computed from the output files. Items marked *(audit)* come from my non-blinded visual inspection of ~75 frames (`audit_manual_spotcheck.md`) and are lower bounds. Nothing here is an accuracy measurement. No distance, velocity, acceleration, force, impact, load, fatigue or exposure variable is computed.\n")
add(f"Files analysed (sha256 prefix): tracking.csv `{sha('out/tracking.csv')}`, annotated.mp4 `{sha('out/annotated.mp4')}`, raw_detections.pkl `{sha('out/raw_detections.pkl')}`, cuts.json `{sha('out/cuts.json')}`.\n")

# ---------------- 1
add("## 1. Totals and status counts *(pipeline)*")
add(f"- Total frames: {N} (0-1500, {N / fps:.2f} s at {fps:.3f} fps); one CSV row per frame.")
for s in ["MEASURED", "PARTIAL", "PREDICTED", "UNRESOLVED"]: add(f"- {s}: {pct(int((df.status == s).sum()))}")
add(f"- Tracked (MEASURED + PARTIAL; a COM computed from landmarks): {pct(int(df.status.isin(TR).sum()))}")
add(f"- Frames with any COM value (tracked + PREDICTED): {pct(int(df.COM_x_pixel.notna().sum()))}; UNRESOLVED frames never carry a COM.")

# ---------------- 2
add("\n## 2. Raw pose landmarks: the 791 frames with, and what happened in the other 710 *(pipeline)*")
add("`tracking_landmarks_raw.csv` holds the 17 raw landmarks of the **one detection the tracker accepted as Cena**. It is not a record of whether the pose model produced output. `raw_detections.pkl` holds every detection (all people) with keypoints for all 1,501 frames.")
w = int(df.has_selected_landmarks.sum())
add(f"- Frames with selected-Cena landmarks: **{pct(w)}** = {int(df.status.isin(TR).sum())} tracked + {w - int(df.status.isin(TR).sum())} UNRESOLVED frames where a candidate was accepted but observed segment mass was < 0.40 (insufficient anatomy; no COM produced).")
add(f"- Frames without selected-Cena landmarks: **{pct(N - w)}**: {int(((~df.has_selected_landmarks) & (df.status == 'PREDICTED')).sum())} PREDICTED (no candidate accepted; COM extrapolated, no landmarks) + {int(((~df.has_selected_landmarks) & (df.status == 'UNRESOLVED')).sum())} UNRESOLVED (no candidate accepted; no COM).")
a = df[~df.has_selected_landmarks]
add("\nReason codes for the frames with no selected landmarks (derived from raw detections; gates = confidence >= 0.30 and box height >= 50 px):\n")
add("| Reason | Frames | Share of 710 |\n|---|---|---|")
names = {"UNRESOLVED_PERSON_BOX_PRESENT_CLOSEUP_SCALE_NOT_ACCEPTED_AS_CENA": "UNRESOLVED: person box present, close-up scale (>=300 px tall), not accepted as Cena",
         "UNRESOLVED_PERSON_BOX_PRESENT_NOT_ACCEPTED_AS_CENA": "UNRESOLVED: person box(es) present, none accepted as Cena",
         "UNRESOLVED_NO_PERSON_DETECTION_PASSING_GATES": "UNRESOLVED: detections exist but none pass the size/confidence gates",
         "UNRESOLVED_NO_PERSON_DETECTION_RAW": "UNRESOLVED: no detection at all (conf >= 0.10)",
         "PREDICTED_PERSON_BOX_PRESENT_NOT_ACCEPTED_AS_CENA": "PREDICTED: person box(es) present, none accepted as Cena",
         "PREDICTED_PERSON_BOX_PRESENT_CLOSEUP_SCALE_NOT_ACCEPTED_AS_CENA": "PREDICTED: close-up scale box present, not accepted",
         "PREDICTED_NO_PERSON_DETECTION_PASSING_GATES": "PREDICTED: detections exist but none pass the gates",
         "PREDICTED_NO_PERSON_DETECTION_RAW": "PREDICTED: no detection at all"}
for k, v in a.landmark_absence_reason.value_counts().items(): add(f"| {names.get(k, k)} | {v} | {100 * v / len(a):.1f}% |")
g = int((a.n_gated_person_detections > 0).sum()); rr = int((a.n_raw_person_detections > 0).sum())
add(f"\n- **{g} of the 710 frames ({100 * g / 710:.1f}%) had at least one person detection (with keypoints) passing the gates, but none was accepted as Cena.** In those frames the limiting step was the identity gate (denim colour / continuity), not pose detection. {rr} had at least one raw detection; {710 - rr} had none.")
add(f"- Only {710 - g} frames ({100 * (710 - g) / 710:.1f}%) had no person detection passing the gates.")
add("- Reading the codes against the video *(audit, shot-level, approximate)*: the large close-up bucket is Cena in close-up with shorts out of view (tracker cannot identify him); frames with no detection at all are mostly crowd shots or severe occlusion; in crowd-only shots (segments 21 and 23) there is no Cena to find, so UNRESOLVED is the correct output there. Per-frame detail: `frames_without_landmarks_accounting.csv`.")
add("\nPer-shot count of frames without selected landmarks (shot id: frames): " + ", ".join(f"{k}: {v}" for k, v in a.groupby("camera_segment").size().items()))

# ---------------- 3
add("\n## 3. Camera cuts *(pipeline; not validated against a human list)*")
cl = cuts["cuts"]
add(f"- {len(cl)} cuts; 25 shots (segments 0-24). Parameters: `cut_detection_params.json`. Frame index = first frame of the new shot.\n")
add("| frame | time | bg-registration inliers | hist dist | pixel diff |\n|---|---|---|---|---|")
for c in cl: add(f"| {c['frame']} | {T(c['frame'])} | {c['inliers']} | {c['bd']:.2f} | {c['md']:.1f} |")
add(f"- Photometric events judged not cuts: {[p['frame'] for p in cuts['photometric_events']]} (colour-inverted flash frames; background still registers). Two of them (473, 628) produced wrong-person selections (section 5).")
add("- Least certain: f434 (inlier count 24, near threshold of a pan/zoom), f1062 and f1070 (two events 8 frames apart), f280 and f292 (two cuts 12 frames apart).")
add("- Handling verified in the CSV: no cut frame is PREDICTED, no PREDICTED run follows a cut, spatial state is reset at each cut. COM values exist on both sides of 9 cuts with pixel jumps up to 728 px; these are camera changes, not movement.")

# ---------------- 4
add("\n## 4. Tracking losses and reacquisition latency *(pipeline; derived states in tracking_full.csv)*")
add("Derived states are computed after the run (the tracker keeps no loss state): ACQUIRED_FIRST_IN_SHOT, TRACKED, LOST_PREDICTED, LOST_UNRESOLVED, REACQUIRED_AFTER_LOSS, NOT_YET_ACQUIRED. Counts: " + str(df.derived_track_state.value_counts().to_dict()))
starts = [0] + [c["frame"] for c in cl]; ends = [c["frame"] - 1 for c in cl] + [N - 1]
add("\n**Acquisition at the start of each shot** (latency = frames until the first MEASURED/PARTIAL frame):\n")
add("| shot | frames | first tracked | latency (fr / s) | tracked share |\n|---|---|---|---|---|")
lat = []
for i, (s, e) in enumerate(zip(starts, ends)):
    gg = df[(df.frame >= s) & (df.frame <= e)]; t = gg[gg.status.isin(TR)]
    if len(t): l = int(t.frame.min()) - s; lat.append(l); add(f"| {i} | {s}-{e} | f{int(t.frame.min())} | {l} / {l / fps:.2f} | {len(t)}/{len(gg)} |")
    else: add(f"| {i} | {s}-{e} | never | - | 0/{len(gg)} |")
add(f"\n- Shots acquired: {len(lat)} of 25; never acquired: {25 - len(lat)}. Latency 0 frames in {sum(1 for x in lat if x == 0)} shots; median {np.median(lat):.0f}, max {max(lat)} frames.")
ev = []
for seg, gg in df.groupby("camera_segment"):
    gg = gg.reset_index(drop=True); nt = ~gg.status.isin(TR).values
    for s, e in runs(nt):
        if not gg.status.iloc[:s].isin(TR).any(): continue
        ev.append((int(gg.frame[s]), int(gg.frame[e]), e - s + 1, e + 1 < len(gg), gg.status.iloc[s:e + 1].value_counts().to_dict()))
add(f"\n**Loss events** (non-tracked run after tracking had begun in the same shot): {len(ev)} events; recovered within the shot: {sum(1 for x in ev if x[3])}; ended by the shot ending: {sum(1 for x in ev if not x[3])}; median length {np.median([x[2] for x in ev]):.0f} frames; longest {max(x[2] for x in ev)}; {sum(1 for x in ev if x[2] >= 10)} events >= 10 frames.\n")
add("| frames | time | length | outcome | statuses |\n|---|---|---|---|---|")
for s, e, n, rec, st in ev: add(f"| {s}-{e} | {T(s)}-{T(e)} | {n} | {'recovered f' + str(e + 1) if rec else 'shot ended'} | {st} |")

# ---------------- 5
add("\n## 5. Suspected identity switches / wrong-person selections")
fl = df["flags"].fillna("")
add(f"- Automatic flags *(pipeline)*: 'jump' on {df[fl.str.contains('jump')].frame.tolist()}; 'ambiguous' on {df[fl.str.contains('ambiguous')].frame.tolist()}; identity held by continuity only on {int((df.identity_basis == 'continuity').sum())} frames.")
wr = sorted(df[df.audit_identity_on_wrong_target_confirmed_or_inferred].frame)
trk_wr = [f for f in wr if df.loc[f, 'status'] in TR]
add(f"- Wrong-target frames *(audit; lower bound)*: **{len(wr)} frames** ({len(trk_wr)} labelled MEASURED/PARTIAL, {len(wr) - len(trk_wr)} labelled UNRESOLVED or PREDICTED but still anchored to the wrong target): f386-404 (opponent lying on the mat; viewed 9 of 19, rest inferred), f473 (spectator, flash frame), f474 (PREDICTED from that anchor), f615/617/618 (tiny background box), f628 (spectator-sized box, flash frame).")
caught = [f for f in wr if 'jump' in fl[f]]
add(f"- Flag sensitivity against these: 'jump' fired on {caught} = {len(caught)} of {len(wr)}; the f386-404 error was a wrong acquisition after a cut, not a jump, so no flag could fire. 'jump' also fired on f629 and f755, which I viewed and judged plausible.")
add("- No selection of the referee was observed in any viewed frame, and no wrong-person selection in the clean wide shots I sampled. These are statements about viewed frames only. The tracker has no per-frame way to know it switched; a switch can only be established against labelled data.")
add("- Mechanism *(pipeline + audit)*: the denim rule has no specificity. Denim fraction on the wrong-target tracked frames ranged 0.30-0.91, against a median of 0.15 over all tracked frames, so a high value does not indicate Cena. The ring floor, banners and flash-inverted frames fall in the accepted hue range.")

# ---------------- 6
add("\n## 6. Landmark failure patterns *(pipeline; selected-Cena frames only, n = 791; available = confidence >= 0.50)*")
av = lm.groupby("landmark").agg(avail=("used_for_status_com", "mean"), shown=("drawn_in_overlay", "mean"), mc=("keypoint_conf", "mean")).sort_values("avail")
add("| landmark | available >=0.50 | shown >=0.70 | mean conf |\n|---|---|---|---|")
for k, r in av.iterrows(): add(f"| {k} | {100 * r.avail:.0f}% | {100 * r.shown:.0f}% | {r.mc:.2f} |")
lm2 = lm.merge(df[["frame", "status"]], on="frame")
add("\nAvailability by status (share of frames with the landmark >= 0.50):\n")
add("| landmark | MEASURED | PARTIAL | UNRESOLVED (landmarks present) |\n|---|---|---|---|")
pv = lm2.pivot_table(index="landmark", columns="status", values="used_for_status_com", aggfunc="mean")
for k in av.index: add(f"| {k} | " + " | ".join(f"{100 * pv.loc[k, c]:.0f}%" if c in pv.columns else "-" for c in ["MEASURED", "PARTIAL", "UNRESOLVED"]) + " |")
miss = lm[~lm.used_for_status_com].groupby("frame").landmark.apply(lambda s: tuple(sorted(s)))
add("\nMost common missing-landmark sets (frames; none missing in the rest):\n")
cn = Counter(miss.values); add(f"- Frames with no missing landmarks: {791 - len(miss)}; frames with >= 1 missing: {len(miss)}")
for k, v in cn.most_common(8): add(f"- {v} frames missing: {', '.join(k)}")
nl = lm.groupby("frame").used_for_status_com.sum()
add(f"\nLandmarks >= 0.50 per frame: mean {nl.mean():.1f}, median {nl.median():.0f}, min {nl.min()}; frames with 17/17: {int((nl == 17).sum())}.")
add("- Pattern: the face (ears, eyes, nose) fails most, then ankles and wrists. This fits heads turned away or cropped, feet cropped or hidden by the mat or the opponent, and hands lost in grappling. Hips and shoulders are rarely missing, but a high-confidence hip does not prove the hip was visible (section 9).")

# ---------------- 7
add("\n## 7. Difficult body states and shot conditions *(ranges are my visual-audit labels, approximate; extents inferred between sampled frames)*")
BS = [("Rapid locomotion / ropes, wide shot", [(29, 155)], "viewed 50, 75, 100, 125, 150"),
      ("Clean upright/standing, wide-medium", [(156, 225), (300, 360), (546, 599)], "viewed 175-225, 300-350, 550-575"),
      ("Lifting / being lifted (opponent overhead)", [(245, 279)], "viewed 250, 255, 270, 275"),
      ("Fireman's-carry (opponent on shoulders)", [(918, 957)], "viewed 925, 936, 939, 942, 950"),
      ("Grounded / grappling / pin", [(755, 780), (1062, 1214)], "viewed 755, 775, 1075, 1100, 1125, 1150, 1175, 1200"),
      ("Bent-over / crouched / kneeling", [(600, 660), (800, 850)], "viewed 600, 619-629, 650, 800-850"),
      ("Back-turned / torso-only medium view", [(700, 752)], "viewed 700, 725, 750"),
      ("Occluded behind opponent / start of clip", [(0, 13), (75, 78)], "viewed 0, 75"),
      ("Close-up, lower body out of frame", [(361, 404), (434, 545), (851, 917), (958, 1061), (1270, 1396), (1463, 1500)], "viewed 375, 386-404, 440-525, 875, 900, 975-1050, 1275-1375, 1475, 1500"),
      ("Crowd-only (Cena not in frame)", [(405, 433), (1215, 1269), (1397, 1462)], "viewed 425, 1225, 1250, 1400-1450")]
add("| Body state / condition | frames | MEAS / PART / PRED / UNRES | mean conf (tracked) | mean landmarks >=0.5 | overlap IoU>=0.30 | evidence |\n|---|---|---|---|---|---|---|")
for name, rg, ev_ in BS:
    idx = sorted({f for a_, b_ in rg for f in range(a_, b_ + 1)}); g_ = df[df.frame.isin(idx)]; vc = g_.status.value_counts()
    t_ = g_[g_.status.isin(TR)]
    add(f"| {name} {rg} | {len(g_)} | {vc.get('MEASURED', 0)} / {vc.get('PARTIAL', 0)} / {vc.get('PREDICTED', 0)} / {vc.get('UNRESOLVED', 0)} | {t_.tracking_confidence.mean():.2f} | {g_.n_landmarks_ge_0p5.mean():.1f} | {int((g_.max_overlap_iou >= 0.30).sum())} | {ev_} |")
add("- **Airborne:** no clearly airborne Cena frame was identified in the frames I viewed, so no claim is made about airborne states. This is a gap in the audit, not a finding.")
add("- **Rapid movement / motion blur:** viewed at f29-110 and f300; skeletons are rough but on the correct person. Not systematically quantified.")
add("- Observed pattern: in overlap states (lifted, carry, grounded) the tracker emits MEASURED with high landmark counts on skeletons that visibly mix bodies; in close-ups it emits almost nothing (the 22 tracked frames in the close-up row are mostly the wrong-target f386-404 and the distorted f440-444). The status labels therefore do not separate good from bad frames in the states that matter most for the research question.")

# ---------------- 8
add("\n## 8. Anatomically / geometrically implausible pose predictions")
BON = [(5, 7, "L_upper_arm"), (7, 9, "L_forearm"), (6, 8, "R_upper_arm"), (8, 10, "R_forearm"), (11, 13, "L_thigh"), (13, 15, "L_shank"), (12, 14, "R_thigh"), (14, 16, "R_shank")]
sus = {}
for t, j in zip(df.frame, df.selected_det_index):
    if np.isnan(j): continue
    d = dets[t]; j = int(j); b = d["box"][j]; dg = np.hypot(b[2] - b[0], b[3] - b[1]); kp = d["kp"][j]; kc = d["kpc"][j]; why = []
    for x, y, n in BON:
        if kc[x] >= .5 and kc[y] >= .5 and np.hypot(*(kp[x] - kp[y])) > .5 * dg: why.append(f"{n}>0.5xdiag")
    for x, y, n in [(15, 16, "ankles"), (9, 10, "wrists"), (13, 14, "knees")]:
        if kc[x] >= .5 and kc[y] >= .5 and np.hypot(*(kp[x] - kp[y])) < 2.0: why.append(f"{n}_coincident")
    o = sum(1 for i in range(17) if kc[i] >= .5 and (kp[i][0] < b[0] - 10 or kp[i][0] > b[2] + 10 or kp[i][1] < b[1] - 10 or kp[i][1] > b[3] + 10))
    if o: why.append(f"{o}_landmarks_outside_own_box")
    if why: sus[t] = why
add(f"- Automatic geometry checks *(pipeline; 2D heuristics, suspicious not proof)*: {len(sus)} of {w} landmark frames trip >= 1 check (limb > 0.5x box diagonal, coincident left/right joints, landmarks > 10 px outside own box). Frames: {sorted(sus)}")
add("- Visually identified *(audit)*: (a) skeletons joining two or three bodies in overlap/lift/carry/pin sequences (f245-279, f918-957, f1062-1214, f775; ~214 tracked frames, 208 MEASURED); (b) distorted torso skeleton with legs out of frame at f440-444, status PARTIAL; (c) rough skeletons under motion blur at f300; (d) coincident/outside-box landmarks in the carry at f936-942.")
add("- Sensitivity of the automatic checks: they flag ~30 frames and ~81 overlap frames versus ~214 visually affected frames, so they miss most visible contamination. They must not be used as a failure detector.")

# ---------------- 9
add("\n## 9. COM anomalies *(pipeline checks; the COM itself is provisional and unvalidated)*")
tr = df[df.status.isin(TR) & df.COM_x_pixel.notna()].reset_index(drop=True)
out_box = [int(r.frame) for _, r in tr.iterrows() if not (r.selected_box_x1 - 5 <= r.COM_x_pixel <= r.selected_box_x2 + 5 and r.selected_box_y1 - 5 <= r.COM_y_pixel <= r.selected_box_y2 + 5)]
add(f"- COM outside its own selected person box (+-5 px): {len(out_box)} frames. (Weak check: a COM can sit inside the box and still belong to a merged body.)")
mj = []
for i in range(1, len(tr)):
    p, c = tr.loc[i - 1], tr.loc[i]
    if c.frame == p.frame + 1 and c.camera_segment == p.camera_segment and abs(c.visible_mass_fraction - p.visible_mass_fraction) >= .25:
        dg = np.hypot(c.selected_box_x2 - c.selected_box_x1, c.selected_box_y2 - c.selected_box_y1)
        mj.append((int(c.frame), round(float(abs(c.visible_mass_fraction - p.visible_mass_fraction)), 2), round(float(np.hypot(c.COM_x_pixel - p.COM_x_pixel, c.COM_y_pixel - p.COM_y_pixel) / dg), 2)))
add(f"- Visible-mass jumps >= 0.25 between consecutive tracked frames: {len(mj)} (frame, dMass, COM shift / box diagonal): {mj}. The renormalised PARTIAL COM moves when segments drop in or out, independent of movement; largest single-step shift {max(x[2] for x in mj):.2f} box diagonals (f619).")
cj = []
for c in cl:
    f = c["frame"]
    if pd.notna(df.loc[f - 1, "COM_x_pixel"]) and pd.notna(df.loc[f, "COM_x_pixel"]): cj.append((f, round(float(np.hypot(df.loc[f - 1, 'COM_x_pixel'] - df.loc[f, 'COM_x_pixel'], df.loc[f - 1, 'COM_y_pixel'] - df.loc[f, 'COM_y_pixel'])), 1)))
add(f"- Pixel jump in COM across a camera cut (camera change, not movement): {cj}")
pr = df[df.status == "PREDICTED"]
add(f"- PREDICTED COM: {len(pr)} frames; confidence declines as last_conf x 0.9^k x 0.5 (max {pr.tracking_confidence.max():.2f}). Visible drift *(audit)* at f474-488 and f445-459 (marker off Cena; anchored to a wrong or very short acquisition). The prediction has no validation and uses an ad-hoc 0.5 damping factor.")
add("- Implementation quirk (not fixed): the smoothed pixel velocity is updated on every tracked frame from `com - prev_com`, where prev_com may be many frames old after a loss, so the first update after a long gap contains a multi-frame displacement. It only affects later PREDICTED values.")
add("- Systematic bias sources: Dempster cadaver proportions; COCO keypoints are not anatomical joint centres; PARTIAL COM = centroid of visible mass only; hands and feet are lumped into forearm and leg; merged-body skeletons give a COM that is not Cena's alone; `com_uncertainty_px_heuristic` is a heuristic, not a confidence interval.")

# ---------------- 10
add("\n## 10. Other failures and questionable behaviour")
add("- **Keypoint confidence is not visibility.** MEASURED requires trunk + enough segments at keypoint confidence >= 0.50; occluded joints can be inferred with high confidence. 208 of 650 MEASURED frames lie in visibly merged-body sequences.")
add("- **tracking_confidence is uncalibrated** (detector conf x appearance factor x mean landmark conf); values of 0.63-0.80 occur on merged-body frames.")
add("- **Identity cue fails when shorts are not visible**, which is about a third of the clip (close-ups); there the output is UNRESOLVED while Cena is plainly in frame (e.g. f375, 450-525, 875-900, 975-1050, 1275-1375, 1475-1500).")
add("- **Predicted/unresolved while Cena is visible and detectable:** f150, f650 (PREDICTED); f616 (UNRESOLVED: feet cropped, mass < 0.40).")
add("- **Single-target only:** the opponent and referee are never tracked; their only trace is the grey 'other' boxes in the video.")
add("- **Cut detection not human-validated.**")
add("- **Environment rebuilt mid-task** after a sandbox reset; see `REPRODUCIBILITY.md`.")

# ---------------- 11
add("\n## 11. What this report cannot say")
add("It cannot state accuracy, identity-switch rate, landmark error, COM error or the true fraction of correct frames: there are no labels. The audit sampled ~5% of frames and extrapolated ranges. Everything flagged as failure is a lower bound.")

add("\n---\n## Appendix A. Original automatic diagnostic report (unchanged)\n")
add(open("out/diagnostic_report.md").read().replace("\n# ", "\n### ").replace("\n## ", "\n#### "))
open("out/diagnostic_report_full.md", "w").write("\n".join(L)); print("written", len("\n".join(L)), "chars")
