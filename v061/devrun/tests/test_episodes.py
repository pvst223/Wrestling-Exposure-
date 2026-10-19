import os, sys, unittest, random
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, REPO)
from v061.devrun import episodes as E
def cands(n_shots, per_shot, gap=100):
    return [dict(frame=s * 1000 + i * gap, det=0, tid=f"t{s}_{i}", shot=s, box_h=100.0 + (i % 3)) for s in range(n_shots) for i in range(per_shot)]
class T(unittest.TestCase):
    def valid(self, seeds, m, min_shots):
        self.assertEqual(len(seeds), m); self.assertGreaterEqual(len({s["shot"] for s in seeds}), min_shots)
        for s in {x["shot"] for x in seeds}: self.assertLessEqual(sum(1 for x in seeds if x["shot"] == s), 2)
        fr = sorted(x["frame"] for x in seeds); self.assertTrue(all(b - a >= 60 for a, b in zip(fr, fr[1:])))
    def test_strict_when_feasible(self):
        r = E.select_seeds("k", cands(5, 4)); self.assertEqual((r["status"], r["rule"]), ("OK", "STRICT_4")); self.valid(r["seeds"], 4, 2)
    def test_relaxed_3_when_two_shots_one_crop_short(self):
        c = [dict(frame=0, det=0, tid="a", shot=0, box_h=100.), dict(frame=100, det=0, tid="b", shot=0, box_h=100.), dict(frame=5000, det=0, tid="c", shot=1, box_h=100.)]
        r = E.select_seeds("k", c); self.assertEqual(r["rule"], "RELAXED_3"); self.valid(r["seeds"], 3, 1)
    def test_relaxed_2_single_shot(self):
        r = E.select_seeds("k", cands(1, 5)); self.assertEqual(r["rule"], "RELAXED_2"); self.valid(r["seeds"], 2, 1)
    def test_insufficient(self):
        c = [dict(frame=0, det=0, tid="a", shot=0, box_h=100.), dict(frame=10, det=0, tid="b", shot=0, box_h=100.)]
        self.assertEqual(E.select_seeds("k", c)["status"], "INSUFFICIENT_SEEDS"); self.assertEqual(E.select_seeds("k", [])["status"], "NO_ELIGIBLE")
    def test_deterministic_and_k_varies(self):
        c = cands(6, 6); a = E.select_seeds("x|k0", c); b = E.select_seeds("x|k0", c); self.assertEqual(a, b)
        self.assertGreater(len({tuple((s["tid"]) for s in E.select_seeds(f"x|k{k}", c)["seeds"]) for k in range(5)}), 1)
    def test_median_rule(self):
        c = cands(4, 4); r = E.select_seeds("k", c); med = sorted(x["box_h"] for x in c)[len(c) // 2 - 1: len(c) // 2 + 1]
        import statistics; m = statistics.median(x["box_h"] for x in c); self.assertTrue(all(s["box_h"] >= m for s in r["seeds"]))
    def test_parity_with_frozen_strict_selector(self):
        sys.path.insert(0, os.path.join(REPO, "v06", "tools"))
        try: import phase1_structure as PS
        except Exception as e: self.skipTest(f"LIVE parity: frozen phase1_structure not importable ({e})")
        PS.MIN_SHOTS = getattr(PS, "MIN_SHOTS", 2); PS.MAX_PER_SHOT = getattr(PS, "MAX_PER_SHOT", 2)
        for ns, ps in ((5, 4), (3, 6), (8, 2)):
            c = cands(ns, ps); ref = PS.select_target_seeds("clipX", "idY", c); mine = E.select_seeds(f"{PS.EPISODE_SEED}|clipX|idY|target", c)
            self.assertEqual([s["tid"] for s in ref["seeds"]], [s["tid"] for s in mine["seeds"]]); self.assertEqual(ref["status"], mine["status"])
    def test_candidate_structure_excludes_seeds_and_maps_y(self):
        lab = {"t1": dict(person_class="WRESTLER", wrestler_id="a"), "t2": dict(person_class="WRESTLER", wrestler_id="b"), "t3": dict(person_class="REFEREE", wrestler_id=""), "t4": dict(person_class="UNLABELABLE", wrestler_id=""), "t5": dict(person_class="RINGSIDE_STAFF", wrestler_id=""), "t6": dict(person_class="WRESTLER", wrestler_id="c")}
        tr = {t: dict(shot=i) for i, t in enumerate(lab)}
        s = E.candidate_structure(lab, tr, "a", "b", {"t2"}); self.assertEqual({x["tid"]: (x["truth"], x["y"]) for x in s}, {"t1": ("a", 0), "t3": ("REFEREE", 2), "t5": ("STAFF", 2), "t6": ("c", 2)})
if __name__ == "__main__": unittest.main()
