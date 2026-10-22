# Stage-D BUILD return — descriptive and integrity verification (V1)

Prepared by the project builder (Claude) from the three files returned by the owner. **This is not the independent audit**; the AUDIT VERDICT is reserved for the independent reviewer. Aggregates only: no per-shot labels, footage, clips or frames are stored in the repository. ANNOTATION_PROVISIONAL; R4 unmet; single non-independent labeller; development/futility gate only; target is broadcast scene/time (X2), not wrestler workload. No exposure-validity claim. CHECK untouched (0 labels, unopened); no classifier constructed, fitted, tuned or inspected.

## 1. Received files (hashes only are recorded in the ledger)
build_return.json (sha256 in ledger ANA28); labels_build.csv 28,004 bytes; match_marks_build.csv 954 bytes.

## 2. Integrity verification (recomputed independently from the supplied files)
| check | result |
|---|---|
| n_shots | 169 (labels file has 169 rows) |
| exported labels vs frozen BUILD manifest `d0c73ca1…99aaf` | all 169 rows identical (shot_id, source_id, t_start_s, t_end_s), same order |
| effective-set SHA256 | recomputed `sha256(labels_build.csv + "\n--MARKS--\n" + match_marks_build.csv)` = `4a002f5dbd31328a7e4dfacd8e43b2a88cecc8157a5f35875dacc8ad03930e85` = value in build_return.json = value reported by the export |
| protocol_version | every label row and mark row carries `0b6c8740…dad9`, equal to build_return.json |
| line endings | LF only (no CRLF) |
| category counts / durations / confidence (overall and by label) / flags / UNKNOWN reasons / U_ref | recomputed from labels_build.csv; all equal the build_return.json values |
| correction | build_return.json: n_corrections 1, shot b1_orton_rollins_wm31_s000, UNKNOWN→LIVE_ACTION, TRANSCRIPTION_ERROR, corrections_chain_ok true. Exported row for that shot: LIVE_ACTION / empty reason / HIGH / empty flags / empty note (consistent with the correction overlay; labelled_at_utc keeps the original 2026-10-21T23:35:50Z) |
| protocol_violations_detected | event_chain_ok true; manifest_tamper false |
| marks | 5 rows, all `NO_D`, start/end empty, evidence notes as scripted (reviewer ruling D2); the match's end is not exposed |
| submission timestamps | monotonic, 2026-10-21T23:35:50Z to 2026-10-22T00:36:52Z; gap between submissions median 17 s (min 8 s, max 146 s) |
| notes | no label has a note |

**Not verifiable from the supplied files:** the original (pre-correction) labels CSV hash `23fd624d…f266`; events_jsonl_sha256 `9717a1f7…061d`, event_chain_last_prev and n_events (2) internals; the content of corrections_log.jsonl itself (only the summary in build_return.json was supplied); the manifest hash at SET_OPEN (the exported rows were compared to the frozen manifest instead). The owner's earlier terminal checks (Step 1, 2a, 2b) are reported, not re-run here.

**Discrepancies between build_return.json and the exported files: none found.**

## 3. Descriptive BUILD statistics (169 shots, 638.233 s)
| label | shots | duration s | share of duration |
|---|---|---|---|
| LIVE_ACTION | 155 | 558.400 | 87.5% |
| CLOSE_UP | 8 | 24.100 | 3.8% |
| NON_MATCH | 1 | 2.033 | 0.3% |
| REPLAY | 0 | 0.000 | 0% |
| UNKNOWN | 5 | 53.700 | 8.4% |

