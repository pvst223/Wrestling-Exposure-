# Stage-D owner shot-labelling tool (implements frozen Protocol V1.1; tool audit pending)

Private tool. Standard library only (ffmpeg optional, for cutting context clips from a private source video).
Contains no classifier, detection, identity, pose, anatomy or ownership code. **No real Stage-D footage has been labelled or loaded.** All tests and the demonstration use synthetic data (`SYN_*` ids, ffmpeg test pattern).

- `labeller_core.py` — rules, schema, state machine, hash-chained event log, corrections, sealing, reliability relabel.
- `labeller_ui.py` — local-only (127.0.0.1) page: one shot at a time, chronological, context clip limited to shot ±5 s, frozen ids/boundaries read-only, final on submit.
- `make_synthetic.py`, `demo_synthetic.py` — synthetic fixtures and the demonstration.
- `tests/test_labeller.py` — 27 tests; run: `python -m unittest discover -s v061/exposure_stage_d/tests -p 'test_*.py'`.
- `results/` — recorded test output and demonstration evidence (synthetic only).

Run (owner machine, private root never committed): `python labeller_ui.py --root <private_dir> --set build --sources sources.json`, after `Workspace.open_set(set, manifest.csv)` with a manifest of exactly `shot_id,source_id,set,t_start_s,t_end_s`.
