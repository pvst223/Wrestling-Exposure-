# 09 Authorised exploratory run: `V0.6.1 DEVELOPMENT / HYPOTHESIS CHECK ONLY` (specified here; NOT run; requires a separate reviewer go-ahead to execute)

Purpose: a single check of whether the decision rule alone (no new training data) changes behaviour on existing exposed data. It cannot support any claim, cannot be iterated, and cannot be optimized against old TEST.

Design (fixed now):
- Head: the frozen V0.6 L1 seed-0 state dict (no retraining).
- Rule: the V0.6.1 two-stage rule (01), L1 grid of 49 points.
- Operating point: selected on old DEV only (Lesnar/Bryan) by the V0.6.1 selection procedure (03 section 3), where the per-fold requirement reduces to the single DEV episode, for L1; B0 re-selected the same way on its original frozen grid. If no feasible point exists, the result is "no feasible operating point" and the run ends.
- Evaluation: once on old TEST units, with the V0.6 unit tables and metrics (FTA, coverage, paired sign test, A-vs-B AUROC, gate AUROC), all labelled `V0.6.1 DEVELOPMENT / HYPOTHESIS CHECK ONLY`.
- No changes to thresholds, grids or the rule after seeing the output. The run is executed once. Any amendment prompted by it falls under the development-lock rule (01 section 7: at most one reviewed amendment round before freeze; no old-TEST-motivated change afterwards).
- Outputs: a hashed result file and ledger entry; no video unless separately authorised; no commit of person-level tables.
- Not a bake-off: no outcome class (KEEP/KILL/MODIFY) is assigned.
