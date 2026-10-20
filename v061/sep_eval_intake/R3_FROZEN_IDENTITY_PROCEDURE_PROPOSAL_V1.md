# R3 — PROPOSED PROCEDURE: HOW FROZEN V0.6.1 OBTAINS ACCEPT_A/B ON GENUINELY NEW CLIPS (PROPOSAL; NOTHING RUN)

Status: proposal for reviewer inspection before any new-clip pipeline run. Uses only the existing frozen identity architecture and rules: **no new head training, no threshold change, no tuning, no appearance re-identification, no outcome-informed selection.** Anatomy V1 and the readiness package are unchanged. Holdout #2 and Gemini untouched. Development-only, ANNOTATION-PROVISIONAL. Rights UNRESOLVED; footage stays private.

## 1. Frozen components used (and where they live)
| Component | Frozen source | Note |
|---|---|---|
| Ingest/provenance record | `v06/tools/ingest_clip.py` | required metadata keys; rights UNRESOLVED; clip guidance 45–150 s |
| Preprocessing | `PREPROCESSING_V1.json` (private frozen record, sha256 a115f25a1ad34060…) | crop static bars by recorded cropdetect, scale to height 360 (`scale=-2:360`, bicubic), keep 30 fps and all frames; shot segmentation = ffmpeg scene score > 0.3 on the ORIGINAL file, events closer than 0.25 s merged |
| Detection | `v06/tools/detect_clips.py` | YOLOv8m-pose (local sha256 dbe539ea…), imgsz 960, conf 0.10, stride 3, CPU |
| Tracklets | `v06/tools/build_tracklets.py` | IoU ≥ 0.3 within a shot, conf ≥ 0.3, box height ≥ 50 px at 360p, ≥ 5 detections |
| Label sheets / validation | `v06/tools/make_tracklet_sheets.py`, `validate_labels.py` | label columns tid, person_class, wrestler_id, multi_person_flag |
| Duplicate / leakage audit | `v06/tools/dup_audit.py`, `leakage_audit.py` | counts and pass/fail only |
| Features | `v06/tools/extract_features.py` (backbone `mobileclip_b`, frozen preprocessing hashes) | one crop per candidate detection |
| Seeds / episodes | `v06/tools/phase1_structure.py` (`build_clip`, `select_target_seeds`, `select_referee_seeds`, `EPISODE_SEED=20261018`) under SEED_FEASIBILITY_AMENDMENT_V1 | strict rule: exactly 4 target seeds per identity from ≥ 2 shots, ≤ 2 per shot, ≥ 60 frames apart, box_h ≥ median of eligible detections; 2 referee seeds; seed tracklets excluded from candidates |
| Head | frozen L1 head architecture and recipe (`v06/tools/heads.py`, `phase1_run.train_l1`: Adam lr 0.01, 30 epochs, torch seed 0, deterministic episode order, no auxiliary loss, no ensembling) | see section 4 |
| Decision rule | locked implementation `v061/impl/decision_rule.py` (manifest eb99beb3…) | two-stage rule; operating point see section 4 |
| Anatomy | frozen Anatomical Integration V1 (manifest f5936ce8…), Option W seg, V0.5 ownership, record classifier | unchanged |

