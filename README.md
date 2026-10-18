# Wrestling-Exposure

> **Developers: read [DEVELOPER_NOTICE.md](DEVELOPER_NOTICE.md) first.** Phase 1 of V0.6 is frozen; review is welcome, but do not change the frozen scientific implementation. Scientific changes go in a new V0.6.1+ branch as proposals.

Research code and audit records for a **markerless computer-vision prototype** aimed at understanding musculoskeletal-injury exposure in entertainment wrestling. This is a student research project. It is **not validated**, and nothing here is a clinical, medical or injury-prediction tool.

> **Read this first.** No claim of validation, accuracy, generalisation, clinical utility, workload, fatigue or injury prediction is made anywhere in this repository. Confidence values produced by the pipeline are heuristic evidence, not probabilities. The system is built to **fail closed**: when evidence is weak it abstains.

## Status at a glance

| Version | What it is | Status |
|---|---|---|
| V0.1 | Baseline: YOLOv8 pose detection + simple tracking | Frozen |
| V0.2 – V0.4 | Cut handling, appearance cues, re-ID experiments | Frozen |
| V0.5 | Anatomical ownership + identity pipeline | Frozen. **Failed Holdout #1** (see `versions/holdout1/HOLDOUT1_REPORT.md`) |
| V0.6 | Small learned open-set wrestler re-ID head (L1) vs non-learned baseline (B0), kept separate from anatomical ownership with fail-closed fusion | Phase 1 executed once; **result: MODIFY (ANNOTATION-PROVISIONAL)**. Post-hoc diagnostics complete (`v06/posthoc_v1/`); V0.6.1 is a proposal only, awaiting reviewer authorization. Allowed to fail |

V0.6 Phase 1 summary (full detail in `v06/frozen/phase1_results/`): on the test split, the learned head accepted nothing (coverage 0.000, 0 false accepts) while the baseline had 39 false-accept units (of 111 units). The comparison is vacuous for the learned head and is confounded by domain, resolution and promotion shifts. The head was trained on a single episode with 2 identities. The human annotation-reliability gate was **not satisfied as specified** (a blinded AI second annotator was used, recorded as deviation X1).

## Repository layout

```
baseline_v0.1/          V0.1 code, README, pinned requirements, env capture script
versions/v02..v05/      Frozen code, docs, reproducibility hashes for V0.2-V0.5
versions/holdout1/      V0.5 Holdout #1 code, config, report and metrics
v06/tools/              V0.6 tooling: structure builder, feature extraction, heads, runner, guards, selftests
v061/spec_v2/           V0.6.1 prospective design package, revision 2 (approved with amendments; not implemented; spec_v1 = superseded first draft)
v06/posthoc_v1/         Post-hoc diagnostics of the frozen Phase-1 result (code, numbers, report, V0.6.1 proposal; videos not included)
v06/frozen/             Frozen preregistration, amendments, closure records, dependency registry,
                        READY manifest, hash-chained AUDIT_LEDGER.jsonl, aggregate Phase 1 results
```

Each version directory is a **historical snapshot**. Do not edit frozen code to "improve" results; add new versions instead.

## What is deliberately NOT in this repo

Rights to the source footage are **UNRESOLVED**. Supplying footage to the project is not permission to publish or redistribute it, or to build a persistent spectator/staff dataset. So the repo excludes:

- video, frames, crops, contact sheets and annotation-package images/zips
- detections, tracklets, per-person labels, seed/episode manifests, feature arrays
- model weights (YOLO, MobileCLIP, DINOv2, OSNet, trained heads)
- the internal annotation key

`.gitignore` blocks these. **Do not commit them**, including in forks or branches. Do not re-identify wrestlers from appearance; user-supplied names are authoritative, and unsupported metadata stays UNRESOLVED. Keep imagery of non-target people to a minimum.

Consequence: you cannot reproduce the numeric results from this repo alone. Inputs are obtained privately from the project owner. Result hashes are recorded so reproduction can be checked.

## Getting started

