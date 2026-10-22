# Owner CHECK labelling — Mac instructions (Stage D, frozen Protocol V1.1, same tool, same rules as BUILD)

The independent reviewer has authorized the frozen CHECK evaluation of Rule V1.1. The CHECK set (92 shots, 327.6 s, match 451.5–779.1 s) has **no labels yet**, so you now label it exactly as you did BUILD. **You choose every label.** You will see no classifier output, no rule, no features, no results. Labels are final on Submit; only the same clerical corrections as before (TOOL_ERROR / TRANSCRIPTION_ERROR) are possible, and if you think one is needed, **stop and tell the reviewer first**. Read Protocol sections 2–5 again if needed; nothing here changes them.

You need: the file `manifest_check.csv` I send you (save it in `~/Downloads`). Same package folder and same private folder as before.

## Steps (copy each block into Terminal; stop and report any line that prints REFUSED or an error)
**0. Go to the package and check the CHECK manifest fingerprint** (must print `f1b8664e0238a87c2e8a0eee34f50be5f0ebdb62e78852b5f1c9bf8d43a5517e`):
```
cd ~/Downloads/"STAGE_D_READY_TO_LABEL 3"
shasum -a 256 ~/Downloads/manifest_check.csv
```
**1. Record that the rule is frozen** (this is what lets the CHECK labels be unsealed later; hash = frozen Rule V1.1):
```
python3 v061/exposure_stage_d/stage_d_cli.py --root ~/stage_d_private freeze-rule b2e47698cd391faf86119525cc4dd9c939a0c807bd644069e02f964ba5df5111
```
**2. Open the CHECK set:**
```
python3 v061/exposure_stage_d/stage_d_cli.py --root ~/stage_d_private open-set check ~/Downloads/manifest_check.csv
```
**3. Record the match marks (once).** If you can identify the match START and END (Protocol section 7: start = first frame after the bell / first contact; end = decision frame) on the full match video, enter them in seconds on the source timeline and say what you saw (replace S, E and the text):
```
python3 v061/exposure_stage_d/stage_d_cli.py --root ~/stage_d_private set-marks check rr_balor_full --start S --end E --evidence "what you saw"
```
If you cannot, record NO_D instead:
```
python3 v061/exposure_stage_d/stage_d_cli.py --root ~/stage_d_private set-marks check rr_balor_full --flags NO_D --evidence "start/end not identifiable"
```
**4. Label all 92 shots** (same page as before, new port):
```
python3 v061/exposure_stage_d/labeller_ui.py --root ~/stage_d_private --set check --sources ~/stage_d_private/sources.json --port 8766
```
Open `http://127.0.0.1:8766/`, label shot by shot (category, confidence, UNKNOWN reason if UNKNOWN, flags), Submit. Resume later with the same command. Done when the page says all shots are submitted (`status` should show check 92 / 92).

**5. Close and unseal** (once; run in this order):
```
python3 v061/exposure_stage_d/stage_d_cli.py --root ~/stage_d_private complete check
python3 v061/exposure_stage_d/stage_d_cli.py --root ~/stage_d_private seal-check
python3 v061/exposure_stage_d/stage_d_cli.py --root ~/stage_d_private unseal-check
python3 v061/exposure_stage_d/stage_d_cli.py --root ~/stage_d_private export check ~/stage_d_private/check_export
python3 v061/exposure_stage_d/stage_d_cli.py --root ~/stage_d_private verify-chain
python3 v061/exposure_stage_d/build_return_report.py ~/stage_d_private check > ~/stage_d_private/check_return.json
```
**6. Send back exactly these four files:** `~/stage_d_private/check_export/labels_check.csv`, `~/stage_d_private/check_export/match_marks_check.csv`, `~/stage_d_private/check_return.json`, and `~/stage_d_private/events.jsonl` (the event log: timestamps and hashes of the freeze / seal / unseal steps). No videos, clips or frames.
