#!/bin/bash
# Reproduce the V0.1 baseline end to end. Run from the project root.
# Prereq: python3.12 venv with: torch, torchvision, ultralytics, opencv-python, numpy, pandas, scipy (see environment.txt)
# and models/yolov8m-pose.pt (ultralytics assets v8.3.0, sha256 in environment.txt). ffmpeg on PATH.
set -e
PY=${PY:-python3}
$PY src/stage1_detect.py input.mp4 out/raw_detections.pkl models/yolov8m-pose.pt   # ~30 min on 1 CPU core, resumable
$PY src/cuts.py input.mp4 out/cuts.json
$PY - <<'PYEOF'
import sys; sys.path.insert(0,"src"); import track
track.run("input.mp4","out/raw_detections.pkl","out/cuts.json","out/tracking.csv","out/annotated.mp4","out/run_meta.json")
PYEOF
$PY src/diagnose.py out/tracking.csv out/tracking_landmarks_raw.csv out/cuts.json out/raw_detections.pkl out/diagnostic_report.md out/failure_frames.csv
