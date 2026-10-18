# 06 Leakage register (DRAFT): what in the design could leak information from the old TEST or from future Holdout #2

Severity: H high, M medium, L low. "Control" is what the design does about it; "Residual" is what stays and must be disclosed.

## A. Leakage from the old V0.6 TEST into V0.6.1 design
| # | Path | Sev | Control | Residual |
|---|---|---|---|---|
| A1 | The two-stage rule exists because TEST diagnostics showed A/B degradation and a floor that did not transfer. The rule is TEST-informed. | H | Old TEST permanently ineligible as confirmatory; confirmation only on fresh Holdout #2; the motivation is documented as post-hoc. | V0.6.1 is a hypothesis generated from exposed data; a pass on Holdout #2 supports it only prospectively and once. |
| A2 | Grid ranges (tau_g, delta, B0 extension) chosen after seeing TEST score ranges. | M | Grids fixed in this draft before any new data, wide (7 values per axis), matched budget for both methods, not fitted to scores; disclosed. | Knowledge of the old TEST scale shaped the range. Reviewer may widen but not narrow after approval. |
| A3 | B0 grid extension motivated by the observation that tau=0.30 was non-selective on TEST. | M | Extension is symmetric (same size as L1), pre-specified, and re-selected on development data only. | Open decision O1. |
| A4 | Old TEST data used as development data (training/selection). | M | Allowed but labelled exploratory; identity-component cross-fitting (Andrade links both TEST clips); no claim from any number on it. | Development estimates are optimistic; they must never be quoted as performance. |
| A5 | Backbone choice (MobileCLIP-B) came from a DEV-only Phase-1 rule, but the other two backbones' TEST behaviour is not evaluated and not to be examined. | L | Backbone frozen; no re-selection. | None beyond A1. |
| A6 | Using old-TEST B0 false-accept rate (about 0.35) in sample-size reasoning. | L | Labelled illustrative; not used to set any threshold. | Disclosed. |
| A7 | Planning documents quote TEST diagnostics (e.g. AUROC 0.72). | L | Quoted only as motivation, from frozen reports. | None. |
| A8 | Relaxed TRAIN seed rule chosen after learning that two TRAIN clips were unevaluable. | M | Applies to TRAIN only, pre-specified, ablation drops them; evaluation rule unchanged. | Reviewer decision O2. |
| A9 | Developers or reviewers tuning against old TEST in side experiments. | M | DEVELOPER_NOTICE.md; frozen hashes verified in CI; no thresholds changed outside the frozen procedure. | Cannot be technically prevented; process control. |

## B. Leakage toward Holdout #2
| # | Path | Sev | Control | Residual |
|---|---|---|---|---|
| B1 | Any pixels, frames, features, tracklets, labels or videos from Holdout #2 touched before freeze (including "quick looks", smoke tests, renderer tests, extraction timing). | H | Sealed registry; no Holdout #2 files in the workspace or repo before freeze; opening writes a ledger entry first; all tests use synthetic or development data only. | Process; custodian attestation recorded at freeze. |
| B2 | Same source video, same event, replays or re-uploads shared between Holdout #2 and development clips. | H | Hash-only near-duplicate and same-event audit by the custodian before freeze; flagged clips are removed or moved to development by the reviewer. | dHash misses replays from other angles/slow motion/overlays (known limitation). |
| B3 | Identity overlap between Holdout #2 and development (e.g. Andrade). | M | Determined from user-supplied names only; recorded as a count at freeze; primary analysis uses all units, overlap strata descriptive; open decision O4 on whether to require identity-disjointness. | Knowing identity names is metadata, not imagery; disclosed. |
| B4 | Threshold or grid selection that sees Holdout #2 scores. | H | Operating points frozen from development cross-fitted data; hashed in the ledger before the one-shot run. | None if followed. |
| B5 | Seeds for episodes/bootstrap chosen after seeing results. | M | Seed derived from the frozen spec hash. | None. |
| B6 | Feature-extraction normalization or any statistic fitted on pooled data including Holdout #2. | M | No learned/pooled normalization exists (frozen preprocessing); a test asserts extraction is per-crop and stateless. | None. |
| B7 | Label leakage: annotators or Claude seeing model outputs or B0 decisions before labels are committed. | H | Blinded annotation, labels committed by hash before V0.6.1 outputs; model outputs never in the annotation package. | Human second annotator needs an independent person (O3). |
| B8 | Test-time use of Holdout #2 data to adapt (online non-target gallery growth, calibration, normalisation). | M | online_N stays empty as in V0.6; no recalibration; secondary reporting only. | None. |
| B9 | Multiple looks: rerunning on Holdout #2 after a bug or an unlucky result. | H | One-shot; bug found after the freeze is recorded, original state preserved, reviewer rules (as in DEVELOPER_NOTICE.md). | None. |
| B10 | Holdout #2 clip names, counts or per-clip details published in the repo or issue tracker before freeze. | M | Repo holds only the frozen spec; Holdout #2 manifest enters the repo only after the one-shot result, and without imagery. | Reviewer decides what may be shared. |
| B11 | Renderer or diagnostic videos built on Holdout #2 before the primary result is frozen. | M | Renderer runs only on the frozen decisions file, after freeze. | None. |
| B12 | The development head trained on episodes containing the same shots later appearing in Holdout #2 (same broadcast). | H | Covered by B2; identity-component grouping for all splits. | Same as B2 limits. |
| B13 | Developer review of the repo revealing which wrestlers or clips the owner is considering for Holdout #2. | L | The spec does not name Holdout #2 contents. | Owner discretion. |
| B14 | Shortcut features (background, overlays, resolution, promotion) letting the head separate wrestlers without anatomy-independent identity cues, making dev look good and failing on Holdout #2. This is generalisation risk, not leakage, but it is the likeliest reason for another DEV-to-TEST drop. | M | Pairing only within a clip; per-stratum and per-source reporting; transfer requirement in operating-point selection. | Cannot be removed by design. |

## C. Statements to confirm at freeze
Custodian attestation that Holdout #2 was not opened by Claude, any developer or any script before the freeze; ledger entries showing the order: spec freeze, implementation freeze, dev selection, operating-point freeze, Holdout #2 opening, primary result.
