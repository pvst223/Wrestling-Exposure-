# EXPOSURE V1 — DESIGN PROPOSAL V1 (design only; nothing implemented, nothing run)

Status: proposal for independent reviewer audit. Development-only, ANNOTATION-PROVISIONAL, IDENTITY_UNVALIDATED, rights UNRESOLVED; contact/overlap ownership unresolved. Nothing here validates identity, anatomical ownership, exposure or workload, and nothing is inferred from the fresh qualitative MP4. Not used: Holdout #2, Gemini, C3, partial-release anatomy, any retuning of Anatomy V1 or identity.

## 0. Bottom line
The frozen system cannot currently support any per-wrestler, per-body, or physically-scaled exposure variable (distance, speed, COM, impacts, kinematics). What it can plausibly support, because it needs no identity, no anatomical ownership and no pixel-to-metre scale, is **scene-level temporal structure of a broadcast**: how long the match lasted, and how much of that time the camera actually showed live in-ring action versus replays, close-ups and non-match material. The proposed minimum Exposure V1 is therefore deliberately small: **match duration (a non-CV comparator) plus a fail-closed partition of the broadcast timeline with explicit bounds on observable live-action time.** It is designed so that its likely failure modes are informative: if it fails, we learn the classifier cannot be done cheaply; if it passes but tracks duration (rho ≥ 0.95), we learn duration alone is sufficient (NO_ADDED_VALUE), which is a legitimate scientific result.
Two framing decisions need the owner/reviewer (section 8): which video regime the eventual CMJ study will have, and whether match-level exposure shared by both wrestlers is acceptable.

## 1. Task 1 — the exposure construct
**Question.** Does professional-wrestling workload cause measurable deterioration in lower-extremity neuromuscular function (acute within-wrestler post-match CMJ deviation from baseline)? Exposure V1's job is to provide *objective, external* variables that could later be related to that outcome.

**Definition (project).** *Match exposure* = the external, observable physical activity a wrestler undergoes during a match, as far as it can be recovered from video. It is not internal load (heart rate, RPE, metabolic cost, muscle damage, fatigue), which video does not measure, and it is not a risk or injury quantity.

| Domain | What it would mean | Observable from broadcast video? |
|---|---|---|
| Duration/time | bell-to-bell time; time in live action | Yes in principle (the broadcast clock, shot structure); edited broadcasts hide unseen time |
| Movement/locomotor | distance, speed, accelerations, ring coverage | Not with current evidence: no camera calibration, moving/zooming cameras, cuts, per-wrestler identity unvalidated |
| Action/event | counts of bumps, jumps, landings, strikes, throws | Not reliably: needs per-body pose in contact (unresolved) or event detectors that do not exist |
| Contact/interaction | time in grappling, impacts, holds | Contact is exactly where ownership fails (7/30 contaminated assigned controls; no contact detector) |
| Intensity proxies | speed, joint velocities, movement energy | Pixel kinematics from a moving single view are not physically comparable; contaminated by ownership |
| Recovery/rest structure | pauses, work:rest | Only indirectly (derived from live-time structure); editing hides real rest |
| Internal load | physiological response | **Not measurable by this system**; must come from the CMJ study / wearables |

Two structural limitations apply to every candidate: (1) a match-level variable is **shared by both participants**; it cannot capture within-match differences in role (aggressor vs bump-taker); (2) a broadcast is an *edited sample* of the match (cuts, replays, graphics, close-ups, cutaways, possibly removed commercial breaks), so observed time is at best a lower bound on real activity.

