# SEPARATED-BODY EVALUATION V1 — FINAL PROTOCOL (readiness candidate; NOT EXECUTED on fresh data)

Frozen Anatomy V1 (implementation manifest f5936ce8…) is unchanged. No tuning. No exposure. Holdout #2 and Gemini untouched. Development-only, ANNOTATION-PROVISIONAL, not validation. Rights UNRESOLVED.
This document finalizes `v061/anatomical_separated_eval_design/SEPARATED_BODY_EVALUATION_PROTOCOL_V1_PROPOSAL.md` with the reviewer rulings D1–D6. Where they differ, this document governs.

## 1. Claim ceiling (unchanged, verbatim)
This evaluation tests **anatomical body ownership under the pre-specified separated-body condition only**. It does not validate joint localization, temporal accuracy, identity, exposure, workload, or generalization. KEEP at most supports: "on this fresh development sample, under the separated-body criterion, emitted ASSIGNED skeletons were on the assigned detection's person at a rate whose exact upper bound was X."

## 2. Rulings incorporated
- **D1-A** fresh development footage, used solely for this evaluation: ≥6 clips (see feasibility, section 8, for why more are needed), ≥3 sources/eras/resolutions, ≥2 promotions, new events only; the four burned clips are never confirmatory; D1-B supplementary only if independently eligible and documented; D1-C cannot support KEEP; Holdout #2 sealed.
- **D2** independent human primary + project owner blinded second + Claude disclosed non-independent sensitivity. Claude never determines the gate. If a genuinely independent human primary cannot be obtained: STOP and report; Claude is never substituted as the independent reviewer.
- **D3** eligibility parameters frozen (section 3). No post-hoc tuning; 10%/25% margin analyses are secondary and non-gating.
- **D4** governing KEEP criterion = upper limit of the exact Clopper-Pearson two-sided 95% CI of the WRONG_BODY frame proportion ≤ 5.0%. Allowable event counts are computed from the realized judgeable n (section 5), not hard-coded.
- **D5** 50-frame INELIGIBLE_ASSIGNED contrast stratum kept, descriptive, non-gating.
- **D6** KEEP must independently satisfy every applicable criterion under BOTH human reviewers; no pooling or averaging; the less favorable human result binds.

## 3. Eligibility (frozen; `v061/sep_eval/impl/eligibility.py`)
Geometry only. Inputs: person-class detection boxes and confidences, frame size, stride-3 neighbours, frozen shot index. No skeleton, ownership state/reason, merge guard, identity or verdict input exists (test-enforced). ELIGIBLE iff all hold at frame f and at f−3 and f+3 (same tracklet, same shot):
1. no other person detection with confidence ≥ 0.10 and box height ≥ 25% of the target box height has positive-area overlap with the target box expanded by 15% of its width/height per side (edge-touching does not count);
2. target box ≥ 2% of frame size from every border;
3. target box height ≥ 15% of frame height;
and no camera cut (frozen shot index) within ±3 frames of f. Secondary non-gating margins: 10% and 25%.
Known limit (reported, not tuned): detector misses can make contact frames look separated (measured by the audit); duplicate/fragment detections of the same person count as "other persons" under the literal rule. A descriptive, NOT ADOPTED variant ignoring boxes ≥80% inside the target box raised the burned-clip eligible count 145 → 170 (section 8) and is not part of the protocol.

## 4. Sampling (frozen; `sep_sample.py`)
Seed = int(sha256(protocol_freeze_hash)[:8],16) mod 2^31, where protocol_freeze_hash is the sha256 of this file as registered in the reviewer-approved FREEZE ledger entry that follows the reviewer's inspection of this readiness candidate (SEP1 registers the candidate only; the seed cannot be known before the final freeze). ELIGIBLE stratum: target 150 frozen ASSIGNED_A/B measured rows; ≥30 distinct shots, ≥4 clips (targets; shortfalls reported, never relaxed); source-frame spacing ≥30 within a clip across both strata; ≤10 per shot; ≤40% from one clip; proportional by clip availability. INELIGIBLE stratum: 50 ASSIGNED rows failing the criterion, clip-matched to the eligible picks. Items are shuffled across strata with ids S000…; the blind sheet has only item_id, clip, frame, box. Clips in the burned list are rejected by the sampler.

