# V0.6.1 development: implementation / readiness package (for reviewer inspection)

Status: **IMPLEMENTED (decision-rule, selection, diagnostics, renderer logic) → SELF-TESTED (24 synthetic tests) → AUDIT REQUESTED.** Not validation. R1 CLOSED; R2 CLOSED; **R3 PARKED, UNRESOLVED / THIRD-PARTY TRANSMISSION BLOCKED**; R4 UNMET by declared AI substitution; V0.6.1 ANNOTATION-PROVISIONAL.

## 1. Old-TEST hypothesis check: ALREADY EXECUTED, NOT RERUN
The one-time old-DEV → old-TEST decision-rule-only check (label `V0.6.1 DEVELOPMENT / HYPOTHESIS CHECK ONLY`) was executed before spec_v4: ledger EXR1 (result sha b83e8a40…, bootstrap seed provenance defect) and, under the single defect-only amendment PL8, EXR2 (seed-corrected, result sha 5d5fc476…, script 0c0687d0…). Spec 09 states "No further exploratory run is authorised." Nothing was rerun; the results are preserved unchanged in `v061/exploratory_v1/`. No old-TEST number was generated or inspected in this step.

## 2. What was implemented (new paths only; no frozen file touched)
| Component | File |
|---|---|
| Two-stage rule, grids (L1 20 pts, original B0 20 pts), fail-closed | v061/impl/decision_rule.py |
| Deterministic operating-point selection (c*, tie-breaks, fold constraint) | v061/impl/selection.py |
| Unit tables, exact Clopper-Pearson, paired sign test, AUROC | v061/impl/units.py |
| Grid evaluation + development diagnostics (gate, A/B assignment, abstention vs reject, coverage, false-target acceptance) | v061/impl/evaluate.py |
| Renderer frame-status logic (EVALUATED / CARRIED-FORWARD ≤3 / NO-EVAL), source-rate renderer, sidecar | v061/impl/render/ |
| Env-var paths, no absolute paths | v061/impl/config.py |
| Pinned env, environment record, implementation hash manifest | v061/requirements.lock, ENVIRONMENT.md, v061/tooling/impl_manifest.py |
| Implementation clarifications C1–C8 | v061/impl/IMPLEMENTATION_CLARIFICATIONS.md |

Not implemented here (and not authorized to run): training on the diversified TRAIN set, leave-one-component-out cross-fitting, B0 scoring wrappers over real features, and any execution on real data. These remain under the unchanged frozen recipe and spec 02/03.

## 3. Conformance to spec_v4 (verified by synthetic tests, `v061/tests`)
| Spec clause | Test |
|---|---|
| g = pA+pB gate, reject if g < tau_g | test_basic, test_gate_boundary_inclusive |
| q = pA/(pA+pB); A if q ≥ 0.5+δ, B if q ≤ 0.5−δ, else ABSTAIN; ties always abstain for δ ≥ 0.05 | test_delta_boundary, test_tie_always_abstains… |
| Four outputs; REJECT vs ABSTAIN separate | test_abstain_vs_reject_separated |
| Fail-closed on NaN/inf/degenerate/malformed | test_fail_closed |
| Grids fixed (L1 5×4; B0 original 5×4) | test_grids_fixed |
| Monotonicity sanity (higher tau_g / δ never accepts more) | test_monotone_in_tau_and_delta |
| Identical decisions to the exploratory implementation at all 20 L1 points on 4000 random valid outputs | test_parity_with_exploratory_check |
| Selection: lowest FTA → highest coverage → lexicographic; c* joint; infeasible → none | test_select_ties, test_fold_constraint, test_joint_cstar_none |
| Unit/metric definitions identical to frozen V0.6 code | test_units_parity_v06 (runs when torch available), test_cp_and_paired |
| Deterministic bootstrap; no outcome class emitted | test_end_to_end_synthetic_deterministic |
| Renderer: ≤3 carried frames, held (never interpolated) boxes, EVALUATED count = unique decision frames, input hash changes when decisions change, sidecar reconstructs frame status | test_renderer.py |
| No absolute paths in new code | test_hygiene_paths |

## 4. Operating-point selection logic (unchanged from spec_v4 03 §3; 09 for single DEV episode)
Candidate grid points are evaluated on development data only. c* = largest of {0.5,0.4,0.3,0.2,0.1} reached by at least one point of every method (and, with folds, in every fold). Per method: among points with coverage ≥ c*, lowest unit FTA; ties highest coverage; ties lexicographically smallest (tau_g, δ) [B0: (tau, margin)]. No feasible c* → INCONCLUSIVE-DATA / "no feasible operating point". Same procedure for both methods; both grids have 20 points.

## 5. Hashes
- Implementation manifest (`v061/impl/IMPLEMENTATION_MANIFEST.txt`, 19 files incl. tests, requirements.lock, ENVIRONMENT.md): SHA-256 `5d517493b218912dc7b5afc7cc9ede8046d355efabc689e61cef1971f4d300b9`; per-file hashes inside it; checked in CI.
- spec_v4 manifest (unchanged): `efb2a797c358cdcad73bc933ccc5a80d95979610179240daf6229b4ba86c88af`.
- Expected output schema (synthetic key/type listing): `v061/readiness/EXPECTED_OUTPUT_SCHEMA.json`.

## 6. Data-boundary confirmation
No fresh Holdout #2 information was accessed, acquired, constructed or inferred; no candidate footage inspected; no study imagery sent to Gemini; no real features, weights, TRAIN/DEV/TEST tables were loaded by any new code or test (all fixtures synthetic). No development performance was generated or inspected in this step. Footage selection has not been influenced by V0.6.1 behavior. Old V0.6 TEST remains burned.

## 7. Items for reviewer attention
1. C2 (stricter fail-closed validity check) is the only clarification that goes beyond the spec text; it is inert on valid softmax outputs. Rule parity with the exploratory code is tested.
2. Previously inspected exploratory results exist (EXR1/EXR2), including the L1 point selected there; these motivated nothing in this implementation, and the grids/rules are unchanged.
3. Before any new development performance is generated: reviewer audit of this package, then the implementation hash above is the development lock reference.