UNKNOWN by reason (count / seconds): PIP_AMBIGUOUS 4 / 49.2; CLOSEUP_BORDERLINE 1 / 4.5; all other reasons 0. **BUILD U_ref = 53.7 / 638.233 = 0.08414** (descriptive only; triggers no outcome).
Confidence: HIGH 156, MEDIUM 11, LOW 2. By label: LIVE_ACTION H149/M5/L1; CLOSE_UP H4/M3/L1; NON_MATCH M1; UNKNOWN H3/M2. Flags: BOUNDARY_ISSUE 1 shot; NO_D 1 shot (shot-level; see 4.6). No other flags.
By source (shots / seconds / label counts / U_ref): b1_orton_rollins_wm31 11 / 37.000 / LIVE 8, CLOSE_UP 2, UNKNOWN 1 / 12.2%; b2_batch2_clip_condensed 40 / 120.000 / LIVE 34, CLOSE_UP 5, NON_MATCH 1 / 0%; b2_videoplayback_2 24 / 64.467 / LIVE 23, CLOSE_UP 1 / 0%; b2_videoplayback_5 9 / 119.567 / LIVE 9 / 0%; rr_balor_full (151.367–448.567 s) 85 / 297.200 / LIVE 81 (248.0 s), UNKNOWN 4 (49.2 s) / **16.55%**. Shot duration: median 2.2 s, min 0.267 s, max 39.367 s.
Marks: all five sources `NO_D`.

## 4. Observations for the reviewer (builder's reading; classification of each is the reviewer's decision)
1. **Integrity:** nothing found that blocks classifier construction; every verifiable item is consistent (section 2).
2. **No REPLAY in BUILD (descriptive property, with a design implication).** Zero REPLAY shots: P3 (replay leakage) cannot be exercised and the permitted replay indicator cannot be informed or tested by BUILD labels.
3. **Strong LIVE dominance (a property of the sample, not a defect).** A degenerate rule that calls every shot LIVE would show a duration-weighted LIVE/not-LIVE disagreement of 4.47% on the reference-decidable BUILD duration (26.133 s / 584.533 s), i.e. already within P1 ≤ 10%. P1 on BUILD therefore has little discriminating power against that baseline. Only 9 non-LIVE decidable shots (8 CLOSE_UP, 1 NON_MATCH) exist to inform at most 3 features and 5 thresholds.
4. **Source heterogeneity.** In the match segment the reference has only LIVE (81) and UNKNOWN (4); all 8 CLOSE_UP shots and the only NON_MATCH shot come from the short development excerpts (a different, edited production regime).
5. **PIP prevalence and the reference-adequacy rule.** In the match segment, reference UNKNOWN (4 PIP_AMBIGUOUS shots, 49.2 s) is 16.55% of its 297.2 s. The 10% REFERENCE_INCONCLUSIVE rule applies to the CHECK set, which is entirely match footage; the aggregate BUILD 8.41% is diluted by the short clips. This is a BUILD-derived observation about a risk, not information about CHECK, which has not been accessed.
6. **Shot-level `NO_D` flag on one shot (b2_batch2_clip_condensed_s035).** `NO_D` is defined for source marks; at shot level it has no defined effect on category or P1–P4. It may be an accidental flag tick. Labels are final-on-submission and the correction path is clerical only; no correction has been requested or made. Reported as a descriptive anomaly.
7. **Reliability relabel not yet done** (≥ 7 days after BUILD completion; deterministic 10% sample = 17 shots, seed 20261021). One `BOUNDARY_ISSUE` shot (b2_batch2_clip_condensed_s001) is recorded; boundaries remain frozen.

## 5. What classifier construction is prospectively allowed to use (frozen design, unchanged)
Only the frozen BUILD labels; frozen shot/video information allowed by Exposure V1 (frozen shot boundaries and frozen person-detection boxes); at most 3 shot-level features plus a replay indicator; at most 5 thresholds; deterministic rule; one revision round only; no identity, skeleton/anatomy, ownership, masks, merge guard, carried rows, COM or physical distance/speed fields; CHECK stays sealed and unavailable until the BUILD-derived rule hash is frozen. Nothing is constructed or proposed here.

STOP for independent reviewer audit. No classifier, rule, feature or threshold work is authorized by this document.
