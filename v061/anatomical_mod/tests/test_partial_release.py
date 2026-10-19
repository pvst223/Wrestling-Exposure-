"""Readiness tests for RELEASED_PARTIAL_ANATOMY (12 required properties + extras). Synthetic only; real-cache parity is in parity_check.py."""
import copy, inspect, itertools, json, os, sys, unittest
import numpy as np
try:
    import cv2, scipy  # noqa
except ImportError as e: raise unittest.SkipTest(f"cv2/scipy required: {e}")
HERE = os.path.dirname(os.path.abspath(__file__)); MOD = os.path.dirname(HERE); V = os.path.dirname(MOD)
sys.path[:0] = [os.path.join(V, "anatomical", "tests"), os.path.join(V, "anatomical", "impl"), os.path.join(MOD, "impl")]
import synth, pipeline, carry, record_class as RC, ownership_stage, partial_release as PR, partial_render
FR = (0, 3, 6, 9, 12)
def clip(code="ACCEPT_A", extra_rects=((30, 100, 90, 185),), masks=True):
    dets = {f: synth.det_frame([(60, 100)]) for f in FR}
    seg = {f: synth.seg_frame([synth.person_rect(60)] + list(extra_rects)) for f in FR} if masks else {}
    return [synth.tracklet("c:s0:t0", "c", 0, dets, 0, FR)], dets, synth.decisions("c:s0:t0", FR, code), seg
def base(code="ACCEPT_A", state="OWNERSHIP_UNCERTAIN", reasons=("CONTESTED_LANDMARKS",), cls="WITHHELD_OWNERSHIP_UNCERTAIN", nf=False, pose="MEASURED"):
    kp = [[10.0 + i, 20.0 + 2 * i] for i in range(17)]
    return dict(clip="c", tracklet="t", frame=3, shot=0, record_class=cls, ownership_state_passthrough=state, ownership_state=state, own_reasons=list(reasons), identity_state_passthrough=code,
                identity_code=code, numeric_failure=nf, pose_status=pose, assigned_label=None, landmarks_emitted=False, identity_unvalidated_flag=False, kp=kp, kpc=[0.9] * 17, box=[5, 5, 60, 60],
                merge_guard_would_trigger=False, g=0.5, q=0.5)
