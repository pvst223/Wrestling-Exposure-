# V0.6.1 → ANATOMICAL INTEGRATION: PROSPECTIVE READINESS PACKAGE (V1)

STATUS: PLANNING ONLY. Nothing here was run on real video. No YOLO-seg/pose inference, no cross-fitted decisions consumed, no Holdout #2 access, no Gemini transmission, no outreach, no exposure metric.
Identity layer verdict carried forward verbatim: **MODIFY — sufficient to proceed to anatomical-integration diagnostics; NOT validated; NOT exposure-ready.** R3 PARKED · R4 UNMET · ANNOTATION-PROVISIONAL.
Locked V0.6.1 implementation (manifest eb99beb3…), spec_v4, V0.6 Phase 1, Gemini procedure v1: unchanged. Pipeline: IDENTITY → ANATOMICAL OWNERSHIP → POSE/LANDMARKS → TEMPORAL TRACKING → ANATOMICAL DIAGNOSTIC MP4.
Governing sentence: **Correct anatomical ownership is not evidence of correct wrestler identity.** The two are carried as separate, never-merged fields in every record.

## 1. Identity → ownership interface
- Identity output is tracklet-candidate level (clip, shot, tracklet id → p_A, p_B, p_NT; two-stage rule → code, g, q, numeric_failure). Ownership/pose is per-skeleton-detection level (clip, frame, det index).
- Adapter (NEW, to be written after audit): each skeleton detection inherits its tracklet's identity record via the frozen tracklet→(frame, det) index. Fields passed unchanged: `identity_code` ∈ {ACCEPT_A, ACCEPT_B, ABSTAIN_AMBIGUOUS, REJECT_NONTARGET}, `numeric_failure`, `g`, `q`, `tau_g`, `delta`, `fold`. Only **out-of-fold (cross-fitted) decisions** are consumed (no final all-development head exists or will be trained). Detections with no identity row → `NO_IDENTITY_EVAL`.
- Direction of information: identity → ownership is **metadata only**. Ownership computation (masks, landmarks) never reads identity; identity never reads ownership. They are joined only in the record classifier (§2).

## 2. State propagation (reference: `contract.py`, exhaustively tested)
Precedence, first match wins (fail closed): `NO_POSE` > `INVALID_NUMERIC` > `WITHHELD_MIXED_BODY` > `WITHHELD_OWNERSHIP_UNCERTAIN` / `_NOT_EVALUATED` > identity class.
| identity | ownership SINGLE_BODY_SUPPORTED | MIXED | UNCERTAIN / NOT_EVALUATED | numeric_failure |
|---|---|---|---|---|
| ACCEPT_A | ASSIGNED_A (flag IDENTITY_UNVALIDATED) | WITHHELD_MIXED_BODY | WITHHELD_OWNERSHIP_* | INVALID_NUMERIC |
| ACCEPT_B | ASSIGNED_B (flag IDENTITY_UNVALIDATED) | WITHHELD_MIXED_BODY | WITHHELD_OWNERSHIP_* | INVALID_NUMERIC |
| ABSTAIN_AMBIGUOUS | UNASSIGNED_IDENTITY_AMBIGUOUS (neutral skeleton, never A or B) | WITHHELD | WITHHELD | INVALID_NUMERIC |
| REJECT_NONTARGET | NONTARGET (no landmarks) | WITHHELD | WITHHELD | INVALID_NUMERIC |
| NO_IDENTITY_EVAL | NO_IDENTITY_EVAL (no label) | WITHHELD | WITHHELD | — |
Rules: (a) a plausible skeleton never upgrades ABSTAIN to A/B; (b) `identity_state_passthrough` and `ownership_state_passthrough` are preserved in every record and the sidecar; (c) ASSIGNED_* always carries the persistent flag "identity unvalidated (MODIFY)" and its q-margin; (d) numeric_failure rows are never assigned and are counted separately.

## 3. Ownership logic and vetoes
Reused unchanged (§7): mask-based per-landmark classes OWN_ONLY / CONTESTED / OTHER_ONLY / OUTSIDE; mask cues (opponent landmarks in owner mask, UNEXPLAINED mask share, bones spanning instances / leaving mask); `decide()` → SINGLE_BODY_SUPPORTED | MIXED_BODY_SUSPECTED | OWNERSHIP_UNCERTAIN; geometric cross-body cues from `integrity_v05` (LIMB_TOO_LONG, TORSO_SIDES_ASYMMETRIC, SHARED_JOINT_CONFLICT, TEMPORAL_JOINT_JUMP, …) force MIXED. All thresholds are the V0.5 values in `config_v05.json`; **none retuned**.
Vetoes only (V0.5 principle kept): evidence can lower ownership to UNCERTAIN/MIXED; nothing (appearance, identity, temporal coherence) can raise it.
**Disclosed capability loss:** V0.5's appearance-based vetoes (PART_IDENTITY_CONFLICT, APPEARANCE_SEGMENT_CONFLICT) need manually-seeded per-wrestler appearance models not available for the dev clips; they are DISABLED. Consequence: the residual V0.5 failure class (two bodies in one merged mask; the reason V0.5 failed Holdout #1) has *fewer* independent detectors here. Proposed a-priori compensation (uncalibrated, for reviewer approval): a conservative merge guard — if ≥2 non-duplicate skeletons exist in a shot within MERGE_LOOKBACK (10) source frames and the current frame has one skeleton whose box overlaps the union of the earlier boxes at IoU ≥ MERGE_IOU (0.3), ownership is forced OWNERSHIP_UNCERTAIN for up to MERGE_PERSIST_MAX_FRAMES (150) or until two separate skeletons reappear. Constants are the V0.5 config values; the guard is new code and is not a validated detector.
Mixed-body / uncertain cases fail closed: landmarks are **withheld** (not drawn as skeleton), the box is shown with the reason code, and the frame is excluded from every tracking-quality numerator.

