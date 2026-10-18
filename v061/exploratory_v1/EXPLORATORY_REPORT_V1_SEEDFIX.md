# V0.6.1 DEVELOPMENT / HYPOTHESIS CHECK ONLY: seed-fix result report (supersedes EXR1 for the seed defect ONLY)

Descriptive and exploratory only; development-exposed data; not validation; no KEEP/KILL/MODIFY/INCONCLUSIVE class assigned. Authorised by the reviewer ruling "SINGLE DEFECT-ONLY AMENDMENT AUTHORIZED" (ledger PL8). The original run (EXR1) is preserved unmodified.

## The defect and its correction
- Specification (spec_v3 file 09): bootstrap seed = `int(sha256_hex[:8],16) % 2**31`, where the hash is the SHA-256 of the pre-exploratory spec_v3 MANIFEST recorded at PL6.
- EXR1 supplied `f9a847361a64c48508be0c2c80da80226eb6a6e187e71c579157b8c05b28af8e`, which is the SHA-256 of the audit ledger through PL6 (verified), giving seed 2041071414.
- Correct input: the PL6 spec_v3 manifest SHA-256 `c37ee19190535b462fa25ac7202fe41eb7c1f617aa9e7871ffb0e8edf466de6d` (verified against the PL6 entry and the manifest file), giving seed **1132388753** (`int("c37ee191",16) % 2**31`). The formula is unchanged.
- Code change: only the seed input and ledger/result bookkeeping lines (see diff below). The computation is identical.
- Error disclosure: my earlier report and Chat prompt also mislabelled `f9a84736...` as the spec_v3 manifest SHA-256; that statement was wrong and is corrected here.

## Before/after (EXR1 -> corrected)
Deterministic quantities (all IDENTICAL): selected operating points (B0 tau 0.70 / margin 0.00; L1 tau_g 0.9 / delta 0.30), c* 0.5, joint levels, all DEV grid values, DEV in-sample metrics, TEST unit counts (B0 49/111 false-accept units, L1 0/111), FTA point estimates and exact Clopper-Pearson intervals (B0 0.4414 (0.3473-0.5388); L1 0.0000 (0.0000-0.0327)), coverage point estimates (B0 0.8139, L1 0.0087), paired sign test (b=49, c=0, p=1.8e-15), gate AUROC point estimate 0.9794, assignment AUROC point estimate 0.6841, decision decomposition, accepted-target count 9 (0 wrong wrestler), diagnostic flag values.

Seed-dependent quantities (the only ones that changed):
| quantity | EXR1 (seed 2041071414) | corrected (seed 1132388753) |
|---|---|---|
| B0 coverage 95% bootstrap CI | 0.7336-0.8848 | 0.7351-0.8877 |
| L1 coverage 95% bootstrap CI | 0.0003-0.0202 | 0.0003-0.0204 |
| Gate AUROC 95% CI | 0.9566-0.9921 | 0.9576-0.9925 |
| Assignment AUROC 95% CI | 0.5270-0.8161 | 0.5394-0.8208 |
Flags (descriptive only): D-GATE not flagged; F-ASSIGN interval still excludes 0.5 (lower bound 0.5394); unchanged.

Full leaf-by-leaf comparison: `SEEDFIX_COMPARISON.json` (every output, before, after, identical flag, seed-dependent flag). Result: 8 leaves changed (the seed and seven bootstrap interval endpoints); no deterministic quantity changed; every seed-dependent leaf except one unchanged endpoint changed as expected.

## Confirmation
Not changed: data, Holdout #2 (not accessed), head (frozen weights, hash asserted), thresholds, grids, c*, tie-breaking, matched-coverage definition, rule equations, labels, features, architecture, B0/L1 selected points, analyses (none added), operating points inspected (none beyond the specified ones). No outcome class assigned.

## Pre-freeze development observation (descriptive, non-confirmatory; carried into the final freeze documentation)
"Pre-freeze development observation: On development-exposed V0.6 data, the V0.6.1 two-stage rule using the frozen single-episode head remained strongly fail-closed. Target/non-target gating appeared strong, while A/B assignment appeared to be the principal limiting component. Because these observations arise from development-exposed data and the exploratory run does not include the planned training-diversity intervention, they are descriptive only and create no change to the preregistered evaluation criteria, thresholds, decision rules, or outcome classifications."
This observation is not a hypothesis, success/failure criterion, expected numerical result, diagnostic trigger or design justification.
