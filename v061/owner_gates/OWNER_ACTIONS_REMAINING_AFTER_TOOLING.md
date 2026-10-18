# Minimal remaining owner actions (after tooling merge)

Done by Claude under the owner's administrative authorization: tooling PR #1 opened and merged (merge commit `b6ecccf4c06752ebdb6baae70cc9bcb965fdf379`); `CI` and `frozen-hash check` both succeeded on the PR run (39161304695) and on `main` (39161452689). The proxy this session runs behind does NOT allow writes to GitHub rulesets/branch protection/Actions settings, so those cannot be done by Claude. Nothing below is recorded as done.

## A. GitHub ruleset (one pass, about 3 minutes; this closes R2)
Settings > Rules > Rulesets > New branch ruleset: name `protect-main`; Enforcement **Active**; Bypass list **empty**; Target **Default branch**; tick **Restrict deletions**, **Block force pushes**, **Require a pull request before merging** (set required approvals to **0**: you are the only maintainer and cannot approve your own PR; record this choice), and **Require status checks to pass**, adding **CI** and **frozen-hash check** (both now selectable because they have run). Create. Then tell me "ruleset on" and I will verify via the read-only API what is visible and record it. Optional: Export the ruleset JSON and keep its SHA-256 privately.
After this, pushes to `main` go through pull requests, which I can create and merge via the API (checks must pass).

## B. R1 custodian - one confirmation from you
Reply with this text, filling the bracket (use a pseudonym, not your real name):
> I, [PSEUDONYM], project owner of Wrestling-Exposure, designate myself as the single data custodian for V0.6.1 Holdout #2, effective [DATE]. My custodian role is strictly limited to Holdout #2 eligibility, metadata, duplicate/disjointness checks and sealing, and I will keep it separate from model development where practical. I alone may inspect Holdout #2 names and metadata, solely for those checks, and I will give model developers (including Claude) no Holdout #2 pixels or data before the opening is recorded in the ledger. No other person is a custodian.
I will store your exact reply privately, record only its SHA-256 and the pseudonym in the ledger (OG1), and say in the record that it is an owner chat declaration unless you also provide a separately signed copy.

## C. R3 rights - one confirmation from you
Reply with option A below, unless you can truthfully state a source is ESTABLISHED (then give source, basis, and keep the document privately):
> As of [DATE], the rights status of every source of footage/data planned for V0.6.1 acquisition is UNRESOLVED, including for (a) obtaining/using it and (b) processing by a third-party service (Gemini). I have not independently established permission for any specific source. This is a status record, not permission. I will not obtain, use or transmit material unlawfully or contrary to applicable licence or platform terms; public viewability is not permission. Footage remains private, non-target imagery retention is minimised, no footage, frames or crops go to GitHub, and supplying footage is not permission to publish, redistribute or build a persistent spectator/staff dataset.
R3 stays OPEN for any source until permission is established per source, and Gemini receives nothing from a source not ESTABLISHED for (b).

## D. Gemini owner fields (only you can truthfully supply; no study material may be uploaded)
1. Account type (personal vs Workspace/school) and whether it is a dedicated account.
2. Save the page https://support.google.com/gemini/answer/13594961 as a PDF, note date/time, send me the SHA-256.
3. Turn Keep Activity OFF; turn off personalization / past chats / saved info; disconnect unnecessary Connected Apps; screenshot each setting; send the SHA-256s.
4. Your dated conclusion on the 72-hour retention and possible human safety review (acceptable / not acceptable) and its SHA-256.
5. The no-prior-exposure statement (template in GEMINI_ANNOTATION_PROCEDURE_PROPOSED.md section 9, disclosing the prep-only chat), dated and SHA-256.
Then I fill the config, compute the final hashes and send the frozen-procedure package to the reviewer.

## Visibility notice
The GitHub repository is PUBLIC (visibility read from the API). Everything committed there, including the ledger and these records, is world-readable. Keep real names, signed documents, screenshots and any footage-derived material out of it; use pseudonymous IDs and hashes only. Consider making the repo private if that is not intended.
