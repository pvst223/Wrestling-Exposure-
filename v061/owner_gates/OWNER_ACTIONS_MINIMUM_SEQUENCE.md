# Owner actions to close R1, R2, R3 and the Gemini-procedure owner fields (minimum practical sequence)

Nothing below is done. No Gemini use, acquisition, Holdout #2 access, annotation, training or V0.6.1 run is authorized. Keep signed documents and real identities private; send me pseudonymous IDs, dates and SHA-256 hashes. Hash a file: macOS/Linux `shasum -a 256 FILE`, Windows PowerShell `Get-FileHash FILE -Algorithm SHA256`.

## Step 1 - R2 protections (GitHub, ~10 minutes)
Settings > Rules > Rulesets > New branch ruleset `protect-main`: Active; empty bypass list; target default branch; tick Restrict deletions, Block force pushes, Require a pull request before merging. Do NOT tick required status checks yet. Tell me when on, and the approvals number.

## Step 2 - Tooling PR (R2 checks)
After Step 1, say "go". I push branch `tooling/ci-checks`; you open the PR, review the diff (only .github/workflows/checks.yml and v061/tooling/), merge. Both checks (`CI`, `frozen-hash check`) then run. Send me the run links/IDs.

## Step 3 - Close R2
Edit the ruleset: tick Require status checks to pass, add `CI` and `frozen-hash check`. Export the ruleset JSON, hash it, keep it private. R2 closed only now.

## Step 4 - R1 custodian (you)
Sign the designation and acknowledgement texts in OWNER_CHECKLIST_R1_R4.md section R1 (role strictly limited to Holdout #2 eligibility, metadata, duplicate/disjointness checks, sealing; separate from model development where practical). Send: pseudonymous custodian ID, date, SHA-256 of the signed file.

## Step 5 - R3 rights, per source
Text A (status UNRESOLVED) is the default and is NOT permission. For each planned source, independently establish (licence, written rights-holder permission, or counsel-confirmed terms) whether you may (a) obtain/use it and (b) have it processed by a third-party service (Gemini). Public viewability is not permission. Send: option A or B, date, per-source list with status (UNRESOLVED / ESTABLISHED + basis), SHA-256 of the signed statement and of any supporting documents (kept private). Sources not ESTABLISHED for (b) are never sent to Gemini.

## Step 6 - Gemini owner fields (do in a clean browser profile; do NOT upload any study material while doing this)
a. Choose the account (personal vs Workspace/school; ideally a dedicated account with no other study conversations). Send: account type only, not the address.
b. Capture the Google page https://support.google.com/gemini/answer/13594961 (save as PDF), note date/time, hash it.
c. Set Keep Activity OFF; turn off any personalization / past chats / saved info; disconnect unnecessary Connected Apps. Take a screenshot of each setting, hash them.
d. Write your conclusion on the residual 72-hour retention and possible human safety review (acceptable / not acceptable), dated, hashed. The record cannot call the route zero-retention.
e. Sign the no-prior-exposure statement (template in GEMINI_ANNOTATION_PROCEDURE_PROPOSED.md section 9, with the Gemini UI model name left as "recorded at run time"). Hash and date it. It must be signed before any transmission and must be true. It must disclose the single prep-only interaction (see GEMINI_PREP_INTERACTION_DISCLOSURE.md) and state that no study material has entered any Gemini interface.
f. Send me the hashes; I fill the config, compute the final hashes, and submit the frozen-procedure package for reviewer approval.

## Step 7 - Return to reviewer
I append OG1-OG4 style ledger evidence and the Gemini freeze hashes, re-verify spec_v4/V0.6 hashes, sync non-sensitive records, and STOP for the reviewer's acquisition and Gemini-use authorization.

Dependency order: 1 -> 2 -> 3 (R2). 4, 5, 6 can run in parallel with 1-3. Step 6e must follow 6a-6d. Gemini use additionally needs 5 (per source) and reviewer authorization.
