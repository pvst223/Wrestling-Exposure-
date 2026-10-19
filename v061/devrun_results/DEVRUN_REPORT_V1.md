# V0.6.1 development cross-fit — development package (for reviewer audit)
Label: **V0.6.1 DEVELOPMENT ONLY (cross-fitted, development-exposed data; exploratory; NOT validation).** No outcome class assigned. R3 PARKED / UNRESOLVED / THIRD-PARTY TRANSMISSION BLOCKED; R4 UNMET (declared AI substitution); V0.6.1 ANNOTATION-PROVISIONAL.

## 1. Operation performed (once; ledger DR0 → DR1)
spec_v4 02 §2.3 + 03 §3 on the six existing development-pool clips, MobileCLIP-B only: 5 leave-one-component-out folds; frozen L1 recipe (Adam, lr 0.01, 30 epochs, seed 0) with K = 5 deterministic seed resamples per clip pair (strict seed rule first; relaxed fallback: HBK/Benjamin m = 3, Rock/HHH m = 2); three folds contain a strictly evaluable episode (4 episodes, 200 units, 100 target units; 7,022 scored candidate detections); locked two-stage rule on the 20-point L1 grid; B0 (original 20-point grid) scored directly on the same episodes; deterministic selection at joint c* = 0.5. Not run: seeds 1–3, the all-development final head, ablations A/B.

## 2. Hashes
- Locked implementation manifest verified unchanged (preflight + `impl_manifest.py`): `eb99beb359ee28dca883d7976ede4385f8dafb2e739d729f89a3358cd3ea073d`.
- Dev-run code manifest (registered in DR0 before execution): `a252717e0e457f865989c7501a0e1fe56df23cf08940d806e32ea33ee489bbc5`; clarifications D1–D10: `DEVRUN_CLARIFICATIONS.md`.
- Result JSON: `98ebb67ed7553178778ca679db56fff49d10da6e075078375a8056cb0e3341c8`. Private OOF decision table (not committed): `8a64fcbb7f98991bae4598119a61e48c5fa05130c7c6f0e821f40f25cafc7394`.
- Input hashes (seed manifest, extraction manifest, splits, labels, six MobileCLIP-B feature files): inside the result JSON and DR0. spec_v4 manifest `efb2a797…`; ep_seed = int(efb2a797, 16) % 2^31 (value in the result JSON).

## 3. Development diagnostics (pooled out-of-fold; descriptive; thin: 4 episodes, units not independent of identity or clip)
| | B0 (selected tau 0.7, margin 0.0) | L1 two-stage (selected tau_g 0.9, delta 0.10) |
|---|---|---|
| Unit FTA (n = 200) | 91 (0.455; exact CI 0.385–0.527) | 68 (0.340; exact CI 0.275–0.410) |
| Coverage (100 target units) | 0.732 | 0.587 |
| Per-fold coverage | 0.81 / 0.59 / 0.74 | 0.53 / 0.66 / 0.67 |
| FA by stratum (referee 55, staff 20, spectator 25, named-wrestler units 100) | 21, 12, 16, 42 | 8, 7, 0, 53 |
Exploratory paired sign test: b = 44 (B0 only), c = 21 (L1 only), both 47; one-sided p = 0.0030 (exploratory only; development-exposed; no outcome class).
Selected points are not coverage-matched (c* is a floor): L1 0.587 vs B0 0.732.
L1 diagnostics at the selected point: gate AUROC 0.989 (95% CI 0.981–0.994); 331 of 3,058 target candidates rejected at the gate. A/B AUROC 0.808 (CI 0.733–0.875); 591 target candidates abstained; 406 of 2,136 accepted target candidates assigned to the wrong wrestler. Non-target candidates accepted: 43 (referee 16, staff 27, spectator 0). Descriptive flags: D-GATE not flagged; F-ASSIGN interval excludes 0.5. Numeric failures: 0. Full 20-point grids for both methods are in the result JSON. Of 200 units the "named-wrestler" stratum holds 100 target units, so its false accepts are wrong-wrestler assignments; this stratum carries most of the L1 false-accept units (53 of 68).

## 4. Renderer outputs (private; footage-derived; never committed)
Source-rate (30 fps) renders of the four evaluated clips at the selected L1 point (EVALUATED / CARRIED-FORWARD ≤ 3 frames / NO-EVAL; boxes held, not interpolated; sidecar `frame_status` per tracklet). Sanity checks passed: EVALUATED set equals the decision table exactly; max carried age 3; frame counts equal the source.
Orton/Rollins 1,110 frames (EVALUATED 976 / CARRIED 2,056 / NO-EVAL 140 tracklet-frame statuses); Mysterio/Andrade clip 3,600 (2,047 / 4,306 / 206); Lesnar/Bryan clip 2,300 (1,982 / 4,177 / 200; extraction limit 1,934 frames); Andrade/Omega clip 3,587 (2,017 / 4,234 / 234). Hashes in RENDER_SUMMARY.json and RENDER_DELIVERY_COPIES.json (the delivered MP4s are H.264 re-encodes of the mp4v renders).

## 5. Blockers and items for reviewer ruling
1. **Old-TEST clips as development data.** The Andrade clips are old V0.6 TEST; spec 02 §2.2–2.3 designates them development data, so the Andrade fold scores them out-of-fold and they train the other folds. This is not the burned one-time check (not rerun; different head, cross-fitted), but please confirm this reading. Numbers are exploratory.
2. **Spec wording.** 02 §2.3 says evaluable episodes exist in "4 of 5 folds"; the manifest gives 3 evaluable folds (4 episodes). No change made.
3. **Choices left to code (D3–D5):** relaxed-seed fallback m = 3/2, resampling of target seeds only, candidate construction. Pre-registered in DR0, mirror the frozen rule, strict selector parity-tested; reviewer may rule on them. HBK and Rock contribute training only.
4. **Diversified TRAIN beyond existing data is blocked, not by training mechanics**: more diverse training needs new development clips (02 §2.5), which require reviewer approval and rights/privacy review first and are not obtainable now (R3 parked; no acquisition performed or planned). Training on the existing six clips is unblocked and done above.
5. **Not run:** seeds 1–3 variance, final all-development head, ablations A/B (spec: after the primary result is frozen; Holdout #2 not involved).
6. Evidence is thin: 4 evaluable episodes, 200 units, 100 target units, clustered by clip and identity; nothing here supports generalisation.

## 6. Boundaries
Old V0.6 TEST check not rerun; Holdout #2 not accessed, constructed or inferred; no study imagery sent to Gemini; no outreach; no performance-driven change to the rule, grids, selection, metrics, renderer, diagnostics or C1–C8.
