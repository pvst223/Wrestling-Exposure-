# Anatomy V2 (C3) — implementation (candidate; NOT evaluated)

Implements exactly `v061/anatomical_contact_design/ANATOMY_V2_C3_JOINT_TWO_BODY_OWNERSHIP_DETAILED_DESIGN_V1.md` plus `C3_ANCHOR_INDEPENDENCE_CORRECTION_V1.md`. No design change during implementation. Development-only, rights UNRESOLVED; no accuracy, validation or exposure claim.

- `impl/c3_core.py` — pure logic: observation state, independence, anchor pair pick, finite hypothesis set, exclusion-based uniqueness with integer margin, landmark evidence mapping, carry suppression.
- `impl/c3_scene.py` — contact predicate, intervals, clean views, anchors, cast, mask informativeness, double claim, appearance votes. Calls only frozen functions (`integrity_v05.evaluate`, `ownership_v05.*`, `appearance.*`).
- `impl/c3_apply.py` — subtract-only post-filter on frozen V1 rows; invariants `verify_invariants`; frozen carry recomputed then suppressed in/adjacent to intervals.
- `geometry_feasibility.py` — counts only, for the burned clips (no correctness labels read).
- `tests/` — synthetic tests (`python -m unittest discover -s v061/anatomical_v2/tests -p 'test_*.py'`).
- `c3_manifest.py` — implementation manifest (`C3_IMPLEMENTATION_MANIFEST.txt`).

Notes for the reviewer (implementation interpretations, none changes the design):
1. Landmark set L = frozen LMS landmarks with confidence >= 0.5 (as written in the design). The frozen renderer draws only landmarks of bones with confidence >= 0.7, so every drawn landmark is in L (L is a superset, hence more conservative).
2. Co-located detections are taken from the frozen `overlap`/`shared_joints` info, detections whose owner mask touches the target's dilated owner mask, and detections with any confident landmark inside the dilated owner mask.
3. Intervals are built over the target tracklet's measured rows (consecutive pose frames, gap <= stride); a missing detection breaks a run; overlapping/adjacent extended runs merge.
4. The cast is taken at the interval's first contact frame; at later frames every co-located detection must map (via the V1 row of that detection) to a tracklet in the cast, otherwise UNANCHORED_PARTICIPANT.
