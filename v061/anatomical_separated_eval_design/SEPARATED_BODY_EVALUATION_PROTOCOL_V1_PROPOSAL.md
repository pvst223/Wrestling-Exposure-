# FROZEN ANATOMY V1 — SEPARATED-BODY EVALUATION: PROPOSED PROTOCOL (DESIGN ONLY; NOT EXECUTED)

Status: proposal for reviewer ruling. Nothing here is run, sampled, imaged or reviewed. Anatomy V1 (implementation manifest f5936ce8…) is unchanged. No tuning. No exposure work. Holdout #2 untouched. The earlier Exposure Architecture request is superseded by the revised ruling and not begun. Everything is development-only, ANNOTATION-PROVISIONAL, not validation. Rights UNRESOLVED.

**Disclosure that limits independence of the design:** the designer (Claude) has seen M9/M9B/M9C results, including the 0/20 no-contact ASSIGNED finding. Parameter values below are therefore *not* independent of that knowledge. They are fixed by round-number convention, to be frozen before any fresh data exist, and the reviewer may amend them.

## 1. Question and claim ceiling
Question: for the unchanged frozen `ASSIGNED_A/B` pathway, under a pre-specified separated-body condition, are the emitted landmarks and bones on the body of the person in the assigned detection (**anatomical body ownership**)?
It does **not** test: joint-position accuracy, temporal accuracy, depth, or whether label A/B is the right wrestler (identity V0.6.1 is unvalidated; see section 9).
Claim ceiling even at KEEP: "on this fresh development sample, under the separated-body criterion, emitted skeletons were on the assigned detection's person at a rate whose exact upper bound was X." No population, generalisation, accuracy, exposure or clinical claim.

## 2. Separated-body eligibility (prospective; no anatomical verdicts or ownership states used)
Computed only from person-class detections and frame geometry, never from skeleton correctness, ownership state/reasons, merge guard, identity scores or any verdict. A frame/assigned detection is **ELIGIBLE** iff all hold:
1. No other person-class detection (confidence ≥ 0.10, box height ≥ 25% of the target box height) intersects the target box expanded by 15% of its width and height on each side. The low confidence floor is deliberate so occluding people missed at the normal threshold still count.
2. Target box is ≥ 2% of frame size away from every frame border.
3. Target box height ≥ 15% of frame height.
4. Criteria 1–3 also hold on the previous and next stride-3 pose frames (temporal stability, rejects transient separation).
5. No camera cut within ±3 frames of the frame (frozen shot index).
Frozen as code + hash before data. Stated limit: person-detector misses can still make a contact frame look separated; this is measured by the audit in section 6, not assumed away. The criterion uses boxes (not V0.5 masks) to avoid circularity with the mask-based ownership layer, but crowd people behind the wrestler will make some separated frames ineligible; yield is reported, never tuned.
Pre-specified secondary sensitivities (reported, not gating): margin 10% and 25%.

## 3. Fresh data and independence
Required: no frame, shot, clip, event, source file or upload used in M9/M9B/M9C review or in any parameter choice here; M9/M9B/M9C judgments are not confirmatory evidence and are not pooled.
Options (reviewer to choose, D1):
- **D1-A. New development clips** (recommended). Matches the data plan (≥6 new clips): target ≥ 6 clips, ≥ 3 sources/eras/resolutions, ≥ 2 promotions, from events not in any development clip. Requires explicit new-footage authorization, owner-supplied names/metadata only, no re-identification from appearance, Jeff Hardy excluded, Cena development-only, Holdout #2 identities absent.
- **D1-B. The two unused development-pool clips (HBK/Benjamin, Rock/HHH).** Never anatomy-reviewed, but not run through the anatomy pathway either (excluded in OGR18), would need pose/seg extraction and OOF identity outputs (to be verified) and authorization. Only two clips: cannot meet the clip minimum below alone; at best a supplement.
- **D1-C. Unreviewed shots of the four burned clips.** Not independent (same broadcasts, same wrestlers, same scenes the design knowledge came from). Exploratory only; cannot support KEEP.
- **Holdout #2: not used.** Using it would spend its one-shot sealed role for identity. Separate justification and authorization required; I do not recommend it.
Feasibility count (no verdicts, no images): once data are authorized, count identity-ACCEPT ASSIGNED frames meeting eligibility per clip from pipeline outputs. If the pre-specified minimum cannot be reached the result is INCONCLUSIVE_DATA; nothing is relaxed.

