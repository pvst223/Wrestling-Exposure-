# PHASE1_IMPLEMENTATION_CLOSURE_V1

Status: specification/implementation record written under the reviewer ruling "PROSPECTIVE PHASE-1 IMPLEMENTATION CLOSURE AUTHORIZED". Phase 1 is NOT authorised. PREREGISTRATION_V3 is unchanged. Study status: ANNOTATION-PROVISIONAL; the preregistered human reliability gate is NOT SATISFIED AS SPECIFIED (deviation X1, return R1). Dependency B resolved. OSNET_INPUT_CLOSURE_V1 ratified as written. No experimental backbone features, training, B0/L1 decisions, thresholds, FTA/coverage, comparisons, test results or adjudication of the 86 disagreements were produced. Only structural manifests (frame keys, tracklet-detection indices, seed eligibility) were read from frozen detections/tracklets/first-pass labels.

## A. Implemented as ruled
- B1: `tools/extract_features.py` (v2) iterates the sorted ACTUAL frame keys of the frozen detection dict; it never indexes a missing key, synthesises detections, re-runs the detector or alters detections. Sparse-key selftests in `selftest6.py`.
- B2: explicit adapters `mobileclip_b` (V0.5 loader, [0,1], no normalisation), `dinov2_vits14` (official code, strict load, no registers, 224x224, ImageNet mean/std, CLS after final norm, 384-d), `osnet_x1_0` (official osnet.py, strict load, OSNET_INPUT_CLOSURE_V1: PIL fromarray -> BILINEAR resize W128xH256 -> ToTensor -> ImageNet mean/std -> 512-d). Selftest proves the OSNet preprocessing is bit-identical to the official torchreid test pipeline. Disclosed limitation preserved: the square letterbox is anisotropically resized, unlike OSNet's training crop geometry.
- B3: extraction occurs only on frame keys present in each clip's frozen detection dict (vp2 exclusion frames >= 1934 absent). Materialised `EXTRACTION_FRAME_MANIFEST_V1.csv` (13,188 rows). Detections extracted within those frames are the retained-tracklet detections (V3 section 3: one crop per retained tracklet detection).
- B4: `SEED_EPISODE_MANIFEST_V1.json`: seed 20261018; 4 target seeds from 4 distinct shots, pairwise >= 60 frames (2 s at 30 fps), box height >= that clip/target's median of eligible detections; 2 referee seeds (distinct shots where feasible); unordered pairwise episodes for every 2-combination of named wrestlers in a clip, A = lexicographically smaller identity, seeds selected once per identity and reused across pairs; seed_N = referee seeds + seeds of named wrestlers that are NON-TARGET for the pair; online_N empty; episodes lacking 4 qualifying seeds for A or B are UNEVALUABLE and not relaxed.
- B5: exhaustive deterministic TRAIN episodes (all OK pairs in TRAIN clips; candidates sorted by tracklet id then frame; full-batch per episode; episodes in id order; no shuffling or weighting; heads.train unchanged: Adam lr 0.01, 30 epochs, seed 0 primary, 128-d linear, no ensemble, no auxiliary losses). heads.py required no sampling choice.
- B6/B7: `tools/phase1_run.py` (grids, c*, DEV-only selection, backbone selection, unit tables, paired sign test, criteria, outcome logic, LOCO, seed 1-3 variance) and fixed L1 margin 0.0, L1 score = max(pA,pB) before the floor. `tools/authorization_guard.py` makes extraction and the runner fail closed until a reviewer BAKEOFF_AUTHORIZATION ledger entry matches a READY manifest. All logic selftested synthetically (`tools/selftest6.py`).

## B. Closure decisions that go beyond the literal ruling (non-performance-based; flagged for reviewer ratification at re-audit)
- D1 Seed eligibility excludes tracklets with multi_person_flag = 1 (a seed crop containing two people is not an identity prototype; matches the annotation package practice). Chosen before the feasibility result was seen.
- D2 Seed removal is at TRACKLET level (V3 section 3 "seed tracklets are removed"), which removes the selected seed detections; for each episode, tracklets containing ANY seed used by that episode (A, B or N seeds, including referee seeds and third-wrestler seeds) are excluded from that episode's candidates, to prevent trivial self-match.
- D3 Referee seeds have no median-height rule (V3 imposes it on targets only). A third wrestler with fewer than 4 qualifying seeds contributes the seeds it has to seed_N.
- D4 Unit aggregation across pairwise episodes: false accept = OR across episodes; target coverage = mean over the episodes in which the unit is a target. (On the current data every clip has exactly two named wrestlers, so each clip yields one episode and this rule is inert; it is selftested.)
- D5 Matched coverage: c* is per backbone (largest of .5,.4,.3,.2,.1 reached by >= 1 DEV point of both methods; none -> NO JOINT COVERAGE -> INCONCLUSIVE-DATA for that backbone). Backbone selection uses a COMMON c* (largest level jointly reachable by every backbone that has one) so B0 dev FTA is compared at the same coverage; ties by osnet_x1_0, dinov2_vits14, mobileclip_b. V3 says "c*" in the singular without defining it across backbones.
- D6 Outcome precedence INCONCLUSIVE-DATA > KEEP > KILL > MODIFY (V3 is silent; e.g. b=4,c=0 with only 4 baseline false-accept units satisfies KEEP criterion 1 and also the INCONCLUSIVE condition). With the annotation gate NOT satisfied, KEEP/KILL are capped at MODIFY (label "MODIFY (ANNOTATION-PROVISIONAL)"); the uncapped class is also reported.
- D7 LOCO (secondary only): components = identities linked across clips; thresholds for each fold set in-sample on the training fold with the same c*/lowest-FTA rule; run only after the primary result file exists.
- D8 If no evaluable TRAIN, DEV or TEST episode exists, nothing is trained or evaluated and the result is INCONCLUSIVE-DATA (V3: "analysis cannot be completed").

## C. Structural feasibility finding (READY-relevant; not a performance result)
Under the literal seed rule the structural manifest gives (episode status: seeds obtained / 4):
| split | clip | identity seeds | episode |
|---|---|---|---|
| train | b1_hbk | shawn_michaels 2, shelton_benjamin 3 | UNEVALUABLE |
| train | b1_orton_rollins | randy_orton 4, seth_rollins 3 | UNEVALUABLE |
| train | b1_rock_hhh | the_rock 1, triple_h 1 | UNEVALUABLE |
| dev | b2_videoplayback_2 | brock_lesnar 4, daniel_bryan 4 | OK |
| test | b2_batch2_clip_condensed | andrade 4, rey_mysterio 4 | OK |
| test | b2_videoplayback_5 | andrade 3, kenny_omega 3 | UNEVALUABLE |
Consequence: ZERO evaluable TRAIN episodes, so L1 cannot be trained from the TRAIN split and the primary experiment cannot be completed as preregistered (D8: INCONCLUSIVE-DATA). Variant check (structural only, reported not adopted): without D1 (multi-person tracklets allowed as seeds) the vp5 test episode and the HBK/Shawn identity become obtainable, but Benjamin and Rollins still yield only 3 seeds each, and Rock and HHH have a single shot each, so none reaches 4 qualifying seeds, so all TRAIN episodes remain UNEVALUABLE. The shortfall is a property of the acquired data (too few distinct shots per training identity) and cannot be fixed by an implementation choice; relaxing the seed rule or the training-data requirement would be a prospective amendment requiring reviewer decision.

## D. Hashes
Recorded in the audit ledger entry CL1 and in FINAL_READY_MANIFEST_V2.json.