## 5. Statistics and mechanical decision (frozen; `impl/sep_stats.py`, `sep_join.py`)
Frame verdict is derived, never typed: NOT_JUDGEABLE if the reviewer marks it or fewer than 3 landmarks are drawn; WRONG_BODY if any landmark or bone is attributed to another person; OFF_BODY_ONLY if only off-body landmarks (localization, not an ownership error); else OWNERSHIP_CORRECT.
Per human reviewer, on ELIGIBLE frames:
- **INCONCLUSIVE_DATA** (no KEEP/MODIFY/KILL) if judgeable < 100, or shots with a judgeable frame < 20, or clips < 3.
- **KILL** if WRONG_BODY point estimate ≥ 10.0%; or WRONG_BODY frames in ≥ 3 distinct shots; or audit false-eligibility > 10.0%; (or irreproducible recomputation).
- **KEEP** if all: exact 95% upper bound ≤ 5.0%; WRONG_BODY in ≤ 1 distinct shot; audit false-eligibility ≤ 5.0%; NOT_JUDGEABLE ≤ 20%.
- otherwise **NOT_KEEP_NEEDS_REVIEWER_INTERPRETATION** (no pathway change; stays visualization-only).
Final = the less favorable of the two human reviewers (binding order as coded: INCONCLUSIVE_DATA first, per the approved minimum-data rule; then KILL; then NOT_KEEP; KEEP only if both reviewers KEEP). Claude's sensitivity file is reported separately and cannot change the final.
Audit false-eligibility = frames judged OTHER_BODY_TOUCHING_OVERLAPPING / frames with an answered audit (CANNOT_TELL excluded from the denominator and reported).
**Allowable KEEP event counts (computed by `sep_stats.max_events_keep`, two-sided exact 95% upper ≤ 5.0%):** n=100 → 0; 120 → 1; 150 → 2 (upper 4.73%); 200 → 3. At n=150 the one-sided 95% bound gives the same count (2 events 4.14%, 3 events 5.09%), so "≤2 at n=150" is confirmed by exact computation, but the rule used is the computed bound at the realized n. (A frame-level bound ignores clustering within shots; the ≤1-shot criterion is the cluster guard.)
Secondary reported (non-gating): contrast-stratum rates; margin-10% and margin-25% eligible subsets; per-clip rates; OFF_BODY_ONLY rate; box_person (non-wrestler emission) and optional A/B correctness against owner annotation (ANNOTATION-PROVISIONAL); primary-vs-owner agreement (raw, kappa on WRONG_BODY).

## 6. Review (frozen forms: `RESPONSE_TEMPLATE.csv`; images: `sep_review_pack.py`)
Step 1 (folder step1/): unannotated frame with only the assigned box outlined → `box_person` ∈ {WRESTLER, REFEREE, SPECTATOR_OTHER, MULTIPLE_PERSONS_IN_BOX, CANNOT_TELL}, `separation_audit` ∈ {SEPARATED, OTHER_BODY_TOUCHING_OVERLAPPING, CANNOT_TELL}. All step-1 entries must be completed for every item before step2/ is opened. Step 2 (folder step2/): same layout with the frozen ASSIGNED skeleton and landmark index labels → `judgeable`, `landmarks_other_person`, `bones_other_person` ("5-7;6-8"), `landmarks_off_body`.
Reviewers: (1) independent human primary — not a developer, not the owner, dated independence attestation ledgered before review; (2) project owner, blinded, 100% of items; (3) Claude, completed and frozen blind, sensitivity only. No reviewer sees another's verdicts, strata, ownership/identity/merge-guard state, eligibility flags or any result before all files are frozen and hashed; the hidden key is joined exactly once afterwards.

