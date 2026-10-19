# M9C REPORT V1

Outcome per frozen Amendment-1 rules and reviewer rulings 5a-5c, applied mechanically by `m9c_join.py decide()`.

**LABEL: development-only, ANNOTATION-PROVISIONAL, primary reviewer Claude is non-independent. No validation, accuracy, generalisation or clinical claim. Rights UNRESOLVED.**

## Outcome

**KILL** (mechanical). Two independent KILL triggers fired:

1. Contamination of judgeable released frames = 12/52 = 23.1% (exact 95% CI 12.5-36.8%) >= 10.0%.
2. Structural wrong-body determination = YES in 5 distinct shots (>= 2), established prospectively by localized inspection (ruling 5a).

The KILL decision does not rely on the structural clause: trigger 1 alone decides. It also holds under every sensitivity below.

## Released stratum (n=60, Claude primary)

- Verdicts: {'CONTAMINATED': 12, 'CORRECT': 9, 'NOT_JUDGEABLE': 8, 'PARTIAL_BUT_USABLE': 31}
- Judgeable 52; usable 40 = 76.9% (CI 63.2-87.5%); NOT_JUDGEABLE 8 = 13.3%.
- Coverage gain 8.21 points of the 2179 identity-ACCEPT measured frames (179 structural releases).

## Gates

- contamination_le_5pct: NOT MET
- coverage_ge_5pts: MET
- hardveto_ge_2x_released: NOT MET
- judgeable_ge_50: MET
- no_clip_ge_3_contaminated: NOT MET
- not_judgeable_le_25pct: MET

Hard-veto control contaminated 10/26 judgeable = 38.5%; ASSIGNED control 7/30 = 23.3%. Hard-veto control is informative (non-zero) but is NOT >= 2x the released rate (38.5% vs 2x23.1%), so that criterion is unmet. Released frames are not cleaner than assigned frames; released contamination is not lower than either control.

## Per clip (released)

| clip | n | judgeable | contaminated |
|---|---|---|---|
| b1_orton_rollins_wm31 | 5 | 4 | 2 |
| b2_batch2_clip_condensed | 21 | 18 | 4 |
| b2_videoplayback_2 | 14 | 14 | 1 |
| b2_videoplayback_5 | 20 | 16 | 5 |

Clips with >=3 contaminated: b2_videoplayback_5 (5). Gate unmet.

## Every contaminated RELEASED frame and wrong-body determination (Claude, localized, prospective rule 5a)

| id | clip | shot | frame | tier-A reasons | determination | note |
|---|---|---|---|---|---|---|
| M026 | b1_orton_rollins_wm31 | 7 | 684 | MASK_NOT_EXPLAINED_BY_SKELETON | YES | long bone from top wrestler's hip runs onto underlying wrestler's head/hand region |
| M033 | b2_videoplayback_5 | 0 | 1077 | MASK_NOT_EXPLAINED_BY_SKELETON | UNDETERMINED | entangled pin; cannot tell which wrestler's body each released landmark lies on |
| M035 | b2_batch2_clip_condensed | 25 | 2127 | MASK_NOT_EXPLAINED_BY_SKELETON | UNDETERMINED | tangle of masked and yellow wrestlers; ownership of released landmarks not resolvable in 2D |
| M041 | b2_videoplayback_5 | 0 | 1155 | MASK_NOT_EXPLAINED_BY_SKELETON | YES | hip landmarks and descending bones lie on the lower wrestler's back, shoulders on the top wrestler |
| M062 | b1_orton_rollins_wm31 | 7 | 723 | MASK_NOT_EXPLAINED_BY_SKELETON | YES | left lower corner of released torso box lies on the underlying wrestler's head/neck |
| M063 | b2_batch2_clip_condensed | 35 | 2997 | CONTESTED_LANDMARKS,TOO_FEW_OWN_ONLY_LANDMARKS | YES | released landmarks lie on the referee's shirt and trousers |
| M064 | b2_batch2_clip_condensed | 20 | 1425 | CONTESTED_LANDMARKS | YES | hip/knee bones lie on the other wrestler's striped trousers |
| M065 | b2_videoplayback_5 | 0 | 1014 | CONTESTED_LANDMARKS | YES | hip landmark lies on the underlying wrestler's back |
| M100 | b2_videoplayback_2 | 15 | 1314 | CONTESTED_LANDMARKS | UNDETERMINED | pile; multiple bodies, ownership not resolvable |
| M105 | b2_videoplayback_5 | 0 | 1119 | MASK_NOT_EXPLAINED_BY_SKELETON | NO | shoulder-hip-knee-foot chain is consistent with the single white-trousered wrestler; frame label CONTAMINATED stands but no wrong-body landmark established |
| M107 | b2_batch2_clip_condensed | 23 | 1863 | MASK_NOT_EXPLAINED_BY_SKELETON | YES | bones span yellow-trouser leg, gold-masked wrestler's chest and underlying body |
| M118 | b2_videoplayback_5 | 0 | 117 | CONTESTED_LANDMARKS,TOO_FEW_OWN_ONLY_LANDMARKS | UNDETERMINED | clinch; waist landmarks may lie on the front wrestler, not resolvable |

Determination caveat: made by the same non-independent reviewer from the drawn 2D image only (no key-derived info beyond identity/reason lists shown in the join); entangled pins are frequently UNDETERMINED. Counting only YES; 5 distinct shots (b1 s7, vp5 s0, b2_batch2 s35, s20, s23).

## Owner second review (separate, does not decide the outcome)

- Overlap n=50: raw agreement 0.56, Cohen kappa 0.36. Released overlap n=30: agreement 0.63, kappa 0.39.
- Owner released overlap: {'CONTAMINATED': 6, 'NOT_JUDGEABLE': 5, 'PARTIAL_BUT_USABLE': 19} (contaminated 6/25 judgeable = 24.0%); Claude on same 30: contaminated 5/25 = 20.0%.
- Main released with owner verdicts substituted on the 30 overlap: contaminated 13/52 = 25.0% (CI 14.0-38.9%): KILL threshold still met.
- Disagreements: on the 30 released overlap, Claude CORRECT vs owner PARTIAL in 4; Claude PARTIAL vs owner CONTAMINATED in 3; Claude CONTAMINATED vs owner PARTIAL in 2. The owner's own released contamination (6/25 = 24%) is also >= 10%, so the KILL outcome does not depend on which reviewer is used.

## Sensitivity

- By contact: no-contact released contamination 0/17; contact 12/35 (all contamination is in contact frames).
- By identity: ACCEPT_A 4/29; ACCEPT_B 8/23.
- Merge-guard flagged items (diagnostic only): 6, of which contaminated 2.
- Lower CI bound of released contamination (12.5%) exceeds 5% and the point estimate exceeds 10%.

## Limitations

Primary reviewer non-independent; strata partly inferable from drawn landmark count; clip imbalance; kappa is only fair (0.36 overall); wrong-body calls are visual 2D judgments. No tuning, rule change, exposure or workload computation was performed. Interpretation of the outcome and of Tier-A subsets is left to the reviewer.
