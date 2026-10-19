# V0.6.1 environment record
- Python 3.13.16; pinned packages in `requirements.lock` (hash-pinned install is optional).
- External paths come only from environment variables read in `v061/impl/config.py`: `V061_FROZEN_DIR`, `V061_FEATURE_DIR`, `V061_WEIGHTS_DIR`, `V061_PRIVATE_DATA_DIR`. No absolute paths in code (a test enforces this).
- Run the synthetic suite: `python v061/tests/run_all.py`. Verify implementation hashes: `python v061/tooling/impl_manifest.py` (regenerate with `--write` only through a reviewed PR).
- CI (`CI` job) installs numpy/scipy/opencv-python-headless/torch (CPU) on Python 3.11; results are not expected to differ for the synthetic suite. CI is a convenience check, not a reproduction of the frozen V0.6 run.
- No weights, media, footage-derived output or person-level tables are committed (hygiene scan enforces).
