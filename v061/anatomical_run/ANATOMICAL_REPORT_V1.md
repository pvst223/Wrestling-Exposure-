# V0.6.1 Anatomical Integration Execution V1 - Report (DEVELOPMENT ONLY; NOT VALIDATION)

Identity layer: MODIFY, **not validated**, not exposure-ready. Ownership/pose use unchanged V0.5 code (unvalidated). R3 PARKED; R4 UNMET; ANNOTATION-PROVISIONAL. Correct anatomical ownership is not evidence of correct wrestler identity. No outcome class; no accuracy/validation/exposure claim.

Executed S0-S6 once on the four approved clips (OGR18/REG1). Segmentation: Option W (stride-3 pose frames; 3411 frames, none missing). Merge guard diagnostic-only.

## Headline descriptive counts (measured pose rows)
- Measured rows: 8707. Ownership: {'OWNERSHIP_UNCERTAIN': 4282, 'SINGLE_BODY_SUPPORTED': 3122, 'MIXED_BODY_SUSPECTED': 1303}.
- Record classes: {'WITHHELD_OWNERSHIP_UNCERTAIN': 4282, 'NONTARGET': 1478, 'WITHHELD_MIXED_BODY': 1303, 'ASSIGNED_B': 269, 'UNASSIGNED_IDENTITY_AMBIGUOUS': 197, 'ASSIGNED_A': 502, 'NO_IDENTITY_EVAL': 676}.
- M2: 1408/2179 identity-ACCEPT measured frames withheld by ownership = 0.646 (95% CI 0.626-0.666); diagnostic flag (>=20%) on 68 of 75 clip/shot units (diagnostic only; not pass/fail).
- M3 disagreements: {'ABSTAIN_with_single_body': 197, 'ACCEPT_but_ownership_not_single': 1408, 'NONTARGET_with_single_body': 1478}.
- M4: 52 A<->B label flips within tracklet runs; 15 frames where the same label sits on two detections.
- M5 temporal: {'max_median_rel': 3.0519351959228516, 'median_of_median_rel': 0.06939052045345306, 'n_joint_jump_rows': 10, 'n_pairs': 5929}.
- M6 landmark coverage: 7661/8707.
- M8 carried share (visualization only): 0.152.
- M9: sheet of 60 frames prepared (>=30 assigned + >=30 withheld; shortfall {}); **verdicts not yet collected**.

## Ownership reasons (descriptive)
{'TOO_FEW_OWN_ONLY_LANDMARKS': 1467, 'OPPONENT_LANDMARKS_IN_MASK': 1383, 'CONTESTED_LANDMARKS': 1249, 'FEW_LANDMARKS': 967, 'BONE_SPANS_INSTANCES': 544, 'SHARED_JOINT_CONFLICT': 500, 'MASK_NOT_EXPLAINED_BY_SKELETON': 496, 'NO_OWNER_MASK': 464, 'BONES_LEAVE_MASK': 375, 'LANDMARKS_IN_OTHER_INSTANCE': 216, 'SOME_LANDMARK_IN_OTHER_INSTANCE': 154, 'LIMB_TOO_LONG:upper_arm': 108, 'LIMB_TOO_LONG:thigh': 79, 'LIMB_TOO_LONG:shank': 78, 'LIMB_TOO_LONG:forearm': 69, 'LANDMARK_OUTSIDE_OWN_BOX': 40, 'TEMPORAL_SCALE_JUMP': 38, 'TORSO_SIDES_ASYMMETRIC': 24, 'TEMPORAL_JOINT_JUMP': 10}

## M7 camera-cut cross-check (reported, not reconciled)
- b1_orton_rollins_wm31: agree 7, frozen-only 3, classifier-only 0
- b2_batch2_clip_condensed: agree 0, frozen-only 39, classifier-only 0
- b2_videoplayback_2: agree 0, frozen-only 23, classifier-only 0
- b2_videoplayback_5: agree 7, frozen-only 1, classifier-only 0
For batch2 and videoplayback_2 the V0.2 classifier labels the frozen shot starts PHOTOMETRIC_REGISTERED (same registered scene) rather than CUT; frozen shot indices were used for resets (as in the identity layer).

## Merge guard (diagnostic only)
Rows flagged would-trigger by ownership state: {'OWNERSHIP_UNCERTAIN': 84, 'SINGLE_BODY_SUPPORTED': 95, 'MIXED_BODY_SUSPECTED': 7}. Correspondence with real mixed-body cases is NOT assessed.

## Limits
Stride-3 pose grid with visualization-only carry; instance masks unvalidated (V0.5 caveats); appearance vetoes disabled; ownership withholding is high, i.e. the ownership layer is conservative and most identity-ACCEPT frames are not emitted as anatomical assignments; no ground truth for skeleton correctness exists yet (M9 pending, single reviewer, ANNOTATION-PROVISIONAL).
No defects occurred during execution.