```bash
git clone https://github.com/pvst223/Wrestling-Exposure-.git
cd Wrestling-Exposure-
python3 -m venv venv && source venv/bin/activate
pip install -r baseline_v0.1/requirements.txt   # pinned for V0.1; V0.6 also needs torch + numpy + scipy + pillow
```

Run the V0.6 synthetic self-tests (no footage, no weights needed):

```bash
cd v06/tools
for t in selftest selftest2 selftest3 selftest4 selftest5 selftest6 selftest7; do python3 $t.py || break; done
```

`selftest` through `selftest5` and `selftest7` use synthetic data and are expected to pass (they passed in a fresh checkout). **`selftest6` is known to fail**: it depends on private files and absolute paths, and one of its assertions (guard fails closed on the real ledger) became stale once Phase 1 was authorized. It is frozen and not patched; see `v06/posthoc_v1/POSTHOC_DIAGNOSTIC_V1.md` section 9. Some scripts assume the original working-directory layout (`frozen/`, `dets/`, `features/`), which you only have if given the private inputs. Paths are mostly passed as arguments (for example `--frozen_dir`, `--feat_dir`, `--out_dir`).

V0.1 baseline instructions: `baseline_v0.1/README.md`. It assumes `input.mp4` and a YOLOv8m-pose weight file, which are not included.

## V0.6 code map (`v06/tools/`)

| File | Role |
|---|---|
| `phase1_structure.py` | Extraction-frame manifest, seed and episode builder |
| `extract_features.py` | Backbone adapters: `mobileclip_b`, `dinov2_vits14`, `osnet_x1_0` (sparse-key safe) |
| `heads.py` | B0 non-learned baseline and L1 linear episodic head |
| `phase1_run.py` | Frozen analysis functions: grids, matched coverage c*, backbone selection, unit tables, sign test, outcome logic, LOCO |
| `phase1_execute.py` | Staged driver enforcing the order: train, DEV selection (frozen), TEST opened once, primary frozen, secondary |
| `authorization_guard.py` | Fails closed unless the ledger holds a matching reviewer authorization |
| `annotation_agreement.py`, `adjudicate.py` | Annotation agreement and adjudication (adjudication has not been run) |
| `selftest*.py` | Synthetic correctness tests |
| `registry.py`, `pipeline_guard.py` | Single-use sealed test/holdout enforcement and freezing |

## Governance rules for contributors

1. **Do not optimize toward a favourable outcome.** V0.6 is allowed to fail.
2. **Frozen means frozen.** `v06/frozen/` and the listed hashes must not change. The audit ledger is hash-chained and append-only (`prev_entry_sha256 = sha256(json.dumps(prev, sort_keys=True))`); only reviewer-authorized entries are appended.
3. **No tuning after test is opened.** TEST and Holdout #2 are single-use; Holdout #2 is untouched. Jeff Hardy footage is excluded (the failed holdout); Cena is development-only.
4. **No Phase 2 work, retuning, or adjudication of the 86 annotation disagreements** without an explicit reviewer ruling.
5. **Report honestly.** Use "ANNOTATION-PROVISIONAL" language; never state validation or predictive claims.
6. **Fail closed.** New code must abstain rather than guess.
7. **Size and hygiene.** Each committed file must stay under 30 MB. No secrets.
8. Prefer short, direct PRs. State which frozen artifacts, if any, a change touches (ideally none).

## Key frozen references

- Preregistration V3 SHA-256: `3e40f5ec3aea93539daeacdac7cb0bf1b4cfadbd90fb7de245641160c5c4ab78` (`v06/frozen/PREREGISTRATION_V3_FROZEN.md`)
- Final audit-ledger SHA-256 (25 entries): `d899a6eef923b85246f59e522c114fa28ef76cb6181d62944e4c0eeb6c0c5960`
- Third-party: `third_party/mobileclip` (Apple, MIT licence, included in version snapshots); DINOv2 and OSNet code/weights are fetched privately and not included.

## Contact

Project owner: @pvst223.
