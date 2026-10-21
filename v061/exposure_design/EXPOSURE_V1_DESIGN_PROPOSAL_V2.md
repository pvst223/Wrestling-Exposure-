# EXPOSURE V1 — DESIGN PROPOSAL V2 (design only; nothing implemented, nothing run)

Status: revision for independent reviewer audit, incorporating the reviewer ruling "EXPOSURE V1 DESIGN V1: MODIFY / PROCEED TO REVISED DESIGN". Development-only, ANNOTATION-PROVISIONAL, IDENTITY_UNVALIDATED, rights UNRESOLVED; contact/overlap ownership unresolved. Nothing here validates identity, anatomical ownership, exposure or workload, and nothing is inferred from the fresh qualitative MP4. Not used or reopened: Holdout #2, Gemini, C3, partial-release anatomy, Anatomy V1 tuning, identity training.

## 0. What changed from V1 (ruling → revision)
| Ruling | Where it is incorporated |
|---|---|
| Frame V1 as a scene/time foundation, not wrestler-specific workload | section 0.1 (terminology), 1, 5 (claim limit), 8 |
| Video regime BOTH (broadcast now; fixed calibratable view planned for the CMJ study where feasible; no locomotor metric authorized now) | sections 1, 4 (X5), 7, 8 (roadmap) |
| Match-level exposure accepted with limited claim | sections 0.1, 5 |
| Owner reference labels approved for development only (ANNOTATION_PROVISIONAL; R4 unmet) | section 6 |
| Fresh acquisition DEFERRED; development futility gate first | sections 6, 7 (stage D before stage F) |
| P1–P4 and fail-closed UNKNOWN retained; P5 recast as a secondary descriptive analysis, no rho = 0.95 cutoff | section 5 |
| NO_ADDED_VALUE remains an authorized outcome | section 5 |
| D always reported | sections 3, 5 |
| Staged roadmap | section 8 |

## 0.1 Terminology and the limit of the claim
- **Broadcast scene/time exposure** (what Exposure V1 measures): how long the match lasted (D) and how much of the broadcast timeline shows live in-ring action, replays, close-ups and non-match material (X2 and its bounds). It is a property of the *match as broadcast*.
- **Wrestler-specific physical workload** (what V1 does NOT measure): what a particular wrestler's legs actually did — loads, jumps, landings, falls, distance, speed, grappling effort — and internal load. None of these is estimated.
- Consequence for the eventual outcome (individual within-wrestler post-match CMJ deviation): X1 and X2 are **shared by both wrestlers of a match** and cannot represent role differences (aggressor vs bump-taker), so they are at most a *necessary scene/time foundation* for later, richer variables. They may be related to CMJ deviation only through between-match contrasts within a wrestler (several matches per wrestler with different durations/observable live time), and any such relationship would remain confounded by unmeasured role-specific load. V1 must never be described as complete or sufficient workload.

## 1. Task 1 — the exposure construct
**Question.** Does professional-wrestling workload cause measurable deterioration in lower-extremity neuromuscular function (acute within-wrestler post-match CMJ deviation from baseline)? Exposure V1 provides *objective, external, scene-level* variables that could later be related to that outcome; it is the first rung of a ladder, not the ladder.

**Definition (project).** *Match exposure* = the external, observable physical activity a wrestler undergoes during a match, as far as it can be recovered from video. It is not internal load (heart rate, RPE, metabolic cost, muscle damage, fatigue), which video does not measure, and it is not a risk or injury quantity.

| Domain | What it would mean | Observable now? |
|---|---|---|
| Duration/time | bell-to-bell time; time in live action | Yes in principle (broadcast clock, shot structure); edited broadcasts hide unseen time. **This is Exposure V1.** |
| Movement/locomotor | distance, speed, accelerations, ring coverage | No on broadcast (no calibration, moving/zooming cameras, cuts, identity unvalidated). May be reopened only under a separate prospective fixed-camera design |
| Action/event | counts of bumps, jumps, landings, strikes, throws | No reliably: needs per-body pose in contact (unresolved) or event detectors that do not exist |
| Contact/interaction | time in grappling, impacts, holds | Contact is exactly where ownership fails (7/30 contaminated assigned controls; no contact detector) |
| Intensity proxies | speed, joint velocities, movement energy | Pixel kinematics from a moving single view are not physically comparable; contaminated by ownership |
| Recovery/rest structure | pauses, work:rest | Only indirectly (derived from live-time structure); editing hides real rest |
| Internal load | physiological response | **Not measurable by this system**; must come from the CMJ study / wearables |

