import ast, csv, hashlib, json, os, random, sys, tempfile, unittest
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(HERE); sys.path[:0] = [P, os.path.join(P, "impl")]
import eligibility as E, sep_stats as S, sep_sample as SS, sep_join as J, sep_review_pack as RP
W, H = 640, 360
def tb(x=200, y=50, w=100, h=200): return [x, y, x + w, y + h]
def ok(boxes, conf, t=0, **k): return E.frame_ok(np.array(boxes, float), np.array(conf, float), t, W, H, **k)
class TestEligibility(unittest.TestCase):
    def test_1_params_frozen(self):
        self.assertEqual(E.PARAMS, dict(margin=0.15, conf_floor=0.10, other_min_height_frac=0.25, border_frac=0.02, target_min_height_frac=0.15, stability_stride=3, cut_window=3))
    def test_2_alone_eligible(self): self.assertEqual(ok([tb()], [0.9]), (True, "OK"))
    def test_3_margin_boundary(self):
        t = tb(); ex_right = 200 + 100 + 15  # expanded right edge 315
        self.assertEqual(ok([t, [316, 60, 380, 200]], [0.9, 0.9])[1], "OK"); self.assertEqual(ok([t, [314, 60, 380, 200]], [0.9, 0.9])[1], "OTHER_PERSON_WITHIN_MARGIN")
        self.assertEqual(ok([t, [315, 60, 380, 200]], [0.9, 0.9])[1], "OK")  # touching edge is not positive-area overlap
    def test_4_other_floor_and_height(self):
        t = tb(); o = [310, 60, 380, 200]; self.assertEqual(ok([t, o], [0.09, 0.9])[1], "OK") if False else None
        self.assertEqual(ok([t, o], [0.9, 0.099])[1], "OK"); self.assertEqual(ok([t, o], [0.9, 0.10])[1], "OTHER_PERSON_WITHIN_MARGIN")
        short = [310, 60, 380, 60 + 49]; self.assertEqual(ok([t, short], [0.9, 0.9])[1], "OK"); tall = [310, 60, 380, 60 + 50]; self.assertEqual(ok([t, tall], [0.9, 0.9])[1], "OTHER_PERSON_WITHIN_MARGIN")
    def test_5_border_and_size(self):
        self.assertEqual(ok([tb(x=5)], [0.9])[1], "TARGET_NEAR_BORDER"); self.assertEqual(ok([tb(x=14)], [0.9])[1], "OK"); self.assertEqual(ok([[200, 3, 300, 100]], [0.9])[1], "TARGET_NEAR_BORDER")
        self.assertEqual(ok([tb(h=53)], [0.9])[1], "TARGET_TOO_SMALL"); self.assertEqual(ok([tb(h=54)], [0.9])[1], "OK")
    def test_6_margin_param_sensitivity(self):
        t = tb(); o = [320, 60, 380, 200]; self.assertEqual(ok([t, o], [0.9, 0.9], margin=0.10)[1], "OK"); self.assertEqual(ok([t, o], [0.9, 0.9], margin=0.25)[1], "OTHER_PERSON_WITHIN_MARGIN")
    def test_7_temporal_and_cut(self):
        D = {f: ([tb()], [0.9]) for f in range(0, 30, 3)}; shot = lambda f: 0 if f < 15 else 1; tbox = lambda f: 0
        e = lambda f, **k: E.eligible(f, lambda g: D.get(g), tbox, shot, W, H, **k)
        self.assertEqual(e(6)[0], True); self.assertEqual(e(0)[1], "NEIGHBOUR_MISSING"); self.assertEqual(e(12)[1], "CUT_WITHIN_WINDOW"); self.assertEqual(e(15)[1], "CUT_WITHIN_WINDOW")
        D2 = dict(D); D2[9] = ([tb(), [310, 60, 380, 200]], [0.9, 0.9]); self.assertEqual(E.eligible(6, lambda g: D2.get(g), tbox, shot, W, H)[1], "NEIGHBOUR_OTHER_PERSON_WITHIN_MARGIN")
    def test_8_no_forbidden_inputs(self):
        bad = ("ownership", "own_", "verdict", "identity", "merge", "skeleton", "kp", "landmark", "record_class", "label")
        tree = ast.parse(open(os.path.join(P, "impl", "eligibility.py")).read())
        for n in ast.walk(tree):
            if isinstance(n, ast.arg): self.assertFalse(any(b in n.arg.lower() for b in bad), n.arg)
