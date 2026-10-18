# SEED_FEASIBILITY_AMENDMENT_V1

Status: PROSPECTIVE protocol amendment layered on the frozen protocol. PREREGISTRATION_V3 is NOT modified (sha256 3e40f5ec3aea93539daeacdac7cb0bf1b4cfadbd90fb7de245641160c5c4ab78); this amendment supersedes only the target-seed shot-diversity clause of V3 section 3 for the bake-off, and the reviewer-ratified D1-D8 of PHASE1_IMPLEMENTATION_CLOSURE_V1 as clarified below. Authority: independent reviewer ruling "PROSPECTIVE SEED-FEASIBILITY AMENDMENT AUTHORIZED". Recorded in the audit ledger as AM0 (before any amendment work), at 2026-10-18T05:49:01Z. Phase 1 NOT authorised; ANNOTATION-PROVISIONAL; human reliability gate NOT SATISFIED AS SPECIFIED.

## 1. Rule
OLD (V3 section 3): 4 qualifying target seed detections from 4 distinct shots, >= 2 s apart, box height >= clip/target eligible-detection median.
NEW (uniform across TRAIN, DEV and TEST; never TRAIN-only):
- exactly 4 target seed detections;
- drawn from at least 2 distinct shots; no shot contributes more than 2 of the 4;
- selected seed detections pairwise >= 2 s (60 frames at the frozen 30 fps) apart;
- the box-height >= clip/target eligible-detection median criterion, multi-person-tracklet exclusion (D1), deterministic seed 20261018 and tracklet-level seed removal (D2) are unchanged;
- no seed is chosen using embeddings or model performance;
- an identity that cannot supply 4 detections satisfying this rule makes every episode containing it UNEVALUABLE; no further relaxation.
Selection algorithm (deterministic, performance-free): the qualifying detections of each shot are shuffled with random.Random(f"20261018|clip|identity|target") after sorting; shots are shuffled the same way; candidates are ordered round-robin by rank within the shuffled shots (rank 0 of every shot, then rank 1, ...); the first 4-subset in depth-first order that satisfies all constraints is selected (exhaustive search, so UNEVALUABLE is declared only when no valid 4-subset exists).
Referee seeds are unchanged (2 seeds, distinct shots where feasible, no median rule).

## 2. Rationale (recorded verbatim)
"The original four-distinct-shot seed requirement proved structurally infeasible before feature extraction or model evaluation: zero TRAIN episodes could be constructed. The amendment preserves four identity-reference detections and requires representation from multiple shots while relaxing only the number of distinct shots from four to at least two. It was adopted prospectively, before any experimental feature extraction, training, threshold selection, model comparison, or test-performance evaluation, and therefore was not selected in response to model performance."

## 3. Rulings on D1-D8 (reviewer)
D1 ratified. D2 ratified. D3 ratified with clarification (referee seeds need no median criterion; a third named wrestler contributes frozen identity seeds to seed_N only when NON-TARGET for the active pair; no evaluation-derived or online-adapted examples in seed_N). D4 ratified (kept prospectively although inert). D5 ratified (c* within backbone first; a backbone with no joint operating point down to 0.10 is INCONCLUSIVE and does not determine the common c*; fixed tie order OSNet, DINOv2, MobileCLIP-B). D6 AMENDED: precedence INCONCLUSIVE-DATA > substantive KEEP/KILL/MODIFY; the runner reports (1) uncapped_methodological_outcome in {KEEP, MODIFY, KILL, INCONCLUSIVE-DATA} under the frozen performance criteria and (2) reportable_status; a favourable KEEP is reported ANNOTATION-PROVISIONAL and no stronger than MODIFY for advancement; a KILL remains KILL (annotation uncertainty does not rescue a method that fails its prespecified criteria; the V3 KILL clause 'annotation gate satisfied' is not applied); if annotation uncertainty directly prevents interpretable classification the report is INCONCLUSIVE-DATA. D7 ratified (LOCO secondary only). D8 ratified.

## 4. Scope
No detection, tracklet, crop, label, split, backbone or annotation file is changed. Only the seed-selection implementation, the runner's D6 reporting, selftests and the seed manifest (SEED_EPISODE_MANIFEST_V2) change. V1 seed manifest is kept unchanged as history.
