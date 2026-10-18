# 03 V0.6.1 evaluation preregistration (DRAFT; becomes binding only when frozen in the ledger before any new-data result exists)

Unit: (clip, shot, identity/class) as in V0.6. Repeated seed resamples never create units. Unit-level false-target-acceptance (FTA) with exact Clopper-Pearson 95% CIs; coverage = unweighted mean over target units of the per-unit accepted-as-own fraction (bootstrap CI over units, seeded, explicitly not exact). Strata with fewer than 15 units are descriptive only.

## 1. Estimand
Does the two-stage learned component, trained on the diversified development set, improve the unit-level FTA versus coverage trade-off relative to the non-learned B0 baseline, on never-opened Holdout #2, without compromising the independent anatomical-ownership / fail-closed architecture? The outcome says only whether the evidence justifies further development.

## 2. Primary analysis (one shot, Holdout #2)
- Operating points are fixed from development data only (section 3) and the head is trained on development data only.
- Primary endpoint: paired exact one-sided sign test on Holdout #2 negative units, b = units false-accepted only by B0, c = only by V0.6.1. Same definition as V0.6.
- Primary coverage criterion: V0.6.1 coverage >= B0 coverage - 0.10.
- Backbone: MobileCLIP-B (frozen, not re-selected). Re-selecting the backbone would use old-TEST-exposed knowledge; any other backbone is outside V0.6.1.

## 3. Operating-point selection (development data only; same procedure for both methods)
1. Candidate scores come from the leave-one-component-out cross-fitted predictions on development episodes (02 section 2.3); B0 needs no training and is scored directly.
2. Matched coverage c*: the largest of {0.5, 0.4, 0.3, 0.2, 0.1} that BOTH methods reach on the pooled out-of-fold development data AND reach in every evaluable development fold (transfer requirement; the transfer requirement is new and exists because single-fold DEV selection failed to transfer in V0.6).
3. Per method, among grid points with pooled dev coverage >= c* and per-fold coverage >= c*, choose the lowest pooled dev unit-FTA; ties: highest coverage; then lexicographically smallest parameters (L1 order: tau_g, then delta).
4. If no point satisfies the constraints for either method: INCONCLUSIVE-DATA.
5. Final head: retrained on all development training episodes with the frozen recipe; thresholds from step 3 are applied unchanged. No re-selection after Holdout #2 is opened.

## 4. Pre-registered secondary / descriptive metrics (cannot change the outcome)
- Gate: AUROC of g = pA + pB for target vs non-target candidates, unit-clustered bootstrap CI (2000 resamples).
- Assignment: AUROC of q for A-vs-B among target candidates, unit-clustered bootstrap CI; wrong-wrestler (swap) accept rate among accepted target candidates; swap units.
- Decision decomposition: shares of ACCEPT / REJECT_NONTARGET / ABSTAIN_AMBIGUOUS per stratum.
- Calibration transfer: dev-vs-holdout shift in distribution of g and of |q - 0.5| (descriptive; no recalibration allowed).
- Unit-level risk-coverage curves for both methods (exploratory).
- Per-clip and per-identity-component breakdown, with n shown; seeds 1-3 variance of the head (as in V0.6).
- All metrics are on the same unit tables; nothing is re-weighted.

## 5. Falsification criteria (each stated before any new-data result)
- F-PRIMARY (rule+training package): falsified if b <= c, or the one-sided exact p > 0.10, at the DEV-selected points.
- F-GATE: the gate component is falsified if the Holdout #2 gate-AUROC 95% lower bound < 0.70.
- F-ASSIGN: the assignment component is falsified if the A-vs-B AUROC 95% interval includes 0.5. If only F-ASSIGN fails, the finding recorded is "the learned head supplies a target gate but no identity assignment"; assignment would fall back to B0-style prototype scoring only in a later, separately authorised version.
- F-COVERAGE: falsified if coverage < B0 coverage - 0.10.
- F-TRANSFER: the dev-selected operating point is declared non-transferring if the Holdout #2 coverage at the frozen point is less than half of the pooled development out-of-fold coverage at that point. Recorded as a finding; it feeds the outcome as MODIFY, not KEEP.
- Thresholds in F-GATE (0.70), F-ASSIGN (0.5), F-TRANSFER (one half) and the 0.10 margins are set a priori and not derived from Holdout #2.

## 6. Descriptive ablations (run only after the primary result is frozen; Holdout #2 once)
A: old rule (3-class floor) + new training; B: new rule + old single-episode head. Not part of the decision. Reported to separate rule effect from data effect, with the explicit caveat that they re-use Holdout #2 only after the primary was frozen and cannot change it.

## 7. Outcome logic (mirrors V0.6 section 6 with the D6 amendment)
Precedence: INCONCLUSIVE-DATA > KEEP > KILL > MODIFY; annotation gate NOT satisfied caps KEEP at MODIFY-equivalent (reported "ANNOTATION-PROVISIONAL"), KILL stays KILL.
- KEEP (all): (1) b + c >= 4, b > c, one-sided exact p <= 0.10; (2) V0.6.1 coverage >= B0 coverage - 0.10; (3) no negative stratum with >= 15 units where V0.6.1 has >= 3 more false-accept units than B0; (4) F-GATE and F-ASSIGN and F-TRANSFER not triggered; (5) annotation gate satisfied (else reported with the ANNOTATION-PROVISIONAL label and no stronger than MODIFY for advancement).
- KILL (all): b <= c; B0 had at least 5 false-accept units on Holdout #2; annotation gate satisfied.
- INCONCLUSIVE-DATA: B0 has fewer than 5 false-accept units; fewer than 15 post-seed target units; missing dependency, labels or annotation; no feasible operating point in step 3.4.
- MODIFY: everything else, including a component-level failure (F-GATE/F-ASSIGN/F-TRANSFER), mixed strata, or results explained by disclosed data limits.
Interpretation guard: KEEP justifies further development only. KILL means this formulation did not outperform B0 on this holdout. Neither is validation.

## 8. Annotation gate for V0.6.1
Holdout #2 labels: blinded annotation with an independent HUMAN second annotator on a pre-specified reserve (open decision O3); kappa >= 0.60 is a reliability gate only, not label validation; below it the outcome is ANNOTATION-PROVISIONAL. Labels and agreement are committed by hash before any V0.6.1 score for Holdout #2 exists.
