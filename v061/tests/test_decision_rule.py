import unittest, importlib.util, os, numpy as np
import _path
from v061.impl import decision_rule as R
class T(unittest.TestCase):
    def test_basic(self):
        d = R.decide_one
        self.assertEqual(d(.8, .1, .1, .5, .05), "ACCEPT_A"); self.assertEqual(d(.1, .8, .1, .5, .05), "ACCEPT_B")
        self.assertEqual(d(.2, .2, .6, .5, .05), "REJECT_NONTARGET"); self.assertEqual(d(.45, .45, .1, .5, .05), "ABSTAIN_AMBIGUOUS")
    def test_gate_boundary_inclusive(self):   # g == tau_g passes (reject only if g < tau_g)
        self.assertEqual(d := R.decide_one(.375, .125, .5, .5, .05), "ACCEPT_A"); self.assertEqual(R.decide_one(.374, .125, .501, .5, .05), "REJECT_NONTARGET")
    def test_delta_boundary(self):   # q == 0.5+delta accepts (exactly representable case)
        self.assertEqual(R.decide_one(.75, .25, 0., .5, .25), "ACCEPT_A"); self.assertEqual(R.decide_one(.25, .75, 0., .5, .25), "ACCEPT_B"); self.assertEqual(R.decide_one(.5, .5, 0., .5, .25), "ABSTAIN_AMBIGUOUS")
    def test_tie_always_abstains_with_delta_ge_005(self):
        for tg, dl in R.GRID_L1: self.assertEqual(R.decide_one(.3, .3, .4, min(tg, .6), dl), "ABSTAIN_AMBIGUOUS" if .6 >= min(tg, .6) else "REJECT_NONTARGET")
    def test_fail_closed(self):
        for p in ([np.nan, .5, .5], [np.inf, 0, 0], [0, 0, 1], [1e-13, 1e-13, 1 - 2e-13], [-0.2, 0.7, 0.5], [1.2, -.1, -.1], [.3, .3, .3]):
            code, bad, g, q = R.decide(np.array([p]), .5, .05); self.assertEqual(int(code[0]), R.REJECT_NONTARGET, p); self.assertTrue(bad[0], p)
    def test_grids_fixed(self):
        self.assertEqual(len(R.GRID_L1), 20); self.assertEqual(sorted({t for t, _ in R.GRID_L1}), [.5, .6, .7, .8, .9]); self.assertEqual(sorted({d for _, d in R.GRID_L1}), [.05, .1, .2, .3])
        self.assertEqual(len(R.GRID_B0), 20); self.assertEqual(sorted({t for t, _ in R.GRID_B0}), [.3, .4, .5, .6, .7]); self.assertEqual(sorted({m for _, m in R.GRID_B0}), [0., .02, .05, .1])
    def test_param_validation(self):
        for a in ((0., .05), (1.1, .05), (.5, -.01), (.5, .5)):
            with self.assertRaises(ValueError): R.decide(np.array([[.5, .3, .2]]), *a)
        with self.assertRaises(ValueError): R.decide(np.zeros((3, 2)), .5, .05)
    def test_monotone_in_tau_and_delta(self):
        rng = np.random.default_rng(0); p = rng.dirichlet([1, 1, 1], 500)
        acc = lambda tg, dl: (R.decide(p, tg, dl)[0] <= 1)
        for dl in (.05, .1, .2, .3): self.assertTrue(all((acc(.9, dl) <= acc(.5, dl))))
        for tg in (.5, .9): self.assertTrue(all((acc(tg, .3) <= acc(tg, .05))))
    def test_live_parity_with_exploratory_check(self):
        """Rule parity with the frozen exploratory implementation (read-only import) on valid softmax outputs, all 20 grid points."""
        pth = os.path.join(_path.REPO, "v061", "exploratory_v1", "exploratory_check_v061.py")
        if not os.path.exists(pth): self.skipTest("LIVE parity: frozen exploratory source absent from this package (golden parity in test_parity_golden is the required check)")
        spec = importlib.util.spec_from_file_location("expl", pth); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        rng = np.random.default_rng(7); P = np.concatenate([rng.dirichlet([.5, .5, .5], 2000), rng.dirichlet([3, 3, 1], 2000)])
        names = {"A": R.ACCEPT_A, "B": R.ACCEPT_B, "REJECT": R.REJECT_NONTARGET, "ABSTAIN": R.ABSTAIN_AMBIGUOUS}
        for tg, dl in R.GRID_L1:
            code = R.decide(P, tg, dl)[0]
            ref = np.array([names[m.two_stage_label(a, b, c, tg, dl)] for a, b, c in P]); self.assertTrue((code == ref).all(), (tg, dl))
if __name__ == "__main__": unittest.main()