## 2. What the frozen code requires of a new clip (these shape the acquisition manifest)
1. Exactly **two named wrestlers (A, B)** whose names are supplied by the owner. (`build_clip` makes one episode per unordered pair of named wrestlers; a third named wrestler would create several episodes and several conflicting A/B decisions for the same tracklet. Clips with other, unnamed wrestlers are fine: label `OTHER_WRESTLER_UNNAMED`.)
2. Each named wrestler needs eligible seed tracklets (`multi_person_flag == 0`) allowing **4 seeds from ≥ 2 shots**, ≤ 2 per shot, ≥ 60 frames apart. If `select_target_seeds` returns INSUFFICIENT_SEEDS the clip is **UNEVALUABLE and yields no identity decisions**. The relaxed 3/2-seed fallback was approved for TRAINING episodes only and is **not** used here.
3. At least one eligible referee tracklet (2 referee seeds; fewer is recorded as FEWER_THAN_2 and is still what the frozen code does).
4. Named wrestlers **absent from the development identity list** (shawn_michaels, shelton_benjamin, randy_orton, seth_rollins, the_rock, triple_h, andrade, rey_mysterio, brock_lesnar, daniel_bryan, kenny_omega; plus Cena development-only, Jeff Hardy excluded) and from Holdout #2 (checked only by the Holdout #2 custodian). Purpose: the identity head must be genuinely out-of-training for the new identities. If the reviewer prefers to allow overlapping identities, the overlap is disclosed per clip and the identity-ACCEPT rates are labelled not out-of-training.
5. Clip guidance from the frozen ingest tool: 45–150 s, native height ≥ 720 preferred (warnings, not rejections). Static end cards/fades are excluded by a metadata frame limit defined BEFORE any model run (as for `b2_videoplayback_2`).

## 3. Step-by-step procedure (each step ledgered; stop on any defect, no silent repair)
- **P0 Intake:** owner supplies clips and the filled acquisition manifest (names and metadata only; names are owner-authoritative; Claude never identifies wrestlers from appearance). Manifest hash ledgered; manifest itself and footage stay private.
- **P1 Ingest + audits:** `ingest_clip.py` per clip; `dup_audit.py` between every new clip and all development clips and within the new set (counts and pass/fail only; a flag removes the clip or reclassifies it by reviewer decision); custodian disjointness check against Holdout #2 (names only; Claude receives only pass/fail and counts); event/broadcast/source/upload disjointness from development clips from the manifest.
- **P2 Preprocess:** frozen PREPROCESSING_V1 rules, per-clip cropdetect value recorded **once, measured not tuned**; exclusion frame limits (if any) fixed before P3.
- **P3 Detect + shots + tracklets:** `detect_clips.py`, frozen shot segmentation, `build_tracklets.py`. Cut-time files are produced by the frozen scene rule (score > 0.3, merge < 0.25 s), not hand-edited.
- **P4 Label tracklets (first-pass):** see section 5 for who/what; sheets by `make_tracklet_sheets.py`; labels validated by `validate_labels.py`; labels file hashed BEFORE features are extracted.
- **P5 Features:** `extract_features.py` with `mobileclip_b`; extraction manifest per `phase1_structure.extraction_rows`.
- **P6 Episodes:** `phase1_structure.build_clip` unchanged, with split tag `D1A_SEP_EVAL` (a new tag; it never enters any training set). Record per clip: status OK / UNEVALUABLE and reasons. UNEVALUABLE clips are reported and dropped; nothing is repaired or re-drawn.
- **P7 Head and decisions:** see section 4: apply the designated frozen head to each OK episode with the frozen scoring code, then the frozen two-stage rule at the frozen operating point; write `decisions_<clip>.csv` in the existing format.
- **P8 Anatomy:** the frozen Anatomical Integration V1 pipeline run on the new clips exactly as in AR1 (Option W seg on stride-3 pose frames; V0.5 ownership; record classifier; carry); no parameter changes. ASSIGNED_A/B rows are the candidate set for the separated-body evaluation.
- **P9 Feasibility count:** `v061/sep_eval/feasibility_count.py` on the new rows (counts only). Returned to the reviewer. **Stop.** Sampling, images and reviews happen only after separate authorization.

