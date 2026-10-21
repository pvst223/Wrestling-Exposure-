# Owner package V1.1 — defect-only change report

**Defect (reviewer ruling "STAGE-D OWNER BUILD LABELLING PACKAGE: MODIFY / OPTION (a)").** The context-clip cutter in `labeller_ui.ffmpeg_clip_provider` removed source audio (`-an`), although frozen Protocol V1.1 §5 permits the labeller to use the shot's picture and sound.

**Change (implementation correction only).** `labeller_ui.py`: replaced `-an -c:v libx264 …` by `-map 0:v:0 -map 0:a:0? -c:v libx264 … -c:a aac -b:a 128k`. The audio track of the same `-ss/-to` window is kept; if the source has no audio stream the optional map selects nothing and no audio is created. Nothing else in the tool changed.
`README_OWNER.md`: the "silent clips" warning is removed and replaced by the statement that the labelling clip contains the available source picture and sound for the authorized context window; the package folder/zip name is now `STAGE_D_OWNER_PACKAGE_V1_1`. `build_owner_package.py`: output folder name only.

**Unchanged (byte-identical to package V1):** `labeller_core.py`, `stage_d_cli.py`, `build_return_report.py`, `setup_owner.py`, `step3_set_marks.sh`, Protocol V1.1 (sha256 `0b6c8740…dad9`), `manifest_build.csv` (sha256 `d0c73ca106c9cef5e34766aaabfdceaf039e2735e58c76a52362c0a7d3a99aaf`; D1 Option A). No change to shot ids/boundaries, the ±5 s window, categories, UNKNOWN handling, confidence/flags/notes, final-on-submit, schema, corrections, sealing, leakage controls, or BUILD/CHECK separation.

**Re-verification (synthetic tests + package install; no real label submitted, scratch deleted).**
- Synthetic source with audio → clip has audio + video streams, duration equals the frozen context window (±0.6 s tolerance); video-only source → clip succeeds with video only (no invented audio). Test class `T10_AudioInContextClips`; 30 tests pass.
- Package install: setup finds all five sources and opens the 169-shot BUILD set; five NO_D marks recorded; real-source context clips (one 12.2 s clip from the match source, one 12.0 s clip from an Orton–Rollins shot, both within the expected shot ± 5 s window) contain audio + video; context start/end and shot boundaries are as displayed by the unchanged view; labels submitted: BUILD 0, CHECK 0.
- Source audio streams (technical fact): orton_rollins_wm31 1, videoplayback_2 1, videoplayback_5 1, rr_balor_full 1, **batch2_clip_condensed 0** (that source file has no audio track, so its clips are silent by nature).
- No CHECK, classifier, preflight or result files are in the package.
Evidence: `OWNER_PACKAGE_V1_1_VERIFICATION.json`, `TEST_RESULTS.txt`.