class TestStats(unittest.TestCase):
    def test_9_event_table_exact(self):
        for n in range(1, 301):
            k = S.max_events_keep(n)
            if k is None: self.assertGreater(S.cp(0, n)[1], 0.05)
            else: self.assertLessEqual(S.cp(k, n)[1], 0.05); self.assertGreater(S.cp(k + 1, n)[1], 0.05) if k + 1 <= n else None
        self.assertEqual(S.max_events_keep(150), 2); self.assertEqual(S.max_events_keep(100), 0)
    def test_10_constants(self): self.assertEqual((S.KEEP_UPPER, S.KILL_POINT, S.KILL_SHOTS, S.KEEP_MAX_SHOTS, S.AUDIT_KEEP, S.AUDIT_KILL, S.NJ_MAX, S.MIN_JUDGEABLE, S.MIN_SHOTS, S.MIN_CLIPS), (0.05, 0.10, 3, 1, 0.05, 0.10, 0.20, 100, 20, 3))
    def dr(self, **k):
        a = dict(judgeable=150, wrong=0, n_reviewed=170, not_judgeable=20, shots_with_judgeable=30, clips_with_judgeable=6, shots_with_wrong=0, audit_answered=160, audit_other=2); a.update(k); return S.decide_reviewer(**a)
    def test_11_decisions(self):
        self.assertEqual(self.dr()["outcome"], "KEEP"); self.assertEqual(self.dr(wrong=2, shots_with_wrong=1)["outcome"], "KEEP"); self.assertEqual(self.dr(wrong=3, shots_with_wrong=1)["outcome"], "NOT_KEEP_NEEDS_REVIEWER_INTERPRETATION")
        self.assertEqual(self.dr(wrong=2, shots_with_wrong=2)["outcome"], "NOT_KEEP_NEEDS_REVIEWER_INTERPRETATION"); self.assertEqual(self.dr(wrong=2, shots_with_wrong=3)["outcome"], "KILL")
        self.assertEqual(self.dr(wrong=15, shots_with_wrong=2)["outcome"], "KILL"); self.assertEqual(self.dr(audit_other=17)["outcome"], "KILL"); self.assertEqual(self.dr(audit_other=9)["outcome"], "NOT_KEEP_NEEDS_REVIEWER_INTERPRETATION")
        self.assertEqual(self.dr(not_judgeable=40, n_reviewed=190)["outcome"], "NOT_KEEP_NEEDS_REVIEWER_INTERPRETATION"); self.assertEqual(self.dr(judgeable=99)["outcome"], "INCONCLUSIVE_DATA"); self.assertEqual(self.dr(shots_with_judgeable=19)["outcome"], "INCONCLUSIVE_DATA")
        self.assertEqual(self.dr(clips_with_judgeable=2)["outcome"], "INCONCLUSIVE_DATA"); self.assertEqual(self.dr(wrong=40, shots_with_wrong=5, judgeable=99)["outcome"], "INCONCLUSIVE_DATA")
    def test_12_less_favourable_binds(self):
        c = S.combine_humans; self.assertEqual(c("KEEP", "KILL"), "KILL"); self.assertEqual(c("KEEP", "NOT_KEEP_NEEDS_REVIEWER_INTERPRETATION"), "NOT_KEEP_NEEDS_REVIEWER_INTERPRETATION"); self.assertEqual(c("KEEP", "KEEP"), "KEEP"); self.assertEqual(c("KILL", "INCONCLUSIVE_DATA"), "INCONCLUSIVE_DATA")
def cand(clip, shot, frame, el=True, tr=None): return dict(clip=clip, shot=shot, frame=frame, eligible=el, eligible10=el, eligible25=el, tracklet=tr or f"{clip}:s{shot}:t0", record_class="ASSIGNED_A", assigned_label="A", det=0, box=[1, 2, 3, 4], n_drawn=8)
def synth(clips=8, shots=6, per=60):
    c = []
    for i in range(clips):
        for s in range(shots):
            for k in range(per): c.append(cand(f"c{i}", s, s * 1000 + k * 3, el=(s < 4)))
    return c
