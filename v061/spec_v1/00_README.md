# V0.6.1 prospective design package (DRAFT FOR REVIEWER APPROVAL; NOT IMPLEMENTED)

Status: planning only. Nothing here has been implemented, trained, tuned, run or evaluated. No Holdout #2 material was acquired, opened or inspected. Frozen V0.6 (`v06/`) and POSTHOC_DIAGNOSTIC_V1 are unchanged and permanently frozen. V0.6.1 work lives only under `v061/`. Study status stays ANNOTATION-PROVISIONAL. No claim of validation, accuracy, generalisation, clinical utility, workload, fatigue or injury prediction is made; scores are heuristic evidence, not probabilities.

Reviewer ruling this builds on: preregistered label D2 retained; reviewer scientific interpretation D3 (mixed): both DEV-to-TEST operating-point/calibration transfer and A-vs-B identity discrimination degraded.

| File | Content |
|---|---|
| `01_SPEC_decision_rule.md` | Two-stage decision rule, what is frozen, what changes |
| `02_DATA_PLAN.md` | Training-diversity plan, data eligibility, Holdout #2 preservation |
| `03_EVALUATION_PREREGISTRATION_DRAFT.md` | Metrics, operating-point selection, falsification criteria, KEEP/MODIFY/KILL/INCONCLUSIVE |
| `04_VIDEO_RENDERER_PLAN.md` | Annotated-video renderer, separate from inference |
| `05_TOOLING_PLAN.md` | Tooling and reproducibility fixes (V0.6.1+ only) |
| `06_LEAKAGE_REGISTER.md` | Leakage risks from old TEST and toward Holdout #2, with controls |
| `07_OPEN_DECISIONS.md` | Decisions only the reviewer can make |
| `MANIFEST_SHA256.txt` | Hashes of the files above |

Approval sequence (nothing proceeds without each explicit reviewer authorization): (1) approve or amend this package; (2) authorize data acquisition (rights and privacy first); (3) authorize implementation; (4) V0.6.1 freeze (code, grids, seeds, dev selection procedure) recorded in the ledger; (5) one-shot Holdout #2 evaluation.
