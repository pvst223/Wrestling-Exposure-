# ANATOMY V2 C3 — JOINT TWO-BODY OWNERSHIP DETAILED DESIGN V1

**Detailed design only. Nothing implemented, run, sampled or reviewed.** Label: development-only, ANNOTATION-PROVISIONAL, rights UNRESOLVED. No validation, accuracy, generalisation, clinical, exposure, workload, fatigue or injury claim. No Holdout #2, no Gemini, no exposure, no final MP4. R3 identity/parity/new-footage work is on HOLD (ruling 6).

Reviewer rulings carried (ANA-contact ruling): taxonomy T1–T6 provisional, T5 a hard ceiling; **C3 only**; C1's clean-anchor evidence may be a pre-specified evidence source inside C3; **C0 approved as the mandatory comparator**; C2 parked; burned M9/M9B/M9C verdicts closed to any further use for selecting constants, margins, weights, expiry horizons, thresholds or KILL criteria; one acquisition may later serve both questions but **no clip is confirmatory for both** evaluations.

Governing principle (verbatim): **unique supported current-frame ownership or WITHHOLD.** C3 never manufactures, carries, interpolates or repositions a landmark.

---

## 0. Position of C3 and what it is not

- C3 is a **post-filter on frozen Anatomy V1 output**. It runs after V1's record classifier and can only **remove** an `ASSIGNED_A/B` row (→ new withheld class `WITHHELD_C3`), or leave it exactly as V1 produced it. It cannot add a row, release a V1-withheld row, change a keypoint, or alter V1's identity or ownership decisions. Formally: `emitted(V2) ⊆ ASSIGNED(V1)`, and emitted keypoints are bitwise equal to V1's measured keypoints for that detection. (This is why it is not the killed partial release: that class created output from V1-withheld frames; C3 only subtracts.)
- C3 makes **no claim about identity.** "Ownership ≠ identity" and the `identity_unvalidated` flag are preserved. If V1's pre-contact tracklet label is wrong, C3 faithfully preserves the wrong label.
- Name: "Anatomy V2 (C3)". Frozen Anatomy V1 (manifest f5936ce8…) and the locked V0.6.1 implementation are untouched; V2 code lives in a separate folder with its own manifest.

## 1. Inputs available to C3 (all already produced by frozen stages; no new model)

Per shot, per stride-3 pose frame f: all pose detections (17 keypoints, confidences, boxes), cached YOLOv8m-seg instance masks (320×180, per detection owner mask via the frozen `owner_for`), V1 per-detection ownership evaluation (`ownership_stage.evaluate`, which takes **no identity input**), V1 measured rows (tracklet, identity code, record class), the frozen shot/cut index, and the source video pixels at pose frames (needed only by the frozen appearance descriptors; decoding is part of the determinism requirement, section 14).

## 2. Frozen or structural constants — the complete constants audit

C3 introduces **no new tunable numeric constant.** Every number is one of:

| constant | value | source |
|---|---|---|
| keypoint confidence for landmark use | 0.5 | frozen `pose.KP_CONF` (V1) |
| keypoint confidence for appearance regions | 0.3 | frozen `appearance.KP_CONF` |
| overlap tests | IoU 0.3; cover-other 0.5; ≥3 other joints inside box; duplicate IoU 0.5; shared joints ≥3 within 0.05·diag | frozen `integrity` section |
| mask tolerance; duplicate-mask IoU; min landmarks; opponent-landmark min n | 4 px; 0.8; 4; 3 | frozen `ownership` section |
| unexplained-mask limit | 0.25 | frozen `ownership.UNEXPL_MAX` |
| appearance: D_SEP_MIN 0.15, VOTE_DELTA 0.25, REGION_MIN_PIX 120, MODEL_MIN_PIX 300, histogram quantisation, region geometry, REGION_MASS (Dempster/Winter) | as listed | frozen `appearance` section and `appearance.py` |
| view spacing | 60 source frames | frozen strict-seed spacing `MIN_GAP` (V0.6.1 `devrun/episodes.py`) |
| pose stride | 3 | frozen |
| structural minima | 2 views per body; ≤3 anchored bodies in a union region; 1 pose-frame interval extension each side; "zero contradictions"; "≥1 positive source per landmark" | not tuned; arithmetic/structural (a noise floor needs 2 views; wrestlers + referee = 3; stride is 3; a contradiction is a contradiction) |