## 4. Pose model and landmark representation
YOLOv8m-pose (COCO-17), weights sha256 `dbe539ea…3c90` (recorded in the frozen Phase 1 manifests; preflight must re-verify, else STOP). Primary pose source = the **frozen cached detections** (`dets_*.pkl`: box, conf, kp (n,17,2), kpc), which exist on **every 3rd source frame only** (e.g. frames 0,3,6,…). Landmarks used for ownership: nose, shoulders, elbows, wrists, hips, knees, ankles (V0.5 `LMS`); display confidence ≥0.7 per V0.5 `DISPLAY_KP_CONF`. Instance masks: YOLOv8m-seg (sha `51fa7e5e…`), which **do not exist for the dev clips** and must be extracted (same frames, via unchanged `seg_extract.py`) in the execution phase after a registered, hashed run script. No fine-tuning, no new model.

## 5. Temporal tracking, reacquisition, camera cuts
- Shot boundaries: the frozen shot indices used by the identity layer. The V0.2+ camera-event classifier (`cuts_events.py`, CUT / PHOTOMETRIC_REGISTERED / TRANSIENT / SAME_SCENE_RETURNS) is run as an independent cross-check; disagreements are **reported, not reconciled**.
- Within a shot: tracklet continuity is already encoded in the frozen tracklets; no new association is invented. Temporal pose checks use the unchanged `integrity_v03.temporal_check` (applicable only when frame gap ≤ TEMPORAL_MAX_GAP).
- Carry: visualization only, ≤3 source frames after a MEASURED ASSIGNED_* anchor, never across a cut, never from a non-assigned anchor, never interpolated, never counted in a metric (`contract.carry`, tested). With stride-3 pose this means each pose frame is shown for itself + ≤2 carried frames. **No V0.5 6-frame COM prediction is used** (it served COM, which is out of scope).
- Cut / reacquisition: at a CUT all anchors and carries reset. No identity or ownership is inherited across a cut; a new shot starts from its own identity decision and its own ownership evaluation. Reacquisition after loss within a shot requires a fresh identity ACCEPT **and** fresh SINGLE_BODY_SUPPORTED; no sticky labels.

## 6. Fail-closed summary
Withheld (no landmarks emitted): MIXED_BODY_SUSPECTED, OWNERSHIP_UNCERTAIN, OWNERSHIP_NOT_EVALUATED (no masks/too few landmarks), numeric failure, merge-guard active. Neutral (landmarks shown, no label): ABSTAIN_AMBIGUOUS with SINGLE_BODY. Nothing is "defaulted to the more likely wrestler".

## 7. Reuse and provenance (exact hashes: `REUSE_PROVENANCE.json`)
Reused **byte-identical** (copies already in `versions/holdout1/`, hashes match): `ownership_v05.py` 8cec4f1a…, `integrity_v05.py` 0702b568…, `integrity_v03.py` 843d64b2…, `integrity_v04.py` 8799cc3d… (only if part_check is needed; appearance-dependent calls disabled), `cuts_events.py` 184a649b…, `seg_extract.py` 58f98624…, `config_v05.json` 7e511eec…. Models: yolov8m-pose dbe539ea…, yolov8m-seg 51fa7e5e…
Present but **NOT reused**: `track_v05.py` (monolithic; fuses V0.5 appearance identity, COM eligibility and prediction), `reid_v05/appearance/embed_*` (V0.5 identity — superseded by V0.6.1 identity), `com_model.py` (COM = exposure-adjacent, out of scope), `render_v05.py` (layout concepts only; new renderer, §10).
Honest note: V0.5 ownership code was audited on one clip in-sample and V0.5 failed Holdout #1; "reused" means unchanged code, **not** validated behaviour.

## 8. Changes versus the previously audited ownership implementation
1. NEW identity→detection adapter (§1). 2. NEW record classifier (§2) replacing V0.5's identity/ownership/COM fusion. 3. Appearance vetoes DISABLED (§3). 4. NEW merge guard (§3), approval requested. 5. COM, prediction (≤6 frames), exposure fields REMOVED. 6. Evaluation on OOF V0.6.1 decisions instead of V0.5 seeded identity. 7. Ownership thresholds unchanged. Everything else in ownership/integrity is byte-identical.

