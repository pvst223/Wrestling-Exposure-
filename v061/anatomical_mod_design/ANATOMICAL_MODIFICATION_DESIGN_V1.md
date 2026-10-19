# ANATOMICAL MODIFICATION DESIGN V1

**Status:** DESIGN ONLY. Nothing implemented, tuned or run. No exposure/COM/distance/impact/workload metric. Development-only, fail-closed. R3 PARKED, R4 UNMET, ANNOTATION-PROVISIONAL. Holdout #2 sealed; Jeff Hardy excluded; Cena development-only; no new footage; no new claim of validation, accuracy, generalisation, clinical utility, fatigue or injury prediction.
**Evidence used (frozen only):** Anatomical Integration V1 records (1408 withheld measured rows with identity ACCEPT; 2179 identity-ACCEPT measured rows in total), M9 V1 (60), M9B (60). Single non-independent reviewer; M9B stratified, not proportional.

## 0. Proposal in one paragraph (smallest prospective modification)
Do **not** relax ownership globally and do **not** relax any hard-veto family. Add one new record class, `RELEASED_PARTIAL_ANATOMY_A/B`, for a withheld frame only when **all three** hold: (i) state is `OWNERSHIP_UNCERTAIN` (never `MIXED_BODY_SUSPECTED`); (ii) **every** listed ownership reason is in Tier A = {`CONTESTED_LANDMARKS`, `TOO_FEW_OWN_ONLY_LANDMARKS`, `MASK_NOT_EXPLAINED_BY_SKELETON`}; (iii) no numeric failure, no `NO_POSE`, identity ACCEPT_A/B unchanged. For such a frame, emit **only the landmarks the unchanged V0.5 per-landmark classification labels OWN_ONLY**, and only bones whose both endpoints are released. CONTESTED, OTHER_ONLY and OUTSIDE landmarks are dropped, not guessed. The merge guard remains diagnostic-only and is not an input.

## 1. What M9B/M9 V1 support, by reason family
Counts are verdicts among M9B items carrying the reason (items overlap). "Single" = the only reason on the item.
| Reason | M9B items | Verdicts (CORR/PART/CONT/NJ) | Single-reason items | Family |
|---|---|---|---|---|
| CONTESTED_LANDMARKS | 12 | 1/10/1/0 | 5: 1/4/0/0 | **Tier A candidate** |
| TOO_FEW_OWN_ONLY_LANDMARKS | 11 | 1/9/1/0 | 3: 0/3/0/0 | **Tier A candidate** |
| MASK_NOT_EXPLAINED_BY_SKELETON | 7 | 0/5/0/2 | 2: 0/1/0/1 | **Tier A candidate** (2 NJ = no skeleton drawn) |
| BONES_LEAVE_MASK | 5 | 2/3/0/0 | 2 | Tier B: not now (n too small) |
| TORSO_SIDES_ASYMMETRIC | 2 | 0/2/0/0 | 2 | Tier B: not now |
| TEMPORAL_JOINT_JUMP | 1 | 0/1/0/0 | 1 | Tier B: not now |
| OPPONENT_LANDMARKS_IN_MASK | 10 | 3/5/1/1 | 5: 3/1/1/0 | **Keep vetoed for V1** (largest withheld reason, 467 rows; 1 contaminated; mixed evidence; first target for a later, separate study) |
| SHARED_JOINT_CONFLICT | 10 | 1/5/2/2 | 10: 1/5/2/2 | **Hard veto** (2/8 judgeable contaminated, both tangled contacts) |
| BONE_SPANS_INSTANCES | 8 | 4/2/2/0 | 5: 2/1/2/0 | **Hard veto** (2 contaminated, both clinch/pin) |
| LANDMARKS_IN_OTHER_INSTANCE / SOME_LANDMARK_IN_OTHER_INSTANCE | 4 / 1 | 2/1/1/0 ; 0/1/0/0 | | **Hard veto** (name says another body owns landmarks) |
| NO_OWNER_MASK | 2 | 0/1/1/0 | | **Hard veto** (no ownership evidence; 1 contaminated) |
| LIMB_TOO_LONG:* | M9B 7; M9 V1 9 | M9B: 0/5/1/1; M9 V1: 4 of 9 contaminated | | **Hard veto** (geometric cross-body signature) |
| FEW_LANDMARKS | 2 | 0/1/0/1 | | Stay withheld (too sparse to judge) |
| TEMPORAL_SCALE_JUMP, LANDMARK_OUTSIDE_OWN_BOX | 0 in M9B | not observed | | **Hard veto by default** (unobserved = fail closed) |
(SHARED_JOINT_CONFLICT singles: 10 items = 1 CORRECT/5 PARTIAL/2 CONTAMINATED/2 NJ; all 10 had no other reason.)

