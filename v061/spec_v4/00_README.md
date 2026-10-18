# V0.6.1 prospective design package, REVISION 4 (CORRECTED FINAL FREEZE CANDIDATE; NOT IMPLEMENTED)

Status: planning only. Nothing here has been implemented, trained, tuned, run or evaluated. No Holdout #2 material was acquired, opened or inspected. Frozen V0.6 (`v06/`) and POSTHOC_DIAGNOSTIC_V1 are unchanged and permanently frozen. V0.6.1 work lives only under `v061/`. Study status stays ANNOTATION-PROVISIONAL. No claim of validation, accuracy, generalisation, clinical utility, workload, fatigue or injury prediction is made; scores are heuristic evidence, not probabilities.

Revision 4 = revision 3 plus the reviewer-authorised single defect-only seed-provenance correction (ledger PL8/EXR2), the carried-forward development observation (file 10) and provenance notes. No design element changed. Revision 3 incorporates the reviewer ruling "FINAL FREEZE REVIEW: APPROVED AFTER SPECIFIC EDITS" (ledger PL5), on top of revision 2 (PL3). `spec_v1/` and `spec_v2/` are kept unchanged as superseded drafts. See `08_AMENDMENT_LOG.md` for how each amendment was applied.

Reviewer ruling the first draft built on: preregistered label D2 retained; reviewer scientific interpretation D3 (mixed): both DEV-to-TEST operating-point/calibration transfer and A-vs-B identity discrimination degraded.

| File | Content |
|---|---|
| `01_SPEC_decision_rule.md` | Two-stage decision rule, what is frozen, what changes |
| `02_DATA_PLAN.md` | Training-diversity plan, data eligibility, Holdout #2 preservation |
| `03_EVALUATION_PREREGISTRATION_DRAFT.md` | Metrics, operating-point selection, falsification criteria, KEEP/MODIFY/KILL/INCONCLUSIVE |
| `04_VIDEO_RENDERER_PLAN.md` | Annotated-video renderer, separate from inference |
| `05_TOOLING_PLAN.md` | Tooling and reproducibility fixes (V0.6.1+ only) |
| `06_LEAKAGE_REGISTER.md` | Leakage risks from old TEST and toward Holdout #2, with controls |
| `07_OPEN_DECISIONS.md` | Items remaining for final freeze review |
| `08_AMENDMENT_LOG.md` | Reviewer amendment to change mapping |
| `09_EXPLORATORY_RUN_SPEC.md` | The single authorised decision-rule-only development/hypothesis check (design text unchanged; provenance section added) |
| `10_PRE_FREEZE_DEVELOPMENT_OBSERVATION.md` | Descriptive, non-confirmatory development observation carried into the freeze documentation |
| `MANIFEST_SHA256.txt` | Hashes of the files above |

Approval sequence (nothing proceeds without each explicit reviewer authorization): (1) this pre-exploratory revision is recorded (ledger PL6); (2) the single exploratory check (09) is executed exactly once (authorised by PL5); (3) reviewer rules on the freeze candidate; (4) data acquisition and implementation only after the final specification freeze; the freeze is recorded in the ledger and starts the development-lock (01 section 7); (5) one-shot Holdout #2 evaluation.
