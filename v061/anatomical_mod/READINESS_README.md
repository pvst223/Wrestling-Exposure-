# ANATOMICAL MODIFICATION READINESS CANDIDATE (V1)

**Scope:** machinery and self-test only. No M9C sampling, no images, no verdicts viewed, no performance-driven change. Locked V0.6.1 implementation, the anatomical V1 implementation (manifest f5936ce8…), `ownership_v05`, `integrity_v05`, the record classifier and the merge guard are untouched. R3 PARKED, R4 UNMET, ANNOTATION-PROVISIONAL. No exposure/COM/distance/impact/workload field exists.

## Contents
- `impl/partial_release.py`: Tier A constant, per-landmark recomputation (`landmark_classes`, unchanged V0.5 `metrics` on frozen pose dets + frozen seg cache), `eligible`, `apply_release` (no merge-guard or identity-score parameter), `released_bones`, `mask_unreleased`, `coverage_report`.
- `impl/partial_render.py`: `style="partial"` (dashed, tag) for deliverable video; `style="neutral"` (solid, untagged, released landmarks only) for the blind review composite.
- `tests/test_partial_release.py`: 13 tests covering the 12 required properties (+ pipeline integration). Existing suites: anatomical 41/41, plan 12/12, all pass.
- `parity_check.py` -> `PARITY_RESULT_V1.json`: recomputation parity and determinism on the frozen caches.
- `feasibility_m9c.py` -> `M9C_FEASIBILITY_COUNTS_V1.json`: counts only.
- `M9C_EXECUTION_SEQUENCE.md` (proposed, not executed), `MANIFEST.txt` (code hashes).

## Test map (required property -> test)
1 deterministic recomputation `test_01`; 2 exact Tier-A eligibility `test_02`; 3 any non-Tier-A reason vetoes (14 non-Tier-A reasons × all Tier-A subsets) `test_03`; 4 MIXED/other states always veto `test_04`; 5 only OWN_ONLY emitted, others None (never zero-filled) `test_05`; 6 bones need both endpoints, isolated points stay withheld `test_06`; 7 PARTIAL never ASSIGNED (`landmarks_emitted=False`, `assigned_label=None`, class outside locked vocabulary) `test_07`; 8 no carry from/across PARTIAL `test_08`; 9 merge guard no effect (signature, source, toggle) `test_09`; 10 identity and numeric-failure handling unchanged `test_10`; 11 existing behaviour unchanged outside the new class (grid of identity × mask × competing-mask pipeline runs, plus locked truth table) `test_11`/`test_11b`; 12 no exposure fields (AST name/key scan + report schema) `test_12`.

## Recomputation-parity evidence (frozen caches, 4 dev clips, run twice)
- 7984 measured detections with masks recomputed with the unchanged V0.5 module: **7984/7984** ownership summaries (owner, cover, own_only/contested/other_only/unexplained fractions), `S` and `n_landmarks` identical to the frozen V1 rows (exact float equality).
- 7326 rows whose frozen state/reasons derive from `decide()` alone: **7326/7326** identical state and reason list (0 mismatches).
- 723 rows have no own-summary (cross-body MIXED before masks, or no masks): never eligible, unchanged.
- Second full run identical; hash of all recomputed per-landmark classes `942c0520112b…` (full value in `PARITY_RESULT_V1.json`).
- **Zero unexpected changes**: applying the release rule over all frozen rows changed only eligible rows, and each released frame's landmark set equals exactly its OWN_ONLY set.
- Structural ceiling (counts, not performance): 223 rows have all reasons in Tier A; **179 are released** (A 97 / B 82; per clip in the JSON) and 44 stay withheld because they have no bone with both endpoints OWN_ONLY. 179 = 8.2 percentage points of the 2179 identity-ACCEPT measured frames (gate: ≥5.0).

## M9C feasibility conflict (needs reviewer ruling; nothing was changed)
Counting only: of the 179 released frames, **57 unique frames (58 rows) remain** after excluding the 120 reviewed frames and every frame within ±30 source frames of them; at ≥30-frame spacing at most **35** can be chosen. Per clip after exclusion: b1_orton 2 (1 at gap 30), b2_batch2 26 (14), vp2 14 (8), vp5 15 (12). The approved KEEP criterion needs ≥50 **judgeable** frames, and per-clip stratification is impossible for b1_orton. Alternatives (unique frames / chosen at gap 30 / gap 15):
| exclusion radius | unique frames | greedy ≥30 apart | ≥15 apart |
|---|---|---|---|
| ±30 (approved) | 57 | 35 | 41 |
| ±15 | 89 | 51 | 60 |
| burned frames only (±0) | 160 | 80 | 100 |
Options for the reviewer: (a) keep ±30 and accept that ≥50 judgeable is unreachable (M9C would be descriptive and cannot KEEP); (b) shrink the exclusion radius (±15 gives 51–60 at 30/15-frame spacing; still may fall short after NOT_JUDGEABLE); (c) relax the within-clip spacing as in M9B (30→15→0) with ±30 kept: ≤57 frames, ≥50 judgeable would still need ≤7 NOT_JUDGEABLE; (d) take every eligible frame (census) rather than a sample. I recommend (b) with ±15 and the M9B spacing relaxation ladder, but this changes a reviewer-approved parameter, so it is left to the reviewer.

## Known limits
Parity is verified on the same frozen caches that produced the V1 rows (deterministic recomputation, not independent re-extraction). Synthetic tests cover logic, not real-scene behaviour. Release counts say nothing about correctness; no verdicts have been viewed for any released frame.
