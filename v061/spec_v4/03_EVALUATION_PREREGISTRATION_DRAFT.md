# 03 V0.6.1 evaluation preregistration (REVISION 3; becomes binding only when frozen in the ledger before any new-data result exists)

Unit: (clip, shot, identity/class) as in V0.6. Repeated seed resamples never create units. Unit-level false-target-acceptance (FTA) with exact Clopper-Pearson 95% CIs; coverage = unweighted mean over target units of the per-unit accepted-as-own fraction (bootstrap CI over units, seeded, explicitly not exact). Strata with fewer than 15 units are descriptive only.

## 1. Estimand
Does the two-stage learned component, trained on the diversified development set, improve the unit-level FTA versus coverage trade-off relative to the non-learned B0 baseline (original frozen Phase-1 grid), on never-opened Holdout #2, without compromising the independent anatomical-ownership / fail-closed architecture? The outcome says only whether the evidence justifies further development.

## 2. Primary analysis (one shot, Holdout #2)
- Operating points are fixed from development data only (section 3) and the head is trained on development data only.
- Primary endpoint: paired exact one-sided sign test on Holdout #2 negative units, b = units false-accepted only by B0, c = only by V0.6.1. Same definition as V0.6.
- Primary coverage criterion (retained): V0.6.1 coverage >= B0 coverage - 0.10.
- Backbone: MobileCLIP-B (frozen, not re-selected).
- B0: original frozen Phase-1 grid (tau in {0.30,...,0.70} x margin in {0,0.02,0.05,0.10}), selected by the same procedure as L1 (section 3). The comparator is not extended.

## 3. Operating-point selection (development data only; same procedure for both methods)
1. Candidate scores come from leave-one-component-out cross-fitted predictions on development episodes (02 section 2.3); B0 needs no training and is scored directly.
2. Matched coverage c*: the largest of {0.5, 0.4, 0.3, 0.2, 0.1} that BOTH methods reach on the pooled out-of-fold development data AND in every evaluable development fold.
3. Per method, among grid points with pooled dev coverage >= c* and per-fold coverage >= c*, choose the lowest pooled dev unit-FTA; ties: highest coverage; then lexicographically smallest parameters (L1 order: tau_g, then delta).
4. If no point satisfies the constraints for either method: INCONCLUSIVE-DATA.
5. Final head: retrained on all development training episodes with the frozen recipe; thresholds from step 3 applied unchanged. No re-selection after Holdout #2 is opened.
The per-fold requirement in step 2 is a selection constraint, not an outcome criterion. Both grids have 20 points.

## 4. Pre-registered secondary / descriptive metrics (cannot change the primary outcome)
- Gate: AUROC of g = pA + pB for target vs non-target candidates, unit-clustered bootstrap CI (2000 resamples).
- Assignment: AUROC of q for A-vs-B among target candidates, unit-clustered bootstrap CI; wrong-wrestler (swap) accept rate among accepted target candidates; swap units.
- Decision decomposition: shares of ACCEPT / REJECT_NONTARGET / ABSTAIN_AMBIGUOUS per stratum.
- Calibration transfer: dev-vs-holdout shift in the distributions of g and |q - 0.5| (descriptive; no recalibration).
- Unit-level risk-coverage curves for both methods (exploratory); per-clip and per-identity-component breakdowns with n; seeds 1-3 head variance.
- Same unit tables throughout; no re-weighting.

## 5. Falsification criteria and diagnostic flags (all fixed before any new-data result)
Component falsification criterion (may change the outcome):
- **F-ASSIGN**: the A-vs-B assignment component is falsified if the Holdout #2 A-vs-B AUROC 95% interval (unit-clustered bootstrap) includes 0.5. Effect: outcome is MODIFY / component failure (section 7). No automatic substitution of B0 assignment within V0.6.1; any hybrid fallback needs a separately authorised future version.

Primary criteria (as in V0.6): the sign-test criterion and the coverage criterion (>= B0 coverage - 0.10) are KEEP/KILL inputs (section 7).

Preregistered diagnostic / transfer flags (reported, NOT hard KEEP requirements):
- **D-GATE**: flagged if the Holdout #2 gate-AUROC 95% lower bound < 0.70.
- **D-TRANSFER**: flagged if Holdout #2 coverage at the frozen operating point is less than half of the pooled development out-of-fold coverage at that point.
D-GATE and D-TRANSFER remain diagnostic flags only (reviewer F6). A flag is recorded and discussed; by itself it does not block KEEP unless a stronger independent justification is supplied and accepted by the reviewer before the freeze (the reviewer may promote a flag to a criterion only prospectively). Cut-offs are set a priori and not derived from Holdout #2.

## 6. Descriptive ablations (run only after the primary result is frozen; Holdout #2 once)
A: old rule (3-class floor) + new training; B: new rule + old single-episode head. Not part of the decision; reported to separate rule effect from data effect, with the caveat that they re-use Holdout #2 only after the primary was frozen and cannot change it.

## 7. Outcome logic (mirrors V0.6 section 6 with the D6 amendment)
Precedence: INCONCLUSIVE-DATA > KEEP > KILL > MODIFY. Annotation gate NOT satisfied caps KEEP at "ANNOTATION-PROVISIONAL" (no stronger than MODIFY for advancement); KILL stays KILL.
- KEEP (all): (1) b + c >= 4, b > c, one-sided exact p <= 0.10; (2) V0.6.1 coverage >= B0 coverage - 0.10; (3) no negative stratum with >= 15 units where V0.6.1 has >= 3 more false-accept units than B0; (4) F-ASSIGN not triggered; (5) annotation gate satisfied (human second annotator, kappa >= 0.60; else reported ANNOTATION-PROVISIONAL).
- KILL (all): b <= c; B0 had at least 5 false-accept units on Holdout #2; annotation gate satisfied.
- INCONCLUSIVE-DATA: B0 has fewer than 5 false-accept units; fewer than 15 post-seed target units; missing dependency, labels or annotation; no feasible operating point (section 3 step 4).
- MODIFY: everything else, including: criteria 1-3 met but F-ASSIGN triggered (reported "MODIFY / component failure: gate-only"); mixed strata; results explained by disclosed data limits; a KEEP that is annotation-provisional.
Interpretation guard: KEEP justifies further development only. KILL means this formulation did not outperform B0 on this holdout. Neither is validation. D-GATE and D-TRANSFER flags are reported next to the outcome.

## 8. Annotation gate for V0.6.1
Independent blinded HUMAN second annotator on a prospectively selected 20% reserve of Holdout #2 tracklets (seed from the frozen spec hash) representing every clip and major truth class where feasible, with a dated independence attestation (02 section 2.6). kappa >= 0.60 is a reliability gate only, not evidence that labels are validated. Agreement statistics (raw agreement, kappa including and excluding UNLABELABLE) are always reported. Labels and agreement are committed by hash before any V0.6.1 score for Holdout #2 exists.
