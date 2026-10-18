# POSTHOC_DIAGNOSTIC_V1

**Status: post-hoc, descriptive diagnostic only. Cannot alter Phase 1.** Phase 1 remains frozen: uncapped_methodological_outcome = MODIFY; reportable_status = MODIFY (ANNOTATION-PROVISIONAL). Study status ANNOTATION-PROVISIONAL; human reliability gate NOT SATISFIED AS SPECIFIED. Authorized by ledger entry PH2, after the primary result (PR1) and secondary result (SE1) were frozen. V0.6.1 is a proposal only and is not implemented. No claim of validation, accuracy, generalisation, clinical utility, workload, fatigue or injury prediction is made. Scores are heuristic evidence, not probabilities.

Method: frozen MobileCLIP-B features, the frozen L1 seed-0 state dict and the frozen episode manifest were read; L1 and B0 scores were recomputed with the frozen functions and reproduce the frozen TEST L1 scores (max abs difference 7.5e-09). Nothing was retrained, retuned or re-selected. Frozen parameters used throughout: B0 tau=0.30 margin=0.02; L1 floor=0.80, margin 0.0.

Data scale (important for every number below): TRAIN = 1 episode (2 identities); DEV = 1 episode (Lesnar/Bryan); TEST = 2 episodes (Andrade/Mysterio, Andrade/Omega), 111 units (56 target, 55 non-target). Domain, resolution and promotion shifts between splits are confounded with every DEV-to-TEST difference reported here.

## Pre-written classification rule
`CLASSIFICATION_RULE_V1.md` (SHA-256 `661c03ba8a392c842de8525a72928f0cda0ffb26b424f8c3069f39177c0cbb57`) was written and hashed before any score was computed.

## 1. Score-distribution findings (L1 max(pA,pB), candidate level)
| split / candidate role | n | q10 | median | q90 | max |
|---|---|---|---|---|---|
| train/TARGET | 268 | 0.923 | 0.988 | 0.994 | 0.995 |
| train/NONTARGET | 708 | 0.000 | 0.002 | 0.009 | 0.992 |
| dev/TARGET | 595 | 0.630 | 0.862 | 0.949 | 0.976 |
| dev/NONTARGET | 1387 | 0.001 | 0.003 | 0.058 | 0.874 |
| test/TARGET | 2195 | 0.449 | 0.556 | 0.697 | 0.800 |
| test/NONTARGET | 1869 | 0.000 | 0.000 | 0.014 | 0.759 |

- TEST target scores are shifted far down and compressed: median 0.556 vs DEV 0.862; the TEST maximum is 0.800, so the frozen floor 0.80 is essentially unreachable on TEST.
- Non-target scores stay near zero on both splits (TEST median 0.000; TEST pNON-TARGET median for non-targets 1.000).
- Because max(pA,pB) is capped when probability mass is split between A and B, a low score can mean "A/B ambiguous" and not only "not a target" (see section 3).

## 2. Threshold-free discrimination findings
Unit-clustered bootstrap (2000 resamples, seed 20261018); units = (clip, shot, truth).
| split | L1 AUROC target vs non-target (95% CI) | B0 AUROC (95% CI) | target / non-target units |
|---|---|---|---|
| TRAIN | 0.999 (0.991-1.000) | 0.937 (0.834-0.987) | 11 / 11 |
| DEV | 0.991 (0.980-0.998) | 0.957 (0.916-0.982) | 33 / 34 |
| TEST | 0.974 (0.951-0.989) | 0.914 (0.864-0.951) | 56 / 55 |

Per TEST episode L1 AUROC: Andrade/Mysterio 0.979; Andrade/Omega 0.982. Unit-level AUROC (mean score per unit): TEST L1 0.989, B0 0.938.

Finding: separating the two named wrestlers (as a pair) from everyone else is largely retained on TEST for L1 (and is higher than B0), with a small drop from DEV.

### 2b. Supplementary (added after first inspection of results; disclosed; does not change the pre-written classification): A-vs-B identity discrimination
AUROC of pA-pB (L1) or sA-sB (B0) for telling the two named wrestlers apart, among target candidates:
| split | L1 AUROC (95% CI) | B0 AUROC (95% CI) |
|---|---|---|
| TRAIN | 1.000 | 0.839 |
| DEV | 0.804 (0.631-0.929) | 0.919 (0.843-0.974) |
| TEST | 0.716 (0.606-0.842) | 0.807 (0.707-0.921) |
| TEST Andrade/Mysterio | 0.790 | 0.930 |
| TEST Andrade/Omega | 0.448 | 0.518 |

