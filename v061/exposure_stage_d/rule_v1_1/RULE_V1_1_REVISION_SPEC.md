# STAGE-D RULE V1.1 — REVISION SPECIFICATION (the single authorized pre-CHECK revision)
Written and hashed BEFORE any Rule V1.1 BUILD diagnostic was computed. No CHECK information was accessed (check_opened=false, labels submitted 0, no CHECK frames decoded, no CHECK features, no CHECK evaluation).

- Frozen Rule V1 SHA256 (preserved unchanged): 4dc574dfd71f3bc86b6d2a1ab22d6fb4778b9fbc4966d380fa4cd257e691bb1b
- Failed assumption addressed (reviewer ruling): a tight-framing / person-box-height cue (F2 veto) is not specific for non-action material, because observable professional-wrestling action often occurs under tight broadcast framing.
- Feature removed: F2_h_max_med. Threshold removed: T3 (0.80).
- Feature retained: F1_frac_ge2 (fraction of sampled frames with >= 2 gated person boxes), definition unchanged. Its rationale (ring cameras show both wrestlers; face/crowd/desk/graphic shots show 0-1 bodies) does not depend on framing height and is unaffected by the falsified assumption.
- Thresholds retained unchanged: T1 = 0.20, T2 = 0.50. Both are kept because the fail-closed design requires a shot that meets neither the NOT_LIVE nor the LIVE criterion to be UNKNOWN, never silently LIVE; removing the band would force a binary call on ambiguous shots. This is a design reason independent of BUILD accuracy. No threshold value is changed and none is searched.
- Replay indicator: unchanged, inert (R=0), 0 thresholds.
- Hierarchy V1.1: (1) no sampled frame -> UNKNOWN (NO_FEATURES); (2) R=1 -> REPLAY_SUSPECT (unreachable); (3) F1 < T1 -> NOT_LIVE; (4) F1 >= T2 -> LIVE; (5) otherwise UNKNOWN.
- Complexity: 1 feature (+ inert replay indicator), 2 thresholds. Fewer than V1 (2 features, 3 thresholds).
- Exactly one variant is evaluated. No alternatives are tested; no grid search; no new feature or framing proxy; no BUILD footage inspected. Revision budget is spent by this revision.