## 4. Sampling (frozen before images)
- Primary stratum **ELIGIBLE_ASSIGNED**: target 150 frames drawn by seeded selection (seed = int(sha256(protocol_freeze_hash)[:8],16) mod 2^31) from frozen ASSIGNED_A/B records meeting section 2; ≥ 30 distinct shots; ≥ 4 clips; ≥ 30-frame spacing within a clip; ≤ 10 frames per shot; ≤ 40% from one clip. Proportional-by-clip allocation with the shortfall reported, never hidden.
- Contrast stratum **INELIGIBLE_ASSIGNED**: 50 ASSIGNED frames failing the criterion, same spacing rules, clip-matched. Purpose: show whether the criterion carries information. Descriptive only, no gate.
- Items shuffled, stratum hidden. Images show the assigned detection's skeleton exactly as the frozen renderer emits it, neutral style, same two-panel layout as M9.

## 5. Review that tests ownership, not plausibility
Two steps per item, under ids that reveal no stratum:
1. Unannotated full-frame/crop with only the assigned detection box outlined. Reviewer records: `box_person` ∈ {WRESTLER, REFEREE, SPECTATOR/OTHER, MULTIPLE_PERSONS_IN_BOX, CANNOT_TELL} and `separation_audit` ∈ {SEPARATED, OTHER_BODY_TOUCHING/OVERLAPPING, CANNOT_TELL}.
2. Overlay revealed. For every drawn landmark and bone: on the boxed person's body / on another person's body (name which: referee, spectator, other wrestler) / off any body. Reviewer lists the indices not on the boxed person.
Frame verdicts: **OWNERSHIP_CORRECT** (all drawn landmarks on the boxed person), **WRONG_BODY** (≥ 1 drawn landmark or bone on another person), **OFF_BODY_ONLY** (no other-person landmark, but ≥ 1 landmark on no body: localization, reported separately and not counted as an ownership error), **NOT_JUDGEABLE** (e.g. fewer than 3 drawn landmarks or unresolvable).
Primary outcome: WRONG_BODY frame proportion among judgeable eligible frames, with exact Clopper-Pearson 95% CI, plus the shot-level analogue (shots with ≥ 1 WRONG_BODY frame).

