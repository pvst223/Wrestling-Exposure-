import os, sys, unittest, tempfile, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, REPO)
from v061.devrun2 import secondary_run as S2
from v061.impl import evaluate as E
def ep(P, truths, A="a", B="b", clip="c"):
    return dict(id="e", targets=(A, B), clip=clip, rows=[dict(clip=clip, shot=i, truth=t) for i, t in enumerate(truths)], P=np.array(P, float))
class T(unittest.TestCase):
    def test_old_rule_matches_argmax_with_floor(self):
        e = ep([[.7, .2, .1], [.2, .7, .1], [.3, .3, .4], [.45, .4, .15], [.2, .2, .6]], ["a", "b", "REFEREE", "a", "REFEREE"])
        acc = [r["accepted"] for r in S2.old_rule_rows(e, 0.5)]; self.assertEqual(acc, ["a", "b", "", "", ""])
        acc = [r["accepted"] for r in S2.old_rule_rows(e, 0.4)]; self.assertEqual(acc, ["a", "b", "", "a", ""])   # nontarget argmax (.4 of .3,.3,.4) never accepted
    def test_old_rule_failclosed_nan(self):
        self.assertEqual(S2.old_rule_rows(ep([[np.nan, .5, .5]], ["a"]), .4)[0]["accepted"], "")
    def test_dist_summary(self):
        d = S2.dist_summary([0, 1, 2, np.nan, 3, 4]); self.assertEqual(d["n"], 5); self.assertEqual(d["median"], 2.0); self.assertIsNone(S2.dist_summary([]))
    def test_breakdown_confusion(self):
        e = ep([[.9, .05, .05], [.05, .9, .05], [.1, .85, .05], [.02, .02, .96], [.45, .45, .1]], ["a", "a", "b", "a", "b"])
        bd = S2.ab_breakdown([e], (0.5, 0.1))["e"]["confusion"]
        self.assertEqual(bd, {"true_a->accepted_as_a": 1, "true_a->accepted_as_b": 1, "true_b->accepted_as_b": 1, "true_a->rejected_at_gate": 1, "true_b->abstained": 1})
    def test_calibration_transfer_shapes(self):
        P = np.array([[.9, .05, .05], [.05, .9, .05], [.02, .02, .96]]); y = np.array([0, 1, 2]); e = ep(P, ["a", "b", "REFEREE"])
        ct = S2.calibration_transfer([dict(ep=dict(y=y), P=P)], [e]); self.assertEqual(ct["training_episodes_in_sample"]["ab_auroc"], 1.0); self.assertEqual(ct["out_of_fold"]["g"]["n"], 2)
    def test_groups_keep_component_together(self):
        eps = [dict(clip="x"), dict(clip="y"), dict(clip="z")]; g = S2.groups_of(eps, {"x": "A", "y": "A", "z": "B"}); self.assertEqual([len(x) for x in g], [2, 1])
    def test_preflight_requires_dr2(self):
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, "AUDIT_LEDGER.jsonl"), "w").write(json.dumps({"id": "X"}) + "\n")
            with self.assertRaises(SystemExit): S2.preflight(d, os.path.join(d, "r.json"))
    def test_fixed_param_is_dr1_point(self): self.assertEqual(S2.FIXED_PARAM, (0.9, 0.1))
class T2(unittest.TestCase):
    def test_analyse_end_to_end_synthetic(self):
        rng = np.random.default_rng(0); base = {"a": [.8, .1, .1], "b": [.1, .8, .1], "REFEREE": [.03, .03, .94]}
        def mk(i, clip):
            tr = [["a", "b", "REFEREE"][j % 3] for j in range(60)]; P = np.array([np.clip(np.array(base[t]) + rng.normal(0, .03, 3), .001, None) for t in tr]); P = P / P.sum(1, keepdims=True)
            return dict(id=f"e{i}", targets=("a", "b"), clip=clip, rows=[dict(clip=clip, shot=j % 4, truth=t) for j, t in enumerate(tr)], P=P)
        L = [mk(0, "c1"), mk(1, "c2"), mk(2, "c3")]; comp = {"c1": "F1", "c2": "F2", "c3": "F2"}
        B0 = S2.grid_pts(L, S2.groups_of(L, comp), lambda e, tau, mg: [dict(clip=r["clip"], shot=r["shot"], truth=r["truth"], accepted=("a" if r["truth"] == "a" else "")) for r in e["rows"]], [(0.5, 0.0)])
        out = S2.analyse(L, comp, B0, 3, B=50); self.assertEqual(len(out["grid"]), 20); self.assertIn("fixed_point", out); self.assertEqual(len(out["grid"][0]["fold_coverages"]), 2)
        self.assertGreater(out["fixed_point"]["gate_auroc"], .99); self.assertIn("reselected_point", out)
        ab = S2.grid_pts(L, S2.groups_of(L, comp), lambda e, tau: S2.old_rule_rows(e, tau), [(t,) for t in S2.OLD_FLOOR_GRID]); self.assertEqual(len(ab), 5)
if __name__ == "__main__": unittest.main()