## 2. Task 2 — capability-to-metric map
### 2.1 What the frozen system provides, with the failure modes already measured (development-only, small samples)
| Layer | What exists | Measured limitation (source) |
|---|---|---|
| Shots/cuts | deterministic ffmpeg scene score > 0.3, events < 0.25 s merged | 54 shots in 150 s of the fresh segment (mean about 2.8 s); V0.1: 24 cuts in 1,501 frames plus 4 photometric events judged not cuts; M7 cut cross-check OPEN/NON-BLOCKING |
| Person detection | pinned YOLOv8m-pose, conf 0.10, stride 3 (10 fps), boxes + 17 landmarks | V0.1: 710 of 1,501 frames had no selected landmarks; crowd/referee/staff detected as persons |
| Tracklets | greedy IoU within a shot (conf ≥ 0.3, box ≥ 50 px at 360p, ≥ 5 detections); never cross shots | no cross-shot continuity by construction |
| Identity (L1, V0.6.1) | open-set A/B/non-target head | gate AUROC 0.984–0.989 (wrestler vs non-wrestler) but A/B AUROC 0.722–0.808 across seeds; wrong-wrestler 406/2,136 (seed 0) to 700/2,278 (seed 3) accepted target candidates; unit FTA 0.34–0.415; V0.5 Holdout #1: 14/87 wrong-person emissions. **Unvalidated (MODIFY).** |
| Anatomical ownership + pose | V0.5 ownership, record classifier, stride-3 pose, visualization-only carry | 64.6% of identity-ACCEPT measured frames withheld (1,408/2,179); assigned control 7/30 contaminated (23.3%), all in contact; no-contact 0/20; carried rows 15.2% of rows; C3 contact repair closed NO_ADDED_VALUE |
| Fresh qualitative MP4 | frozen V1 on 150 s | 535 measured + 1,059 carried assigned rows of 5,041 (31.6%); 50.6% withheld; **qualitative only** |
| Camera/geometry | none | V0.1 pixel COM never established as comparable across camera segments; no ring/court calibration; broadcast pan/zoom/replays/picture-in-picture graphics |

### 2.2 Candidate variable → minimum upstream dependency → contaminating failure modes
| ID | Candidate | Minimum dependency chain | Failure modes that contaminate it |
|---|---|---|---|
| X1 | Match duration D | video timeline, start/end definition | none from CV; depends on how start/end are defined and whether the clip is the full match |
| X2 | Observable live-action time T_live (with bounds) | shot boundaries + shot-level class (LIVE / REPLAY / CLOSE-UP / NON-MATCH / UNKNOWN) | cut-detector misses; replay detection; close-up vs live ambiguity; picture-in-picture replay graphics; editing |
| X3 | Engagement fraction E (two-body physical engagement share of T_live) | X2 + two-body contact interpretation | contact/overlap ownership unresolved; referee/spectator contact; occlusion |
| X4 | Grounded-person event count | tracklets + orientation (box aspect or pose) | merged boxes in clinches; replays double-count; camera zoom; identity if per-wrestler |
| X5 | Distance / speed / acceleration | tracklets + identity + camera calibration + scale | no calibration; cuts; zoom; identity wrong ~19–31% of accepted targets; pixel ≠ metres |
| X6 | Aerial/jump–landing count | pose (ownership) + camera-invariant vertical reference | 2D single view; contact ownership; carry; stride 3 |
| X7 | Impact/contact load | contact interpretation + a force model | no force measure; contact unresolved |
| X8 | Per-wrestler on-camera time | identity | identity unvalidated; on-camera time reflects direction/editing |
| X9 | Pose-derived intensity (joint speed, ROM, movement energy) | pose ownership + physical scale | contamination 23% in assigned control; carry; stride 3; 2D |
| X10 | COM trajectory | pose ownership + mass model + scale | all of the above |
| X11 | Rest/recovery structure | X2 (+ X3) | editing hides rest; holds/rest-holds ambiguous |
| X12 | Cut rate / shot count | shot boundaries | production artefact, not exposure (usable only as an editing-density covariate) |

## 3. Task 3 — candidate Exposure V1 metrics (small set)
Only the variables that survive a first pass are specified in full. Everything else is in the kill table (section 4).

**X1 — Match duration D (comparator, no CV).**
1. Definition: seconds from the pre-defined match start to match end in the video timeline (start = bell or first in-ring contact; end = decision/bell; definition frozen before use). 2. Rationale: the simplest external time-exposure; any CV variable must show value beyond it. 3. Inputs: video timecode; human start/end marking. 4. Unit: seconds. 5. Confounders: edited/condensed matches; commercial breaks removed; clip may be a segment. 6. Validation: second marking of start/end on a subset (agreement tolerance reviewer-set). 7. Support: yes (trivial). 8. Failure invalidates only X1 (and the baseline comparison).