Structural limitations of every candidate: (1) a match-level variable is shared by both participants (section 0.1); (2) a broadcast is an *edited sample* of the match (cuts, replays, graphics, close-ups, cutaways, possibly removed commercial breaks), so observed time is at best a lower bound on real activity.

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

**X2 — Observable live-action time with bounds (broadcast scene/time exposure).**
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
| X5 | Distance/speed/acceleration | **KILL for broadcast footage; may be reopened only under a separate prospective fixed-camera design** | pixel displacement is not distance: no calibration, cuts, pan/zoom; identity unreliable; V0.1 pixel coordinates were never shown comparable across cuts. Owner ruling: the eventual CMJ study should, where feasible, add a fixed, study-controlled, calibratable ring view; this does NOT authorize any locomotor metric now |
| X6 | Aerial/jump–landing count | **PARK** | lower-extremity relevant but needs per-body pose in motion and a camera-invariant vertical reference |
| X7 | Impact/contact load | **KILL** | no force/acceleration measure from 2D video; contact interpretation unresolved; any number would be unvalidatable |
| X8 | Per-wrestler on-camera time | **KILL** | identity unvalidated; measures the director, not the wrestler |
| X9 | Pose-derived intensity | **KILL** | ownership contamination (23% of assigned controls), carry, stride-3 sampling, single-view 2D, no scale |
| X10 | COM trajectory | **KILL** | sophisticated-looking, scientifically undefendable here (ownership, scale, mass model, calibration) |
| X11 | Rest/recovery structure | **PARK** | derived quantity; editing hides rest; revisit after X2 |
| X12 | Cut rate/shot count | **KILL as exposure** | production artefact; retained only as an editing-density covariate/diagnostic |

Carried anatomy is excluded from every measurement variable by construction. Nothing is derived from the qualitative MP4.

## 5. Task 5 — minimum Exposure V1
**Scientific purpose.** Provide an objective, reproducible account of the *time structure of a broadcast match* — total duration D and the bounded amount of observable live action — as the scene/time foundation for later exposure variables, and test cheaply and informatively whether a scene-derived live-time variable carries usable information. It is a measurement-validity study of a scene-level variable. It is **not** a workload-validity claim and **not** a wrestler-specific measure.

**Exact outputs (per match; no per-wrestler field exists).**
D (X1, always reported); T_live_lo, T_live_hi, T_closeup, T_replay, T_nonmatch, T_unknown (X2); coverage C = T_live_lo / D; evaluability flag with reason; per-shot class table (private); code/manifest hash; input/shot-boundary/box-input hashes.

**Required inputs.** Full-match video (or declared segment), frozen shot boundaries, frozen stride-3 person-detection boxes. **Forbidden inputs and fields (dependency tests, as in SEP V1):** identity, anatomy/skeleton, ownership state/reason, masks, merge-guard output, carried (visualization-only) anatomy, any verdict, any COM or physical-distance/speed/acceleration field. The tests scan inputs, schema and code for these tokens and fail closed.

**Deliberately NOT measured.** Anything per wrestler; distance, speed, acceleration, COM; impacts, falls, jumps, landings; contact/engagement; joint kinematics; intensity; rest/recovery; internal load; fatigue; injury risk. T_live is observable broadcast time, not total or wrestler-specific activity.

**Failure/abstention behaviour (fail-closed, unchanged).** A shot that does not meet the preregistered rule for a class is UNKNOWN, never silently LIVE. UNKNOWN time widens [T_live_lo, T_live_hi]. A match is NOT_EVALUABLE if UNKNOWN > 15% of D, if the shot-boundary check fails, or if the video is a declared partial segment without marked start/end. Replay-classified time can never enter T_live.

**Classifier complexity budget (unchanged).** Deterministic rule on at most 3 shot-level features from the frozen detections (e.g. number of person boxes above the frozen height gate, largest box height relative to frame height, fraction of frames with ≥ 2 such boxes) plus a replay indicator; at most 5 thresholds; **one** revision round. No learned classifier unless this fails and the reviewer authorises a specific alternative.