## 7. Fresh-data intake (requires owner action; NOT performed)
1. Owner supplies ≥6 new clips (see section 8 on volume) with NAMES/metadata only; events/sources/uploads disjoint from every development clip and from Holdout #2; Jeff Hardy excluded; Cena development-only; no Holdout #2 identity; no re-identification from appearance; unsupported metadata stays UNRESOLVED.
2. Duplicate/replay audit against all development clips with the existing dHash tool (counts and pass/fail only), manual spot check.
3. Run the **unchanged** frozen pipeline (V0.6.1 identity rule, V0.5 ownership, record classifier, stride-3 pose) on the new clips. **Open item for the reviewer (R3):** the frozen identity layer needs per-clip enrolment/seed episodes under the strict seed rule; the procedure for obtaining ACCEPT_A/B on new identities out-of-fold (no new head training, no tuning) must be confirmed by the reviewer before the run.
4. Only then: feasibility count (`feasibility_count.py`) on the new rows, ledgered; reviewer inspects; only after authorization: registration → sampling → images → blinded reviews frozen → single key join → report → STOP.

## 8. Feasibility result (no fresh clips exist yet; INDICATIVE ONLY)
Fresh-data feasibility count: **NOT POSSIBLE YET** (no fresh clips or pipeline outputs). Using the four burned clips from frozen outputs only (counts; no verdicts, images or skeletons viewed; cannot support KEEP):
- 771 ASSIGNED_A/B measured rows; **145 eligible (18.8%)**; 152 at margin 10%; 102 at margin 25%; descriptive non-adopted variant: 170.
- Eligible rows fall in only 17 of 64 shots carrying ASSIGNED rows (per clip: 2/9, 11/30, 1/19, 3/6).
- Dominant causes (descriptive): neighbouring frame has another person within the margin, neighbour near border, tracklet absent at a neighbour.
- Applying the frozen sampling constraints (spacing ≥30, ≤10/shot) the selectable eligible frames number only **≈34 over 17 shots** in these clips (≈45 at spacing 15; ≈74 with spacing 0, shot cap binding), because eligible frames cluster in a few shots.
- Total source footage ≈ 10,233 frames. At this indicative yield (≈3.3 selectable eligible frames per 1,000 source frames, ≈1.7 shots per 1,000): minimum data (≥100 judgeable, assuming ~85–90% judgeable) needs roughly ≥3× this footage in fresh clips (~30–35k source frames, e.g. ~14 clips of similar length); the 150-frame target needs roughly 4–5× (~45k frames, ~18 clips of similar length); 20 shots need ≥12k frames. **A 6-clip acquisition at this yield would likely end INCONCLUSIVE_DATA.** Yield on fresh clips can be higher or lower: it depends on identity ACCEPT coverage and footage style; the burned clips are one data point.
These are feasibility facts, not criteria changes; no rule was relaxed.

## 9. Decisions/items requested of the reviewer before any execution
R1 Fresh-footage volume target (~14–18 clips of similar length, or equivalent minutes) instead of ≥6; or accept the INCONCLUSIVE_DATA risk. R2 Confirm the frozen spacing (30) and per-shot cap (10) stay; any change would be a design amendment, not tuning on results. R3 The identity run procedure for new clips (section 7.3). R4 Name and attestation process for the independent human primary reviewer (execution blocked until obtained). R5 Confirm acceptance of the literal duplicate-detection behaviour (section 3). R6 Authorize acquisition of the clips and the pipeline run on them.

## 10. Frozen artifacts in this package
`impl/eligibility.py`, `impl/sep_stats.py`, `impl/drawn.py`, `feasibility_count.py`, `sep_sample.py`, `sep_review_pack.py`, `sep_join.py`, `RESPONSE_TEMPLATE.csv`, `tests/test_sep_eval.py` (27 synthetic tests), this protocol, `SEP_FEASIBILITY_BURNED_INDICATIVE_V1.json`, package scripts, `DEPENDENCY_HASHES.txt`. Candidate hashes are ledgered at SEP1; the binding freeze entry (and the protocol_freeze_hash that seeds sampling) is written only after reviewer approval of this candidate.

## 11. Prohibited (unchanged)
All Section 7 prohibited downstream uses of `ANATOMY_V1_FINAL_DEVELOPMENT_ASSESSMENT.md`; no exposure, COM, distance, speed, acceleration, impact, workload, fatigue or injury inference; no tuning of Anatomy V1 or of the criterion; no use of M9/M9B/M9C verdicts as confirmatory evidence; no Holdout #2 or Gemini.
