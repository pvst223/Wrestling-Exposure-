# Owner BUILD labelling — start sheet (authorized under frozen Protocol V1.1)

Frozen inputs (reviewer-approved; Option A; no regeneration): BUILD manifest sha256 `d0c73ca106c9cef5e34766aaabfdceaf039e2735e58c76a52362c0a7d3a99aaf` (169 shots, 638.233 s); CHECK manifest sha256 `f1b8664e0238a87c2e8a0eee34f50be5f0ebdb62e78852b5f1c9bf8d43a5517e` (92 shots, 327.600 s). Verify with `sha256sum` before `open-set`.

Order: finish BUILD first where practical. CHECK may be labelled, but stays sealed from the rule builder until the BUILD-derived rule hash is frozen.

Marks (reviewer D2): BUILD — all five sources `--flags NO_D` with an evidence note, e.g.
`python stage_d_cli.py --root R set-marks build b1_orton_rollins_wm31 --flags NO_D --evidence "short excerpt, no bell"` (repeat for the other three clips and `rr_balor_full` = "partial segment 150-450 s"). Never put the match end in BUILD marks.
CHECK — `set-marks check rr_balor_full --start <s> --end <s> --evidence "<what you saw>"` (full-match start/end, 0.1 s).

After BUILD labelling: `python stage_d_cli.py --root R complete build`, then
`python build_return_report.py R build > build_return.json` and send back ONLY that JSON, plus
`python stage_d_cli.py --root R export build <dest>` for the rule builder. Do not send check labels, clips or frames.
The report contains: category counts and durations, UNKNOWN reason counts and durations, build U_ref (descriptive), confidence and flag distributions, corrections, label hash, event-chain hash.
