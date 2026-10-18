# V0.6.1 DEVELOPMENT / HYPOTHESIS CHECK ONLY: result report

Descriptive and exploratory only. It cannot support any claim and is not validation. Old V0.6 TEST is development-exposed; nothing here is confirmatory. No KEEP/KILL/MODIFY/INCONCLUSIVE class is assigned. Executed exactly once (ledger PL7 before, EXR1 after). No head was trained or changed (frozen V0.6 L1 seed-0 MobileCLIP-B head); Holdout #2 was not accessed; no data was acquired.

Design as specified in spec_v3 file 09: V0.6.1 two-stage rule; L1 grid tau_g {0.5,0.6,0.7,0.8,0.9} x delta {0.05,0.10,0.20,0.30}; B0 original frozen grid; thresholds selected on old DEV only (Lesnar/Bryan; matched coverage c* = 0.5, reached by both methods; all five levels were jointly reachable); evaluated once on old TEST (Andrade/Mysterio, Andrade/Omega; 111 units, 56 target). Bootstrap seed 2041071414 (derived from the pre-exploratory spec manifest hash).

## Selected operating points (DEV only)
- B0: tau 0.70, margin 0.00 (DEV unit FTA 0.463, coverage 0.589). Note B0 was re-selected under the V0.6.1 procedure; it is not the Phase-1 point (0.30, 0.02).
- L1 two-stage: tau_g 0.9, delta 0.30 (DEV unit FTA 0.179, coverage 0.548). This is the most conservative corner of the grid on both axes.

## Old TEST results (exploratory)
| | B0 | L1 two-stage (frozen head) |
|---|---|---|
| false-accept units | 49 / 111 | 0 / 111 |
| unit FTA (exact 95% CI) | 0.441 (0.347-0.539) | 0.000 (0.000-0.033) |
| target coverage (bootstrap 95% CI) | 0.814 (0.734-0.885) | 0.009 (0.0003-0.020) |

- Paired sign test: b = 49 (B0 only), c = 0, one-sided p = 1.8e-15. This is vacuous because the two-stage rule accepted almost nothing; it says nothing about discrimination.
- Gate AUROC (g = pA+pB, target vs non-target): 0.979 (0.957-0.992).
- Assignment AUROC (q, A vs B among targets): 0.684 (0.527-0.816).
- Decision decomposition (candidates). Targets (2195): ABSTAIN-ambiguous 1867, REJECT-nontarget 319, ACCEPT 9 (0 as the wrong wrestler). Referee (1065): REJECT 1046, ABSTAIN 19. Staff (197): REJECT 174, ABSTAIN 23. Spectator (607): REJECT 607. There were no non-target accepts.
- Diagnostic flags (descriptive only): D-GATE not flagged (lower bound 0.957 > 0.70). F-ASSIGN interval excludes 0.5, but only narrowly (lower bound 0.527).
- Frozen Phase-1 reference (unchanged): B0 FTA 0.351 / coverage 0.731; L1 FTA 0.000 / coverage 0.000; reportable MODIFY (ANNOTATION-PROVISIONAL).

## Observations (not conclusions)
1. The rule-only change did not recover usable coverage on old TEST: L1 stays fail-closed with 9 target candidates accepted of 2195 (coverage 0.009), and the DEV-selected point sits at the most conservative grid corner.
2. The new rule's gate separates targets from non-targets well (AUROC 0.979), as in the post-hoc diagnostic. The binding constraint is the assignment stage: 1867 of 2195 target candidates are abstained as A/B-ambiguous, consistent with the assignment AUROC of 0.684.
3. DEV could not offer a lower-FTA point at coverage >= 0.5 than the corner; DEV in-sample L1 FTA was still 0.179 (12 false-accept units), so DEV selection itself was constrained.
4. B0's re-selected point trades more false accepts (0.441) for higher coverage (0.814) than the Phase-1 point.
5. This check bundles no training-diversity effect: the head is the single-episode frozen head. It therefore speaks to the rule alone on exposed data.

## Defect review (development-lock, 01 section 7)
I checked the implementation against spec_v3 (rule equations, grids, c* and tie-break procedure, matched-coverage definition, bootstrap seed derivation, labelling). I found no genuine specification or implementation defect and propose no correction. In particular, the corner selection and the coverage collapse are consequences of the specified procedure, not errors, and under the development-lock they cannot be addressed by changing the grid, equations, thresholds/selection procedure, architecture or comparator.

## Freeze candidate
The freeze candidate is `v061/spec_v3` unchanged (manifest SHA-256 `f9a847361a64c48508be0c2c80da80226eb6a6e187e71c579157b8c05b28af8e`), with this exploratory result attached for the reviewer. No amendment is proposed. Reviewer decision needed: freeze spec_v3 as is, or authorise the single defect-only amendment round with a stated defect.
