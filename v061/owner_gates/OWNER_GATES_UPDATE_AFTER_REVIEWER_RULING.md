# Owner gates: updated instructions after the reviewer ruling (ledger OGR1)

spec_v4 (manifest SHA-256 `efb2a797c358cdcad73bc933ccc5a80d95979610179240daf6229b4ba86c88af`) remains frozen and is not modified. This document only applies the reviewer's ruling to `OWNER_CHECKLIST_R1_R4.md` (that file's text and clauses still apply unless changed below). Acquisition is NOT authorized. Nothing here is recorded as done.

## What to do, in order
1. **R2 first (provisional).** In GitHub, create the `protect-main` ruleset exactly as in the checklist, enabling now: Require a pull request before merging, Restrict deletions, Block force pushes, and an EMPTY bypass list. Leave "Require status checks" for step 3. Tell me when each setting is on (and how many PR approvals you chose).
2. **Tooling PR (I prepare; you merge).** After you confirm step 1, I push a branch `tooling/ci-checks` containing only the CI and frozen-hash check tooling (no scientific code, no spec, no frozen V0.6 change). You open a pull request from it (GitHub shows a "Compare & pull request" button), review it, and merge it (tooling-only PRs may be maintainer-merged). After the merge, both checks run.
3. **R2 closure.** When both checks, named exactly `CI` and `frozen-hash check`, have run successfully, edit the `protect-main` ruleset, tick "Require status checks to pass", and add those two checks. R2 is fully closed only then. Export the ruleset (ruleset page > the "..." menu > Export) and keep it privately.
4. **R1 custodian.** You may be the single custodian. The role is strictly limited to Holdout #2 eligibility, metadata, duplicate/disjointness checks and sealing. Prefer separation from model development where practical. Use the designation and acknowledgement texts in the checklist (you sign both).
5. **R3 rights status.** Use text A from the checklist: UNRESOLVED for every source unless permission has independently been established for that source. At each acquisition a per-source status line will be added. The status is not authorization; the privacy conditions apply.
6. **R4 annotator.** Same attestation as the checklist with one clause added to cover the ruling's "exposure" wording:
> 7. I have not been exposed to any Holdout #2 material before signing this attestation.
The attestation must be signed and dated before the annotator sees or annotates anything from Holdout #2.

## Evidence to send me (keep signed documents and real names private)
- OG1: pseudonymous custodian ID, date, SHA-256 of the signed designation and acknowledgement.
- OG2: date; the four settings confirmed; number of required approvals; ruleset export SHA-256; the status of the two checks (links or run IDs of the successful runs).
- OG3: option A or B, date, SHA-256 of the signed statement (and of any supporting document).
- OG4: pseudonymous annotator ID, attestation date, SHA-256 of the signed attestation and owner confirmation, and a statement that it predates any exposure.
How to get a SHA-256: macOS/Linux `shasum -a 256 FILE`; Windows PowerShell `Get-FileHash FILE -Algorithm SHA256`.

I will append OG1-OG4, re-verify that spec_v4 and the frozen V0.6 hashes are unchanged, sync only non-sensitive records to GitHub, and stop for the reviewer's acquisition decision.