ALL_OWN = {i: "OWN_ONLY" for i in PR._own().LMS}
class T(unittest.TestCase):
    def setUp(self): self.cfg = ownership_stage.load_cfg(); self.own = ownership_stage._mods()[0]
    def fs(self, seg, f=0): return self.own.FrameSeg(seg[f], 200, 200, self.cfg.seg.SEG_CONF_MIN)
    # 1 deterministic per-landmark recomputation
    def test_01_deterministic_recomputation(self):
        tr, dets, dec, seg = clip(); a = PR.landmark_classes(0, dets[0], self.fs(seg), self.cfg); b = PR.landmark_classes(0, dets[0], self.fs(seg), self.cfg)
        self.assertEqual(json.dumps(a[0], sort_keys=True), json.dumps(b[0], sort_keys=True)); self.assertEqual(a[2], b[2])
        rows, _ = pipeline.run_clip(tr, dets, dec, seg, [], 200, 200); M = a[1]
        for k in ("own_only_frac", "contested_frac", "other_only_frac", "unexplained_frac"): self.assertEqual(M[k], rows[0]["own_summary"][k])   # parity with locked pipeline row
        self.assertEqual(rows[0]["S"], a[2])
    # 2 exact Tier-A-only eligibility
    def test_02_tier_a_exact(self):
        self.assertEqual(set(PR.TIER_A), {"CONTESTED_LANDMARKS", "TOO_FEW_OWN_ONLY_LANDMARKS", "MASK_NOT_EXPLAINED_BY_SKELETON"})
        for k in range(1, 4):
            for combo in itertools.combinations(sorted(PR.TIER_A), k): self.assertTrue(PR.eligible(base(reasons=combo)), combo)
        self.assertFalse(PR.eligible(base(reasons=())))
    # 3 any non-Tier-A reason vetoes release
    def test_03_non_tier_a_vetoes(self):
        others = ["OPPONENT_LANDMARKS_IN_MASK", "BONES_LEAVE_MASK", "TORSO_SIDES_ASYMMETRIC", "TEMPORAL_JOINT_JUMP", "SHARED_JOINT_CONFLICT", "BONE_SPANS_INSTANCES", "LANDMARKS_IN_OTHER_INSTANCE",
                  "SOME_LANDMARK_IN_OTHER_INSTANCE", "NO_OWNER_MASK", "FEW_LANDMARKS", "LIMB_TOO_LONG:thigh", "TEMPORAL_SCALE_JUMP", "LANDMARK_OUTSIDE_OWN_BOX", "ANYTHING_NEW"]
        for o in others:
            for tier in itertools.chain.from_iterable(itertools.combinations(sorted(PR.TIER_A), k) for k in range(0, 4)):
                r = base(reasons=list(tier) + [o]); out = PR.apply_release(r, ALL_OWN); self.assertEqual(out, r); self.assertEqual(out["record_class"], "WITHHELD_OWNERSHIP_UNCERTAIN")
    # 4 MIXED always vetoes
    def test_04_mixed_vetoes(self):
        for reasons in (["CONTESTED_LANDMARKS"], [], ["BONE_SPANS_INSTANCES"]):
            r = base(state="MIXED_BODY_SUSPECTED", reasons=reasons, cls="WITHHELD_MIXED_BODY"); self.assertEqual(PR.apply_release(r, ALL_OWN), r)
        for st, cl in (("SINGLE_BODY_SUPPORTED", "ASSIGNED_A"), ("OWNERSHIP_NOT_EVALUATED", "WITHHELD_OWNERSHIP_NOT_EVALUATED")):
            r = base(state=st, cls=cl); self.assertEqual(PR.apply_release(r, ALL_OWN), r)
    # 5 only OWN_ONLY landmarks emitted
    def test_05_only_own_only(self):
        cls = {i: "OWN_ONLY" for i in ALL_OWN}; cls.update({9: "CONTESTED", 10: "OTHER_ONLY", 13: "OUTSIDE"}); out = PR.apply_release(base(), cls)
        self.assertEqual(out["record_class"], "RELEASED_PARTIAL_ANATOMY_A"); self.assertTrue(set(out["released_landmarks"]).isdisjoint({9, 10, 13}))
        self.assertEqual(out["released_landmarks"], sorted(i for i in ALL_OWN if i not in (9, 10, 13)))
        v = PR.mask_unreleased(out); self.assertTrue(all(v[i] is None for i in range(17) if i not in out["released_landmarks"])); self.assertTrue(all(v[i] is not None for i in out["released_landmarks"]))
    # 6 bones need both released endpoints
    def test_06_bones_both_endpoints(self):
        cls = {i: "OWN_ONLY" for i in ALL_OWN}; cls[7] = "CONTESTED"; out = PR.apply_release(base(), cls); s = set(out["released_landmarks"])
        for a, b in out["released_bones"]: self.assertTrue(a in s and b in s)
        self.assertNotIn([5, 7], out["released_bones"]); self.assertNotIn([7, 9], out["released_bones"]); self.assertIn([5, 6], out["released_bones"])
        self.assertEqual({tuple(b) for b in out["released_bones"]}, {b for b in PR._own().BONES if b[0] in s and b[1] in s})
        iso = {i: "CONTESTED" for i in ALL_OWN}; iso[0] = "OWN_ONLY"; iso[5] = "OWN_ONLY"      # two own-only landmarks that share no bone: nothing to release
        r = base(); self.assertEqual(PR.apply_release(r, iso), r)
        self.assertEqual(PR.apply_release(r, {}), r); self.assertEqual(PR.apply_release(r, None), r)
    # 7 PARTIAL can never become ASSIGNED
    def test_07_partial_is_not_assigned(self):
        out = PR.apply_release(base(), ALL_OWN); self.assertNotIn(out["record_class"], RC.ASSIGNED); self.assertIn(out["record_class"], PR.PARTIAL_CLASSES)
        self.assertFalse(out["landmarks_emitted"]); self.assertIsNone(out["assigned_label"]); self.assertEqual(out["anatomy_completeness"], "PARTIAL"); self.assertTrue(out["identity_unvalidated_flag"])
        self.assertTrue(out["partial_landmarks_emitted"]); self.assertEqual(PR.apply_release(base(code="ACCEPT_B"), ALL_OWN)["record_class"], "RELEASED_PARTIAL_ANATOMY_B")
        self.assertNotIn(out["record_class"], RC.CLASSES)    # locked class vocabulary is untouched
        self.assertFalse(any("PARTIAL" in c for c in RC.CLASSES))
        with self.assertRaises(ValueError): PR.mask_unreleased(base())
    # 8 no carry from / across PARTIAL
    def test_08_no_carry_from_or_across_partial(self):
        asg = dict(base(cls="ASSIGNED_A", state="SINGLE_BODY_SUPPORTED", reasons=()), frame=0)
        part = PR.apply_release(dict(base(), frame=3), ALL_OWN); asg2 = dict(asg, frame=6)
        out = carry.source_rate([asg, part, asg2], []); by = {r["frame"]: r for r in out}
        self.assertEqual(by[3]["record_class"], part["record_class"]); self.assertEqual(by[3]["pose_status"], "MEASURED")
        self.assertNotIn("CARRIED_RELEASED_PARTIAL_ANATOMY_A", {r["record_class"] for r in out})
        self.assertNotIn(4, by) if by.get(4) and by[4]["record_class"].startswith("CARRIED_RELEASED") else None
        self.assertFalse(any(r["record_class"].startswith("CARRIED_RELEASED") for r in out))
        out2 = carry.source_rate([part], []); self.assertEqual(len(out2), 1)       # nothing is carried after a PARTIAL anchor
        self.assertFalse(any(r["pose_status"] == "CARRIED" for r in out2))
        out3 = carry.source_rate([asg, dict(part, frame=2)], []); by3 = {r["frame"]: r for r in out3}; self.assertEqual(by3[1]["record_class"], "CARRIED_ASSIGNED_A"); self.assertNotIn(3, by3)
        out4 = carry.source_rate([dict(asg, frame=0), dict(part, frame=2), dict(asg, frame=9)], []); self.assertNotIn(3, {r["frame"]: r for r in out4})   # PARTIAL at 2 blocks carry from the anchor at 0
    # 9 merge guard cannot affect release
    def test_09_merge_guard_has_no_effect(self):
        self.assertEqual(list(inspect.signature(PR.apply_release).parameters), ["rec", "cls"]); self.assertEqual(list(inspect.signature(PR.eligible).parameters), ["rec"])
        a = base(); b = dict(a, merge_guard_would_trigger=True, merge_guard_reason="X", merge_guard_since_frame=1)
        oa, ob = PR.apply_release(a, ALL_OWN), PR.apply_release(b, ALL_OWN); self.assertEqual({k: v for k, v in oa.items() if not k.startswith("merge_guard")}, {k: v for k, v in ob.items() if not k.startswith("merge_guard")})
        self.assertNotIn("merge_guard", inspect.getsource(PR.apply_release)); self.assertNotIn("merge_guard", inspect.getsource(PR.eligible))
    # 10 identity uncertainty unchanged
    def test_10_identity_unchanged(self):
        for code in ("ABSTAIN_AMBIGUOUS", "REJECT_NONTARGET", "NO_IDENTITY_EVAL"):
            r = base(code=code); self.assertEqual(PR.apply_release(r, ALL_OWN), r)
        for code in ("ACCEPT_A", "ACCEPT_B"):
            r = base(code=code); o = PR.apply_release(r, ALL_OWN)
            for k in ("identity_state_passthrough", "identity_code", "g", "q"): self.assertEqual(o[k], r[k])
        self.assertTrue(PR.apply_release(base(nf=True), ALL_OWN)["numeric_failure"] and PR.apply_release(base(nf=True, cls="INVALID_NUMERIC"), ALL_OWN)["record_class"] == "INVALID_NUMERIC")
        self.assertEqual(PR.apply_release(base(pose="NONE", cls="NO_POSE"), ALL_OWN)["record_class"], "NO_POSE")
    # 11 existing behaviour unchanged outside the new class
    def test_11_existing_behaviour_unchanged(self):
        for code, masks, extra in itertools.product(("ACCEPT_A", "ABSTAIN_AMBIGUOUS", "REJECT_NONTARGET"), (True, False), ((), ((30, 100, 90, 185),))):
            tr, dets, dec, seg = clip(code, extra, masks); rows, _ = pipeline.run_clip(tr, dets, dec, seg, [], 200, 200)
            fs = self.fs(seg) if masks else None
            for r in rows:
                cls = PR.landmark_classes(r["det"], dets[r["frame"]], self.fs(seg, r["frame"]) if masks else None, self.cfg)[0]; o = PR.apply_release(r, cls)
                if o["record_class"] in PR.PARTIAL_CLASSES: self.assertTrue(PR.eligible(r)); self.assertEqual(r["record_class"], "WITHHELD_OWNERSHIP_UNCERTAIN")
                else: self.assertEqual(o, r)
        for r in itertools.product(RC.ID_STATES, (False, True), RC.OWN_STATES, ("MEASURED", "NONE")): RC.classify(*r)      # locked classifier still callable, vocabulary unchanged
        self.assertEqual(len(RC.CLASSES), 12)
    def test_11b_release_in_pipeline(self):
        tr, dets, dec, seg = clip(); rows, _ = pipeline.run_clip(tr, dets, dec, seg, [], 200, 200); r = rows[0]; self.assertEqual(set(r["own_reasons"]) <= PR.TIER_A, True)
        cls = PR.landmark_classes(r["det"], dets[r["frame"]], self.fs(seg, r["frame"]), self.cfg)[0]; o = PR.apply_release(r, cls)
        self.assertEqual(o["record_class"], "RELEASED_PARTIAL_ANATOMY_A"); self.assertEqual(o["released_landmarks"], sorted(i for i, c in cls.items() if c == "OWN_ONLY")); self.assertEqual(o["n_released"], 7)
        img = np.zeros((200, 200, 3), np.uint8); partial_render.draw_partial(img, o); self.assertGreater(int(img.sum()), 0)
        n = np.zeros((200, 200, 3), np.uint8); partial_render.draw_partial(n, o, style="neutral"); self.assertGreater(int(n.sum()), 0); self.assertFalse(((n[..., 0] == 0) & (n[..., 2] == 255)).any())
    # 12 no exposure / COM / distance / impact / workload fields
    def test_12_no_exposure_fields(self):
        forb = ("com", "centre_of_mass", "center_of_mass", "distance", "speed", "velocity", "impact", "workload", "exposure", "intensity", "fatigue", "injury", "load")
        o = PR.apply_release(base(), ALL_OWN)
        for k in o: self.assertFalse(any(f == k.lower() or f in k.lower().split("_") for f in forb), k)
        import ast
        names = set()
        for f in (PR.__file__, os.path.join(MOD, "impl", "partial_render.py")):
            tree = ast.parse(open(f).read())
            doc = {id(n.body[0].value) for n in ast.walk(tree) if isinstance(n, (ast.Module, ast.FunctionDef)) and n.body and isinstance(n.body[0], ast.Expr) and isinstance(getattr(n.body[0], "value", None), ast.Constant)}
            for n in ast.walk(tree):
                if isinstance(n, ast.Name): names.add(n.id.lower())
                elif isinstance(n, ast.Attribute): names.add(n.attr.lower())
                elif isinstance(n, ast.keyword) and n.arg: names.add(n.arg.lower())
                elif isinstance(n, ast.FunctionDef): names.add(n.name.lower())
                elif isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in doc: names.add(n.value.lower())
        for n in names: self.assertFalse(any(b in n for b in ("centre_of_mass", "center_of_mass", "workload", "fatigue", "exposure", "distance", "velocity", "impact")), n)
        rep = PR.coverage_report([o], 2179); self.assertEqual(set(rep), {"class_counts", "n_partial", "n_released_hist", "clips", "coverage_gain_points_of_identity_accept_measured"})
if __name__ == "__main__": unittest.main(verbosity=2)
