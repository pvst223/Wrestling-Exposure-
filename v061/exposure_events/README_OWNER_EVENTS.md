# LANDING event coding tool — V1.1 (owner package)

> ## ⛔ DO NOT START PASS 1 YET
> This package is delivered for **independent reviewer audit**. Do **not** run `setup`, `run`, or open any footage with this tool until the
> reviewer has approved the implementation **and** you have been told in writing to begin. Three of the five sources
> (`b2_batch2_clip_condensed`, `b2_videoplayback_2`, `b2_videoplayback_5`) are flagged `UNRESOLVED_PROVENANCE` in `source_table_v1_1.json`
> (wrestler names not on record); the tool **refuses to set up** until the reviewer resolves them.

## What this is
A local, offline tool for recording **LANDING** events (first foot contact ending a visible airborne phase) exactly as defined in
`EXPOSURE_CONSTRUCT_AUDIT_EXPERIMENT_V1_1_DESIGN.md` (sha256 `c82971641c0a5c618604455e454d982716670966059958a807e6e86c7f8599a0`).
The definitions are shown verbatim inside the tool ("Show / hide coding manual"). Nothing else is shown: no event lists, no counts,
no previous-pass information, no model/CV/identity/anatomy/pose/mask/physical output, no Rule V1/V1.1 or classifier information.

## One-time checks (after approval)
1. `python3 verify_package.py` — recomputes every file hash against `MANIFEST.json`. Must print `PACKAGE OK`.
2. `python3 -m unittest discover -s tests -p 'test_*.py'` — the synthetic test suite (no real footage or labels involved). `TEST_RESULTS_SYNTHETIC.txt` is the recorded run.
3. Needs Python 3.10+ and a modern browser (Chrome/Safari/Firefox). `ffmpeg` is **not** needed for coding.

## Setup (after approval only)
`python3 event_cli.py --root ~/landing_events_private setup --search ~/Movies --search ~/Downloads`
Finds your five source videos by byte size + SHA-256 (nothing is copied or altered), records the design, source-table, tool and metric-code
hashes in the first audit record, and refuses if the design hash or any source provenance is unresolved.

## Pass 1
`python3 event_cli.py --root ~/landing_events_private run --pass 1` opens the tool in your browser (http://127.0.0.1:8765).
- You code **one source at a time, in table order**. Playback is limited to the allowed range of the source (b2_videoplayback_2 only up to frame 1933; rr_balor_full only to 779.133 s).
- Controls: play/pause, scrub, ±1 s / ±5 s, frame-by-frame, speed, exact time display, sound on. Looking within ±5 s of a moment to name the performer or judge observability is allowed.
- To record an event: set the time (0.1 s; "use current time" rounds the current position), choose performer (or UNCLEAR), choose FULL / PARTIAL / INFERRED, add evidence (required for PARTIAL / INFERRED), optional note (≤200 characters), **Submit**. A submission is **final**; you cannot edit or delete it in the tool.
- Press **finish source** only after you have actually watched the whole source (the tool checks that ≥95 % of it was played continuously at ≤2× speed).
- You may stop (Ctrl-C) and resume any time with the same command; the log is append-only.
- **Clerical corrections only** (typo in time, wrong button, duplicate): `python3 event_cli.py --root … correct --pass 1 --event-id ev_xxxxxxxxxx --reason TRANSCRIPTION_ERROR --explanation "…" --event-time-s 12.3` (or `--retract`). The id is shown after each submission. Each correction is a permanent, hash-chained audit record; the original stays in the log. Corrections are not possible for a finished source or a completed pass. Do **not** use corrections to change a judgement.
- When all sources are finished, click **Complete and freeze this pass** (irreversible). The tool records the pass hash and the earliest Pass-2 opening time.

## Export after completion
`python3 event_cli.py --root … export --pass 1` writes `landing_events_pass1.csv` and prints its sha256 (the "pass hash"). Send the CSV and the `audit.jsonl` to the reviewer; keep the originals. `python3 event_cli.py --root … verify-chain` checks log integrity at any time.

## How the Pass-2 lock works
The Pass-1 completion record in the hash-chained log stores `pass2_not_before_utc` = completion time + 7 days. `open-pass 2` / `run --pass 2` refuse (in code, not by memory) until the current UTC time is at or after that value. Pass 2 reads only Pass-2 records, so it shows nothing from Pass 1 (tests assert that no Pass-1 string, time, performer, observability or count is reachable). Pass 2 uses the identical definitions and tool.
Limits you should know: the lock uses your computer's clock; the tool refuses to write if the clock goes backwards or the log is edited, and every record carries a UTC timestamp, so tampering is detectable by the reviewer, not physically impossible.

## Files
`event_core.py` (log, rules, lock) · `event_ui.py` (browser interface) · `event_cli.py` (commands) · `landing_metrics.py` (frozen evaluation code; **not run by you**) ·
`source_table_v1_1.json` · `config_v1_1.json` · design `.md` · `tests/` · `MANIFEST.json` · `TEST_RESULTS_SYNTHETIC.txt`.