A test will compare every numeric literal read by the C3 module with this table and with the hashes of the frozen config files. If the reviewer wants a time cap on anchor age or a different spacing, that is a new constant requiring a ruling; none is assumed.

## 3. Contact/overlap interval — exact definition

Applies to a **target detection** `d_t` = the detection of a V1 `ASSIGNED_A/B` row, per shot.

`Contact(f, d_t)` is TRUE iff any of the following holds at pose frame f (all geometric/mask/pose, no identity, no verdict):
- (a) the frozen `overlap_context`: a non-duplicate other detection with box IoU ≥ 0.3, or cover-other ≥ 0.5, or ≥ 3 of its confident joints inside `d_t`'s box;
- (b) mask contact: the tolerance-dilated owner mask of `d_t` intersects the (non-duplicate, SEG_DUP_IOU 0.8) instance mask of any other detected person, with or without a pose detection;
- (c) any V1 ownership trouble cue on `d_t`: a CONTESTED or OTHER_ONLY landmark; opponent landmarks inside the owner mask (any, not only ≥ 25%); a shared-joint conflict (frozen ≥3 within 0.05·diag);
- (d) mask or pose evidence cannot be evaluated for `d_t` or for a neighbouring person's mask (treated as contact-suspected, fail closed).

`Interval` = a maximal run of consecutive pose frames in one shot with `Contact` TRUE, **extended by exactly one pose frame on each side** (onset/offset lies between stride-3 samples). Cuts end an interval. The merge guard remains diagnostic-only and is not used.

Outside any interval, V1 behaviour is passed through unchanged (`c3_status = PASS_THROUGH`). The predicate's sensitivity is itself tested (section 17: interval-miss report), because the descriptive burned counts showed that box overlap alone is a weak contact signal. No part of the predicate was chosen from burned verdicts.

## 4. Clean anchor — exact definition, expiry, and establishment without trusting tracklet identity

**Clean frame for body b (a "view").** A pose frame in which tracklet `t_b`'s detection: has `Contact` FALSE; is V1 `SINGLE_BODY_SUPPORTED` (computed by the frozen identity-free `ownership_stage.evaluate`, also for tracklets that V1 did not assign); has ≥ 3 confident torso joints (frozen `REL_MIN_TORSO_JOINTS`) and ≥ 6 confident joints (frozen `REL_MIN_JOINTS`); and has appearance regions meeting REGION_MIN_PIX.

**Anchor for body b.** Two views of `t_b` from the **same shot**, at least 60 source frames apart (frozen `MIN_GAP`), both **after the end of the previous interval in that shot** (an anchor is never reused across an earlier contact) and before the onset of the current interval. Two views are structurally required because the frozen appearance code defines its within-person noise floor from a pair of views; one view gives no usable noise (that region type is then unused, per the frozen code).

**Expiry (structural, no time constant).** An anchor expires at: a camera cut; the start of any interval (anchors are never built from, or chained through, in-contact frames); the loss of the tracklet (a tracklet that ends is not an anchor for a later one); or the absence of a qualifying second view. There is **no age cap**: the evidence used from the anchor (colour of body regions) is slowly varying within a shot. Anchor age is recorded and reported (not tuned). If the reviewer prefers an age cap, it would be a new constant.

