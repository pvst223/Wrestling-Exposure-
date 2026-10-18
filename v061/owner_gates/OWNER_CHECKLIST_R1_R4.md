# V0.6.1 owner-action checklist R1-R4

Status: preparation only. spec_v4 (manifest SHA-256 `efb2a797c358cdcad73bc933ccc5a80d95979610179240daf6229b4ba86c88af`) is FROZEN and is not modified by this document; nothing here is a new requirement. Every item cites the spec clause it comes from. **Acquisition is NOT authorized until all four gates are complete and the reviewer authorizes it.** Nothing below is recorded as done; I (Claude) will append ledger entries only after you return the evidence.

Where the frozen spec does not give exact wording, the text below is a draft that only restates spec clauses; you may adapt the wording, but do not drop a clause.

Privacy note (a suggestion, not a spec requirement): the ledger is in the GitHub repo. If the repo is or may become public, record a pseudonymous ID and the SHA-256 of your signed statement in the ledger, and keep the signed statement and real names privately.

---
## R1. Designate the single data custodian (spec 02 section 2.6)
Spec text: "exactly one custodian, designated by the project owner and recorded in the ledger before acquisition. The custodian alone may inspect names and metadata, solely for eligibility and duplicate/disjointness checks. Model developers (including Claude) receive no Holdout #2 pixels or data before the opening is recorded."

**You decide/do**
1. Choose exactly one person to be the custodian.
2. Open decision for you or the reviewer: the spec does not say whether the custodian may also be a repo developer or the project owner. To avoid inventing a rule, either ask the reviewer to confirm, or choose someone who is not developing the V0.6.1 model.
3. Have the custodian read the duties (below) and sign the acknowledgement.

**Designation text (you sign)**
> I, [OWNER NAME OR ID], project owner of Wrestling-Exposure, designate [CUSTODIAN NAME OR ID] as the single data custodian for V0.6.1 Holdout #2, effective [DATE]. No other person is a custodian.

**Custodian acknowledgement (custodian signs)**
> I, [CUSTODIAN NAME OR ID], accept designation as the single data custodian for V0.6.1 Holdout #2 on [DATE]. I understand that I alone may inspect Holdout #2 names and metadata, solely for eligibility and duplicate/disjointness checks. I will not give model developers (including Claude) any Holdout #2 pixels or data before the opening is recorded in the ledger.

**Ledger evidence to append after completion** (entry id OG1, kind `V061_R1_CUSTODIAN_DESIGNATED`): custodian ID or pseudonym; designation date; SHA-256 of the signed designation and acknowledgement (files kept privately); statement that the custodian is the only custodian; reviewer confirmation on the developer-overlap question if asked.

---
## R2. Protected `main` (spec 05, row "Protected `main` (reviewer F8)")
Spec text: "Required settings (to be applied by the repository owner in GitHub settings; the Claude GitHub App cannot set them): require a pull request before merging; required status checks = CI (synthetic tests, secret/media/weights scan, 30 MB cap) and the frozen-hash check; no force pushes; no deletion; do not rewrite frozen history (commit `f93a6ea` and everything under `v06/` and `v06/posthoc_v1/`). Tooling-only PRs may be maintainer-merged after review if no scientific path is touched; any PR touching scientific paths (rule, grids, thresholds, training-data selection, comparator, evaluation code, `v061/spec_*`) needs explicit reviewer authorization recorded in the V0.6.1 ledger."

**You do (GitHub web UI, repository owner account; do not tell me they are enabled until you have confirmed them on the settings page)**
1. Open `https://github.com/pvst223/Wrestling-Exposure-` > **Settings** > **Rules** > **Rulesets** > **New ruleset** > **New branch ruleset**.
2. Ruleset name: `protect-main`. Enforcement status: **Active**.
3. Bypass list: leave **empty** (so nobody, including admins, can bypass force-push and deletion rules).
4. Target branches: **Add target** > **Include default branch** (this is `main`).
5. Under Branch rules tick:
   - **Restrict deletions**
   - **Block force pushes**
   - **Require a pull request before merging**
   - **Require status checks to pass** (see the note below on adding the two checks)
6. Click **Create**.
7. (Classic alternative if rulesets are unavailable: Settings > Branches > **Add branch protection rule** for `main`: tick *Require a pull request before merging*, *Require status checks to pass before merging*, and leave *Allow force pushes* and *Allow deletions* unticked; do not grant bypass.)

**Items the GitHub settings cannot enforce by themselves**
- "Do not rewrite frozen history" is satisfied by the force-push block plus not deleting branches/tags; there is no separate GitHub switch.
- "Any PR touching scientific paths needs explicit reviewer authorization recorded in the V0.6.1 ledger" is a process control, not a GitHub setting.
- The number of required PR approvals is not specified in the spec; choose it yourself and note it in the evidence.

**Open sequencing issue (flagged, not resolved by me):** the two required status checks, "CI" and "frozen-hash check", do not exist yet. GitHub only offers a check as "required" after it has run in the repo, and implementing them is V0.6.1 tooling work I have not been authorized to do. Please ask the reviewer whether R2 may be treated as complete with the four settings that can be enabled now (PR required, no force pushes, no deletion, empty bypass) and the two status checks added once the CI is implemented via an authorized tooling PR. Do not report R2 as fully satisfied until the reviewer rules.