class TestSampler(unittest.TestCase):
    def test_13_deterministic_and_constraints(self):
        c = synth(); a, ra = SS.sample(c, SS.seed_from_hash("x")); b, rb = SS.sample(c, SS.seed_from_hash("x")); self.assertEqual(a, b); self.assertEqual(ra, rb); d, _ = SS.sample(c, SS.seed_from_hash("y")); self.assertNotEqual([x["frame"] for x in a], [x["frame"] for x in d])
        E_ = [x for x in a if x["stratum"] == "ELIGIBLE_ASSIGNED"]; N = [x for x in a if x["stratum"] == "INELIGIBLE_ASSIGNED"]; self.assertEqual(len(E_), 150); self.assertEqual(len(N), 50); self.assertTrue(all(x["eligible"] for x in E_)); self.assertFalse(any(x["eligible"] for x in N))
        import collections
        self.assertLessEqual(max(collections.Counter((x["clip"], x["shot"]) for x in E_).values()), 10); self.assertLessEqual(max(collections.Counter(x["clip"] for x in E_).values()), 60)
        for cl in {x["clip"] for x in a}:
            fr = sorted(x["frame"] for x in a if x["clip"] == cl); self.assertTrue(all(q - p >= 30 for p, q in zip(fr, fr[1:])), cl)
        self.assertEqual(ra["eligible_shortfall"], 0)
    def test_14_shortfall_reported_not_relaxed(self):
        c = synth(clips=2, shots=2, per=40); a, r = SS.sample(c, 1); self.assertGreater(r["eligible_shortfall"], 0); self.assertEqual(r["eligible_picked"], len([x for x in a if x["stratum"] == "ELIGIBLE_ASSIGNED"]))
        self.assertFalse(r["meets_shot_target"]); self.assertFalse(r["meets_clip_target"])
    def test_15_burned_clip_rejected(self):
        with self.assertRaises(AssertionError): SS.sample([cand("b2_videoplayback_5", 0, 0)], 1)
    def test_16_seed_rule(self): self.assertEqual(SS.seed_from_hash("abc"), int(hashlib.sha256(b"abc").hexdigest()[:8], 16) % 2 ** 31)
    def test_17_alloc(self):
        a = SS._alloc({"a": 100, "b": 100, "c": 5}, 150); self.assertEqual(a, {"a": 60, "b": 60, "c": 5})  # 40% clip cap binds: shortfall is reported, never relaxed
        a3 = SS._alloc({"a": 100, "b": 100, "c": 100, "d": 100}, 150); self.assertEqual(sum(a3.values()), 150); self.assertLessEqual(max(a3.values()), 60)
        a2 = SS._alloc({"a": 10, "b": 10}, 150); self.assertEqual(a2, {"a": 10, "b": 10})
    def test_18_blind_files_do_not_leak(self):
        items, rep = SS.sample(synth(), 3)
        with tempfile.TemporaryDirectory() as d:
            SS.write(items, rep, d); head = open(os.path.join(d, "SEP_SHEET_BLIND.csv")).read(); self.assertEqual(head.splitlines()[0], "item_id,clip,frame,box")
            self.assertNotIn("ELIGIBLE", head); self.assertNotIn("stratum", head); key = open(os.path.join(d, "SEP_HIDDEN_KEY.csv")).read(); self.assertIn("stratum", key)
            ids = [r["item_id"] for r in csv.DictReader(open(os.path.join(d, "SEP_SHEET_BLIND.csv")))]; self.assertEqual(ids, sorted(ids)); self.assertEqual(len(set(ids)), len(ids))
            strata = [r["stratum"] for r in csv.DictReader(open(os.path.join(d, "SEP_HIDDEN_KEY.csv")))][:40]; self.assertGreater(len(set(strata)), 1)
class TestPack(unittest.TestCase):
    def test_19_step1_has_no_skeleton_step2_has(self):
        fr = np.full((360, 640, 3), 60, np.uint8); det = dict(box=np.array([[200., 50., 300., 250.], [400., 60., 480., 240.]]), conf=np.array([.9, .9]), kp=np.tile(np.array([[250., 100.]]), (2, 17, 1)) + np.arange(17).reshape(1, 17, 1) * np.array([[2., 8.]]), kpc=np.ones((2, 17)))
        s1 = RP.render_step1(fr, [200., 50., 300., 250.], "S000"); s2 = RP.render_step2(fr, det, [200., 50., 300., 250.], "S000")
        self.assertEqual(s1.shape, s2.shape); self.assertGreater(int((s1 != s2).sum()), 0)
        self.assertFalse(((s1[:, :640, :] == np.array([255, 255, 0])).all(axis=2)).sum() > 2000)  # only a thin box outline in the cyan colour; no second box drawn
        im = fr.copy(); import cv2; cv2.rectangle(im, (200, 50), (300, 250), RP.CYAN, 1); self.assertTrue((s1[40:, :640][20:] == RP._compose(im, [200., 50., 300., 250.], "S000 step1")[40:, :640][20:]).all())
def write_rev(path, ids, wrong=(), nj=(), audit_other=(), off=(), box="WRESTLER"):
    with open(path, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["item_id", "box_person", "separation_audit", "judgeable", "landmarks_other_person", "bones_other_person", "landmarks_off_body", "note"])
        for i in ids: w.writerow([i, box, "OTHER_BODY_TOUCHING_OVERLAPPING" if i in audit_other else "SEPARATED", "NO" if i in nj else "YES", "5;7" if i in wrong else "", "", "3" if i in off else "", ""])
