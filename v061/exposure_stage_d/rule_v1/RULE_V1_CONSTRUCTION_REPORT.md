# STAGE-D RULE V1 — CONSTRUCTION REPORT (frozen; returned to the independent reviewer BEFORE CHECK)
Status: ANNOTATION_PROVISIONAL; R4 unmet; development futility gate only. No validation, generalization, exposure-validity, workload, identity or anatomy claim. **CHECK was not opened, decoded, featurised, summarised or evaluated.**

## 1. Frozen Rule V1 SHA256
`4dc574dfd71f3bc86b6d2a1ab22d6fb4778b9fbc4966d380fa4cd257e691bb1b` = sha256(json.dumps({rule_id, config, code_sha256}, sort_keys=True)). Full artifact: `RULE_V1_FROZEN.json`.

## 2. Specification (declared before any BUILD number; prospective note sha256 85fb9f8a…8cd56, file `PROSPECTIVE_SPEC_PRE_BUILD_NUMBERS.md`)
Inputs: frozen shot frame ranges; frozen stride-3 person boxes (box, confidence, frame size only; frozen gate conf ≥ 0.3 and height ≥ 50 px at 360p).
- **F1 frac_ge2** = fraction of the shot's sampled frames with ≥ 2 gated boxes (0–1). Rationale: ring cameras show both wrestlers (usually plus referee); face/crowd/desk/graphic shots show 0–1 bodies.
- **F2 h_max_med** = median over sampled frames of (tallest gated box height / frame height) (0–1; 0 if no gated box). Rationale: one body filling most of the frame signals tight framing.
- **Replay indicator R**: inert, R = 0 always, 0 thresholds. With zero BUILD REPLAY examples any replay cue would be an invented, untestable threshold. R = 1 would map to REPLAY_SUSPECT (never LIVE) — unreachable in V1.
- **Thresholds**: T1 = 0.20, T2 = 0.50, T3 = 0.80 (round values from rationale: <1-in-5 frames with two bodies; majority; >80% of frame height).
- **Hierarchy**: (1) no sampled frame → UNKNOWN (NO_FEATURES; missing is never LIVE); (2) R = 1 → REPLAY_SUSPECT; (3) F1 < T1 → NOT_LIVE; (4) F1 ≥ T2 and F2 ≤ T3 → LIVE; (5) otherwise UNKNOWN.
- **P1 calculation**: duration-weighted LIVE/not-LIVE disagreement on reference-decidable duration; classifier UNKNOWN counts as not-LIVE; reference UNKNOWN rows excluded from numerator and denominator (5 shots / 53.7 s). Identical for the all-LIVE baseline.
- **Complexity**: 2 features (limit 3) + replay indicator (inert); 3 thresholds (limit 5). Deterministic; no learned component, no fitting.

## 3. BUILD-only diagnostics (169 shots / 638.233 s; decidable 584.534 s). Descriptive; not evidence of performance.
| | disagree s | decidable s | P1 |
|---|---|---|---|
| **Rule V1** | 218.833 | 584.534 | **37.44%** |
| **All-LIVE baseline** | 26.133 | 584.534 | **4.47%** |

Rule classes: LIVE 112 shots / 424.1 s; NOT_LIVE 4 / 10.3 s; UNKNOWN 53 / 203.8 s. Reference × rule (shots / s): LIVE_ACTION→LIVE 102/355.0, →UNKNOWN 49/193.1, →NOT_LIVE 4/10.3; CLOSE_UP→LIVE 4/13.4, →UNKNOWN 4/10.7; NON_MATCH→LIVE 1/2.0; reference-UNKNOWN→LIVE 5/53.7 (excluded from P1). No shot lacked features. P1 by source: orton 20.6%, batch2_clip 36.5%, vp2 29.2%, vp5 42.1%, match 40.0%.

**Rule V1 is worse than the trivial baseline on BUILD.** Cause (descriptive): of 49 LIVE_ACTION shots the rule sent to UNKNOWN, 35 (140.3 s) were vetoed by F2 > T3 (tight live camera work: median F2 of LIVE_ACTION shots is 0.68, CLOSE_UP 0.80, so F2 barely separates them) and 14 (52.8 s) fall in the F1 band 0.2–0.5. F1 separates little as well (CLOSE_UP median 0.76, LIVE_ACTION 1.0). Only 9 non-LIVE decidable BUILD shots exist, so BUILD cannot support a threshold choice for them.

## 4. Which BUILD examples drove threshold selection
None. T1–T3 were fixed from rationale before any BUILD feature was computed, and were not changed after the BUILD result was seen. Retuning on the observed failure would be BUILD-fitting on ~9 exceptions; it is not done here.

## 5. Reproducibility
Detector: frozen YOLOv8m-pose weights (sha dbe539ea…), imgsz 960, conf 0.10, stride 3, boxes only; four clips use the frozen existing detections; the match BUILD range (absolute frames 4541–13457, 2,972 detections, frames 4542–13455) was produced by `det_match_build.py` with PREPROC_V1 normalisation (scale=-2:360 bicubic, 30 fps). All code/config/input hashes: `RULE_V1_FROZEN.json`. Rerun: `build_diagnostics.py` (private inputs).

## 6. CHECK status
CHECK labels submitted 0, opened=false (per build_return.json). Detection decoded only frames ≤ 13457 (CHECK starts at frame 13546); only BUILD ids were read from the shot-frame table. No CHECK feature, clip, frame, label, summary or result was used or produced. **No CHECK inference or evaluation has been performed.**

## 7. Limitations / construction concerns for the reviewer
1. Rule V1 as declared would very likely exceed the P1 > 20% STOP bound, mainly through UNKNOWN abstention (counted as not-LIVE). Freezing it as is would spend the single CHECK on a rule already known to be worse than all-LIVE on BUILD. I did not alter it unilaterally; the reviewer should decide whether to (a) authorise a documented pre-CHECK reconstruction (e.g. remove the F2 veto), or (b) proceed to CHECK as frozen.
2. BUILD cannot inform replay recognition (R inert); a CHECK replay would leak into LIVE only if it also looks like a two-person scene (P3 untested).
3. Heavy LIVE dominance; non-LIVE BUILD examples come from short excerpts; reference-UNKNOWN PIP shots (4 / 49.2 s, rule says LIVE) are invisible to box features.
4. Box features cannot see picture-in-picture, graphics or replay.
