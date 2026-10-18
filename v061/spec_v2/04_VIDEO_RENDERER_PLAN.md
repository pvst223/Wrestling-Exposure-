# 04 V0.6.1 annotated-video renderer plan (REVISION 2; architecture APPROVED by reviewer; separate from scientific inference)

## Problem in V0.6 diagnostics
Frozen decisions exist only at candidate frames (about every 3rd source frame, sometimes 6). The V0.6 videos wrote only those frames at 10 fps, so playback looked choppy and was not source-rate.

## Design
- Separate module `v061/render/` with its own entry point. It imports nothing from the inference, training or threshold-selection code. Input is a frozen decisions file only: per-candidate rows (clip, tracklet, frame, truth class, g, q, decision, reason, B0 decision) plus frozen tracklet boxes and the normalized source video. No model is loaded; no scores are computed or changed.
- Output at source frame rate (30 fps) and full source length, so playback is smooth.
- Every output frame has exactly one status, written to a sidecar JSON/CSV (`frame_status`):
  - EVALUATED: this frame has a frozen decision. Bright coloured box and full decision text (OK, MISS, SWAP-FA, FA, rej, ABSTAIN reasons).
  - CARRIED-FORWARD: no decision on this frame; the box and label of the most recent EVALUATED frame of the same tracklet are shown, at most 3 source frames old (the detection stride). Drawn dashed, desaturated, and stamped "carried +Nf (visualization only)". Never coloured as a correct/false accept. Boxes are NOT interpolated; they are held at the last evaluated position.
  - NO-EVAL: farther than 3 frames from an evaluated frame, or outside the tracklet's span: no overlay except a small "no evaluated detection" badge.
- On-screen counters per video: evaluated frames, carried-forward frames, no-eval frames (also in the sidecar); a legend explains the three states and the frozen parameters.
- Decision text never changes across a carried-forward run.
- Smooth-playback option: none beyond holding; no optical flow, no tracking, no re-detection.

## Safeguards
- Renderer test (synthetic only): hash of the decisions table read equals the hash recorded in the frozen result; the count of EVALUATED frames equals the number of unique (clip, frame) pairs in the decisions table; no CARRIED frame older than 3 source frames; a deliberately perturbed decisions file must change the renderer's input hash.
- Renderer is not run on Holdout #2 before the V0.6.1 freeze, and after the freeze it runs only on the frozen output file.
- Videos are footage-derived: never committed to the repository; only their hashes and the sidecar frame-status counts (no imagery) are recorded.
- Rendering parameters (colours, fonts, stride limit 3) are frozen in the renderer's config and hashed.
