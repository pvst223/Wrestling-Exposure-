"""Parity of standalone unit/metric code with frozen V0.6 phase1_run (read-only import; skipped if torch is unavailable)."""
import unittest, sys, os, numpy as np
import _path
class T(unittest.TestCase):
    def test_parity(self):
        try: import torch  # noqa
        except Exception: self.skipTest("torch unavailable")
        sys.path.insert(0, os.path.join(_path.REPO, "v06", "tools"))
        try: import phase1_run as RUN
        except Exception as e: self.skipTest(f"v06 tools not importable: {e}")
        from v061.impl import units as U
        rng = np.random.default_rng(3); truths = ["a", "b", "REFEREE", "SPECTATOR", "RINGSIDE_STAFF", "Other Guy"]; rows_new = []; rows_old = []
        for i in range(300):
            t = truths[rng.integers(0, 6)]; shot = int(rng.integers(0, 4)); acc = ["", "a", "b"][rng.integers(0, 3)]
            rows_new.append(dict(clip="c", shot=shot, truth=t, accepted=acc)); rows_old.append(dict(clip_id="c", shot=shot, truth_id=t, accepted_role=acc))
        ep = dict(A="a", B="b"); Un = U.unit_table([(("a", "b"), rows_new)]); Uo = RUN.unit_table([(ep, rows_old)])
        self.assertEqual(U.table_metrics(Un), RUN.table_metrics(Uo)); self.assertEqual(sorted(Un), sorted(Uo))
if __name__ == "__main__": unittest.main()
