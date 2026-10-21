# Owner BUILD labelling — Mac instructions (Stage D, frozen Protocol V1.1)

You are the human reference labeller. **You** choose every label. This package has no classifier, no CHECK information and no results.

## Your only task for every shot
Choose the **broadcast-production reference category** under Protocol V1.1 (`v061/exposure_design/EXPOSURE_V1_STAGE_D_LABELLING_PROTOCOL_V1_1.md` — read sections 2–5 first; it is the authority, nothing here simplifies it):
`LIVE_ACTION` · `REPLAY` · `CLOSE_UP` · `NON_MATCH` · `UNKNOWN`
plus **confidence** (HIGH / MEDIUM / LOW), a **reason if UNKNOWN** (required; `OTHER` also needs a note), and any **flags** that apply. You are not judging wrestlers, effort, contact, identity or anything else. Labels are final when you press Submit.

> The labelling clip for each shot contains the available source picture **and sound** for the authorized context window (the shot ± 5 s), as Protocol §5 allows. If a source has no audio track, the clip is simply silent; no sound is ever added.

## What you need on the Mac
- **Python 3** (check: Terminal → `python3 --version`; if it asks to install developer tools, accept, or run `xcode-select --install`).
- **ffmpeg** (check: `ffmpeg -version`; if missing: install Homebrew from https://brew.sh then `brew install ffmpeg`).
- **Your five existing source videos**, any folder under your home folder (Downloads, Movies, Desktop or Documents are searched automatically). They are never copied, trimmed or changed. The setup program finds them by their SHA-256 fingerprint, so the file name does not matter:

| source id | project file name | bytes | SHA-256 |
|---|---|---|---|
| b1_orton_rollins_wm31 | orton_rollins_wm31.mp4 | 19786272 | eb9625d30eef49670fdb6d469f77d549ec364005f95e73c207150320c16b3723 |
| b2_batch2_clip_condensed | b2_batch2_clip_condensed.mp4 | 20652610 | e89e92c71690d2e7285ebce6e0877d74b9c685cb3ca504e83644fc2814bb5486 |
| b2_videoplayback_2 | b2_videoplayback_2.mp4 | 5156110 | d6728cb914fd0bbd2e4efdb14a4e1a08a8c8dfbaa387db3b6535417008136319 |
| b2_videoplayback_5 | b2_videoplayback_5.mp4 | 11023849 | e72c5561b15de92fc5c34f24ad54097111c753ce49c12603cbaccc5265fcb575 |
| rr_balor_full | FULL_MATCH_-_Roman_Reigns_vs__Finn_Bálor_Raw__July_25__2016_-_WWE__1080p_.mp4 | 385742414 | 7d718d6c82fd893c62634a5b62ec48178543bfec95164d80c344614057ee26ee |

To check a file yourself: `shasum -a 256 "/path/to/file.mp4"` must print the SHA-256 above.

## Steps
1. **Unzip.** Double-click `STAGE_D_OWNER_PACKAGE_V1_1.zip`. Open Terminal and go there: `cd ~/Downloads/STAGE_D_OWNER_PACKAGE_V1_1`
2. **Source videos.** Make sure the five files above exist somewhere under your home folder (do not rename or edit them).
3. **Setup (once).** `python3 setup_owner.py`
   It checks Python/ffmpeg, the frozen protocol and the frozen BUILD manifest (169 shots, sha256 `d0c73ca1…99aaf`), finds your five videos, writes `~/stage_d_private/sources.json`, and opens the BUILD set. If a video is "MISSING", re-run with `--search /folder/where/it/is` or `--path source_id=/full/path/file.mp4`.
4. **Record the five BUILD match-marks (once).** `bash step3_set_marks.sh`
   (All five are `NO_D` — reviewer ruling D2. Do not enter any match end time.)
5. **Start the labelling page.** `python3 v061/exposure_stage_d/labeller_ui.py --root ~/stage_d_private --set build --sources ~/stage_d_private/sources.json --port 8765`
   Leave this Terminal window open.
6. **Open in your browser:** `http://127.0.0.1:8765/`
7. **For each shot** (shown one at a time, in time order; "Shot n / 169"): play the clip (with sound; the highlighted part of the bar is the shot; the rest is the allowed ±5 s context); choose one **category**; choose **confidence**; if UNKNOWN pick the **reason** (and write a **note** if OTHER); tick any **flags**; optionally a short note (≤ 200 chars); press **Submit label**. It is final. The next shot appears automatically.
8. **Stop and resume safely.** Every submitted label is saved to disk immediately. To stop, go to the Terminal window that is running Step 5 and press `Control` + `C`. To resume, run the Step 5 command again; it continues at the next unlabelled shot. Never delete `~/stage_d_private`, never re-run Step 3 or 4, and never edit its files.
9. **Check progress / completion.** `python3 v061/exposure_stage_d/stage_d_cli.py --root ~/stage_d_private status`
   Done when it shows `"labels_submitted": 169` and `"total_shots": 169` for `build` (the page also says "All shots in this set have been submitted").
10. **Mis-click or typing slip?** Only a clerical correction is allowed, never a change of mind. Example:
   `python3 v061/exposure_stage_d/stage_d_cli.py --root ~/stage_d_private correct build <SHOT_ID> --reason TOOL_ERROR --explanation "mis-click" --label CLOSE_UP --confidence HIGH`
   (reasons: `TOOL_ERROR` or `TRANSCRIPTION_ERROR`; add `--unknown_reason`, `--flags`, `--note` as needed.) The original is kept in a log.
11. **Complete the BUILD set (once, when all 169 are done).** `python3 v061/exposure_stage_d/stage_d_cli.py --root ~/stage_d_private complete build`
12. **Create the return file.** `python3 v061/exposure_stage_d/build_return_report.py ~/stage_d_private build > ~/stage_d_private/build_return.json`
13. **Send back for the independent reviewer audit exactly one file:** `~/stage_d_private/build_return.json`. Do **not** send videos, clips, frames, `labels_build.csv` or anything else unless asked. (The reviewer's workflow later asks for the BUILD export through `stage_d_cli.py … export build <folder>`; do not run it until told.)

## Rules to keep
Do not label from memory of anything other than the protocol; do not look for or use classifier output (none exists here); the CHECK segment is not in this package and is not labelled now. Rights are unresolved: the videos and clips stay private on your Mac.