**Establishing α (target body) and β (rivals) without assuming identity through contact.**
1. At interval onset, take the target tracklet `t_t` of the row under test and the tracklets of every other non-duplicate detection that is co-located in the union region at the last pre-onset pose frame in which it was a **separate detection** (Contact FALSE, no mask contact with `t_t`). Bodies are therefore defined while spatially separate, where detection-to-body association does not depend on contact.
2. `α` := the body of `t_t`'s pre-onset views; `β_k` := the bodies of those co-located tracklets' pre-onset views; the cast Ω = {α, β_1, …}. A tracklet born inside the interval has no pre-onset views → no anchor → WITHHOLD.
3. Nothing is assumed about which body `d_t` is *inside* the interval. That is the question C3 tests (hypotheses below). The only assumption is the weaker one that tracklets of **separated** bodies are continuous before onset (assumption AS1; failures of AS1 appear as contamination or as anchors that fail the discriminability gate and are measured, not hidden).
4. Post-contact frames are not used as anchors in this version (re-linking after contact is the identity question).

## 5. Missing anchors, more than two people, referee

- No anchor for α → WITHHOLD (`NO_TARGET_ANCHOR`).
- Co-located non-duplicate detection or competing instance mask with **no anchored body** → WITHHOLD (`UNANCHORED_PARTICIPANT`). This also covers a referee or third person who was never seen separated.
- Mask contact (b) with no second detection and no anchored rival → WITHHOLD (`NO_RIVAL_ANCHOR`): an unobserved body cannot be excluded.
- |Ω| > 3 → WITHHOLD (`CAST_TOO_LARGE`).
- A referee anchored like any other body participates in Ω; pairwise appearance models (α vs each β_k) are built separately. If the referee's clothing does not separate from α under the frozen gap test, the referee rival cannot be excluded → WITHHOLD.

## 6. Finite hypothesis set

For a row under test, with cast Ω = {α, β_1, …, β_m} (m ≤ 2) and the target landmark set L = the landmarks the V1 renderer draws (the frozen set 0, 5–16, those with confidence ≥ 0.5):
- **H_α:** every landmark of `d_t` lies on α. (the claim to accept)
- **H_swap(β_k):** `d_t` is body β_k (tracklet jump through contact). Equivalent to "all landmarks foreign".
- **H_foreign(j, β_k):** landmark j ∈ L lies on β_k, all other landmarks on α, for every j ∈ L and every k. (single-landmark foreign; any partially-mixed skeleton is a union of these, so excluding all singles excludes every mixed subset.)

Joint assignment: when other detections `d_o` are co-located, hypotheses are evaluated as detection-to-body assignments π: D_c → Ω (injective). The evidence for `d_t` under π is combined with the evidence for every `d_o` under the same π (a swap of `d_t` implies `d_o` is α). If |D_c| > |Ω|, rule in section 5 applies.

Total: at most 1 + m + m·|L| hypotheses per row (≤ 1 + 2 + 26 = 29). Fully enumerated, deterministic order.

## 7. Evidence terms — every one, with normalisation

There is **no weighted cost** and no scaling constant. Evidence is discrete (a vote, a membership class, a count) and is combined by exclusion logic (section 8). Two evidence families:

**E_A — anchored appearance (the clean-anchor evidence proposed in C1).**
- Models: built by the frozen `appearance.Models` from the two views of each body (α and β_k pairwise), relabelled A/B internally; the frozen `noise`, `dsep`, `gap` per region type; region types whose `gap < D_SEP_MIN` are **unused** (vote 0).
- Current-frame descriptors: the frozen `descriptors` of `d_t`'s skeleton regions (torso, thigh_L/R, shank_L/R, arm_L/R, head) at frame f.
- Vote per region r and rival β_k: the frozen `region_votes`: +1 if r looks like α more than β_k by more than `max(0.25·dsep, noise)`, −1 if it looks like β_k by that margin, 0 otherwise or unavailable. No lighting compensation (frozen limitation).
- Landmark-to-region map (landmarks may belong to two regions): torso {5,6,11,12}; arm_L {5,7}; arm_R {6,8}; thigh_L {11,13}; thigh_R {12,14}; shank_L {13,15}; shank_R {14,16}; head {0}. **Wrists 9 and 10 belong to no frozen region**, so appearance cannot attribute them; they need mask evidence.
- Landmark j is **appearance-positive** iff at least one region containing j has vote +1 against *every* rival β_k, and **appearance-contradicted** iff any region containing j has vote −1 against any rival.

