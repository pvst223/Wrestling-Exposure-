#!/bin/bash
cd /home/claude/proj
{ echo "# Environment for V0.1 baseline run (captured $(date -Is))"; python3 --version; /home/claude/venv/bin/python --version
  echo "--- key packages (venv)"; /home/claude/venv/bin/pip list 2>/dev/null | grep -i -E "^(torch|torchvision|ultralytics|opencv|numpy|pandas|scipy|ultralytics-thop|pillow|pyyaml)[ -]"
  echo "--- ffmpeg"; ffmpeg -version | head -1
  echo "--- model weights"; sha256sum models/yolov8m-pose.pt; ls -la models/yolov8m-pose.pt
  echo "--- model source: https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8m-pose.pt (COCO-17 keypoints)"
  echo "--- input video"; sha256sum input.mp4; ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames -of default=nw=1 input.mp4
  echo "--- hardware"; nproc; grep -m1 "model name" /proc/cpuinfo; free -g | head -2
  echo "--- inference settings: imgsz=960, conf=0.10, device=cpu, ultralytics default NMS"
} > out/environment.txt
