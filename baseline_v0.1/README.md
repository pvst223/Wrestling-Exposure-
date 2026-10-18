# V0.1 baseline — professional-wrestling single-target tracking (research prototype)

Frozen baseline for independent audit. Read `out/BASELINE_EVALUATION_REPORT.md` first. **Nothing is validated; no ground truth exists.** Position/identity feasibility test only: no distance, velocity, acceleration, force, impact, load, fatigue or exposure variables.

## Files
| File | What |
|---|---|
| `out/annotated.mp4` | full annotated video (skeleton drawn only for landmarks >= 0.70 conf; COM = labelled diamond+crosshair; status, confidence, segment, cut banner) |
| `out/tracking.csv` | frame-level output (1,501 rows). Columns: frame (0-based), time_s, camera_segment, identity, identity_basis, COM_x_pixel, COM_y_pixel, tracking_confidence, status, visible_landmarks, camera_cut, plus diagnostics visible_mass_fraction, com_uncertainty_px_heuristic, com_source, denim_fraction, det_conf, n_candidates, flags, missing_landmarks, observed_segments |
| `out/tracking_landmarks_raw.csv` | every raw landmark (x, y, confidence) of the selected detection per frame, including those not drawn |
| `out/tracking_with_overlap.csv` | tracking.csv + audit column max_overlap_iou |
| `out/cuts.json` | 24 detected cuts (+ 4 photometric events judged not cuts) |
| `out/diagnostic_report.md` | automatic diagnostics |
| `out/BASELINE_EVALUATION_REPORT.md` | evaluation with visual audit findings |
| `out/audit_manual_spotcheck.md`, `out/audit/*.jpg` | manual spot-check table and the contact sheets I viewed |
| `out/failure_frames.csv` | automatic list of 75 flagged frames |
| `out/failure_frames_manual.csv` | ranges of likely failures/ambiguity with category and evidence level |
| `out/raw_detections.pkl` | cached YOLO output for all 1,501 frames (Python pickle: load only if you trust this package) |
| `out/environment.txt`, `out/run_meta.json` | versions, hashes, hardware, frozen config, learned denim rule |
| `out/preview_and_scratch/` | the approved 300-frame preview and early smoke-test outputs |
| `out/tracking_full.csv` | all 1,501 rows; original 20 columns unchanged + loss/reacquisition state, landmark-quality counts, selected box, raw/gated detection counts, landmark-absence reason, audit annotations (prefixed `audit_`, my manual audit, not tracker output) |
| `out/frames_without_landmarks_accounting.csv`, `out/accounting_summary.json` | per-frame reason for the 710 frames without selected landmarks |
| `out/diagnostic_report_full.md` | complete diagnostic report |
| `out/cut_detection_params.json` | cut-detector, pose, tracker, display parameters and detected cuts |
| `out/COM_DOCUMENTATION.md` | exact COM method (not validated) |
| `out/REPRODUCIBILITY.md` | versions, hashes, commands |
| `out/FAILURE_AND_DO_NOT_TRUST_LIST.md` | consolidated frame ranges not to trust |
| `src/` | all code |

`status` values: MEASURED, PARTIAL, PREDICTED, UNRESOLVED. `identity_basis`: appearance, continuity, prediction, none. **Pixel COM values on either side of a camera cut are not comparable**; exclude cross-`camera_segment` differences.

## Reproduce
Inputs not included: the video (sha256 in `environment.txt`) and weights `yolov8m-pose.pt` from https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8m-pose.pt (sha256 dbe539ea268db2534390942cfdf206e521f376f19e5415967a57f6a2ddfa3c90). Put them at `input.mp4` and `models/yolov8m-pose.pt`, install the packages in `requirements.txt`, then `bash src/run_all.sh` (about 30 min on one CPU core, mostly pose inference; resumable). Python 3.13.16, torch 2.14.1 (CPU used), ultralytics 8.4.177, OpenCV 5.0.0.93. YOLO inference on a different CPU/BLAS may differ in the last digits.

## Code map
`stage1_detect.py` pose cache; `cuts.py` camera cuts; `com_model.py` Dempster/Winter COM; `track.py` identity, COM, status, annotation (parameters in `CONFIG`; display-only settings in `DISPLAY`); `diagnose.py` report; `audit_montage.py`, `viz_dets.py` audit helpers; `run_all.sh`.

## Change log (after the approved 300-frame preview)
1. `track.py`: added `max_frames` argument (preview only); added display-only skeleton filter (`DISPLAY`) and COM marker restyle; added export-only `*_landmarks_raw.csv`. No change to tracking, COM, identity, cut, confidence or status logic. Verified: first 300 rows of `tracking.csv` identical to the preview CSV in all columns.
2. `diagnose.py`: rewritten with loss, latency, overlap, geometry and COM-consistency analyses; fixed pandas `df.flags` attribute collision and a mislabelled counter. Analysis only.
3. `audit_montage.py`: fixed a frame index beyond the end of video. Audit helper only.
4. Environment was rebuilt after a sandbox reset (details in the report, section 8).

5. Documentation phase: added analysis-only scripts `build_full_outputs.py`, `diagnose_full.py`, `make_failure_list.py`. Hashes of tracking.csv, annotated.mp4, cuts.json, raw_detections.pkl, track.py, com_model.py, cuts.py, stage1_detect.py verified unchanged.

## Not implemented (by instruction)
V0.2, two-wrestler tracking, any exposure metric. See report section 10 for the documented future architecture.
