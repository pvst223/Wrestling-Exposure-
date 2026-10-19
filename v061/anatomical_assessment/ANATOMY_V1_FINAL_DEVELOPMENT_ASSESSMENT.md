# ANATOMY V1 FINAL DEVELOPMENT ASSESSMENT (documentation and analysis only)

Sources: only already-frozen evidence (Anatomical Integration V1 execution AR1, M9, M9B, M9C). No new computation of anything beyond re-reading frozen counts. No exposure, COM, distance, speed, impact, workload or fatigue computed. No Holdout #2, new footage or Gemini. No new classifier or gate designed. Label for everything below: **development-only, ANNOTATION-PROVISIONAL, single non-independent primary reviewer (Claude, also the implementer), owner second review on a 50-item subset only. Not validation. Rights UNRESOLVED.**

## 0. Reviewer rulings recorded (M9C)
1. KILL of `RELEASED_PARTIAL_ANATOMY_A/B` confirmed. Reverted scientifically to frozen Anatomical Integration V1 behavior; the partial-release class is not part of any production/development anatomy pipeline. No retuning of Tier A, thresholds, structural minimums, reason families, merge guard or sampling from M9C. No M9D / Tier-A permutation.
2. **Contact finding (exploratory only):** M9C RELEASED contamination was 0/17 judgeable no-contact frames vs 12/35 contact frames. Hypothesis-generating; no contact-gated rule is implemented or tested.
3. **AF1 — In the M9C blinded development control sample, frozen ordinary ASSIGNED anatomy had 7/30 contaminated frames (23.3%). Together with the concentration of RELEASED contamination in contact scenes, current anatomical ownership cannot be assumed reliable in overlapping/entangled multi-person scenes.** It does not retroactively alter frozen M9/M9B results and is not a population accuracy estimate.
4. Merge guard stays diagnostic-only and unsupported as a solution. M7 stays OPEN/NON-BLOCKING.

## 1. What frozen Anatomy V1 demonstrably does
Descriptive, from the one execution on four out-of-fold clips (AR1):
- Runs identity (V0.6.1 rule) → V0.5 per-detection ownership → locked record classifier → stride-3 pose → visualization-only carry, deterministically and reproducibly (parity and clean-unzip tests pass; 8707 measured rows, 3411 stride-3 frames, no defects).
- Emits a skeleton as an ASSIGNED_A/B record only when identity is ACCEPT **and** ownership is SINGLE_BODY_SUPPORTED: 771 assigned records (A 502, B 269). Everything else is withheld with a recorded reason. Withholding is large: 1408/2179 identity-ACCEPT measured frames (64.6%, CI 62.6–66.6%) are not emitted.
- Frame-level human review (blind, exploratory) of what it draws:
  - M9 ASSIGNED: 19 CORRECT / 10 PARTIAL / 1 CONTAMINATED / 0 NOT_JUDGEABLE of 30 (contaminated 1/30 = 3.3%, CI 0.08–17.2%).
  - M9C ASSIGNED control: 16 CORRECT / 7 PARTIAL / 7 CONTAMINATED of 30 (23.3%, CI 9.9–42.3%).
- Frames without body contact looked reliable in the sample: M9C ASSIGNED control no-contact 0/20 contaminated (16 CORRECT, 4 PARTIAL); the 20 no-contact released frames had 0 contaminated of 17 judgeable.

