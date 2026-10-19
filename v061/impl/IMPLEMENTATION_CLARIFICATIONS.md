# V0.6.1 implementation clarifications (recorded prospectively, before any new development performance is inspected)

None changes the hypothesis, grids, equations, architecture, loss, thresholds or comparator of spec_v4. Each only resolves something spec_v4 left unspecified for code.

- **C1 Output reason for numeric failure.** spec_v4 01 says a numerical failure yields "not accepted". The code returns `REJECT_NONTARGET` (one of the four specified outputs) and a separate boolean `numeric_failure`; counted as not accepted, reported separately in diagnostics (`n_numeric_failures`).
- **C2 Definition of numerical failure.** spec_v4 names NaN/inf and pA+pB < 1e-12. The code additionally treats as failure any probability outside [0,1] by more than 1e-6 or |pA+pB+pN-1| > 1e-4 (fail-closed). For valid softmax outputs this never fires; it was chosen so malformed input cannot be accepted. Parity with the exploratory implementation holds on all valid softmax inputs (test_parity_with_exploratory_check).
- **C3 Boundaries.** g == tau_g passes the gate (reject only if g < tau_g); q == 0.5+delta accepts A; q == 0.5-delta accepts B. Same as the exploratory implementation. Floating-point arithmetic is IEEE-754 float64 and is not adjusted.
- **C4 Parameter validation.** tau_g must be in (0,1], delta in [0,0.5) (spec: tau_g > 0, delta in [0,0.5)); otherwise ValueError.
- **C5 Selection with folds.** spec_v4 03 section 3 needs per-fold coverage; `selection.py` accepts optional `fold_coverages` per grid point. With none given (single development episode) it reduces to pooled coverage, as in spec 09. No other selection logic exists.
- **C6 Unit and metric definitions** are re-implemented standalone (numpy/scipy) with the same definitions as frozen V0.6 `phase1_run.unit_table/table_metrics/paired`; a parity test against the frozen code runs when torch is available.
- **C7 Diagnostics** are descriptive only: they assign no KEEP/KILL/MODIFY class and no validation language. D-GATE and F-ASSIGN appear as descriptive flags, as in the 03 definitions.
- **C8 Training.** No training code is added here. Training remains the frozen recipe (spec_v4 01 "Kept frozen"); the training-data change requires the diversified TRAIN set under 02 and is not part of this package.