L1 separates the two wrestlers perfectly on its single TRAIN episode but much less well on DEV and TEST; on Andrade/Omega both L1 and B0 are near chance. B0 is better than L1 at telling the two wrestlers apart on DEV and TEST. This is a distinct failure from the target/non-target gate.

## 3. DEV-to-TEST confidence / calibration findings
- Fraction of target candidates with L1 max(pA,pB) >= 0.80: DEV 0.666, TEST 0.000. Non-target candidates >= 0.80: DEV 0.005, TEST 0.000.
- Reliability (share of candidates in a confidence bin that are targets assigned to the correct wrestler): on TEST the 0.4-0.6 bin is 0.498 (coin-flip) and 0.6-0.8 is 0.884; on DEV 0.8-0.9 is 0.832. Confidence carries information on TEST, but its scale is shifted down by roughly 0.2.
- Descriptive floor sweep (uses TEST labels; NOT an operating point and not usable for selection). Share of target candidates accepted as the correct wrestler / as the wrong wrestler / non-target candidates accepted:
  - TEST floor 0.50: 0.562 / 0.302 / 0.028
  - TEST floor 0.60: 0.270 / 0.028 / 0.009
  - DEV floor 0.80: 0.587 / 0.079 / 0.005
  Wrong-wrestler acceptance is about 30% at floors up to 0.5 on TEST and falls to under 3% at 0.6, so the confidence ordering is informative, but no floor on TEST gives high coverage with low error.

## 4. Abstention / rejection structure (frozen L1 rule, floor 0.80)
- TEST: all 2195 target candidates are either ABSTAIN (2062) or NON-TARGET (133); none accepted as A or B. All of the ABSTAIN target candidates whose argmax was A or B (1375 argmax-A, 631 argmax-B) were rejected only by the floor.
- TEST non-targets: referees 996/1065 labelled NON-TARGET, staff 152/197, spectators 607/607; the rest ABSTAIN; zero false accepts.
- DEV for comparison: 396 of 595 target candidates accepted; 7 false accepts among non-target candidates.
- Interpretation: L1 failed closed on TEST. The failure to accept is almost entirely floor-driven abstention, not rejection as non-target (8.6% of target candidates had NON-TARGET as argmax on TEST, 3.5% on DEV).