**Criteria (P1–P4 as before; P5 recast).** Unit of analysis = match; reference T_live_ref from owner labels (ANNOTATION_PROVISIONAL).
- P1 duration-weighted LIVE vs not-LIVE shot-class disagreement ≤ 10% (UNKNOWN counted as not-LIVE for the lower bound).
- P2 interval honesty: T_live_ref inside [T_live_lo, T_live_hi] in ≥ 90% of evaluable matches.
- P3 replay leakage (replay seconds inside T_live_hi) ≤ 5% of T_live_hi.
- P4 UNKNOWN ≤ 15% of D in ≥ 80% of matches.
- **P5 (secondary, descriptive — no cutoff).** Incremental information over duration is reported, not decided by a threshold: the joint distribution and relationship of T_live_lo, coverage C and D across matches (scatter, rank correlation with interval, ratio T_live_lo / D with range, residual of T_live_lo after regressing on D), with uncertainty. No rho value is a KEEP or NO_ADDED_VALUE cutoff in the initial evaluation. Any later inferential or decision threshold must be justified for the eventual sample (including how many matches per wrestler the CMJ study will have) and requires a new reviewer ruling.

**Outcomes.**
- **KEEP**: P1–P4 pass. KEEP means the scene/time partition is measurable fail-closed; it does **not** assert added value over D (reported descriptively under P5) and does not assert workload validity.
- **NO_ADDED_VALUE** (authorized scientific outcome): P1–P4 pass but the descriptive P5 evidence shows that scene-derived live time contributes essentially no useful information beyond D, as judged by the reviewer from the descriptive analysis (not by an automatic cutoff). Meaning: duration alone is the usable time exposure.
- **MODIFY**: P1, P2 and P3 pass but P4 fails (rule over-abstains), or one of P1–P3 fails by ≤ 5 points.
- **KILL**: P1 > 20%, or P2 < 70%, or P3 > 15%.
- **INCONCLUSIVE_DATA**: fewer than 12 evaluable matches or fewer than 3 distinct sources (applies to the confirmatory stage only).
Caveat: thresholds are reviewer-set utility choices, not statistically derived; with ~12 matches the intervals are wide.

**What each outcome teaches.** KEEP: scene-level observable time can be measured fail-closed from broadcast video; a reviewer decision follows on V1.1 candidates. NO_ADDED_VALUE: CV adds no time information beyond D; per-body exposure stays blocked by unresolved anatomy/identity/camera issues. MODIFY: sound but over-abstaining; one scoped revision. KILL: even scene-level broadcast structure cannot be extracted cheaply; stop CV exposure on edited broadcasts and direct effort to controlled capture. INCONCLUSIVE_DATA: acquire more matches; no outcome.

## 6. Development stage D (the futility gate; occurs BEFORE any fresh acquisition)
Only authorized development material is used. No fresh clip or match is acquired for this stage.

**Material.** The Reigns–Bálor match beyond the first 150 s (about 629 s of the 779 s source; the first 150 s were already used for the qualitative MP4 and are treated as seen, which does not affect shot-class labelling), and the four burned development clips (short). Footage stays private; rights UNRESOLVED.

**Reference labels.** The owner labels every shot of the development material as LIVE / REPLAY / CLOSE_UP / NON_MATCH (plus start/end marks for D on the match), ANNOTATION_PROVISIONAL; R4 remains unmet, labeller is non-independent of the project, and this is disclosed in every output. A labelling protocol (category definitions with examples, borderline rules, tool) will be written for audit **before** labelling begins; labelling instructions and any examples will not be changed after rule construction starts.

**Fixed split (set before labels exist).** Rule build set = burned short clips + the match from 150 s to 450 s; check set = the match from 450 s to 779 s. The rule is built using the build set only (complexity budget above), frozen, then evaluated once on the check set. One revision round is allowed after the check; a second check after revision is reported as **not independent**.

