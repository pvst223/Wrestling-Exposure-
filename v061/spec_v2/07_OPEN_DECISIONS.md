# 07 Items for final freeze review (REVISION 2)

Resolved by the reviewer ruling (PL3): two-stage rule approved; B0 grid kept at the original 20 points; relaxed TRAIN-only seed rule and K=5 resampling approved; human second annotator with ~20% reserve required; Holdout #2 identity-, event- and source-disjoint with prospective duplicate/replay audit; one exploratory run allowed; repository/tooling controls approved; B0-error-based Holdout sizing removed; F-GATE and F-TRANSFER reclassified as diagnostic flags; F-ASSIGN failure gives MODIFY with no automatic B0 fallback; development-lock added; renderer approved.

Items still needing a reviewer decision before the freeze:
F1. L1 grid is 49 points against B0's 20. Keep (disclosed asymmetry) or shrink the L1 grid (e.g. tau_g {0.5,0.6,0.7,0.8,0.9} x delta {0.05,0.10,0.20,0.30} = 20 points) to match the comparator without changing B0.
F2. Exact reserve fraction and stratification for the human second annotator (default: 20%, at least 10 tracklets per truth class per clip where available), and the selection seed procedure (derived from the frozen spec hash).
F3. Independence criteria for the human annotator (not the project owner, not a developer on the repo, not exposed to model outputs or B0 decisions); how independence is documented.
F4. Operational definition of "event/source-video disjoint" (default: different broadcast event/date and different source file/upload; owner-declared and hash-audited) and who acts as custodian.
F5. Execution go-ahead and exact timing for the exploratory run (09), and whether the single amendment round after it may include changes to the L1 grid.
F6. Whether D-GATE or D-TRANSFER should be promoted to hard KEEP criteria; reviewer may do so only prospectively with independent justification, before the freeze.
F7. Rights and privacy review of acquisition (size targets approved in principle): sources, handling of non-target people, retention limits.
F8. Who may merge V0.6.1 pull requests and the branch-protection settings on `main`.
