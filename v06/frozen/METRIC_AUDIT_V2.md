# Metric audit: phase1_metrics.py v2 vs PREREGISTRATION_DRAFT_V2 (every primary quantity)
Code: tools/phase1_metrics.py (sha in ARTIFACT_HASHES_V2.txt). Tests: tools/selftest5.py (deterministic; all pass) plus selftest, selftest2-4.
| Preregistered quantity (section) | Implementation | Unit of analysis / n | Verifying test |
|---|---|---|---|
| Independent unit (4) | units_of(): key (clip_id, shot, truth_id); tracklets, frames, detections only collected as descriptive counts | unit | selftest5 #1 (50 tracklets x 40 detections = 1 unit), #3 (split across tracklets unchanged), #4 (shots/identities/clips are separate units) |
| Unit-level FTA by stratum, pooled (4) | metrics()["fta_by_negative_stratum"], ["fta_all_negative_units"]: unit has any false-accepted detection | n = units | #2 (1 false accept in 2000 detections = unit FTA 1/1), #1 |
| Exact CI (4) | cp(k, n) with k, n counted over units only | units | #1 (CI computed with n=1, not 2000), #7 |
| Descriptive-only n < 15 (4) | descriptive_only_n_lt_15 flag per stratum/pooled | units | #7 (14 units flagged, 15 not, regardless of 1400 detections) |
| A/B swap (4) | ab_swap_units; also inside OTHER_NAMED_WRESTLER stratum | wrestler units | #6 |
| Primary coverage (4) | target_coverage.coverage_mean_of_unit_fractions = unweighted mean of (correct accepts / detections) per target unit; no pooled version computed | target units | #5 (10/10 and 0/1000 gives 0.5, not 0.0099), #5b (two tracklets of one unit pool inside the unit) |
| Coverage CI (4) | seeded percentile bootstrap over units, labelled NOT EXACT; secondary exact CP on 'units with any correct accept' | target units | #10 (determinism) |
| Frame-level FTA (4) | secondary_descriptive_frame_level, no CI, labelled descriptive | detections | #2 |
| Paired endpoint b, c, exact sign test (6) | paired_sign(): per-unit false-accept flags, requires identical unit sets, p = P(X >= b), Binomial(b+c, 0.5) | units | #8 (prereg table values 0.0625, 0.03125, 0.125, 0.0625, 0.03515625), #8b (30 detections in one unit = 1 discordant unit), unit-set mismatch raises |
| Seed exclusion (3) | exclude_seed_tracklets() removes only listed tracklets | tracklets | #9 |
| Risk-coverage (5, secondary) | risk_coverage(): at each threshold recomputes unit FTA and mean-of-unit-fraction coverage | units | selftest5 #10 (metrics deterministic) |
| LOCO (7, secondary) | by_component(): descriptive per-component metrics; no decision logic anywhere in the code | units | #11 |
| KEEP / MODIFY / KILL rule (6) | NOT implemented as code on purpose: decided by the registered human review of metrics.json (no auto-decision) | n/a | n/a |
Known limits: the bootstrap CI for coverage is not exact and not strictly independent (units within a shot-adjacent sequence may be correlated); it is secondary. Adjacent shots of the same match are treated as independent units (disclosed, preregistered).
Changed since v1 code: v1 treated a tracklet as the unit, computed pooled frame coverage and gave frame-level quantities CIs; v1 outputs are not used anywhere. The old file is kept as phase1_metrics_v1_superseded.py for the audit trail only.
