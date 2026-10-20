import copy, json, os, re, ast, subprocess, sys, unittest
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); V2 = os.path.dirname(HERE); REPO = os.path.abspath(os.path.join(V2, "..", ".."))
sys.path[:0] = [HERE, os.path.join(V2, "impl")]
try:
    import cv2, scipy  # noqa
except ImportError as e: raise unittest.SkipTest(f"cv2/scipy required: {e}")
import c3_synth as S, c3_core as K
from c3_apply import apply_c3, verify_invariants
T0, T1 = "c:s0:t0", "c:s0:t1"
def run(b, pixels=True, cuts=()):
    sc = S.scene_of(b, pixels); return sc, apply_c3(sc, b["rows"], list(cuts))
def by(rows, tid): return {r["frame"]: r for r in rows if r["tracklet"] == tid}
class TState(unittest.TestCase):
    def kp(self, flip=False, lying=False, kc=0.9):
        k, c = S.skel(100, 100, flip)
        if lying: k = k.copy(); k[5] = [100, 92]; k[6] = [102, 110]; k[11] = [170, 95]; k[12] = [170, 110]
        return k, c
    def test_facing_and_posture(self):
        self.assertEqual(K.view_state(*self.kp(False), 0.5), (-1, True)); self.assertEqual(K.view_state(*self.kp(True), 0.5), (1, True))
        self.assertEqual(K.view_state(*self.kp(False, True), 0.5)[1], False)
    def test_ties_and_missing_are_undefined(self):
        k, c = self.kp(); k2 = k.copy(); k2[6, 0] = k2[5, 0]; self.assertIsNone(K.view_state(k2, c, 0.5))
        k3 = k.copy(); k3[11] = [k3[5][0] + 10, 100]; k3[12] = [k3[6][0] + 10, 100]; sh = (k3[5] + k3[6]) / 2; hip = (k3[11] + k3[12]) / 2; k3[11:13, 1] = sh[1] + abs(hip[0] - sh[0]); self.assertIsNone(K.view_state(k3, c, 0.5))
        c2 = c.copy(); c2[11] = 0.1; self.assertIsNone(K.view_state(k, c2, 0.5))
    def test_independence(self):
        a, b = (-1, True), (1, True); self.assertTrue(K.independent(a, b)); self.assertFalse(K.independent(a, a)); self.assertFalse(K.independent(None, a)); self.assertFalse(K.independent(a, None))
class TAnchorPick(unittest.TestCase):
    def v(self, f, s): return dict(frame=f, state=s)
    def test_most_recent_then_earlier_different(self):
        e = [self.v(30, (1, True)), self.v(27, (1, True)), self.v(24, (-1, True)), self.v(21, (1, False))]
        pair, d = K.pick_anchor_pair(e); self.assertEqual(d, "OK"); self.assertEqual((pair[0]["frame"], pair[1]["frame"]), (30, 24))
    def test_failures_are_labelled(self):
        self.assertEqual(K.pick_anchor_pair([])[1], "NO_CLEAN_VIEW"); self.assertEqual(K.pick_anchor_pair([self.v(3, (1, True))])[1], "ONE_CLEAN_VIEW")
        self.assertEqual(K.pick_anchor_pair([self.v(6, (1, True)), self.v(3, (1, True))])[1], "SAME_STATE")
    def test_no_frame_gap_requirement(self):
        pair, d = K.pick_anchor_pair([self.v(6, (1, True)), self.v(3, (-1, True))]); self.assertEqual(d, "OK")
