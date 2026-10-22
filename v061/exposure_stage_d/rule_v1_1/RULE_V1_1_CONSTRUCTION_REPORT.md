# STAGE-D RULE V1.1 — SINGLE AUTHORIZED REVISION, FROZEN (returned to the independent reviewer BEFORE CHECK)
ANNOTATION_PROVISIONAL; R4 unmet; development futility gate only. No validation/generalization/exposure-validity claim. **Rule V1.1 was NOT run on CHECK. CHECK remains sealed.**

## 1. Hashes
- Frozen Rule V1.1 SHA256: `b2e47698cd391faf86119525cc4dd9c939a0c807bd644069e02f964ba5df5111` (`RULE_V1_1_FROZEN.json`).
- Revision spec SHA256 `13473914ff1b173dac6467f87f05a62b94eed96cfc68d7ebf614ecdfe3d2b62b`, committed and pushed (branch commit "revision spec (pre-diagnostics)") before any V1.1 BUILD number was computed.
- Frozen Rule V1 SHA256 `4dc574dfd71f3bc86b6d2a1ab22d6fb4778b9fbc4966d380fa4cd257e691bb1b` — **preserved unchanged**; its hash was recomputed from the repo files and reproduces.

## 2. Exact V1 → V1.1 change (default minimal revision; one variant evaluated)
Removed: feature F2_h_max_med and threshold T3 (0.80). Retained unchanged: F1_frac_ge2, T1 = 0.20, T2 = 0.50, inert replay indicator, input gate, P1 calculation. V1.1 hierarchy: no sampled frame → UNKNOWN; R=1 → REPLAY_SUSPECT (unreachable); F1 < 0.20 → NOT_LIVE; F1 ≥ 0.50 → LIVE; otherwise UNKNOWN. Justification (given before results, see spec): F2 is the component whose assumption the reviewer found falsified; F1's rationale does not depend on framing height; both F1 thresholds are kept because the fail-closed design requires an abstention band rather than a forced binary call. No threshold value changed; no alternatives tested; no BUILD footage inspected.

## 3. Rule V1.1 BUILD diagnostics (169 shots / 638.233 s; decidable 584.534 s; reference-UNKNOWN excluded)
| rule | disagree s | decidable s | P1 |
|---|---|---|---|
| Rule V1.1 | 88.766 | 584.534 | **15.19%** |
| Rule V1 (frozen) | 218.833 | 584.534 | 37.44% |
| All-LIVE baseline | 26.133 | 584.534 | 4.47% |

Rule classes: LIVE 150 shots / 574.5 s; NOT_LIVE 4 / 10.3 s; UNKNOWN 15 / 53.4 s. Reference × rule (shots / s): LIVE_ACTION→LIVE 137/495.2, →UNKNOWN 14/52.8, →NOT_LIVE 4/10.3; CLOSE_UP→LIVE 7/23.6, →UNKNOWN 1/0.5; NON_MATCH→LIVE 1/2.0; reference-UNKNOWN→LIVE 5/53.7 (excluded). P1 by source: orton 11.367/32.5 s (35.0%), batch2_clip 43.0/120.0 (35.8%), vp2 14.9/64.467 (23.1%), vp5 6.633/119.567 (5.5%), match 12.867/248.0 (5.2%).
Complexity: 1 feature + inert replay indicator (V1: 2), 2 thresholds (V1: 3). Missing features: none occurred; a shot with no sampled frame → UNKNOWN.

## 4. What the revision fixed / cannot distinguish
Fixed: the F2 veto's over-abstention (LIVE_ACTION→UNKNOWN fell from 193.1 s to 52.8 s); P1 moved from 37.44% to 15.19%, below the 20% futility line on BUILD. This shows only that removing the failed component addressed the identified BUILD failure — not validation or generalization.
Still cannot distinguish: 7 of 8 CLOSE_UP shots (23.6 s) and the NON_MATCH shot are called LIVE (two bodies are visible in most sampled frames); P1 is still **3.4× the all-LIVE baseline** (15.19% vs 4.47%), i.e. the rule is worse than trivial on BUILD; 4 LIVE_ACTION shots (10.3 s) are NOT_LIVE; picture-in-picture and replay are invisible to box counts. The only improvement over all-LIVE would come from detecting CLOSE_UP, and it detects almost none.

## 5. Status
- Revision budget: **SPENT**. No Rule V1.2 or further revision without a new reviewer ruling.
- CHECK seal: check_opened=false; check_labels_submitted=0; check_frames_decoded=false; check_features_computed=false; check_evaluation_performed=false. Detections cover frames ≤ 13455 (CHECK starts 13546); only BUILD ids read from the shot-frame table. All five conditions verified true; no breach.
- Limitations: heavy LIVE dominance (non-LIVE decidable BUILD time is 26.1 s, 4.5%); non-LIVE BUILD examples are from short excerpts; replay indicator untestable; BUILD P1 is descriptive only; the 4.47% baseline is not beaten.

## 6. Recommendation (not an authorization): **PROCEED_TO_REVIEW_FOR_CHECK**, with the caveat that the rule is worse than all-LIVE on BUILD and its value in CHECK rests only on the fixed 20% futility test; STOP_BEFORE_CHECK is also defensible if the reviewer regards "worse than trivial" as disqualifying. Reviewer decides.