**E_M — informative mask membership.**
- Per-landmark class from the frozen `ownership_v05.metrics`: OWN_ONLY / CONTESTED / OTHER_ONLY / OUTSIDE.
- Mask evidence is **informative** only if all hold: (i) every co-located detection has its own distinct owner mask (owner masks pairwise IoU < SEG_DUP_IOU 0.8; masks not shared); (ii) no other detection's confident landmarks lie inside `d_t`'s owner mask (opponent-inside fraction = 0, not merely < 25%); (iii) `unexplained_frac ≤ 0.25` (frozen). Condition (i)–(ii) are exactly the merged-mask situations (taxonomy T1) in which OWN_ONLY says nothing; when they fail, mask evidence is **uninformative** and contributes neither support nor contradiction.
- Landmark j is **mask-positive** iff mask evidence is informative and j is OWN_ONLY; **mask-contradicted** iff j is OTHER_ONLY or CONTESTED (informative or not: a contested landmark is never positive).
- Mutual exclusion (frozen shared-joint rule): a landmark within 0.05·diag of the same-index landmark of another detection counts as contradicted (double claim).

**Not used (and why).** Anchored limb-length ratios and torso-centred motion since the anchor were considered. Limb ratios mostly detect cross-body bones that V1's frozen `LIMB_TOO_LONG` already catches, and they are noisy under foreshortening; an anchor-referenced motion term would require an anchor-age constant. Both are reported as diagnostics only (not decision terms). V1's frozen 3-frame temporal check is already a prerequisite (an ASSIGNED row has passed it). Mask-vs-skeleton agreement beyond the above, merge guard, identity (g, q) and box IoU are not decision terms.

## 8. Uniqueness / ambiguity margin — definition without numeric thresholds

A row under test is **SUPPORTED_UNIQUE** iff all of the following hold (otherwise WITHHELD_C3 with the first failing reason, recorded):

1. Anchors and cast conditions of sections 4–5 are satisfied.
2. **No contradiction:** no landmark in L is appearance-contradicted, mask-contradicted or double-claimed; and no co-located `d_o` is appearance-contradicted as β under the same assignment.
3. **Every rival is positively excluded:** every landmark j ∈ L has at least one positive source (appearance-positive or mask-positive). This excludes every H_foreign(j, β_k); and because H_swap(β_k) asserts that all landmarks are foreign, it is excluded as soon as any landmark is positive.
4. **Ties withhold:** if the evidence that excludes a rival is identical to the evidence that supports it (no discriminating element), the rival is not excluded. Nothing is tie-broken.

The **ambiguity margin** of a row is the integer `margin(f) = min over j ∈ L of (number of positive sources for j)` ∈ {0, 1, 2}; SUPPORTED_UNIQUE needs `margin ≥ 1` and zero contradictions. It is reported for every row (including how many landmarks were supported by both families). The rule replaces a numeric score margin precisely so that no margin constant needs to be chosen. Frame-level ownership requires every landmark to be attributed; a row is also withheld if |L| < the frozen minimum (4 confident landmarks).

Interaction with the principle: weak or absent discrimination (similar clothing, merged masks, wrists with no appearance region and uninformative masks) yields WITHHOLD, never forced attribution (T5 ceiling).

## 9. Landmark-level versus frame-level withholding

**Primary (adopted for the design): frame-level, all-or-nothing.** If any landmark in L lacks a positive source or has a contradiction, the whole row is withheld. Rationale: emitting a landmark subset of a skeleton is structurally the same shape as the killed partial release; a subset's remaining landmarks would also depend on the rest of the assignment being correct. Per-landmark evidence is computed and logged (for diagnostics and audit) but not used to emit subsets.

**Option O-LM (not adopted, requires a separate ruling):** emit only the positively attributed landmarks of a V1-ASSIGNED row. It would raise contact yield but looks like partial release (even though it only subtracts from a V1-ASSIGNED row and uses positive exclusion evidence). I recommend it only be considered if frame-level C3 is safe but has too little yield.