## 5. B0 false-accept structure (tau 0.30, margin 0.02)
- Unit level (frozen primary result): 39 of 111 units false-accepted (FTA 0.351): wrestler-assigned-to-the-other-wrestler 19 of 56, referee 9 of 33, staff 7 of 13, spectator 4 of 9 (the last two strata are descriptive, n<15).
- B0's tau=0.30 is non-selective on this backbone: 1.000 of TEST non-target candidates and 1.000 of target candidates have best cosine >= 0.30. Acceptance is therefore governed by the margin rule (0.02), which is small.
- Candidate level on TEST: of 2195 target candidates, 1371 accepted, of which 211 as the wrong wrestler; referees 41 of 1065, staff 29 of 197, spectators 7 of 607 falsely accepted. Most false-accept units are partial (median 12.5% of a unit's candidates) and 8 of 39 are a single candidate.
- Concentration: B0 false accepts concentrate in a few shots: Andrade/Omega Andrade shots 3 and 6 (40 and 34 false candidates) and Omega shot 0 (34); Andrade/Mysterio shots 13 (Mysterio, 13), 20 (Andrade, 16) and 31 (Andrade, 11).

## 6. Annotated diagnostic videos (post-hoc visualizations of frozen Phase-1 behaviour only)
Rendered from frozen features/head/manifests/tracklets with the frozen parameters; frozen TEST decisions were asserted equal to the recomputed ones. One output frame per frozen candidate frame, 10 fps; no interpolation; boxes are frozen tracklet boxes. Outputs are derived from source footage and are NOT in the repository (rights UNRESOLVED); they are delivered to the project owner only.
| video | SHA-256 | bytes | frames |
|---|---|---|---|
| DEV_lesnar_bryan.mp4 | `c04411e13cb7d349dd691fdc68dd5ac812ca509ceb167b26348e6f4658e1d548` | 9317168 | 504 |
| TEST_condensed_andrade_mysterio.mp4 | `a2f67d410a13306fbfdf0373caf70b30bcdc5ef400d05994afacfcf64d636083` | 20777730 | 1094 |
| TEST_andrade_omega.mp4 | `66943e59bd1cdbcefa9b41cb8638d413ae2388202feb23030324938dcf5ed53e` | 18766027 | 1009 |

Candidate-level outcome counts shown in the videos (B0 / L1): DEV OK 324/349; TEST (both episodes) L1 OK 0 and L1 false accepts 0; B0 TEST OK 1160. Full counts: `VIDEO_HASHES.json`.

## 7. Diagnostic classification
Per the pre-written rule: **D2 (primarily calibration / operating-point transfer failure)**. TEST L1 target-vs-non-target AUROC 0.974 (95% CI 0.951-0.989) vs DEV 0.991; the frozen floor accepted 0.000 of TEST target candidates.

**Caveat the reviewer should weigh (not a reclassification):** the rule was keyed to target-vs-non-target discrimination. The supplementary A-vs-B result (2b) shows that identity discrimination between the two named wrestlers degraded on TEST (L1 AUROC 0.716; 0.448 on Andrade/Omega, where B0 is also near chance), and that part of the "calibration" failure is the A/B split of probability mass. The rule-based label is D2; the full picture is closer to mixed. The reviewer may rule D2 or D3. Evidence is limited: 1 DEV and 2 TEST episodes, confounded shifts.

## 8. Smallest proposed V0.6.1 modification (PROPOSAL ONLY; NOT IMPLEMENTED)
- **Motivating observations:** (i) target-vs-non-target separation transferred (AUROC 0.97 on TEST); (ii) the DEV-selected floor 0.80 on max(pA,pB) did not (0 of 2195 target candidates cleared it); (iii) A-vs-B discrimination was weak on TEST while TRAIN was perfect.
- **Hypothesized mechanism:** the single softmax over A / B / NON-TARGET couples two different decisions. When the head cannot tell the two wrestlers apart, probability mass splits and max(pA,pB) stays low even for a clear target, so a single floor on max(pA,pB) rejects genuine targets. Separately, training on one episode with two identities likely left the A/B axis specific to that pair.
- **What should change (decision rule only):** decouple the decisions. (a) A target gate on the non-target probability, i.e. on 1 - pNON-TARGET = pA + pB, with its own DEV-chosen floor. (b) A wrestler assignment on pA / (pA + pB) with its own margin, abstaining when it is ambiguous. No new loss or architecture.
- **What stays frozen:** MobileCLIP-B backbone and preprocessing, the L1 architecture and training recipe (seed 0, Adam lr 0.01, 30 epochs), the episodic protocol and seeds, unit definitions, B0 as the comparator, c* matched-coverage selection rule, the paired exact sign test, outcome logic, annotation status, and all Phase-1 artifacts and results.
- **More TRAIN data:** required, not merely desirable, for any claim that A/B identity discrimination generalises (currently 1 TRAIN episode, 2 identities). The decision-rule change alone is a smaller step and could be evaluated without more TRAIN identities, but its A/B component should be expected to stay weak.
- **Falsification experiment (prospective):** pre-register the two-stage rule and the DEV-only selection of both thresholds; evaluate once on data not used in any diagnostic (Holdout #2 if the reviewer authorizes it, or newly acquired clips; the current TEST is already opened and cannot be reused for confirmation). Falsified if, at the matched coverage rule, unit-level FTA is not lower than B0's by the paired exact sign test, or if the A-vs-B AUROC interval includes 0.5. If only the A/B part fails, the finding is that the learned head supplies a non-target gate but no identity assignment.
- No training, rule change, data acquisition or new run has been done for this proposal.

## 9. Repository / developer-review findings (not scientific results)
- `selftest6.py` asserts that the authorization guard raises on the real ledger; since AUTH1 was recorded this assertion is stale and the test now fails (AssertionError: guard did not fail closed). It also depends on private files and absolute paths (`/home/claude/proj/v06_phase1/`, a MobileCLIP weight path). Not patched (frozen); recorded for a V0.6.1+ tooling fix. This does not touch any scientific result.
- Absolute paths are hardcoded in `phase1_structure.py`, `extract_features.py` (v05_src default) and selftest6.
- V0.6 has no pinned requirements file (only the V0.1 one exists).
- The README previously said all self-tests must pass from a fresh clone; selftest6 cannot (see above). README corrected.
- Secret scan (token patterns, key names) over the commit: nothing found. No weights, video, images or person-level tables are committed.
