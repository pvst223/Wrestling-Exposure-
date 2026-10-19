import unittest, json, numpy as np
import _path
from v061.impl import selection as S, evaluate as E, units as U, decision_rule as R
def mk(id, clip, seed, n=80, A="a", B="b"):
    rng = np.random.default_rng(seed); rows = []; P = []
    base = {"a": [.8, .1, .1], "b": [.1, .8, .1], "REFEREE": [.03, .03, .94], "SPECTATOR": [.05, .05, .9]}
    for i in range(n):
        t = ["a", "b", "REFEREE", "SPECTATOR"][i % 4]; rows.append(dict(clip=clip, shot=i % 3, truth=t)); p = np.clip(np.array(base[t]) + rng.normal(0, .03, 3), .001, None); P.append(p / p.sum())
    return dict(id=id, targets=(A, B), clip=clip, rows=rows, P=np.array(P))
class T(unittest.TestCase):
    def test_select_ties(self):
        pts = [dict(param=(1, 1), coverage=.5, fta=.2), dict(param=(0, 1), coverage=.5, fta=.2), dict(param=(2, 0), coverage=.6, fta=.2), dict(param=(3, 0), coverage=.3, fta=0.)]
        self.assertEqual(S.select_point(pts, .5)["param"], (2, 0)); self.assertEqual(S.select_point(pts[:2], .5)["param"], (0, 1)); self.assertIsNone(S.select_point(pts, .9))
        self.assertEqual(S.select_point(pts, .3)["param"], (3, 0))  # lowest FTA among coverage >= .3
    def test_fold_constraint(self):
        pts = [dict(param=(0, 0), coverage=.6, fta=0., fold_coverages=[.9, .1]), dict(param=(1, 0), coverage=.5, fta=.1, fold_coverages=[.5, .5])]
        self.assertEqual(S.select_point(pts, .5)["param"], (1, 0)); self.assertEqual(S.joint_cstar({"x": pts, "y": pts}), 0.5)
    def test_joint_cstar_none(self):
        self.assertIsNone(S.joint_cstar({"x": [dict(param=(0,), coverage=.05, fta=0.)], "y": [dict(param=(0,), coverage=.9, fta=0.)]}))
    def test_end_to_end_synthetic_deterministic(self):
        d, t1, t2 = mk("d", "c1", 1), mk("t1", "c2", 2), mk("t2", "c3", 3)
        pts = E.grid_points([d]); self.assertEqual(len(pts), 20); c = S.joint_cstar({"L1": pts}); self.assertEqual(c, .5)
        sel = S.select_point(pts, c); self.assertEqual(sel["fa_units"], 0)
        a = E.diagnostics([t1, t2], *sel["param"], seed=5, B=200); b = E.diagnostics([t1, t2], *sel["param"], seed=5, B=200)
        self.assertEqual(json.dumps(a, sort_keys=True, default=str), json.dumps(b, sort_keys=True, default=str)); self.assertEqual(a["label"], "V0.6.1 DEVELOPMENT / HYPOTHESIS CHECK ONLY")
        self.assertGreater(a["target_gate"]["auroc"], .99); self.assertGreater(a["ab_assignment"]["auroc"], .99); self.assertEqual(a["ab_assignment"]["accepted_as_wrong_target"], 0)
        self.assertEqual(a["false_target_acceptance"]["nontarget_candidates_accepted"], 0); self.assertNotIn("outcome_class", a)
    def test_abstain_vs_reject_separated(self):
        ep = dict(id="e", targets=("a", "b"), clip="c", rows=[dict(clip="c", shot=0, truth="a"), dict(clip="c", shot=0, truth="b"), dict(clip="c", shot=1, truth="REFEREE")], P=np.array([[.45, .45, .1], [.1, .8, .1], [.02, .02, .96]]))
        d = E.diagnostics([ep], .5, .05, 1, B=50); self.assertEqual(d["decision_decomposition_candidates"]["TARGET"], {"ABSTAIN_AMBIGUOUS": 1, "ACCEPT_B": 1}); self.assertEqual(d["decision_decomposition_candidates"]["REFEREE"], {"REJECT_NONTARGET": 1})
    def test_false_accept_and_swap_counted(self):
        ep = dict(id="e", targets=("a", "b"), clip="c", rows=[dict(clip="c", shot=0, truth="a"), dict(clip="c", shot=1, truth="REFEREE")], P=np.array([[.05, .9, .05], [.9, .05, .05]]))
        d = E.diagnostics([ep], .5, .05, 1, B=50); self.assertEqual(d["ab_assignment"]["accepted_as_wrong_target"], 1); self.assertEqual(d["unit_metrics"]["fa_units"], 2); self.assertEqual(d["false_target_acceptance"]["nontarget_candidates_accepted"], 1)
    def test_cp_and_paired(self):
        self.assertEqual(U.clopper_pearson(0, 0), (None, None)); lo, hi = U.clopper_pearson(0, 10); self.assertEqual(lo, 0.0); self.assertAlmostEqual(hi, 0.3084, 3)
        Tb = {1: dict(false=True), 2: dict(false=True), 3: dict(false=False)}; Tl = {1: dict(false=False), 2: dict(false=True), 3: dict(false=True)}
        p = U.paired_sign(Tb, Tl); self.assertEqual((p["b_baseline_only"], p["c_learned_only"], p["both"]), (1, 1, 1)); self.assertEqual(p["one_sided_p_b_gt_c"], .75)
        with self.assertRaises(ValueError): U.paired_sign(Tb, {1: dict(false=False)})
if __name__ == "__main__": unittest.main()