## 9. Prospective metrics (descriptive; none exposure-related; none a probability or validation)
Units are (clip, shot); counts and exact Clopper–Pearson CIs where a proportion is reported; shot-cluster caveat stated.
M1 record-class distribution per clip/shot/identity-code (full joint table identity × ownership). M2 veto rate: share of ACCEPT_A/B frames withheld by ownership. M3 identity-ownership disagreement counts (ACCEPT + MIXED/UNCERTAIN; ABSTAIN + SINGLE_BODY). M4 label-flip count: A↔B switches inside a continuous run without a cut (should be ≈0; each reported). M5 temporal pose consistency: per-joint displacement / body-scale between consecutive measured frames, and TEMPORAL_JOINT_JUMP count. M6 landmark coverage: share of measured frames with ≥N confident landmarks. M7 cut cross-check: shot-index vs classifier disagreements. M8 carried-frame share (visualization only). M9 **status-blind human review** of a stratified sample of ASSIGNED_* frames (and a matched sample of withheld frames): does the drawn skeleton belong to one single person? single reviewer = ANNOTATION-PROVISIONAL, R4 unmet; report each contaminated emission individually; no accuracy claim. Pass/fail thresholds are **not pre-set by me**; reviewer is asked to set descriptive reporting floors before execution (open item Q1). No result is optimized toward KEEP.

## 10. Anatomical MP4 renderer design (new `render_anat.py`, not in locked impl)
30 fps, full source frame left (never cropped), 420 px QC panel right (V0.5 layout concept). Encoding by text + shape + line style, not colour alone:
| record | draw |
|---|---|
| ASSIGNED_A / B (MEASURED) | solid skeleton, green / magenta, label "A"/"B", badge [M], persistent banner "IDENTITY UNVALIDATED"; panel: q, g, tau_g, delta |
| UNASSIGNED_IDENTITY_AMBIGUOUS | white dashed skeleton, label "A|B ?" , q shown |
| NONTARGET | thin grey box "NT", no skeleton |
| INVALID_NUMERIC | yellow box "NUM-FAIL" |
| WITHHELD_MIXED_BODY | red box with X "MIXED — withheld" |
| WITHHELD_OWNERSHIP_UNCERTAIN / NOT_EVALUATED | hollow orange box "OWN ?" with reason code, no skeleton |
| CARRIED (≤3 fr) | hollow dotted skeleton, tag "CARRIED – viz only" |
| NO_POSE | nothing drawn; panel "NO POSE" |
| camera cut | cyan banner 8 frames, all anchors reset |
No COM marker, no distance/speed/impact overlay. Sidecar JSON per frame: record_class, identity/ownership passthrough, reasons, MEASURED/CARRIED/NONE, cut flags; summary counts; source/ output sha256. Per-class legend always on panel.

## 11. Clips and why
Primary set (4): `b1_orton_rollins_wm31`, `b2_batch2_clip_condensed`, `b2_videoplayback_2`, `b2_videoplayback_5` — the clips that have cross-fitted OOF identity decisions and an existing identity MP4 for side-by-side comparison. Not used unless reviewer approves: `b1_hbk_raw_20050502`, `b1_rock_hhh_judgmentday2000` (their OOF decisions exist only inside the thin-evidence folds; adding them is a scope change). Excluded: Jeff Hardy, Holdout #2, TEST. Cena stays development-only. Rights UNRESOLVED: outputs stay private, no redistribution, no footage/frames in GitHub.

## 12. Synthetic/unit tests required before any real-video execution
Implemented now (`tests/test_contract.py`, 12 tests, pass): exhaustive identity×numeric×ownership×pose truth table (assignment iff all gates pass); ABSTAIN never assigned; numeric failure invalid; MIXED vetoes ACCEPT; uncertain ownership withheld; nontarget no landmarks; carry ≤3, no carry across cut / from non-assigned anchor; passthrough preserved; unchanged V0.5 ownership module on synthetic masks (single body → SINGLE; skeleton straddling two masks → MIXED/UNCERTAIN; two skeletons in one merged mask → not SINGLE); reused-file hashes.
Required to be written *after audit and before execution*: adapter test (tracklet→detection mapping, missing rows → NO_IDENTITY_EVAL); merge-guard test; stride-3 carry test; renderer legend/class-coverage test (every class renders distinctly, sidecar matches pixels); preflight tests (pose/seg hash, locked manifest, exactly-once result); cut-reset test; determinism test (same inputs → identical sidecar).

## Open items for reviewer
Q1 descriptive reporting floors for M2/M9. Q2 approve/modify merge guard (§3). Q3 confirm 4-clip primary set. Q4 confirm stride-3 frozen pose as primary (vs new full-rate pose extraction, which would need its own registration). Q5 confirm seg extraction on dev clips as the first execution step.
No real-video anatomical integration will run until the reviewer authorizes it.
