# 07 Decisions only the reviewer can make

O1. B0 grid: keep the Phase-1 grid (20 points) or extend to the matched 49-point grid (recommended, for equal search budget; disclosed as TEST-motivated).
O2. Relaxed seed rule for TRAIN episodes (2 seeds, 1 shot): approve, restrict, or forbid. Without it, only the 4 strictly evaluable episodes (4 of 6 clips; HBK/Benjamin and Rock/HHH unusable) can contribute to training.
O3. Human second annotator for Holdout #2: who, what reserve fraction, whether the kappa gate is again deviated from.
O4. Identity-disjoint Holdout #2: require, or allow overlap with descriptive strata.
O5. Whether a decision-rule-only (no new training data) exploratory run on existing development data is permitted before acquisition, and how it is labelled (it cannot support claims).
O6. Repository controls: branch protection on `main`, required CI, and who may merge.
O7. Acquisition scope and rights review before any new footage: size targets in 02 section 2.5, sources, privacy handling of non-target people, retention limits.
O8. The F-GATE (0.70), F-ASSIGN (0.5), F-TRANSFER (one half) and coverage (0.10) cut-offs: approve or amend before freeze.
O9. Whether the A/B-assignment component, if falsified, should trigger a separately authorised fallback (B0-style assignment) or end the line.
