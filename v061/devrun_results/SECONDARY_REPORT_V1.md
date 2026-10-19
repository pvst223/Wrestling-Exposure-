# V0.6.1 secondary development package: seed variance + descriptive ablations (for reviewer audit)
Label: **V0.6.1 SECONDARY DEVELOPMENT ANALYSIS (development-exposed; exploratory; NOT validation).** Secondary and descriptive; no outcome class; no scientific change; locked rule/grids/selection/metrics/backbone/loss/architecture used unchanged. R3 PARKED (UNRESOLVED / THIRD-PARTY TRANSMISSION BLOCKED); R4 UNMET (declared AI substitution); V0.6.1 ANNOTATION-PROVISIONAL.

## 0. Scope statement (goalposts)
The MP4s delivered with the previous package are a 30 fps **identity-decision** visualization only. They are not the anatomical-ownership / pose / tracking visualization, which is not implemented in V0.6.1 development so far; no claim to that effect is made. No renders were produced in this step.

## 1. Provenance
Executed once after one recorded pre-result crash (ledger DR2X: `KeyError: 'targets'`, a mechanical driver defect before any scoring; fixed and re-registered as DR2R). Seed 0 was re-run as an integrity check and **reproduced the DR1 L1 grid exactly** (`l1_grid_identical_to_dr1 = true`). Not done: final all-development head; old-TEST rerun; Holdout #2 access. Same data, folds and K = 5 seed draws for all seeds; heads differ only by training/initialisation seed.

## 2. Seeds 1–3 variance (L1 two-stage rule, pooled out-of-fold, 200 units)
Fixed point = the DR1 seed-0 point (tau_g 0.9, delta 0.10) applied unchanged:

| seed | FA units (FTA) | coverage | gate AUROC | A/B AUROC (95% CI) | wrong-wrestler / accepted target | abstained | gate-rejected targets |
|---|---|---|---|---|---|---|---|
| 0 | 68/200 (0.340) | 0.587 | 0.989 | 0.808 (0.733–0.875) | 406/2136 | 591 | 331 |
| 1 | 71/200 (0.355) | 0.549 | 0.984 | 0.770 (0.698–0.853) | 586/2258 | 304 | 496 |
| 2 | 83/200 (0.415) | 0.564 | 0.984 | 0.749 (0.677–0.826) | 689/2391 | 346 | 321 |
| 3 | 78/200 (0.390) | 0.536 | 0.985 | 0.722 (0.637–0.819) | 700/2278 | 393 | 387 |

Across seeds 0–3 (min / mean / max): fta 0.340 / 0.375 / 0.415; coverage 0.536 / 0.559 / 0.587; gate_auroc 0.984 / 0.986 / 0.989; ab_auroc 0.722 / 0.762 / 0.808. Seed 0 (the DR1 headline) is the most favourable of the four on FTA and A/B AUROC.

Re-selection view (same deterministic procedure at the joint c* = 0.5, V0.6 variance precedent):

| seed | selected (tau_g, delta) | FA units (FTA) | coverage | A/B AUROC |
|---|---|---|---|---|
| 0 | (0.9, 0.1) | 68/200 (0.340) | 0.587 | 0.808 |
| 1 | (0.7, 0.2) | 76/200 (0.380) | 0.551 | 0.770 |
| 2 | (0.7, 0.2) | 79/200 (0.395) | 0.548 | 0.749 |
| 3 | (0.9, 0.1) | 78/200 (0.390) | 0.536 | 0.722 |

The gate is stable across seeds (AUROC 0.984–0.989). A/B assignment is not: AUROC 0.722–0.808, wrong-wrestler assignments 406–700 of 2,136–2,391 accepted target candidates. B0 is deterministic (unchanged: 0.455 FTA, 0.732 coverage at its selected point).

## 3. Ablation A: old 3-class floor rule + new cross-fitted head (seed 0)
Selected floor 0.6 at c* = 0.5: FA units 75/200 (0.375), coverage 0.611; wrong-wrestler 425/2194; non-target candidates accepted 69 (new rule at its selected point: 68/200, 0.587, 406/2,136, 43). The two rules give similar A/B behaviour on the same head; the old rule accepts more non-target candidates (69 vs 43). Descriptive; operating points are not coverage-matched.

## 4. Ablation B: new rule + frozen V0.6 single-episode head (trained on Orton/Rollins), scored on the other 3 evaluable episodes (178 units); comparison = seed-0 cross-fitted head, same episodes
Fixed point (0.9, 0.10):

| head | FA units (FTA) | coverage | gate AUROC | A/B AUROC (95% CI) | wrong-wrestler / accepted target | abstained | gate-rejected targets |
|---|---|---|---|---|---|---|---|
| old single-episode | 44/178 (0.247) | 0.468 | 0.979 | 0.715 (0.595–0.819) | 144/1179 | 1212 | 399 |
| new cross-fitted (seed 0) | 59/178 (0.331) | 0.577 | 0.989 | 0.814 (0.730–0.887) | 353/1908 | 577 | 305 |

