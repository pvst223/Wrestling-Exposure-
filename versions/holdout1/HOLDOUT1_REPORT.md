# V0.5 Holdout #1 (Jeff Hardy clip) — Factual Report
Diagnostic stress test of FROZEN V0.5, run once, unchanged. NOT validation. Nothing tuned, no reseeding, no V0.5.1/V0.6.
A = Jeff Hardy, B = opponent, referee = NEITHER. 706 frames, 1280x720 source, 30 fps.

## Disclosures
- Single, non-independent reviewer (the developer-assistant). Heuristic evidence, not probabilities.
- Cursor exposure of Jeff: UNVERIFIED. Treat Jeff as possibly not fully untouched.
- Preprocessing used a 640x360 downscale (V0.5's development resolution); review tiles use original 720p.
- Pose weight yolov8m-pose v8.3.0 (sha dbe539ea...3c90) is the prospectively pinned Stage-1 dependency; NOT known to be the original V0.1 artifact.
- Run on x86-64; development-era ARM64 vs x86-64 differences (~0.4% boundary-sensitive frames) apply.
- Denim calibration seed cue was built for Cena; not changed.
- Seed freeze: 10 seeds (4 A, 4 B, 2 NEITHER) hashed before any tracker output (config/seeds_holdout1.json).
- Review sample strata R3 selected frames where the tracker assigned a detection (status never shown to reviewer). Blind verdicts hashed before join.

## Coverage (automated)
- A: 87/706 emitted (37 MEASURED, 50 PARTIAL), 0 PREDICTED, 619 UNRESOLVED.
- B: 195/706 emitted (160 MEASURED, 32 PARTIAL, 3 PREDICTED), 511 UNRESOLVED.
- Plain-frame check (every 30th frame): A clearly visible 23, emitted 3; B visible 19, emitted 8. Overlap frames: A emitted 0/10, B 2/11.
- Shots with an A emission: 6/10; with a B emission: 8/10.

## Identity integrity (manual, blind) — FAILURE FOUND
- A emissions reviewed in preregistered sample: 34 of 87; 5 were a spectator, not Jeff (all emitted PARTIAL, identity tier ACCEPT, LOW_MASS, SINGLE_BODY_SUPPORTED, identity SUPPORTED_INDEPENDENT). Random A sample R1: 4/30 wrong-person.
- Post-hoc diagnostic (separately labelled, not preregistered) on the other 53 A emissions: 9 wrong-person (spectator), 16 clean-but-poor pose, 28 clean.
- Combined across all 87 A emissions: 14 wrong-person (~16%), 0 mixed-body emitted.
- B emissions reviewed: 21 clean, 0 wrong-person (sample only).

## Ownership / merged-person
- Both MIXED_BODIES frames in the sample were withheld (fail-closed worked there).
- Temporal absorbed-person logic fired for B (28 OPPONENT_PRESUMED_ABSORBED, 3 THIRD_PERSON) frames.
- Known weakness confirmed: a lone spectator is a single body, so ownership gates cannot stop a wrong-person emission once identity reaches ACCEPT.

## Fail-closed safety
- Merged/mixed frames withheld in sample. Wrong-person spectator frames mostly withheld (11 of 16 in preregistered tiles) but 14 total leaked into emitted A output. Silent wrong measurement occurred.
- 35 frames with both wrestlers emitted; min COM distance 87.7 px (none <30 px).

## Prediction
- B: 3 PREDICTED (frames 75, 77, 169); A: none. 0 predictions off-image. Prediction log 149 rows. Not independently assessed beyond this.

## Cuts
- 9 CUT events (13, 79, 114, 158, 242, 469, 540, 594, 620) all visually true; 0 false. Frame 343 is a true shot change logged as SAME_SCENE_RETURNS. Frames 189–195, 542–543 are camera motion, not cuts. No missed cuts found in visual check.

## Reproducibility
- Hashes: reproducibility/*.txt, env record JSON, code hashes verified 0 mismatches vs frozen V0.5.

## Bottom line
Frozen V0.5 did not generalise cleanly: low A coverage and a silent spectator wrong-person leak (identity ACCEPT + low-mass single body passes every gate). Reported as a result; not rescued.