**Consequence:** once the PR rule is on, I can no longer push directly to `main`; changes will need a pull request.

**Ledger evidence to append** (OG2, `V061_R2_BRANCH_PROTECTION_CONFIRMED`): date; screenshot or exported ruleset JSON (Settings > Rules > the ruleset > Export) kept privately with its SHA-256; list of enabled rules; whether status checks are enabled now or pending; the number of required approvals; reviewer's ruling on the pending status checks.

---
## R3. Record the footage/data rights stance (spec 02 section 2.7)
Spec text: "Footage remains private; retention of non-target imagery is minimised; no footage, frames or crops are ever committed to GitHub; rights stay UNRESOLVED unless independently established; supplying footage is not permission to publish, redistribute, or build a persistent spectator/staff dataset."

**Two different things; do not mix them**
- *Recording project status* means writing down what is factually true today (for example "rights UNRESOLVED"). This is a record, nothing more.
- *Establishing permission* means actually having a lawful basis to obtain and use specific material (a licence, written permission from the rights holder, or applicable terms/exceptions confirmed independently, for example by counsel). Recording the status does **not** grant permission. If the status is UNRESOLVED, that is not authorization to obtain or use material unlawfully or contrary to applicable licence or platform terms. I am not a lawyer and cannot establish rights for you.

**You decide/do**
1. State the actual position for the planned Holdout #2 and development acquisition (by source). If you do not know, the factual status is UNRESOLVED.
2. If you claim rights are established, identify the basis (rights-holder permission, licence, or other) and keep the supporting document privately.
3. Confirm you will follow the privacy conditions: footage private, non-target retention minimised, nothing on GitHub, no redistribution, no persistent spectator/staff dataset.

**Text to record (choose A or B, whichever is true)**
A. Status only:
> As of [DATE], the rights status of the footage/data planned for V0.6.1 acquisition is UNRESOLVED. I have not independently established permission for any specific source. This record is a status entry, not permission. I will not obtain or use material unlawfully or contrary to applicable licence or platform terms. Footage will remain private, retention of non-target imagery will be minimised, no footage, frames or crops will be committed to GitHub, and supplying footage is not permission to publish, redistribute, or build a persistent spectator/staff dataset.

B. Permission established for named sources:
> As of [DATE], I have established permission for the following sources: [SOURCE LIST], on this basis: [LICENCE / WRITTEN PERMISSION / OTHER, with reference]. For all other sources the status remains UNRESOLVED. This record is a status entry and the supporting documents are held privately. The privacy conditions in spec 02 section 2.7 apply to all material.

**Ledger evidence to append** (OG3, `V061_R3_RIGHTS_STANCE_RECORDED`): date; which option (A or B); source list if B; SHA-256 of the signed statement and of any supporting document (documents kept privately); explicit field `status_is_not_permission: true`.

---
## R4. Independent human annotator and dated independence attestation (spec 02 section 2.6)
Spec text: "The annotator must NOT be the project owner, a repo developer, or the first annotator, and must not be exposed to any model or B0 output or to first-pass labels; a dated independence attestation is recorded in the ledger before annotation starts. The AI second annotator used in V0.6 (deviation X1) is not acceptable here." The annotator is an independent, blinded HUMAN.

**You decide/do**
1. Choose one human annotator who is not you, not a repo developer, and not the first annotator. An AI annotator is not acceptable.
2. Have them read the clauses below and sign and date before they see any Holdout #2 material. (Holdout #2 has not been acquired; nothing for them to see yet.)

**Independence attestation (annotator signs; dated before annotation starts)**
> I, [ANNOTATOR NAME OR ID], attest on [DATE] that:
> 1. I am a human annotator.
> 2. I am not the project owner.
> 3. I am not a developer of the Wrestling-Exposure repository.
> 4. I am not the first annotator of Holdout #2.
> 5. I have not been exposed to, and will not be exposed to before completing my annotation, any model output, any B0 output, or any first-pass label for Holdout #2.
> 6. I will annotate blind, independently, and will not consult the owner, developers, or any other annotator's labels while annotating.
> Signed: [SIGNATURE] Date: [DATE]

**Owner confirmation (you sign)**
> I, [OWNER NAME OR ID], confirm on [DATE] that [ANNOTATOR NAME OR ID] has been designated as the independent human second annotator for V0.6.1 Holdout #2 and that the attestation above was signed before any annotation began.

**Ledger evidence to append** (OG4, `V061_R4_INDEPENDENT_ANNOTATOR_ATTESTED`): annotator ID or pseudonym; attestation date; SHA-256 of the signed attestation and owner confirmation (kept privately); statement that attestation predates any annotation. Not yet in scope: the 20% reserve selection (done later, with the seed derived from the frozen spec hash, before any model output exists).

---
## After you complete R1-R4
Send me, for each gate: the filled-in text or a statement of what you did, the SHA-256 of each private document, and (for R2) your confirmation that each setting is on. I will append OG1-OG4 to the ledger, sync the non-sensitive records to GitHub, and report. Then the reviewer decides whether acquisition may begin. I will not begin acquisition, access Holdout #2, run any analysis, or modify spec_v4 in the meantime.