## 2. What it does not establish
- No validated anatomical accuracy: no ground-truth skeleton, no joint-error measurement; all verdicts are visual, categorical, by one non-independent reviewer (owner agreement on the 50-item overlap: kappa 0.36, raw 0.56).
- No population rate. Samples are small (n=30 per stratum), clustered in four clips and a few shots, drawn by different rules in M9 (7–8 per clip per stratum) and M9C (±15 exclusion, spacing ladder). The 1/30 (M9) and 7/30 (M9C) assigned rates are **not pooled** and not reconciled; their difference may reflect sampling and contact composition (10 of the 30 M9C assigned controls were contact frames; the M9 sample was not stratified by contact) and I do not claim to know which.
- Correct anatomical ownership is not evidence of correct wrestler identity. Identity is MODIFY, unvalidated, not exposure-ready; ASSIGNED_A/B labels are `identity_unvalidated`.
- No generalisation beyond the four development clips (Holdout #2 sealed; R3 PARKED; R4 UNMET).
- No evidence about temporal accuracy, joint-angle accuracy, left/right correctness, depth, or anything kinematic. Pose is single-view 2D landmarks at stride 3; carried frames are visualization-only.
- No knowledge of the real fraction of ASSIGNED frames that are in contact scenes: no contact detector exists; the `contact` field is a Claude judgment on the reviewed sample only.
- Merge guard: no demonstrated correspondence with real mixed-body cases (in M9C it flagged 6 of 120 items, 2 contaminated); diagnostic only.

## 3. The unresolved contact/occlusion failure mode
Evidence (M9C, all strata, Claude primary, contact flag Claude's):
| stratum | contact YES | contact NO |
|---|---|---|
| ASSIGNED control (30) | 7 CONTAMINATED / 3 PARTIAL (n=10) | 0 CONTAMINATED / 16 CORRECT / 4 PARTIAL (n=20) |
| RELEASED (60) | 12 CONTAMINATED of 35 judgeable (40 items) | 0 of 17 judgeable (20 items) |
| HARD-VETO control (30) | 10 CONTAMINATED of 19 judgeable (20 items) | 0 of 7 judgeable (10 items) |

Pattern: in this sample **all** 29 contaminated M9C frames (7 assigned + 12 released + 10 hard-veto) were in frames flagged as contact; no contaminated frame was flagged no-contact (no-contact counts: 20 assigned, 17 judgeable released, 7 judgeable hard-veto), including frames the frozen layer ASSIGNED with SINGLE_BODY_SUPPORTED and no withholding reason (the M9 case R049 and, in M9C, ASSIGNED controls). Mechanism evident in the images: pins, lifts and clinches where masks and keypoints of two bodies interpenetrate, so a landmark inside one person's mask can be anatomically on the other. The ownership layer, which uses masks and landmark/mask consistency, cannot separate these. The structural-clause review found released OWN_ONLY landmarks on the wrong body in 5 distinct shots (7 frames; 4 further frames undetermined in 2D).
Unresolved: whether any rule can separate these; M9C does not tell us, and the reviewer has forbidden designing one now.

## 4. Implications of 7/30 contaminated ASSIGNED controls
- The one state the layer treats as safe (SINGLE_BODY_SUPPORTED + identity ACCEPT) is not safe in contact scenes. "Assigned" therefore cannot be read as "correct body".
- Any downstream quantity that depends on **which body a landmark belongs to** (per-wrestler joint position, per-wrestler distance/speed, any per-wrestler exposure) would inherit the contamination, at a rate that in contact scenes (7/10 of reviewed assigned contact frames, n=10, uninformative as a rate) is plausibly large.
- The failure concentrates exactly where exposure in wrestling is most interesting (holds, pins, throws, impacts). Excluding contact frames would therefore remove most of the target events, not just noise.
- Averaging or pooling over frames does not cancel it: the contamination is systematic (same scene configuration), not random.
- It is not a clean "contact detector" problem either: no validated way to tell contact scenes exists, and the contact finding is exploratory.

## 5. Which anatomical outputs remain defensible for downstream exploratory exposure work
Defensible (exploratory, labelled, with the limits above):
- Visualization overlays of ASSIGNED and withheld skeletons for human inspection, labelled unvalidated.
- Record-class counts, withholding reasons and coverage (M2/M6/M8-style) as **process diagnostics**, not as measurements about wrestlers.
- Per-frame "an assigned skeleton exists" as a weak, unvalidated flag, only if no per-body attribution of anything is made from it.
- ASSIGNED anatomy in frames independently judged non-contact, **only** as hand-reviewed illustration; 0/20 in a single-reviewer sample cannot support a rate or an automatic rule (the exact 95% upper bound for 0/20 is 16.8%).
Not defensible: see section 7.

## 6. Options for the next phase and recommendation
(a) **Exposure using only conservative eligible anatomy / non-contact states.** Requires an automatic, validated contact/occlusion determination that does not exist and whose design is prohibited now. Without it the non-contact subset is defined by human judgment. The retained frames would also exclude the contact events of interest, and 0/20 (CI upper 16.8%) is weak support. Not recommended as the next phase.
(b) **Design exposure to avoid dependence on pose ownership altogether** (e.g. scene-level or detection-level quantities that do not require attributing individual landmarks to a specific wrestler; they would still need their own validation and would still depend on identity, which is unvalidated). Addresses the demonstrated failure mode directly. Open question: which quantities are meaningful without ownership; that is a design question for the reviewer.
(c) **Anatomy remains a visualization-only branch for now.** Consistent with all frozen evidence and costs nothing; does not itself produce an exposure path.

**Recommendation: (c) immediately and (b) as the next design phase.** Anatomy stays visualization-only; the next authorized phase, if any, should be a documentation-and-design exercise on exposure concepts that do not require per-person landmark ownership, with explicit pre-registration and evaluation. (a) should be revisited only if a future, separately authorized contact/occlusion design is prospectively evaluated on fresh data. Rationale: the two sources of failure that M9C exposed (ownership in contact; identity not validated) both attack the premise of per-wrestler anatomy-based exposure, and the evidence is development-only from four clips and a single reviewer, so the conservative default is to avoid depending on it.

## 7. Explicit prohibited downstream uses of unreliable anatomy
Until separately validated, ASSIGNED or released anatomy must NOT be used for: per-wrestler or per-body exposure, center-of-mass, distance, speed, acceleration, impact or contact-force estimates; joint angles, ranges of motion or kinematics; workload, fatigue, injury-risk, injury-prediction or clinical statements; ranking or comparing wrestlers; training or tuning any head, gate or threshold on these frames; treating "assigned" as "correct body" or "correct wrestler"; any claim of validation, accuracy or generalisation; redistribution of footage-derived overlays (rights UNRESOLVED); re-identification from appearance; training or tuning on Holdout #2 or any burned clip as confirmatory evidence. Partial release (the KILLED class) must not be re-enabled, and the merge guard must not be used as a filter.

## 8. Limits of this assessment
Single non-independent reviewer; contact flag is subjective and unvalidated; small clustered samples; M9 and M9C used different sampling; wrong-body calls are visual 2D. STOP for reviewer ruling.
