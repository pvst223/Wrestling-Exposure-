# FRESH-FOOTAGE ACQUISITION MANIFEST — INSTRUCTIONS (V1; template only, nothing acquired)
Authorized by reviewer R6 for preparation under the frozen D1-A constraints. **No evaluation, sampling or review begins from this.** The filled manifest, the footage, names and any real identities stay **private** (never committed). The ledger records only the manifest's sha256, clip count and aggregate counts.

## Targets (reviewer R1/R2)
- About **18 new clips** of similar duration to the development clips (30–120 s each; frozen ingest guidance 45–150 s), or equivalent total footage (~45,000 source frames ≈ 25 minutes at 30 fps); **≥ 14 clips is an approximate feasibility floor, not a scientific criterion**. If the fresh feasibility count (P9) shows adequate yield with fewer, stop acquiring; if ~18 are insufficient, no criterion is relaxed.
- Set-level diversity (D1-A): ≥ 3 distinct sources/eras/resolutions, ≥ 2 promotions, new events only.
- The frozen minimum-data and sampling criteria are unchanged (≥ 100 judgeable, ≥ 20 shots, ≥ 3 clips; spacing ≥ 30 source frames; ≤ 10 per shot).

## Per-clip requirements (what the frozen identity code needs; see R3 proposal section 2)
1. Exactly two named wrestlers (A, B), names supplied by the owner (`names_basis` = owner-supplied; Claude never identifies anyone from appearance); other unnamed wrestlers are allowed.
2. Each named wrestler appears with a single, clearly visible body (no tangled shots) in enough separate shots for 4 seeds from ≥ 2 shots, ≥ 60 frames apart (planning target: visible in ≥ 4 shots).
3. A referee is visible at least once.
4. Named wrestlers not in the development list (see the R3 proposal), never Jeff Hardy, never Cena; not any Holdout #2 identity (**not checked by Claude**; the Holdout #2 custodian checks names only and returns pass/fail).
5. Event/broadcast/source file/upload not shared with any development clip or other clip in this set; no replay duplicates (checked by the frozen dHash audit; limits stated).
6. Record fade/black/end-card frames to exclude **before** any model run (`static_bars_or_end_card_frames_to_exclude`); persistent overlays described.
7. `rights_status` stays UNRESOLVED; no redistribution; no clips, frames or crops in GitHub.
8. `ref_timestamp_A_s` / `ref_timestamp_B_s`: a time in the clip where the owner identifies each named wrestler clearly (used only for first-pass labelling bookkeeping, not appearance re-ID by the pipeline).
9. `source_or_upload_id`: any stable identifier that lets disjointness be checked (e.g. an upload id or file hash).
Do **not** pick or drop clips because of how they might perform; choose by the criteria above only.

## Set summary (to be filled in a separate sheet, private)
Total clips; total duration and frames; counts by promotion, source/era, native resolution; clips failing any requirement (excluded before processing); duplicate/disjointness audit results (counts, pass/fail).

## Hand-off
Return the filled CSV; its sha256 is ledgered BEFORE any clip is processed. The checklist columns are owner assertions; the pipeline's own seed feasibility (INSUFFICIENT_SEEDS) and the audits can still exclude clips by the pre-specified rules.