## 6. Reviewers
- **Primary:** an independent human reviewer who is not a developer and not the project owner (consistent with the Holdout #2 second-annotator independence rule), with a dated independence attestation before review. Claude does not decide the gate.
- **Second reviewer:** the project owner, blinded, on 100% of items if feasible (≥ 50% otherwise, selected by seed). Neither sees any verdict of the other, Claude's output, the stratum, ownership/identity state, merge-guard state or any result before both files are frozen and hashed.
- **Claude:** may review all items as a disclosed, non-independent sensitivity (completed and frozen first, blind), never as the decider.
- Agreement: kappa on WRONG_BODY vs not, raw agreement, reported. KEEP must hold under **both** human reviewers separately (the less favourable one binds).
- **Eligibility audit** from `separation_audit` on eligible frames: false-eligibility rate = proportion judged OTHER_BODY_TOUCHING/OVERLAPPING.
- Hidden key joined exactly once after all verdict files are frozen; verdicts, key and images stay private; no frames/MP4s/crops in GitHub.
- Everything ledgered before/after as in M9C (registration before any image viewed; freeze before join).

## 7. Pre-registered outcomes (decided mechanically; no post-hoc rules)
Minimum data: ≥ 100 judgeable eligible frames, ≥ 20 shots, ≥ 3 clips. Otherwise **INCONCLUSIVE_DATA** (no KEEP/MODIFY/KILL; report and stop).
**KEEP** (restricted pathway retained as "ownership-reliable under separation" development evidence) requires all, under each human reviewer:
a. WRONG_BODY frame proportion with exact 95% upper bound ≤ 5.0% (at n = 150 this allows ≤ 2 events);
b. WRONG_BODY frames in ≤ 1 distinct shot;
c. false-eligibility rate (audit) ≤ 5.0%;
d. NOT_JUDGEABLE ≤ 20%;
e. OFF_BODY_ONLY frame proportion reported (no gate; it matters for any downstream use).
**KILL** if any: WRONG_BODY point estimate ≥ 10.0%; WRONG_BODY in ≥ 3 distinct shots; false-eligibility rate > 10.0%; or irreproducible recomputation.
**MODIFY / NOT_KEEP** otherwise: no pathway change is permitted (no tuning of Anatomy V1 or of the criterion); the restricted pathway stays visualization-only and any further test needs a new reviewer-approved design and fresh data. If the only unmet items are gap-type (e.g. upper bound slightly above 5.0% with low point estimate), report `NOT_KEEP_NEEDS_REVIEWER_INTERPRETATION`; no outcome rule is invented afterwards.
A KILL means the separated-body pathway is closed for this version.

## 8. What KEEP would and would not permit downstream
KEEP would permit only: describing the ASSIGNED pathway, **in eligible separated frames**, as development-evidence ownership-reliable, and proposing a further design for restricted downstream use. It would **not** permit any quantitative measurement. Before any measurement use, still required and not tested here: (1) landmark localization accuracy against independent annotation; (2) temporal continuity; (3) identity validation (item 9) for any per-wrestler attribution; (4) a representativeness argument, because restricting to separated frames drops contact events (holds, pins, throws) that matter most biologically, so any result would be conditional on the separated state and could not stand for exposure in general; (5) adequate eligible yield. If KEEP is not reached, or the above cannot be met, Anatomy stays visualization-only.
Prohibited uses in `ANATOMY_V1_FINAL_DEVELOPMENT_ASSESSMENT.md` section 7 remain in force regardless of outcome.

## 9. Identity V0.6.1 is unvalidated
The gate scores ownership of the boxed person only. `box_person` and, where owner annotation exists for the fresh clips, A/B correctness are recorded as **secondary, annotation-provisional** results (non-wrestler emission rate, A/B swap rate). They do not enter the gate. Any statement of the form "this skeleton is wrestler A" is outside the claim ceiling until identity is validated on Holdout #2 under its own protocol. A high non-wrestler emission rate would be reported as a blocker for per-wrestler downstream use.

## 10. Freeze list and execution gating (for a later authorization)
Frozen and hashed before any fresh data are touched: this protocol (final), eligibility code and parameters, feasibility-count script, sampler, review pack/instructions/templates, join script, tests (synthetic only), implementation manifest check. Self-contained package with clean-unzip verification, as in M9C readiness. Execution only after reviewer authorization, with sequence: feasibility count → registration → sampling → images → blinded reviews frozen → single key join → report → STOP.

## 11. Decisions requested from the reviewer
D1 fresh data source (A/B/C above) and authorization of new footage if A. D2 reviewer structure (independent human primary + owner second + Claude sensitivity). D3 eligibility parameters (15% margin, 0.10 floor, 15% height, 2% border, ±3 stability/cut). D4 thresholds (≤ 5% upper bound, ≤ 1 shot, 10% KILL, 3 shots, audit 5%/10%, n = 150). D5 whether the contrast stratum is wanted. D6 whether KEEP must hold under both human reviewers.

## 12. Known limits
Detector-box criterion is crude and will under-use crowd-heavy frames; no ground truth skeleton; reviewers judge 2D; frames cluster within shots; small data; development-only; R3 PARKED; R4 UNMET; ANNOTATION-PROVISIONAL.
