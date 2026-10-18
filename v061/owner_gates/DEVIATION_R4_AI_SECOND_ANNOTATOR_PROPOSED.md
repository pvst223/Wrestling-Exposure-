# V0.6.1 prospective protocol deviation: AI second annotator in place of the required human (PROPOSED, linked to frozen spec_v4)

Status: PROPOSED deviation record (reviewer-directed, 2026-10-18). spec_v4 (manifest `efb2a797c358cdcad73bc933ccc5a80d95979610179240daf6229b4ba86c88af`) is NOT modified and is not retroactively changed. This record sits beside it and does not hide the unmet requirement.

## Deviation
- Spec requirement (02 section 2.6, reviewer R4): independent, blinded HUMAN second annotator with a dated independence attestation.
- Owner statement: obtaining a suitable human annotator is not practically feasible.
- Deviation: Gemini will be used as a blinded independent AI second annotator.

## Binding limits (reviewer)
1. **R4 remains formally UNMET.** The substitution is not represented as satisfying R4 and is not human inter-rater reliability. No human independence attestation will be claimed for Gemini.
2. **V0.6.1 results remain ANNOTATION-PROVISIONAL** with respect to the human-reliability requirement (outcome cap as in V0.6).
3. **Blinding before annotation:** Gemini receives no model/B0 outputs, first-pass labels, results, outcome information, or Holdout #2 answer key / identity mapping beyond the minimum frozen reference material needed for the annotation task.
4. **No exposure yet:** Gemini must not see any Holdout #2 material before this deviation and the blinding procedure are frozen. Nothing has been sent to Gemini.
5. **Reporting:** agreement with Gemini is reported only as AI-vs-AI / AI-vs-first-pass reproducibility or sensitivity analysis, including the preregistered agreement statistics. Never as human reliability or annotation validation.
6. Spec_v4 is not edited. This is a deviation record linked to it.

## Still to be frozen before any Gemini exposure (not yet done)
- Exact model name/version, access route, settings, and the annotation prompt, hashed.
- The minimum frozen reference material shown to Gemini, hashed; confirmation that it contains no answer key or identity mapping.
- Per-unit presentation (same frames, order, and prompt for every unit); how output is parsed; failure/abstention handling.
- Privacy check of the provider's terms and retention for third-party processing of footage (footage private, non-target retention minimised, rights status R3 UNRESOLVED); frames sent are limited to what the task needs.
- Owner's dated accurate statement describing the AI annotator and that it had no prior exposure.
- Reviewer's acceptance of the frozen procedure.

## Revised gate status (nothing complete)
| Gate | Status |
|---|---|
| R1 custodian (owner, limited role) | OPEN: designation/acknowledgement hash not yet received |
| R2 branch protection | OPEN: owner settings not yet confirmed; tooling PR approved by reviewer; `CI` and `frozen-hash check` not yet run or required |
| R3 rights stance | OPEN: UNRESOLVED per source; statement hash not yet received; status is not authorization |
| R4 independent human annotator | UNMET by design: AI substitution deviation proposed; remains UNMET; results ANNOTATION-PROVISIONAL |
| Deviation blinding procedure | NOT YET FROZEN |
| Acquisition / Holdout #2 / Gemini exposure / annotation / training | NOT AUTHORIZED |