## 10. Prohibition of carry, interpolation and repositioning (explicit protections)

1. Output rows are **V1's own measured rows** or withheld; C3 has no code path that writes a keypoint.
2. **Carry is disabled in and adjacent to intervals.** The frozen V1 visualization-only carry (≤ 3 source frames, from an ASSIGNED anchor) must not draw a carried skeleton for any source frame inside an interval (including the one-frame extensions), and must not use a `WITHHELD_C3` row as an anchor. A pass-through ASSIGNED row immediately before an interval cannot carry into it.
3. Anchors supply **reference descriptors only** (colour histograms). No anchor position is ever copied into the current frame.
4. Tests (section 15): bitwise equality of emitted keypoints with V1's; subset invariant; carry-suppression test; static (AST) test that the C3 module imports no carry or interpolation function and writes no coordinate field.

## 11. Camera cuts and resets

All anchors, intervals, cast definitions and models are per shot. A cut ends any interval; frames after the cut inside a continuing overlap have no anchor → WITHHOLD until a new interval with new pre-onset views exists. Zoom or lighting change inside a shot is not compensated; it surfaces as lowered appearance gap → uninformative → WITHHOLD.

## 12. How constants are chosen without burned labels

They are not chosen: every number is frozen from earlier a-priori config sections, a frozen seed rule, or structural (section 2). No constant in section 2 was derived from, or checked against, M9/M9B/M9C verdicts, the owner's notes, or the contact diagnostics. Descriptive geometry-only **feasibility counts** (how many intervals, anchors and cast sizes exist, how often the appearance gap gate passes) may be run on burned clips as an indicative count with **no verdict joined**, exactly as for SEP; this needs the reviewer's permission (section 19) and cannot adjust any constant.

## 13. C0 — the mandatory comparator

**C0 := withhold every V1 `ASSIGNED_A/B` row for which the frozen `overlap_context` (predicate (a) of section 3) is TRUE.** It uses only pre-existing geometry, no masks beyond V1, no appearance, no anchors. It is computed on the same rows and the same clips, deterministically, from the same V1 output. Row partition used for all comparisons (V1-ASSIGNED rows only):

| | C3 withheld | C3 retained |
|---|---|---|
| C0 withheld | R1 | **R2 rescue (extra yield beyond C0)** |
| C0 retained, in an interval | **R3 (extra safety beyond C0)** | R4c |
| C0 retained, outside any interval | R5 (not applicable: pass-through) | R5 |

C3 is "useful beyond C0" only through R2 (it keeps correct contact anatomy that the simple rule would drop) and R3 (it drops wrong-body anatomy that the simple rule would keep). Pure withholding (R1) is not credited.

## 14. Deterministic reproducibility

Pinned library versions (`requirements.lock`), frozen weights and cached seg outputs hashed as inputs, fixed decode path (frames decoded exactly as in frozen preprocessing; decoder and version recorded), enumeration in sorted order, no randomness, no multithreaded reductions on float sums that change order, ties withhold, exact comparisons on integer evidence (votes/classes/counts) so no floating tolerance enters the decision; the only floats are inside the frozen appearance functions, and a parity test requires identical decisions in two environments (CPU, clean-unzip) on the burned clips **as a reproducibility check only (no accuracy readout)**. Output includes a code-manifest hash and an input-hash block, and the run is exactly-once with a ledger precondition, as in earlier freezes.

## 15. Pre-implementation test plan (synthetic only)

Subset invariant; keypoint bitwise equality; carry suppression in/adjacent to intervals; cut reset; tracklet born in contact → withhold; unanchored participant → withhold; |Ω| > 3 → withhold; two-body toy scenes: separate masks with distinct clothing → SUPPORTED_UNIQUE, merged masks with identical clothing → WITHHELD, merged masks with distinct clothing → decided by appearance only, swapped-body skeleton → WITHHELD (or excluded), single-landmark-foreign skeleton → WITHHELD, wrists with no mask evidence → WITHHELD; ties withhold; input-order permutation invariance; determinism across two runs; constants audit; AST test that C3 reads no verdict, key, M9 file or identity-name field; no forbidden exposure/COM/speed vocabulary.

