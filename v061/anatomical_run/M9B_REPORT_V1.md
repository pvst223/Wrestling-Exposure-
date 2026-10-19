# M9B targeted blind diagnostic — report (V1)

**Status:** exploratory, development-only, single non-independent reviewer (Claude), ANNOTATION-PROVISIONAL. Not validated accuracy. No rule, threshold, or ownership change. Merge guard stays diagnostic-only. M7 stays OPEN/NON-BLOCKING. R3 PARKED, R4 UNMET.

**Population:** measured pose AND identity in {ACCEPT_A, ACCEPT_B} AND ownership in {OWNERSHIP_UNCERTAIN, MIXED_BODY_SUSPECTED}, from the frozen Anatomical Integration V1 records (1383 rows, 1173 unique frames; M9 V1 items excluded). 60 unique frames frozen by deterministic rule (15 per clip = 7 MIXED + 8 UNCERTAIN) before any image was viewed (ledger M9B0). Verdicts frozen and hashed before the key was opened (ledger M9B1, sha 45bd7c69…). Key joined once.

## Overall (n=60)
| CORRECT | PARTIAL_BUT_USABLE | CONTAMINATED | NOT_JUDGEABLE |
|---|---|---|---|
| 11 | 34 | 9 | 6 |

- Usable (CORRECT+PARTIAL) among judgeable: **45/54 = 83.3%** (exact 95% CI 70.7–92.1%).
- Contaminated among judgeable: **9/54 = 16.7%** (exact 95% CI 7.9–29.3%).
- Population-weighted descriptive proportions (cell weights N_cell/n_judgeable, no CI): usable 83.2%, contaminated 16.8%.

## By ownership state
| State | n | C / P / X / NJ | usable (CI) | contaminated (CI) |
|---|---|---|---|---|
| OWNERSHIP_UNCERTAIN | 32 | 6 / 20 / 3 / 3 | 26/29 = 89.7% (72.6–97.8) | 3/29 = 10.3% (2.2–27.4) |
| MIXED_BODY_SUSPECTED | 28 | 5 / 14 / 6 / 3 | 19/25 = 76.0% (54.9–90.6) | 6/25 = 24.0% (9.4–45.1) |

## By clip
| Clip | n | C / P / X / NJ | usable (CI) | contaminated (CI) |
|---|---|---|---|---|
| b1_orton_rollins_wm31 | 15 | 4 / 8 / 2 / 1 | 12/14 = 85.7% (57.2–98.2) | 2/14 = 14.3% (1.8–42.8) |
| b2_batch2_clip_condensed | 15 | 3 / 7 / 4 / 1 | 10/14 = 71.4% (41.9–91.6) | 4/14 = 28.6% (8.4–58.1) |
| b2_videoplayback_2 | 15 | 2 / 9 / 2 / 2 | 11/13 = 84.6% (54.6–98.1) | 2/13 = 15.4% (1.9–45.4) |
| b2_videoplayback_5 | 15 | 2 / 10 / 1 / 2 | 12/13 = 92.3% (64.0–99.8) | 1/13 = 7.7% (0.2–36.0) |

Identity: ACCEPT_A 7 contaminated of 34 items; ACCEPT_B 2 of 26 (descriptive only).

## By ownership reason (items can carry several reasons; counts are per reason)
| Reason | items | verdicts |
|---|---|---|
| CONTESTED_LANDMARKS | 12 | P10 / X1 / C1 |
| TOO_FEW_OWN_ONLY_LANDMARKS | 11 | P9 / X1 / C1 |
| OPPONENT_LANDMARKS_IN_MASK | 10 | C3 / P5 / X1 / NJ1 |
| SHARED_JOINT_CONFLICT | 10 | C1 / P5 / X2 / NJ2 |
| BONE_SPANS_INSTANCES | 8 | C4 / P2 / X2 |
| MASK_NOT_EXPLAINED_BY_SKELETON | 7 | P5 / NJ2 |
| BONES_LEAVE_MASK | 5 | C2 / P3 |
| LANDMARKS_IN_OTHER_INSTANCE | 4 | C2 / P1 / X1 |
| LIMB_TOO_LONG:upper_arm | 3 | P2 / X1 |
| LIMB_TOO_LONG:shank | 2 | P2 |
| FEW_LANDMARKS | 2 | P1 / NJ1 |
| NO_OWNER_MASK | 2 | P1 / X1 |
| TORSO_SIDES_ASYMMETRIC | 2 | P2 |
| LIMB_TOO_LONG:thigh / :forearm, SOME_LANDMARK_IN_OTHER_INSTANCE, TEMPORAL_JOINT_JUMP | 1 each | see JSON |

