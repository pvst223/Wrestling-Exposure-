# Stage-D input preparation, no-label preflight and owner handoff (V1)

Status: for independent reviewer verification. **No label assigned; no classifier implemented; no fresh acquisition.** Machine-readable evidence: `STAGE_D_PREFLIGHT_REPORT_V1.json` (hashes and counts only; no footage, frames or per-shot content in the repo). Rights UNRESOLVED; ANNOTATION_PROVISIONAL; R4 unmet.

## 1. What was prepared
| item | result |
|---|---|
| Protocol V1.1 SHA-256 | `0b6c8740…dad9`, equals the pinned frozen hash |
| Manifest schema | exactly `shot_id, source_id, set, t_start_s, t_end_s` (enforced by the approved tool) |
| BUILD manifest | 169 shots, 638.233 s: 4 burned development clips (orton_rollins_wm31 11, batch2_clip_condensed 40, videoplayback_2 24, videoplayback_5 9) + Reigns–Bálor 85 shots (151.367–448.567 s). sha256 `d0c73ca1…9aaf` |
| CHECK manifest | 92 shots, 327.600 s: Reigns–Bálor (451.533–779.133 s). sha256 `f1b8664e…5517e` |
| Build/check shot-id overlap | 0 |
| Shot boundaries | no shot detection was tuned. Burned clips: the frozen per-clip cut lists, passed through the frozen merge (events < 0.25 s) and frame rounding (30 fps) of `build_tracklets.shots()`; shot counts 11/40/24/9 equal the frozen estimates; videoplayback_2 keeps its frozen frame limit 1934 (t = 64.467 s). Match: the identical frozen rule (ffmpeg scene > 0.3 on the ORIGINAL file, merge < 0.25 s) run once over the whole file (232 shots); its first-150 s cuts equal the earlier 0–150 s segment cuts exactly (60/60, max time difference 0.0 s) |
| Sources | all 5 source ids resolve; original bytes untouched, hashes below |
| Context clips | representative build and check context clips cut and opened; durations 11.73 s each (expected shot ±5 s) |
| Labels / classifier | 0 build labels, 0 check labels; no classifier code exists |

Source SHA-256 (original files, not re-encoded or altered):
- b1_orton_rollins_wm31 `eb9625d3…3723`; b2_batch2_clip_condensed `e89e92c7…b486`; b2_videoplayback_2 `d6728cb9…6319`; b2_videoplayback_5 `e72c5561…5cb`; rr_balor_full `7d718d6c…26ee` (equal to the owner-supplied upload). Full hashes are in the JSON.

## 2. Discrepancies and open items (the reviewer should rule before BUILD labelling)
**D1 — two match shots straddle a split point.** The frozen shot partition has a shot that crosses 150 s (147.133–151.367 s) and one that crosses 450 s (448.567–451.533 s). Because shot boundaries may not be moved or artificially cut, the prepared manifests **exclude both** (option A): BUILD match range 151.367–448.567 s, CHECK 451.533–779.133 s, with 7.2 s unlabelled in total. The 147–151 s shot lies in the already-seen first 150 s. Option B (start-time assignment: a shot belongs to the set containing its start; the 450 s straddler goes to BUILD, the 150 s straddler stays excluded as seen) would add one shot (448.567–451.533 s) to BUILD and leaves CHECK unchanged. Either is deterministic and made before any label exists; the choice is the reviewer's.

**D2 — where the match start/end marks (D) are recorded.** The tool needs a marks row per source per set. The match end lies in the CHECK range. Recording an end mark in the BUILD marks would hand the rule builder a CHECK-range fact. Proposed: BUILD marks for the match use the `NO_D` flag with an evidence note (a partial segment, 150–450 s), and the four burned clips also use `NO_D` (short excerpts, no bell); the match's start/end marks are recorded only in the CHECK marks file (sealed). Needs confirmation.

**D3 — thin command-line wrapper.** The approved tool has no marks/seal/etc. command line; `stage_d_cli.py` adds one-line wrappers (open-set, set-marks, complete, correct, seal-check, freeze-rule, unseal-check, export, summary, status) around the approved core API with no new logic (28 tests pass, including the wrapper). Labels are still entered only in the approved UI.

**D4 — the identity of the "four burned development clips"** was taken to be the four clips of the anatomical/devrun evaluation (orton_rollins_wm31, batch2_clip_condensed, videoplayback_2, videoplayback_5). Please confirm.

## 3. Owner handoff (private; nothing below is committed)
1. **Footage on the labelling machine.** Put the five source files on the machine that will run the tool; verify each SHA-256 above (`sha256sum`). Edit the private `sources.json` so each `source_id` maps to that machine's path. Do not re-encode, trim or rename for labelling convenience.
2. **Install:** Python 3.11+ and ffmpeg. Get the repository at the merged commit (`v061/exposure_stage_d/`); no other dependency.
3. **Private root:** choose a new empty private folder, e.g. `~/stage_d_private` (never inside the repository). Copy `manifest_build.csv` and `manifest_check.csv` into it. Confirm manifest hashes equal those above.
4. **Open both sets (once):** from `v061/exposure_stage_d/`:
   `python stage_d_cli.py --root ~/stage_d_private open-set build ~/stage_d_private/manifest_build.csv`
   `python stage_d_cli.py --root ~/stage_d_private open-set check ~/stage_d_private/manifest_check.csv`
5. **Label:** `python labeller_ui.py --root ~/stage_d_private --set build --sources ~/stage_d_private/sources.json --port 8765`, open `http://127.0.0.1:8765/`. One shot at a time, chronological; labels are final on submit. Use Protocol V1.1 only. (First clip generation per shot takes a second or two.)
6. **Marks:** per D2 once ruled: `python stage_d_cli.py --root … set-marks build <source_id> --flags NO_D --evidence "<note>"` for each of the 5 build sources; `set-marks check rr_balor_full --start <s> --end <s> --evidence "<what you saw>"` (0.1 s) for the check set.
7. **Complete:** `complete build`. Deliver to the rule builder only the exported build files: `export build <dest>` plus the `summary build` output. Do not send check labels.
8. **CHECK:** label with `--set check` at any time; `complete check`; `seal-check` (hash only is shared). The check labels stay unavailable until the rule hash is frozen (`freeze-rule <sha256>` by the ledger entry), then `unseal-check`.
9. **Corrections:** only tool/transcription errors via `correct …` before rule freeze (build) or unsealing (check). Never relabel because of classifier output.
10. **Reliability relabel:** after completing a set, wait at least 7 days; the tool will serve a deterministic 10% sample (seed 20261021).
11. **Return to the project (hashes/counts only):** `events.jsonl` hash, `labels_build.csv` hash, `summary build` JSON. No clips, frames or per-shot content.

## 4. What this does not authorize
BUILD labelling begins only after the reviewer rules on D1–D4. No classifier, no fresh acquisition, no Stage F, no exposure-validity claim.