## 16. Prospective metrics (defined now; nothing computed)

**Contact-yield metric.** Over V1-`ASSIGNED` rows that lie inside C3 intervals on the evaluated fresh clips: `Y = retained by C3 / V1-ASSIGNED in-interval rows`, reported with: number of retained rows, number of distinct shots and clips with ≥ 1 retained row, per-reason withholding counts, anchor availability, appearance-gap pass rate, margin distribution, and the R1–R4c partition of section 13. Yield is reported per clip and pooled; no clip dominates (≤ 40% cap in the sample, as in SEP).

**Wrong-body metric.** From a blinded per-landmark review of the **sampled retained in-interval frames**: each drawn landmark is judged `ON_TARGET_BODY / ON_OTHER_BODY / OFF_BODY / CANNOT_TELL` (a localized judgement, not the frame-level PARTIAL/CONTAMINATED verdict whose owner–primary agreement was κ = 0.36). A frame is **wrong-body** iff ≥ 1 landmark is judged `ON_OTHER_BODY`; a frame is **NOT_JUDGEABLE** if no landmark can be judged. Primary estimate: wrong-body frames / judgeable frames, exact Clopper–Pearson 95% interval, clustered counts by shot and clip reported, reviewer-specific.

## 17. Future fresh-evaluation criteria (to be frozen only after reviewer approval; design now)

Units: V1-ASSIGNED in-interval pose frames on fresh clips, drawn with the SEP-style sampler (≥ 30-frame spacing, ≤ 10 per shot, ≤ 40% per clip, burned clips rejected), blinded strata: **retained (target)**, **R3 control** (C0 retained, C3 withheld), **non-interval V1-ASSIGNED control** (tests the interval predicate). Reviewers: independent human primary (R4-type blocker, same attestation) + owner blinded second + Claude non-independent sensitivity; KEEP must hold under both humans, less favourable binds; no pooling.

- **INCONCLUSIVE_DATA** if judgeable retained < 100, or shots < 20, or clips < 3, or fewer than 100 V1-ASSIGNED in-interval rows exist to draw from.
- **KILL (unsafe)** if wrong-body point ≥ 10% among judgeable retained frames, or wrong-body in ≥ 3 distinct shots, or the anchor audit (human check that anchor views show two separate, correctly delineated bodies) fails > 10%.
- **NO_ADDED_VALUE (C3 ≈ C0; treated as a KILL of C3 as a contact solution; C0 remains the fail-closed behaviour)** if retained yield `Y` < 10% of V1-ASSIGNED in-interval rows, or R2 (rescue) judgeable frames < 50, or the wrong-body rate of R3 (C0-retained, C3-withheld) is not higher than that of the retained frames (so a safety gain over C0 is not shown), or C3's retained set is a subset of C0's retained set. The 10% and 50% figures are **proposals without data justification**, set here by me for the reviewer to confirm or replace *before freeze*; they cannot be derived from burned frames.
- **KEEP** if none of the above and: exact two-sided Clopper–Pearson upper bound on wrong-body ≤ 5.0% among judgeable retained frames, wrong-body in ≤ 1 shot, anchor audit ≤ 5%, NOT_JUDGEABLE ≤ 20%, non-interval control wrong-body point < 10% (otherwise the interval predicate is under-sensitive and the result is MODIFY, not KEEP), and `Y` and R2 thresholds met. Allowable event counts follow the SEP table: n = 100 → 0 events (upper 3.62%), n = 150 → 2 (4.73%), n = 200 → 3.
- **MODIFY** otherwise (safe but borderline, or non-interval control unsafe), with reviewer interpretation required.

**Claim ceiling for any outcome:** a KEEP would mean only that, on the fresh clips and under this geometric interval definition, the frames C3 retained had wrong-body landmark attribution below the stated bound by blinded 2D visual review. It would not establish joint-position accuracy, identity, temporal accuracy, exposure, workload or generalisation, and would not lift any entry of the Section 7 prohibited-use list.

