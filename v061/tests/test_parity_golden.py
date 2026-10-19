"""REQUIRED self-contained parity tests: compare the V0.6.1 code with stored outputs of the FROZEN code (fixtures/parity_golden.json, generated read-only by fixtures/make_parity_fixtures.py). Need only numpy/scipy; no frozen sources, no torch."""
import unittest, json, os
import numpy as np
import _path
from v061.impl import decision_rule as R, units as U
G = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "parity_golden.json")))
class T(unittest.TestCase):
    def test_rule_matches_frozen_exploratory_on_all_20_points(self):
        P = np.array(G["rule"]["P"]); self.assertEqual(len(P), 4000); self.assertEqual(len(G["rule"]["codes"]), 20)
        for k, ref in G["rule"]["codes"].items():
            tg, dl = (float(x) for x in k.split("|")); self.assertTrue((R.decide(P, tg, dl)[0] == np.array(ref)).all(), k)
    def test_units_match_frozen_v06(self):
        rows = [dict(clip="c", **r) for r in G["units"]["rows"]]; self.assertEqual(U.table_metrics(U.unit_table([(tuple(G["units"]["targets"]), rows)])), G["units"]["expected_table_metrics"])
    def test_fixture_provenance_recorded(self):
        for k in ("frozen_exploratory_check_v061_sha256", "frozen_phase1_run_sha256"): self.assertEqual(len(G["provenance"][k]), 64)
if __name__ == "__main__": unittest.main()