Re-selected points: old head (0.8, 0.05) FTA 0.360, coverage 0.582; new head (0.9, 0.1) FTA 0.331, coverage 0.577. At the fixed point the old head abstains far more (1,212 vs 577 target candidates), so its lower FTA comes with lower coverage; at re-selection the new head has lower FTA at similar coverage. A/B AUROC 0.715 (old) vs 0.814 (new).

## 5. Ablation C: drop relaxed-seed training episodes (HBK/Benjamin and Rock/HHH contribute nothing), seeds 0–3, fixed point

| seed | FA units (FTA) | coverage | gate AUROC | A/B AUROC (95% CI) | wrong-wrestler / accepted target | abstained | gate-rejected targets |
|---|---|---|---|---|---|---|---|
| 0 | 69/200 (0.345) | 0.465 | 0.971 | 0.708 (0.634–0.789) | 471/1824 | 496 | 738 |
| 1 | 61/200 (0.305) | 0.515 | 0.966 | 0.739 (0.676–0.808) | 398/1791 | 516 | 751 |
| 2 | 71/200 (0.355) | 0.481 | 0.978 | 0.698 (0.614–0.776) | 481/1948 | 480 | 630 |
| 3 | 68/200 (0.340) | 0.518 | 0.972 | 0.703 (0.633–0.784) | 421/1720 | 748 | 590 |

Mean over seeds 0–3 (with relaxed episodes → without): gate AUROC 0.986 → 0.972; A/B AUROC 0.762 → 0.712; coverage 0.559 → 0.495; FTA 0.375 → 0.336. Without the two extra clips, both gate and assignment AUROC are lower and more targets are rejected at the gate.

## 6. Where the A/B weakness sits (prespecified breakdowns, seed-0 head, fixed point)

| evaluation episode | A/B AUROC (95% CI) | gate AUROC | coverage | FTA (units) | main assignment confusion |
|---|---|---|---|---|---|
| b1_orton_rollins_wm31 (randy_orton/seth_rollins) | 0.836 (0.760–0.915) | 0.991 | 0.671 | 0.409 | randy_orton → seth_rollins: 51; seth_rollins → randy_orton: 2 |
| b2_batch2_clip_condensed (andrade/rey_mysterio) | 0.863 (0.757–0.956) | 0.978 | 0.599 | 0.322 | andrade → rey_mysterio: 49; rey_mysterio → andrade: 43 |
| b2_videoplayback_2 (brock_lesnar/daniel_bryan) | 0.875 (0.752–0.959) | 0.998 | 0.661 | 0.269 | brock_lesnar → daniel_bryan: 39; daniel_bryan → brock_lesnar: 57 |
| b2_videoplayback_5 (andrade/kenny_omega) | 0.530 (0.329–0.666) | 0.991 | 0.237 | 0.571 | andrade → kenny_omega: 135; kenny_omega → andrade: 30 |

The weakness is concentrated: A/B AUROC is 0.84–0.88 in three episodes but 0.530 (CI 0.329–0.666, includes 0.5) in the Andrade/Omega episode, where 135 of 393 target Andrade candidates were accepted as Omega, 189 + 285 target candidates were abstained, and coverage is 0.237. Per-episode intervals are wide (few units; clip-level clustering). The Andrade/Omega clip and the Orton/Rollins episode (Orton → Rollins 51 of 242) carry most wrong-wrestler assignments in absolute terms.

Distribution shift (descriptive adaptation of the calibration-transfer metric): A/B AUROC on training episodes in-sample is 0.995 versus 0.808 out-of-fold; median |q−0.5| for target candidates is 0.498 in-sample versus 0.291 out-of-fold (10th percentile 0.371 vs 0.044); median g is 0.9999 vs 0.9981. The head is near-saturated on its training pairs and much less decisive on held-out pairs.

## 7. Observations for the reviewer's next prospective design decision (descriptive; none is a recommendation or a change)
1. Target/non-target gating is stable across seeds (AUROC 0.984–0.989) and across ablations A and B; it drops when relaxed-seed clips are removed from training (0.966–0.978).
2. A/B assignment is seed-sensitive (0.722–0.808), the DR1 seed-0 headline is the favourable end, and the old 3-class rule shows similar A/B behaviour, so the decoupled rule alone does not address assignment.
3. Assignment failure is localized (Andrade/Omega episode near chance) and the head separates training pairs almost perfectly but held-out pairs much less (in-sample 0.995 vs out-of-fold 0.808), consistent with pair-specific training on few identities. Adding the two relaxed clips helped on average, within this thin evidence.
4. Everything rests on 4 evaluable episodes / 3 evaluable folds (200 units; clustered by clip and identity; erratum 001). Nothing supports generalisation, clinical utility, workload/fatigue or injury prediction.

## 8. Hashes and boundaries
Locked implementation manifest `eb99beb3…` verified unchanged; secondary code manifest (DR2R) `0c34fd47…`; result JSON sha256 recorded in ledger DR3; DR1 result `98ebb67e…` (input). Erratum 001 (`v061/errata/`) records the 3-folds/4-episodes wording correction without altering frozen files. Old-TEST check not rerun; Holdout #2 not accessed; no Gemini transmission; no final head trained; no change to rule, grids, thresholds, selection, metrics, backbone, loss or architecture.