Descriptive in-sample fact (selection-biased, **not an estimate of future performance**): 8 of the 9 contaminated M9B frames carry a non-Tier-A reason as their only reason (LIMB_TOO_LONG, SHARED_JOINT_CONFLICT ×2, NO_OWNER_MASK, BONE_SPANS ×2, LANDMARKS_IN_OTHER_INSTANCE, OPPONENT_LANDMARKS_IN_MASK). The 13 M9B items whose reasons are all in Tier A: 12 judgeable, 11 usable, **1 contaminated (B010)**: 8.3%, exact CI 0.2–38.5%. Non-Tier-A items: 42 judgeable, 8 contaminated (19.0%). The merge guard flagged none of the 9 contaminated frames.

## 2. Population size (frozen records, descriptive)
Rows with identity ACCEPT, measured pose, ownership-withheld: 1408 (64.6% of 2179). Rows whose reasons are all in Tier A: **223 rows = 10.2% of the 2179** (all `OWNERSHIP_UNCERTAIN`; ACCEPT_A 127, ACCEPT_B 96; b2_batch2 80, vp5 60, vp2 57, b1_orton 26; 15 of them merge-guard-flagged). Adding Tier B would reach 343 rows (15.7%); it is excluded from V1. This is an **upper bound on recoverable frames**: per-landmark release and a minimum-released-landmark rule will shrink it.

## 3. Interactions that prevent a one-reason relaxation
1. **B010**: the only Tier-A-only contaminated frame has two Tier A reasons together (CONTESTED + TOO_FEW_OWN_ONLY) during a grapple, with a leg line on the opponent's leg. The pair co-occurs in 7 M9B items (6 usable, 1 contaminated). A frame-level relaxation would have released the whole skeleton including that leg line; the per-landmark OWN_ONLY release would have dropped it. This is why the minimal design releases landmarks, not frames.
2. **Any-hard-reason rule.** A frame is eligible only if reasons ⊆ Tier A. A single hard reason (even alongside Tier A reasons) keeps the frame withheld. 15 M9B items had ≥2 reasons (10 usable, 3 correct, 1 contaminated, 1 NJ); multi-reason frames get no special treatment.
3. **State.** MIXED_BODY_SUSPECTED is excluded outright (24.0% vs 10.3% contamination descriptively); only 16 population rows are Tier-A-only in MIXED.
4. **Contact context.** 7 of 9 contaminated frames are grapple/clinch/pin/carry. Contact is not a rule input (merge guard failed to flag them, and no contact detector exists); it is a stratification variable in evaluation.
5. **Implementation dependency (for reviewer to confirm before any build):** frozen rows keep only per-frame summaries (`own_only_frac`, `contested_frac`, …). The per-landmark labels (`cls`) exist inside the unchanged V0.5 `ownership_v05` module. Release requires recomputing them deterministically from the frozen pose and frozen segmentation cache with the unchanged module (no new inference, no new footage). If that cannot be done byte-identically, the modification is not implementable fail-closed and stops.

## 4. Representing sparse but correctly attributed pose downstream
Never treated as ordinary `ASSIGNED`. New fields on a released frame: `record_class=RELEASED_PARTIAL_ANATOMY_A/B`, `anatomy_completeness=PARTIAL`, `released_landmarks` (mask over the 13 landmarks), `n_released`, `released_bones`, `release_basis` (the Tier A reason set), `IDENTITY_UNVALIDATED`, `ownership_state=OWNERSHIP_UNCERTAIN` retained. Rules: missing landmarks are missing, never zero-filled, interpolated or carried; no carry-forward from or across PARTIAL frames; rendered visibly differently (dashed, distinct colour, label "PARTIAL"); any downstream consumer must filter on `anatomy_completeness` explicitly and may not count PARTIAL frames toward "fully measured anatomy" totals. A minimum released-landmark count is a **structural** constant set before evaluation by anatomical logic (at least one complete limb chain, i.e. two connected released landmarks, to emit a bone; otherwise the frame stays withheld) and is not tuned on M9/M9B.

## 5. Separate PARTIAL_ANATOMY state vs ordinary ASSIGNED (item 7)
Separate state is scientifically preferable: (a) ASSIGNED is defined by frame-level ownership SINGLE_BODY, which these frames do not satisfy; (b) M9B "usable" was a lenient body-attribution judgement on skeletons that were often 1–3 segments, not a statement that the pose is complete; (c) merging would silently dilute any later coverage or contamination rate of ASSIGNED; (d) it preserves the ability to drop the whole class in one filter if the modification is KILLED. Cost: downstream code must handle one more class; accepted.

