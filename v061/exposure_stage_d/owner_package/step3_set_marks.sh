#!/bin/bash
# Records the five BUILD match-marks (reviewer ruling D2): NO_D for every source. Run once.
ROOT="${1:-$HOME/stage_d_private}"; CLI="$(cd "$(dirname "$0")" && pwd)/v061/exposure_stage_d/stage_d_cli.py"
m() { python3 "$CLI" --root "$ROOT" set-marks build "$1" --flags NO_D --evidence "$2" >/dev/null && echo "mark set: $1" || echo "mark NOT set (already recorded?): $1"; }
m b1_orton_rollins_wm31 "short excerpt; no start or end bell in the excerpt (NO_D)"
m b2_batch2_clip_condensed "short condensed excerpt; no start or end bell (NO_D)"
m b2_videoplayback_2 "short excerpt; no start or end bell (NO_D)"
m b2_videoplayback_5 "short excerpt; no start or end bell (NO_D)"
m rr_balor_full "partial segment 150-450 s of a longer match; match start/end marks are recorded only in the sealed CHECK marks (NO_D)"