(Per-reason cells show verdict counts: CORRECT / PARTIAL_BUT_USABLE / CONTAMINATED / NOT_JUDGEABLE as written out in `M9B_JOIN_RESULT.json`; abbreviations in the table are C=CORRECT, P=PARTIAL, X=CONTAMINATED, NJ=NOT_JUDGEABLE.)

## Reason families (item-level, overlapping)
| Family | items | judgeable | usable | contaminated |
|---|---|---|---|---|
| mask_overlap_ownership | 26 | 24 | 22 (91.7%; CI 73.0–99.0) | 2 (8.3%; 1.0–27.0) |
| geometry_cross_body | 19 | 16 | 13 (81.3%; 54.4–96.0) | 3 (18.8%; 4.0–45.6) |
| mask_span_other_instance | 10 | 10 | 7 (70.0%; 34.8–93.3) | 3 (30.0%; 6.7–65.2) |
| mask_support_missing | 9 | 8 | 7 (87.5%; 47.3–99.7) | 1 (12.5%; 0.3–52.7) |

Descriptive reading: usable withheld anatomy is concentrated in the mask-overlap/contested-landmark reasons (CONTESTED_LANDMARKS, TOO_FEW_OWN_ONLY_LANDMARKS, OPPONENT_LANDMARKS_IN_MASK, MASK_NOT_EXPLAINED_BY_SKELETON), which are mostly sparse-but-on-body skeletons. The families with the highest contaminated share are mask_span_other_instance (BONE_SPANS_INSTANCES, LANDMARKS_IN_OTHER_INSTANCE) and SHARED_JOINT_CONFLICT. Cell sizes are small and CIs wide; no family-level claim is made.

## Contaminated cases (9), individually
| id | clip | frame | shot | identity | state | reasons | note |
|---|---|---|---|---|---|---|---|
| B004 | b2_videoplayback_2 | 90 | 0 | ACCEPT_A | MIXED | LIMB_TOO_LONG:upper_arm | zig-zag skeleton spans two overlapping prone bodies |
| B010 | b2_batch2 | 3333 | 39 | ACCEPT_A | UNCERTAIN | CONTESTED_LANDMARKS, TOO_FEW_OWN_ONLY_LANDMARKS | one leg line on opponent's leg |
| B013 | b2_batch2 | 2493 | 31 | ACCEPT_A | MIXED | SHARED_JOINT_CONFLICT | carrier; one leg line on carried opponent |
| B021 | b2_videoplayback_5 | 3489 | 7 | ACCEPT_B | MIXED | SHARED_JOINT_CONFLICT | tangled grappling; lines span two bodies and a background boot |
| B032 | b2_videoplayback_2 | 1773 | 22 | ACCEPT_A | UNCERTAIN | NO_OWNER_MASK | two grappling bodies; lines not attributable to one wrestler |
| B034 | b1_orton_rollins_wm31 | 660 | 7 | ACCEPT_A | MIXED | BONE_SPANS_INSTANCES | pin; lines span top and bottom wrestlers |
| B037 | b2_batch2 | 2922 | 35 | ACCEPT_A | MIXED | LANDMARKS_IN_OTHER_INSTANCE | clinch; clusters on two wrestlers |
| B039 | b2_batch2 | 2967 | 35 | ACCEPT_A | UNCERTAIN | OPPONENT_LANDMARKS_IN_MASK | long leg line across lying opponent |
| B040 | b1_orton_rollins_wm31 | 225 | 1 | ACCEPT_B | MIXED | BONE_SPANS_INSTANCES | clinch; leg and arm segments on opponent |

Seven of nine contaminated frames are grappling/clinch/pin or carry contacts; 6 of 9 are MIXED. Merge guard flagged only 2 of 60 items (B008 PARTIAL, B059 NOT_JUDGEABLE), neither contaminated, so it did not separate these cases.

## Interpretation limits
- Single non-independent reviewer; verdicts were made on the blinded image only, but the reviewer wrote the pipeline and I applied a lenient "on one body" standard for PARTIAL_BUT_USABLE; sparse skeletons (one or two segments) are counted usable. The 6 NOT_JUDGEABLE frames are mostly close-ups with no skeleton drawn.
- Sampling is stratified, not proportional; weighted figures are descriptive, no CI. Temporal/spatial dependence within shots persists despite the ≥30-frame spacing.
- "Usable" is visual body-attribution only, not joint-accuracy, exposure, workload, fatigue or injury evidence.
- Because the sample is restricted to identity-ACCEPT frames, this result concerns withheld anatomy among identity-accepted frames only, and says nothing about the REJECT/ABSTAIN withheld frames.
- Not evidence for relaxing the ownership rule; no tuning was done.