## 6. Prospective evaluation (before implementation)
**New sample (M9C).** Drawn from frozen Tier-A-eligible rows of the same four development clips, excluding all 120 already-reviewed frames and any frame within ±30 source frames of them in the same clip. Seeded deterministic rule, hashed before any image is viewed. Blind composite: the released-frame overlay plus two controls in one shuffled set, identity/state/reasons/class hidden: (a) 30 current ASSIGNED frames; (b) 30 frames carrying a hard-veto reason (to confirm the vetoes still capture contamination). Released frames: target 60 unique frames, stratified across the 4 clips and across shots, ≥30 frames apart. Same four verdicts, applied **per released landmark/bone set**, i.e. verdict on what is actually drawn. A second reviewer is requested for at least 30 frames if one is available (the owner), because Claude's reviews are non-independent; if none, the result is labelled single-reviewer.
**Metrics, all with exact CIs:** (1) contamination among judgeable released frames; (2) usable share among judgeable; (3) NOT_JUDGEABLE share (reported, not dropped); (4) recovered coverage = released frames / 2179 identity-ACCEPT measured frames, and recovered landmarks per released frame; (5) per-clip and per-shot contamination; (6) contact-context stratum (grapple vs open) contamination; (7) control contamination for ASSIGNED and hard-veto strata; (8) net contaminated frames added per 100 identity-ACCEPT measured frames = (released contamination share) × (coverage gain).
**Joint evaluation (item 6).** Coverage is never evaluated alone. The report shows the coverage–contamination pair for the single pre-registered rule (no sweep), and KEEP requires both gates below. No threshold, family or state may be changed after seeing M9C; a different rule requires a new design and a new sample.

**KEEP / MODIFY / KILL (fixed now):**
- **KEEP (development-only):** ≥60 judgeable released frames; contamination ≤3/60 (point ≤5.0%, exact upper ≤13.9% at 3/60; scale pro rata if more are judgeable) **and** recovered coverage ≥5.0 percentage points of the 2179 **and** no clip with ≥3 contaminated released frames **and** hard-veto control still shows contamination clearly above the released stratum (descriptive point estimate ≥2× the released rate) **and** ASSIGNED control unchanged by construction.
- **MODIFY:** contamination within KEEP limits but coverage <5.0 points; or contamination 4–5/60 (point 6.7–8.3%); or ≥3 contaminated in a single clip; or NOT_JUDGEABLE >25% (representation problem). Allowed response: a *new* design (e.g. stricter structural released-landmark rule), re-evaluated on a new sample.
- **KILL:** ≥6/60 contaminated (point ≥10%), or any contaminated frame whose own-only landmarks were labelled OWN_ONLY on the wrong body in ≥2 distinct shots (shows the per-landmark label itself is unreliable), or the per-landmark recomputation is not reproducible (item 3.5). KILL removes the class; withholding returns to the frozen V1 behaviour.
Not sought and not claimed: joint accuracy, exposure suitability, identity validation.

## 7. Development data allowed (item 8)
Allowed: frozen ROWS/SEG/pose caches and identity out-of-fold decisions of the four development clips only (`b1_orton_rollins_wm31`, `b2_batch2_clip_condensed`, `b2_videoplayback_2`, `b2_videoplayback_5`); the 120 reviewed frames as *design-informing, burned* evidence (never reused as confirmation). Not allowed: Holdout #2, Jeff Hardy footage, any new footage, Gemini, final identity head, exposure computation, re-identification from appearance, tuning against M9/M9B/M9C verdicts. Because Tier A was chosen using M9B on the same clips, M9C is prospective with respect to frames, **not independent with respect to clips or shots**; it is a development check of a pre-registered rule and creates no confirmatory claim.

## 8. Known weaknesses
Single non-independent reviewer; Tier A rests on 13 M9B items with one contamination (CI up to 38.5%); sampling clustered within four clips; lenient PARTIAL standard; B010 shows frame-level risk exists even in Tier A, which per-landmark release is expected, not shown, to fix; OPPONENT_LANDMARKS_IN_MASK, the biggest withheld reason, is deliberately left alone, so coverage gain is capped at ≤10.2 points.

## 9. Questions for the reviewer
1. Approve Tier A = {CONTESTED_LANDMARKS, TOO_FEW_OWN_ONLY_LANDMARKS, MASK_NOT_EXPLAINED_BY_SKELETON}, state UNCERTAIN only, per-landmark OWN_ONLY release?
2. Approve a separate `RELEASED_PARTIAL_ANATOMY` class?
3. Approve the KEEP/MODIFY/KILL criteria and M9C design above, including the ±30-frame exclusion and the control strata?
4. May a readiness/self-test phase (item 3.5: byte-identical recomputation of per-landmark labels from the frozen caches; no results viewed) follow before any M9C?