**X2 — Observable live-action time with bounds.**
1. Definition: the broadcast timeline is partitioned by shot into LIVE_ACTION (real-time in-ring view in which wrestlers' bodies are visible), REPLAY (including picture-in-picture/slow-motion replays), CLOSE_UP (match-time shot where action is not visible), NON_MATCH (crowd, entrance, interview, graphics), UNKNOWN. Outputs: T_live_lo = duration of shots classed LIVE with certainty; T_live_hi = T_live_lo + T_unknown; replays are never counted as match time (this prevents double counting). Also T_closeup, T_replay, T_nonmatch, T_unknown and coverage C = T_live_lo / D.
2. Rationale: the only external time-exposure that separates action actually shown from replays and padding; interpreted strictly as a **lower bound of observable activity**, not total activity.
3. Inputs: frozen shot boundaries; frozen person boxes (conf ≥ 0.3, height ≥ 50 px at 360p) per shot; no identity, no skeleton, no ownership, no masks, **no carried rows** (a schema test, as in SEP V1, will enforce this).
4. Unit: seconds (with interval) and a dimensionless coverage.
5. Confounders: cut-detector errors, replay graphics, camera direction choices, removed ad breaks, cutaways during real action.
6. Validation: human shot-level reference labels (section 6); error of T_live and interval honesty on fresh full matches.
7. Support: plausibly yes at shot level; replay detection is the main unknown.
8. Failure invalidates X2 only; X1 remains.

## 4. Task 4 — kill test
Question applied to each: *can it be measured from broadcast wrestling footage with the current architecture without pretending the unresolved anatomy, identity or camera problems are solved?*

| ID | Candidate | Verdict | Reasons |
|---|---|---|---|
| X1 | Match duration | **PROCEED** (comparator) | needs no CV; any other variable must add to it |
| X2 | Observable live-action time with bounds | **NEEDS VALIDATION** (the V1 deliverable) | scene-level; needs no identity, ownership or scale; replay/close-up classification untested; fail-closed bounds make errors visible |
| X3 | Engagement fraction | **PARK** (candidate V1.1 only if X2 is KEEP) | meaningful (grappling is physical exposure) but sits on the unresolved contact failure zone (T5 hard ceiling for single-frame 2D); needs human-labelled engagement reference and a separately authorised design |
| X4 | Grounded-person event count | **PARK** | plausible but box-merging in clinches, replay double-counting and per-wrestler attribution make it unsafe today; revisit only with a replay detector (from X2) and an orientation measure validated against human counts |
| X5 | Distance/speed/acceleration | **KILL for broadcast footage** | pixel displacement is not distance: no calibration, cuts, pan/zoom; identity unreliable; V0.1 pixel coordinates were never shown comparable across cuts. Revisit only if the CMJ study yields **fixed, calibratable** camera video (then a separate design) |
| X6 | Aerial/jump–landing count | **PARK** | lower-extremity relevant but needs per-body pose in motion and a camera-invariant vertical reference |
| X7 | Impact/contact load | **KILL** | no force/acceleration measure from 2D video; contact interpretation unresolved; any number would be unvalidatable |
| X8 | Per-wrestler on-camera time | **KILL** | identity unvalidated; measures the director, not the wrestler |
| X9 | Pose-derived intensity | **KILL** | ownership contamination (23% of assigned controls), carry, stride-3 sampling, single-view 2D, no scale |
| X10 | COM trajectory | **KILL** | sophisticated-looking, scientifically undefendable here (ownership, scale, mass model, calibration) |
| X11 | Rest/recovery structure | **PARK** | derived quantity; editing hides rest; revisit after X2 |
| X12 | Cut rate/shot count | **KILL as exposure** | production artefact; retained only as an editing-density covariate/diagnostic |

Carried anatomy is excluded from every measurement variable by construction. Nothing is derived from the qualitative MP4.

## 5. Task 5 — minimum Exposure V1
**Scientific purpose.** Provide an objective, reproducible account of the *time structure* of a broadcast match — total duration and the bounded amount of observable live action — and test, cheaply and informatively, whether any CV-derived time variable adds value beyond match duration. It is a measurement-validity study of a scene-level variable, **not** a workload-validity claim.

**Exact outputs (per match; no per-wrestler field exists).**
D (X1); T_live_lo, T_live_hi, T_closeup, T_replay, T_nonmatch, T_unknown (X2); coverage C; evaluability flag with reason; per-shot class table (private); code/manifest hash. Provenance: input hash, shot-boundary hash, box-input hash.

**Required inputs.** Full-match video (or declared segment), frozen shot boundaries, frozen stride-3 person detection boxes. Forbidden inputs (test-enforced): identity, skeleton, ownership, masks, merge-guard output, carried rows, any verdict, any COM/distance/speed field.

**Deliberately NOT measured.** Anything per wrestler; distance, speed, acceleration, COM; impacts, falls, jumps, landings; contact/engagement; joint kinematics; intensity; rest/recovery; internal load; fatigue; injury risk. T_live is observable broadcast time, not total activity.

**Failure/abstention behaviour (fail-closed).** A shot that does not meet the preregistered rule for a class is UNKNOWN, never silently LIVE. UNKNOWN time widens the interval [T_live_lo, T_live_hi]. A match is NOT_EVALUABLE if UNKNOWN > 15% of D, if the shot-boundary check fails, or if the video is a declared partial segment without a marked start/end. Replay-classified time can never enter T_live.

**Classifier complexity budget (to avoid open-ended engineering).** Shot class by a deterministic rule on at most 3 shot-level features from the frozen detections (for example number of person boxes above the frozen height gate, largest box height relative to frame height, fraction of frames with ≥ 2 such boxes) plus a replay indicator. The rule is built on development data within a fixed budget of at most 5 thresholds and **one** revision round; if it cannot meet the development floors (below), Exposure V1 stops with KILL-at-development and no fresh data are consumed. No learned classifier unless this simple rule fails and the reviewer authorises a specific alternative.

**Validation strategy (what can and cannot be shown).**
Chain: (1) *measurement validity* against human reference labels — testable here; (2) *convergent/incremental value* versus duration — testable here; (3) *criterion validity* against post-match CMJ deviation — **not testable by the CV project**; it requires the separate human-subject CMJ study with within-wrestler baselines and several matches per wrestler with different exposures. Exposure V1 must not claim (3).
Reference standard: shot-level labels (LIVE / REPLAY / CLOSE-UP / NON-MATCH) and start/end marks by a human labeller on every evaluation match; 20% double-labelled for agreement. R4 (independent human reviewer) is still unmet, so labels remain ANNOTATION-PROVISIONAL until one is available.

**Development data.** The remaining ~630 s of the fresh Reigns–Bálor match (the first 150 s were used for the qualitative MP4 and are treated as seen) and the four burned development clips (short; shot-structure labelling only). Used for rule construction and the futility check; never for confirmation.

**Fresh/held-out data.** At least 12 evaluable **full** matches (planning floor), from at least 3 distinct events/sources, not used in development, with start/end definable; fresh acquisition by the owner under unresolved rights (no redistribution; no footage in GitHub). Holdout #2 stays sealed and is not part of this design. Note: the existing ~18 short-clip acquisition plan is for the separated-body study and does not satisfy the full-match requirement; a different acquisition is needed.

**Preregistered KEEP/MODIFY/KILL (proposed, reviewer-settable; unit of analysis = match; cluster over shots ignored; intervals over matches).**
Primary estimands per match: reference T_live_ref from human labels.
- P1 duration-weighted shot-class disagreement for LIVE vs not-LIVE ≤ 10% (UNKNOWN counted as not-LIVE in the lower bound).
- P2 interval honesty: T_live_ref inside [T_live_lo, T_live_hi] in ≥ 90% of evaluable matches.
- P3 replay leakage (replay seconds in T_live_hi) ≤ 5% of T_live_hi.
- P4 abstention: UNKNOWN ≤ 15% of D in ≥ 80% of matches.
- P5 value over duration: Spearman correlation across matches between T_live_lo and D < 0.95; if ≥ 0.95 the result is NO_ADDED_VALUE.
Outcomes: **KEEP** = P1–P4 pass and P5 passes. **NO_ADDED_VALUE** = P1–P4 pass but P5 fails (T_live ≈ duration; use D alone). **MODIFY** = P1, P2 and P3 pass but P4 fails (rule too conservative), or one of P1–P3 fails by ≤ 5 points. **KILL** = P1 > 20%, or P2 < 70%, or P3 > 15%. **INCONCLUSIVE_DATA** = fewer than 12 evaluable matches or fewer than 3 distinct sources.
Honest caveat: the thresholds are reviewer-set utility choices, not statistically derived; with 12 matches the intervals are wide and P5 has low power. Development futility gate: if on development data P1 > 20% after the single revision round, stop.

**What each outcome teaches.** KEEP: scene-level observable time can be measured fail-closed from broadcast video; proceed to a staged V1.1 (X3 engagement) under a new design. NO_ADDED_VALUE: duration suffices as the time exposure; CV adds no time information, and per-body exposure remains blocked by the unresolved anatomy/identity/camera issues. MODIFY: the rule is sound but over-abstains; one scoped revision with new fresh data. KILL: even scene-level broadcast structure cannot be extracted cheaply; stop CV exposure on edited broadcasts and redirect effort to controlled capture. INCONCLUSIVE_DATA: acquire more matches; no outcome.

## 6. Dependencies and risks
- Broadcast editing means X2 is a lower bound with an interval, not total activity; real activity during close-ups, cutaways and removed ad breaks is invisible.
- Match-level variables cannot separate wrestlers; any within-match role difference stays unmeasured.
- R4 unmet; labels ANNOTATION-PROVISIONAL; single labeller bias; start/end definitions can be ambiguous.
- A full-match corpus must be acquired under unresolved rights; this is an owner action.
- The study that supplies CMJ outcomes determines whether the video is broadcast or study-controlled; this changes what is feasible (section 8).

## 7. Handoff requirements for the CMJ study (so V1 is usable)
Record match identifiers and video source/timecodes; both wrestlers' baselines and post-match CMJ with timing; the match's official start/end; any wearable/IMU/GPS or heart-rate data on even a few matches (these would be the only external reference that could later validate CV locomotor or impact variables); and whether a fixed, calibratable camera is available.

## 8. Decisions requested from the owner/reviewer
1. **Video regime:** will the CMJ study use edited broadcast footage, study-controlled fixed-camera video, or both? (If fixed-camera, X5 locomotor variables become a separate design; if broadcast only, they stay killed.)
2. **Match-level exposure:** is a variable shared by both wrestlers acceptable as the V1 deliverable?
3. **Reference labeller:** may the owner label shot classes (low burden) pending R4, with the provisional status disclosed?
4. **Acquisition:** approve acquisition of at least 12 full matches from at least 3 distinct sources for fresh confirmation (separate from the ~18 short clips).
5. **Thresholds:** approve or set P1–P5 and the outcome map; confirm the complexity budget and the development futility gate.
6. **Comparator:** confirm that duration D must be reported and that NO_ADDED_VALUE is an acceptable outcome.

## 9. Evidence used (repository, no new computation)
`v061/anatomical_assessment/ANATOMY_V1_FINAL_DEVELOPMENT_ASSESSMENT.md`; `v061/devrun_results/DEVRUN_REPORT_V1.md` and `SECONDARY_REPORT_V1.md`; `versions/holdout1/HOLDOUT1_REPORT.md`; `baseline_v0.1/README.md`; `v061/anatomical/OUTPUT_SCHEMA.md`; `v061/sep_eval/SEPARATED_BODY_EVALUATION_V1_FINAL_PROTOCOL.md`; ledger entries ANA9–ANA18 (C3 closure, fresh MP4); private AR1 metrics (M2, M5, M6, M8); fresh-segment shot count (54 in 150 s).

STOP for independent reviewer audit. Nothing implemented.
