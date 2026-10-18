# 08 Reviewer amendments and where they were applied

| Reviewer amendment (PL3) | Applied in |
|---|---|
| Approve two-stage L1 rule | 01 header and rule text |
| Keep original frozen B0 grid; do not extend to match grid size | 01 grids (B0 20 points); 03 sections 2-3; 06 A3; 07 F1 (asymmetry disclosed) |
| Approve relaxed TRAIN-only seed rule and K=5; evaluation strict; resamples not independent | 01 "Training-episode resampling"; 02 section 2.4 |
| Holdout #2 independent blinded HUMAN second annotator, ~20% reserve spanning clips and truth classes; kappa >= 0.60 reliability gate only | 02 section 2.6; 03 sections 7-8; 06 B7; 07 F2-F3 |
| Holdout #2 identity-disjoint; event/source disjoint; prospective duplicate/replay audit | 02 section 2.6; 06 B3, B15, B16; 07 F4 |
| One decision-rule-only exploratory run on exposed data, labelled `V0.6.1 DEVELOPMENT / HYPOTHESIS CHECK ONLY` | 09 (specified, not run); 01 section 7; 06 A10 |
| Repository/tooling controls approved; reviewable commits and reviewer authorization before merge/freeze | 05 (new "Review and merge control" row); 07 F8 |
| Remove Holdout criterion requiring an expected number of B0 false-accept units; size by prospective total/target/negative counts and diversity | 02 section 2.5; 06 B17 |
| Retain primary FTA-vs-coverage and 0.10 coverage margin; F-ASSIGN stays | 03 sections 2, 5, 7 |
| F-GATE (0.70) and F-TRANSFER (half) become preregistered diagnostic/transfer flags (D-GATE, D-TRANSFER), not hard KEEP requirements | 03 sections 5, 7; 07 F6 |
| F-ASSIGN falsified gives MODIFY / component failure; no automatic B0 assignment fallback; hybrid needs a separately authorised version | 03 sections 5, 7 |
| Development-lock rule | 01 section 7; 06 A10, A11 |
| Approve 30-fps renderer (EVALUATED / CARRIED-FORWARD / NO-EVAL; no interpolation or extra inference) | 04 (unchanged architecture, status line updated) |

Superseded: `spec_v1/` (first draft) is kept unchanged for chronology.