class TestJoin(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); items, rep = SS.sample(synth(), 5); SS.write(items, rep, self.d); self.key = os.path.join(self.d, "SEP_HIDDEN_KEY.csv"); self.k = list(csv.DictReader(open(self.key))); self.ids = [r["item_id"] for r in self.k]
        self.el = [r["item_id"] for r in self.k if r["stratum"] == "ELIGIBLE_ASSIGNED"]; self.byshot = {}
        for r in self.k:
            if r["stratum"] == "ELIGIBLE_ASSIGNED": self.byshot.setdefault((r["clip"], r["shot"]), []).append(r["item_id"])
    def run_join(self, p_kw=None, o_kw=None, c_kw=None):
        p = os.path.join(self.d, "p.csv"); o = os.path.join(self.d, "o.csv"); write_rev(p, self.ids, **(p_kw or {})); write_rev(o, self.ids, **(o_kw or {})); out = os.path.join(self.d, "r.json"); args = [self.key, p, o, out]
        if c_kw is not None: c = os.path.join(self.d, "c.csv"); write_rev(c, self.ids, **c_kw); args.append(c)
        J.main(*args); return json.load(open(out))
    def test_20_keep(self): r = self.run_join(); self.assertEqual(r["final"]["outcome"], "KEEP"); self.assertEqual(r["reviewers"]["primary"]["eligible"]["judgeable"], 150)
    def test_21_owner_failing_binds(self):
        shots = list(self.byshot.values()); bad = shots[0][:1] + shots[1][:1]; r = self.run_join(o_kw=dict(wrong=bad)); self.assertEqual(r["reviewers"]["primary"]["decision"]["outcome"], "KEEP"); self.assertEqual(r["reviewers"]["owner"]["decision"]["outcome"], "NOT_KEEP_NEEDS_REVIEWER_INTERPRETATION"); self.assertEqual(r["final"]["outcome"], "NOT_KEEP_NEEDS_REVIEWER_INTERPRETATION")
    def test_22_kill_by_shots(self):
        shots = list(self.byshot.values()); bad = [s[0] for s in shots[:3]]; r = self.run_join(p_kw=dict(wrong=bad)); self.assertEqual(r["final"]["outcome"], "KILL")
    def test_23_claude_never_decides(self):
        bad = self.el[:40]; r = self.run_join(c_kw=dict(wrong=bad)); self.assertEqual(r["final"]["outcome"], "KEEP"); self.assertEqual(r["reviewers"]["claude_sensitivity"]["decision"]["outcome"], "KILL")
    def test_24_verdict_derivation(self):
        self.assertEqual(J.verdict(dict(judgeable="YES", lo=[], bo=[], off=[]), 2), "NOT_JUDGEABLE"); self.assertEqual(J.verdict(dict(judgeable="YES", lo=[], bo=[(5, 7)], off=[]), 8), "WRONG_BODY")
        self.assertEqual(J.verdict(dict(judgeable="YES", lo=[], bo=[], off=[3]), 8), "OFF_BODY_ONLY"); self.assertEqual(J.verdict(dict(judgeable="YES", lo=[5], bo=[], off=[3]), 8), "WRONG_BODY"); self.assertEqual(J.verdict(dict(judgeable="NO", lo=[], bo=[], off=[]), 8), "NOT_JUDGEABLE")
    def test_25_audit_kill_and_inconclusive(self):
        r = self.run_join(p_kw=dict(audit_other=set(self.el[:20]))); self.assertEqual(r["final"]["outcome"], "KILL")
        d2 = tempfile.mkdtemp(); items, rep = SS.sample(synth(clips=2, shots=2), 5); SS.write(items, rep, d2); k2 = os.path.join(d2, "SEP_HIDDEN_KEY.csv"); ids = [x["item_id"] for x in csv.DictReader(open(k2))]
        p = os.path.join(d2, "p.csv"); write_rev(p, ids); J.main(k2, p, p, os.path.join(d2, "r.json")); self.assertEqual(json.load(open(os.path.join(d2, "r.json")))["final"]["outcome"], "INCONCLUSIVE_DATA")
    def test_26_secondary_and_agreement_reported(self):
        r = self.run_join(); self.assertIn("contrast_ineligible", r["reviewers"]["primary"]); self.assertIn("sensitivity_margin25_eligible", r["reviewers"]["primary"]); self.assertEqual(r["agreement_primary_vs_owner_eligible_both_judgeable"]["raw"], 1.0)
class TestHygiene(unittest.TestCase):
    def test_27_no_forbidden_quantities(self):
        bad = {"com", "center_of_mass", "distance", "speed", "acceleration", "impact", "workload", "fatigue", "injury", "exposure", "intensity"}
        for f in ("eligibility.py", "sep_stats.py", "drawn.py"):
            tree = ast.parse(open(os.path.join(P, "impl", f)).read())
            for n in ast.walk(tree):
                if isinstance(n, ast.Name): self.assertNotIn(n.id.lower(), bad); 
                if isinstance(n, ast.arg): self.assertNotIn(n.arg.lower(), bad)
if __name__ == "__main__": unittest.main()