## 4. The head and the operating point (the one genuinely open item)
Facts: DR1 trained five fold heads in memory (one per held-out identity component) and saved decisions, not weights; the all-development "final head" was deliberately **not** run (DR1 D8; reviewer OGR16: no final head).
- **H-a (recommended): reproduce one existing frozen fold head deterministically, with an outcome-blind designation rule.** Rule: among the five frozen DR1 fold heads choose the one trained on the largest number of training episodes (25; the Andrade-held-out head has 20); ties broken by lexicographic component id. That is the head held out for `brock_lesnar` (training = the four other components, 25 episodes). The designation is fixed here by arithmetic on the frozen DR1 training record (`DEVRUN_RESULT_V1.json`, sha256 98ebb67ed7553178…), not by any score or outcome. **Parity gate before first use:** re-running the frozen training code on the frozen training-episode list and features must reproduce, bit-for-bit, the frozen DR1 out-of-fold decision rows for that fold's held-out clip (private `OOF_DECISIONS_PRIVATE.csv`, sha256 8a64fcbb7f98991b…). If parity fails: STOP, record a defect, no head is used.
  - This is reproduction of an existing frozen artifact with identical code, data, seed and order, not new training.
  - Honest caveat: one fold head is a single arbitrary frozen member of a family; its behaviour on new clips is not representative of "the" V0.6.1 head, and identity ACCEPT rates are descriptive only.
- **H-b (alternative, needs explicit reviewer authorization):** the all-development head the spec froze for the one-shot run. Not recommended now because OGR16 withheld a final head.
- **H-c (prohibited):** averaging or ensembling the five heads, selecting a head by its performance on any clip, or training any new head.
- **Operating point:** the frozen DR1 selection for L1, **tau_g = 0.9, delta = 0.10** (pooled out-of-fold development selection under spec_v4 03 §3), used unchanged; no re-selection, no per-clip adjustment.
- **Fail-closed:** non-finite or out-of-range probabilities give REJECT_NONTARGET with numeric_failure (locked rule). A new clip with very low identity-ACCEPT coverage is reported as such; no rule or threshold is relaxed to raise yield.

## 5. First-pass labels (second open item)
`build_clip` consumes first-pass labels for every retained tracklet (WRESTLER with wrestler_id / REFEREE / RINGSIDE_STAFF / SPECTATOR / OTHER_WRESTLER_UNNAMED / UNLABELABLE, plus multi_person_flag). They determine seeds and which tracklets become candidates; unlabelled tracklets would get no identity decision. Frozen precedent: first-pass labels by the developer (Claude) from contact sheets, using only owner-supplied names and reference identification (never appearance-based inference), marked non-independent.
- **R3-L1 (recommended):** same precedent. Owner provides, per clip, the two names and one or more reference timestamps/boxes where each named wrestler is identified; Claude labels all tracklets from the sheets; **the owner audits 100% of the seed detections** (4 + 4 + 2 per clip, shown as crops) before P5, and a wrong seed voids that clip (no repair beyond owner correction recorded in the ledger). Labels are ANNOTATION-PROVISIONAL and are used only for identity bookkeeping; they never enter the ownership gate.
- **R3-L2:** owner labels all tracklets (heavier burden; more independent).
- Either way the independent human primary reviewer must not be a labeller for the same clips.
- Truth labels are used afterwards only for secondary identity descriptives (non-wrestler emission, A/B swaps), never to choose clips or rows.

## 6. Rules that prevent outcome-informed selection
- No clip is added, dropped or re-processed because of its identity coverage, eligibility yield or anything seen after P7, except the pre-specified rules above (duplicate/disjointness audit failure, UNEVALUABLE seeds, owner seed-audit failure).
- If total yield remains insufficient after ~18 clips, **criteria are not relaxed**; the evaluation reports INCONCLUSIVE_DATA or acquisition is extended only under a new reviewer authorization before any sampling.
- Operating point, head designation and the sampling seed rule are fixed before P0 data exist.

## 7. Items for reviewer ruling
H1 Approve H-a (and the designation rule and parity gate), or choose H-b. L1 Approve R3-L1 (Claude first-pass + 100% owner seed audit) or R3-L2. I1 Approve identity-disjointness from the development list (section 2.4) or allow disclosed overlap. S1 Confirm that `D1A_SEP_EVAL` clips never enter training and that no head is retrained on them. D1 Confirm the thin P7 driver may be written (calls frozen functions only; synthetic-tested; parity gate included) after approval.
## 8. Known limits
Single fold head as the identity engine; identity unvalidated (MODIFY); first-pass labels non-independent; 30 fps / cut-rule portability to new sources unchecked; the procedure yields the ASSIGNED candidate set only. Nothing here validates identity or anatomy.