**Gate outcomes (futility only; the gate cannot yield KEEP).**
- **STOP (KILL-at-development)**: P1 > 20% on the check set after the single revision round, or replay leakage (P3) > 15%.
- **CONTINUE**: P1 ≤ 20% and P3 ≤ 15% on the check set. This only makes a request to acquire fresh full matches *justified*; it does not authorize acquisition. The reviewer rules on acquisition separately after seeing the stage D report.
Honest limits: one condensed match plus short clips is a small, non-diverse sample (one source/production style); stage D can show futility, not success; development performance will be optimistic relative to fresh data.

**Fresh stage F (conditional, DEFERRED).** Only after a CONTINUE result and a separate reviewer authorization: acquire ≥ 12 evaluable **full** matches from ≥ 3 distinct sources (planning floor), not used in development, with definable start/end; owner labels shots (≥ 20% double-labelled if a second labeller becomes available); the frozen rule is run once; P1–P4, descriptive P5 and the outcome map above apply. Holdout #2 remains sealed and is not part of this design. The existing ~18 short-clip acquisition plan does not satisfy the full-match requirement.

## 7. Dependencies, risks and the CMJ-study handoff
- Broadcast editing makes X2 a lower bound with an interval; real activity during close-ups, cutaways and removed ad breaks is invisible.
- Match-level variables cannot separate wrestlers; within-match role differences remain unmeasured and confound any relation to individual CMJ deviation.
- R4 unmet; labels ANNOTATION_PROVISIONAL; single labeller bias; start/end definitions can be ambiguous.
- Rights UNRESOLVED; a full-match corpus (stage F) is an owner action and not authorized yet.
**Handoff requirements for the CMJ study:** record match identifiers, video source/timecodes, official start/end; both wrestlers' baselines and post-match CMJ with timing; several matches per wrestler where possible (to allow within-wrestler contrasts); any wearable/IMU/GPS/heart-rate data on even a few matches (the only external reference that could later validate CV locomotor or impact variables). **Fixed-camera plan (planning only, not an authorization):** where feasible, add a fixed, study-controlled, calibratable view of the ring (static camera, ring corners/posts visible, known ring dimensions, constant frame rate with synchronised timestamps, no digital zoom, unobstructed lines of sight); its use for any locomotor variable would require a separate prospective design and validation protocol.

## 8. Staged roadmap (each arrow is a separate reviewer decision; none is authorized by this document)
`Stage D: development futility gate on authorized development material → [STOP | CONTINUE] → reviewer decision on fresh acquisition → Stage F: Exposure V1 scene/time confirmation on fresh full matches (KEEP / NO_ADDED_VALUE / MODIFY / KILL / INCONCLUSIVE_DATA) → validation decision → possible V1.1 engagement/event candidates (X3 engagement fraction, X4 grounded-person events, X6 jump/landing, X11 rest structure; each needs its own design, reference standard and fresh data) → eventual fixed-camera locomotor design only if prospective capture permits (calibration, scale, identity, validated against a physical reference) → CMJ criterion-validity study (outside the CV project: within-wrestler post-match CMJ deviation vs exposure variables).`
Exposure V1 supplies only the first two boxes; it does not claim to supply the others.

## 9. Open items for the reviewer (V2)
1. Approve the stage D design: material, fixed build/check split, one-revision rule, futility thresholds (P1 > 20%, P3 > 15%).
2. Approve writing the owner labelling protocol next (for audit before any labelling).
3. Confirm the recast P5 (descriptive only, no cutoff) and the NO_ADDED_VALUE reviewer-judgement rule.
4. Confirm that stage F fresh acquisition stays deferred until a CONTINUE report is reviewed.

## 10. Evidence used (repository, no new computation)
`v061/anatomical_assessment/ANATOMY_V1_FINAL_DEVELOPMENT_ASSESSMENT.md`; `v061/devrun_results/DEVRUN_REPORT_V1.md` and `SECONDARY_REPORT_V1.md`; `versions/holdout1/HOLDOUT1_REPORT.md`; `baseline_v0.1/README.md`; `v061/anatomical/OUTPUT_SCHEMA.md`; `v061/sep_eval/SEPARATED_BODY_EVALUATION_V1_FINAL_PROTOCOL.md`; ledger entries ANA9–ANA18 (C3 closure, fresh MP4); private AR1 metrics (M2, M5, M6, M8); fresh-segment shot count (54 in 150 s).


STOP for independent reviewer audit. Nothing implemented.
