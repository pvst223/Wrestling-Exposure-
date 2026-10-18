# POSTHOC_DIAGNOSTIC_V1 classification rule (written and hashed BEFORE any score was computed)
Post-hoc, descriptive, cannot alter Phase 1. Primary discrimination statistic: AUROC of L1 score max(pA,pB) separating TARGET candidates (truth = A or B) from NON-TARGET candidates (all other truth classes), per split, with a unit-clustered bootstrap (units = clip, shot, truth; 2000 resamples, seed 20261018) 95% interval. Same statistic for B0 score max(sA,sB).
- D4 INSUFFICIENT EVIDENCE: TEST has fewer than 10 target units or fewer than 10 non-target units, OR the TEST AUROC interval (L1) is wider than 0.40.
- Otherwise let a_T = TEST L1 AUROC, a_D = DEV L1 AUROC.
- D1 DISCRIMINATION FAILURE: upper bound of TEST interval < 0.65, or a_T <= a_D - 0.20 with TEST lower bound < 0.60.
- D2 CALIBRATION/OPERATING-POINT TRANSFER: TEST lower bound >= 0.70 and a_T >= a_D - 0.10, and the frozen floor 0.80 accepts < 5% of TEST target candidates.
- D3 MIXED: anything else (discrimination degraded but not absent, or not meeting D2 conditions).
Unit-level AUROC is also reported (unit score = mean of candidate scores) as a robustness view; it does not change the class.