## 18. Evidence that C3 adds no useful information beyond C0 (to be reported, each prospectively)

1. Retained in-interval yield `Y` below the floor; or R2 (rescue) rows < floor; or R2 empty.
2. R3 contamination ≤ R4c contamination (C3's extra withholding removes no extra wrong-body frames).
3. Appearance discriminability: the share of in-interval V1-ASSIGNED rows in which at least one region type passes the frozen gap gate for every rival — if near zero, E_A never fires and C3 reduces to a stricter mask rule.
4. Anchor availability: the share of in-interval rows with a valid anchor and cast (the burned counts suggested about half of contaminated frames had even a single clean same-track frame; this is a reminder, not a design input).
5. Ablations on the same rows (decisions only, no reviewer data): E_M-only, E_A-only and full C3 give identical retained sets → one family is redundant; retained ⊆ C0-retained → nothing rescued.
6. Contamination among retained frames not lower than among R3 frames judged with the same protocol.

## 19. Fresh-data partition and what comes next

- Partition rule for later use of one acquisition for both the SEPARATED-BODY V1 and the contact evaluations: assign each fresh clip to exactly one confirmatory evaluation **before any pipeline output or review**, by a deterministic function of the clip's manifest id and the relevant freeze hash (stratified so that both evaluations get ≥ 3 sources/eras/resolutions and ≥ 2 promotions where feasible). Non-assigned use is development-only.
- Practical implication: contact needs contact-rich clips; a joint acquisition may therefore need substantially more than ~18 clips for two evaluations. Unknown until counts exist.
- Not started: implementation, tests, geometry-only feasibility counts on burned clips, sampling, reviewer recruitment (the independent human primary reviewer blocker remains for both evaluations).

## 20. Honest expectations and limits

- Likely outcome: contact yield will be low. C3 withholds unless **every drawn landmark** has independent positive support, and wrists cannot be supported by appearance regions at all; entangled pins/piles (T5) will be withheld by design; clothing similar between α and the rival silences appearance; merged masks silence the mask family. A "safe but not useful" outcome (NO_ADDED_VALUE) is a realistic result and is defined as a kill of C3 as a contact solution, not as a success.
- Assumption AS1 (separated tracklets are continuous before onset) is not verified here; the anchor audit tests it on fresh data.
- Appearance evidence is the frozen V0.3/V0.5 colour-histogram machinery: general, not validated on wrestling, not lighting-compensated.
- The interval predicate may be under-sensitive (the burned counts showed that box overlap detects few contaminated frames); the non-interval control exists to measure that.
- Any statement about prevalence of T1–T6 remains provisional; this design does not convert the taxonomy into validated rates.

## 21. Rulings requested

1. Approve the position of C3 as a subtract-only post-filter on V1 `ASSIGNED` output, and frame-level all-or-nothing emission (O-LM landmark-level emission not adopted).
2. Approve the interval definition (section 3) and the clean-anchor/expiry definition (section 4), in particular: no anchor age cap, two views ≥ 60 source frames apart, anchors never built from in-contact frames, post-contact frames not used as anchors.
3. Approve the finite hypothesis set (section 6) and the exclusion-logic uniqueness rule with integer margin (section 8) in place of a weighted cost.
4. Approve the constants audit (section 2): no new tunable constant; confirm the reuse of `MIN_GAP = 60` as view spacing and the structural minima.
5. Approve C0 as defined (frozen `overlap_context` only) and the R1–R4c partition.
6. Set or confirm the proposed usefulness floors (Y ≥ 10%, R2 ≥ 50 judgeable frames) before freeze, and the KEEP/MODIFY/KILL/NO_ADDED_VALUE map.
7. Permit geometry-only feasibility counts (interval, anchor, cast-size and appearance-gap-gate availability) on the burned clips, with no verdict joined and no constant adjustable from them.
8. Confirm the clip-to-evaluation partition rule (section 19).

STOP for reviewer ruling.