class TDecide(unittest.TestCase):
    L = [0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    def ev(self, mask=(), app=(), mc=(), ac=(), dbl=(), n=1):
        return {j: dict(mask_pos=j in mask, mask_contra=j in mc, app_pos_vs=[j in app] * n, app_contra=j in ac, double=j in dbl) for j in self.L}
    def test_hypothesis_count(self):
        self.assertEqual(len(K.hypotheses(self.L, 1)), 1 + 1 + 13); self.assertEqual(len(K.hypotheses(self.L, 2)), 1 + 2 + 26)
    def test_all_positive_unique_margin(self):
        r = K.decide_unique(self.L, self.ev(mask=self.L, app=[j for j in self.L if j not in (9, 10)]), 1); self.assertTrue(r["unique"]); self.assertEqual(r["margin"], 1)
        r = K.decide_unique(self.L, self.ev(mask=self.L, app=self.L), 1); self.assertEqual(r["margin"], 2)
    def test_wrists_need_mask_evidence(self):
        r = K.decide_unique(self.L, self.ev(app=[j for j in self.L if j not in (9, 10)]), 1); self.assertFalse(r["unique"]); self.assertEqual(r["reason"], "NOT_POSITIVELY_ATTRIBUTED"); self.assertEqual(r["landmarks"], [9, 10])
    def test_single_foreign_landmark_withholds_or_not_excluded(self):
        r = K.decide_unique(self.L, self.ev(mask=[j for j in self.L if j != 13], app=[]), 1); self.assertFalse(r["unique"]); self.assertEqual(r["landmarks"], [13])
        r = K.decide_unique(self.L, self.ev(mask=self.L, ac=[13]), 1); self.assertEqual(r["reason"], "APPEARANCE_CONTRADICTION")
        self.assertEqual(K.decide_unique(self.L, self.ev(mask=self.L, mc=[7]), 1)["reason"], "MASK_CONTRADICTION"); self.assertEqual(K.decide_unique(self.L, self.ev(mask=self.L, dbl=[7]), 1)["reason"], "DOUBLE_CLAIM")
    def test_every_rival_must_be_excluded(self):
        e = self.ev(mask=(), app=self.L, n=2); e[5]["app_pos_vs"] = [True, False]; r = K.decide_unique(self.L, e, 2); self.assertFalse(r["unique"])
    def test_no_rival_or_no_evidence_withholds(self):
        self.assertEqual(K.decide_unique(self.L, self.ev(mask=self.L), 0)["reason"], "NO_RIVAL_ANCHOR"); self.assertFalse(K.decide_unique(self.L, self.ev(), 1)["unique"])
    def test_landmark_evidence_mapping(self):
        votes = [{"torso": 1, "arm_L": 1, "head": 0, "shank_L": -1}]; ev = K.landmark_evidence([0, 5, 7, 9, 15], False, {5: "OWN_ONLY", 9: "OWN_ONLY", 7: "CONTESTED"}, votes, set(), 1)
        self.assertTrue(ev[5]["app_pos_vs"][0]); self.assertTrue(ev[7]["app_pos_vs"][0]); self.assertFalse(ev[9]["app_pos_vs"][0]); self.assertFalse(ev[0]["app_pos_vs"][0]); self.assertTrue(ev[15]["app_contra"])
        self.assertFalse(ev[5]["mask_pos"]); self.assertTrue(ev[7]["mask_contra"])
        ev2 = K.landmark_evidence([5, 9], True, {5: "OWN_ONLY", 9: "OUTSIDE"}, None, set(), 1); self.assertTrue(ev2[5]["mask_pos"]); self.assertFalse(ev2[9]["mask_pos"])
class TScene(unittest.TestCase):
    def test_distinct_clothing_distinct_masks_supported(self):
        b = S.build(S.standard(), [S.RED, S.BLUE], [T0, T1]); sc, res = run(b)
        self.assertEqual(sc.intervals(T0)[0]["start_frame"], 15); self.assertEqual(sc.intervals(T0)[0]["end_frame"], 30)
        st = res["stats"]; self.assertEqual(st["n_assigned_v1"], 24); self.assertEqual(st["in_interval"], 12); self.assertEqual(st["supported"], 12); self.assertEqual(st["pass_through"], 12)
        r0 = by(res["rows"], T0); self.assertEqual(r0[18]["c3_status"], "SUPPORTED_UNIQUE"); self.assertEqual(r0[3]["c3_status"], "PASS_THROUGH"); self.assertEqual(r0[15]["c3_status"], "SUPPORTED_UNIQUE")
    def test_same_clothing_falls_back_to_masks_only(self):
        b = S.build(S.standard(a_color=0, b_color=0), [S.RED, S.BLUE], [T0, T1]); sc, res = run(b)
        ctx = sc.interval_ctx(sc.intervals(T0)[0]); self.assertTrue(all(len(m.gap) >= 0 for m in ctx["models"]))
        self.assertEqual(res["stats"]["supported"], 12); self.assertTrue(all(r["c3_margin"] == 1 for r in res["rows"] if r["c3_status"] == "SUPPORTED_UNIQUE"))
    def test_appearance_votes_fire_only_when_clothing_differs(self):
        for cols, expect in (((0, 1), True), ((0, 0), False)):
            b = S.build(S.standard(a_color=cols[0], b_color=cols[1]), [S.RED, S.BLUE], [T0, T1]); sc = S.scene_of(b); iv = sc.intervals(T0)[0]; ctx = sc.interval_ctx(iv)
            row = by(b["rows"], T0)[21]; v = sc._votes(row, ctx["models"][0], "A", "B")
            self.assertEqual(any(x == 1 for x in v.values()), expect); self.assertFalse(any(x == -1 for x in v.values()))
    def test_body_swapped_pixels_withhold(self):
        tl = S.standard(); n0 = 6
        for t in range(n0, n0 + 4): tl[t] = [(60, False, 1), (111, False, 0)]
        b = S.build(tl, [S.RED, S.BLUE], [T0, T1]); sc, res = run(b)
        r0 = by(res["rows"], T0)
        for f in (18, 21, 24, 27): self.assertEqual(r0[f]["c3_status"], "WITHHELD_C3"); self.assertIn(r0[f]["c3_reason"], ("APPEARANCE_CONTRADICTION", "RIVAL_APPEARANCE_CONFLICT")); self.assertEqual(r0[f]["record_class"], "WITHHELD_C3")
    def test_no_independent_anchor_views(self):
        b = S.build(S.standard(sep_flips=(False,) * 6), [S.RED, S.BLUE], [T0, T1]); sc, res = run(b)
        self.assertEqual(res["stats"]["supported"], 0); self.assertEqual(res["stats"]["reasons"], {"NO_INDEPENDENT_ANCHOR_VIEWS": 12})
        self.assertEqual(sc.interval_ctx(sc.intervals(T0)[0])["detail"][T0], "SAME_STATE")
    def test_tracklet_born_inside_contact_has_no_anchor(self):
        b = S.build(S.standard(), [S.RED, S.BLUE], [T0, "c:s1:t0"], born={"c:s1:t0": 6}, shots={"c:s1:t0": 1}); sc, res = run(b)
        r = by(res["rows"], "c:s1:t0")[18]; self.assertEqual(r["c3_status"], "WITHHELD_C3"); self.assertIn(r["c3_reason"], ("NO_INDEPENDENT_ANCHOR_VIEWS",))
    def test_unanchored_participant(self):
        tl = S.standard(cx_contact=(90, 141)); n0 = 6
        for t in range(len(tl)): tl[t] = tl[t] + [(39 if n0 <= t < n0 + 4 else -400, False, 2)]
        b = S.build(tl, [S.RED, S.BLUE, S.GREEN], [T0, T1, None]); sc, res = run(b)
        r0 = by(res["rows"], T0)
        self.assertTrue(any(r0[f]["c3_reason"] == "UNANCHORED_PARTICIPANT" for f in (18, 21, 24, 27)))
    def test_cast_too_large(self):
        old = K.STRUCT["MAX_CAST"]; K.STRUCT["MAX_CAST"] = 1
        try:
            b = S.build(S.standard(), [S.RED, S.BLUE], [T0, T1]); sc, res = run(b)
        finally: K.STRUCT["MAX_CAST"] = old
        self.assertEqual(res["stats"]["reasons"], {"CAST_TOO_LARGE": 12})
    def test_merged_masks_v1_withheld_stays_withheld(self):
        b = S.build(S.standard(), [S.RED, S.BLUE], [T0, T1], masks="merged"); sc, res = run(b)
        for a, c in zip(b["rows"], res["rows"]):
            if a["record_class"] not in K.ASSIGNED: self.assertEqual(a["record_class"], c["record_class"])
        self.assertFalse(any(r["record_class"] in K.ASSIGNED for r in res["rows"] if r["c3_status"] == "WITHHELD_C3"))
    def test_missing_masks_fail_closed_and_no_release(self):
        b = S.build(S.standard(), [S.RED, S.BLUE], [T0, T1], masks="none"); sc, res = run(b)
        self.assertEqual(sum(1 for r in res["rows"] if r["record_class"] in K.ASSIGNED), 0)
    def test_without_pixels_masks_only(self):
        b = S.build(S.standard(), [S.RED, S.BLUE], [T0, T1]); sc, res = run(b, pixels=False)
        self.assertEqual(res["stats"]["supported"], 12); self.assertEqual(sc.interval_ctx(sc.intervals(T0)[0])["models"], None)
class TInvariants(unittest.TestCase):
    def setUp(self):
        self.b = S.build(S.standard(), [S.RED, S.BLUE], [T0, T1]); self.sc, self.res = run(self.b)
    def test_subset_and_bitwise(self):
        verify_invariants(self.b["rows"], self.res["rows"])
        for a, c in zip(self.b["rows"], self.res["rows"]): self.assertTrue(np.array_equal(np.asarray(a["kp"]), np.asarray(c["kp"])) and np.array_equal(np.asarray(a["kpc"]), np.asarray(c["kpc"])))
    def test_violations_are_caught(self):
        bad = copy.deepcopy(self.res["rows"]); bad[0]["kp"][0][0] += 1e-9
        with self.assertRaises(AssertionError): verify_invariants(self.b["rows"], bad)
        v1 = copy.deepcopy(self.b["rows"]); v1[0]["record_class"] = "WITHHELD_OWNERSHIP_UNCERTAIN"; v1[0]["landmarks_emitted"] = False
        with self.assertRaises(AssertionError): verify_invariants(v1, self.res["rows"])
        with self.assertRaises(AssertionError): verify_invariants(self.b["rows"], self.res["rows"][:-1])
    def test_withheld_rows_have_no_release_path(self):
        tl = S.standard(sep_flips=(False,) * 6); b = S.build(tl, [S.RED, S.BLUE], [T0, T1]); sc, res = run(b)
        for a, c in zip(b["rows"], res["rows"]):
            if c["record_class"] == "WITHHELD_C3": self.assertIn(a["record_class"], K.ASSIGNED); self.assertFalse(c["landmarks_emitted"]); self.assertIsNone(c["assigned_label"])
    def test_carry_suppressed_in_and_adjacent_to_intervals(self):
        v1 = [r for r in self.b["src"] if r["pose_status"] == "CARRIED" and 15 <= r["frame"] <= 32]; self.assertTrue(len(v1) > 0, "fixture must have V1 carried rows inside the interval")
        v2 = [r for r in self.res["src"] if r["pose_status"] == "CARRIED" and 15 <= r["frame"] <= 32]; self.assertEqual(v2, [])
        outside = [r for r in self.res["src"] if r["pose_status"] == "CARRIED" and r["frame"] < 15]; self.assertTrue(len(outside) > 0)
    def test_no_new_carried_rows_vs_v1(self):
        k1 = {(r["tracklet"], r["frame"]) for r in self.b["src"] if r["pose_status"] == "CARRIED"}; k2 = {(r["tracklet"], r["frame"]) for r in self.res["src"] if r["pose_status"] == "CARRIED"}; self.assertTrue(k2 <= k1)
    def test_c0_partition_sums(self):
        st = self.res["stats"]; self.assertEqual(sum(st["partition"].values()), st["n_assigned_v1"])
    def test_determinism_and_order_invariance(self):
        j = lambda res: json.dumps([(r["tracklet"], r["frame"], r["record_class"], r["c3_status"], r["c3_reason"], r["c3_margin"]) for r in sorted(res["rows"], key=lambda r: (r["tracklet"], r["frame"]))], sort_keys=True)
        sc2, res2 = run(self.b); self.assertEqual(j(self.res), j(res2))
        rows = list(reversed(self.b["rows"])); b2 = dict(self.b, rows=rows); sc3 = S.scene_of(b2); res3 = apply_c3(sc3, rows, []); self.assertEqual(j(self.res), j(res3))
class TAudit(unittest.TestCase):
    FILES = [os.path.join(V2, "impl", f) for f in ("c3_core.py", "c3_scene.py", "c3_apply.py")]
    def src(self):
        out = {}
        for f in self.FILES:
            with open(f) as h: out[f] = h.read()
        return out
    def test_numeric_literals_are_structural_only_and_no_min_gap(self):
        for f, s in self.src().items():
            for n in ast.walk(ast.parse(s)):
                if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
                    self.assertIsInstance(n.value, int, f"{f}: float literal {n.value}"); self.assertTrue(-1 <= n.value <= 16, f"{f}: numeric literal {n.value}")
            self.assertNotIn("MIN_GAP", s)
    def test_no_forbidden_inputs_or_vocabulary(self):
        bad = ["verdict", "hidden_key", "review_sheet", "holdout", "gemini", "wrestler_id", "truth", "b0_decision", "owner_key", "m9_", "m9b", "m9c", "oof_"]
        voc = ["center_of_mass", "centre_of_mass", "velocity", "speed", "workload", "fatigue", "injury", "impact", "acceleration"]
        for f, s in self.src().items():
            low = s.lower()
            for w in bad + voc: self.assertNotIn(w, low, f"{f}: {w}")
    def test_no_coordinate_writes(self):
        for f, s in self.src().items():
            for n in ast.walk(ast.parse(s)):
                tg = n.targets if isinstance(n, ast.Assign) else ([n.target] if isinstance(n, (ast.AugAssign, ast.AnnAssign)) else [])
                for t in tg:
                    if isinstance(t, ast.Subscript) and isinstance(t.slice, ast.Constant) and t.slice.value in ("kp", "kpc", "box"): self.fail(f"{f}: writes coordinate field {t.slice.value}")
    def test_no_interpolation_calls(self):
        for f, s in self.src().items():
            for w in ("interp", "np.linspace", "polyfit", "spline"): self.assertNotIn(w, s.replace("# ", ""), f)
    def test_constants_come_from_frozen_config(self):
        import c3_scene; c = c3_scene.load_cfg()
        self.assertEqual((c.pose.KP_CONF, c.ownership.SEG_DUP_IOU, c.ownership.UNEXPL_MAX, c.integrity.SHARE_DIST_FRAC, c.appearance.D_SEP_MIN, c.appearance.VOTE_DELTA), (0.5, 0.8, 0.25, 0.05, 0.15, 0.25))
        self.assertEqual(K.STRUCT, dict(MIN_VIEWS=2, MAX_CAST=3, EXT_FRAMES=1, STRIDE=3))
    def test_v1_and_locked_manifests_unchanged(self):
        for cmd in (["v061/anatomical/anat_manifest.py"], ["v061/tooling/impl_manifest.py"]):
            r = subprocess.run([sys.executable, cmd[0]], cwd=REPO, capture_output=True, text=True); self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
if __name__ == "__main__": unittest.main()
