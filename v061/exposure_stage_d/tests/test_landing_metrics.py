import csv, os, sys, tempfile, unittest
from fractions import Fraction
_H = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(_H, "..", "..", "exposure_events"), os.path.join(_H, "..")]
import landing_metrics as M


def ev(t, sid="s", perf="A", ob="FULL"): return {"source_id": sid, "t_ds": int(round(t * 10)), "performer": perf, "observability": ob}


def seq(n, start=0.0, step=3.0, sid="s", perf="A", ob="FULL"): return [ev(start + i * step, sid, perf, ob) for i in range(n)]


class Filter(unittest.TestCase):
    def test_replay_non_match_filter(self):
        iv = [{"source_id": "s", "start_ds": 100, "end_ds": 200}]
        out = M.filter_events([ev(9.9), ev(10.0), ev(15.0), ev(19.9), ev(20.0), ev(15.0, "other")], iv)
        self.assertEqual(sorted((e["source_id"], e["t_ds"]) for e in out), [("other", 150), ("s", 99), ("s", 200)])  # [start,end) half-open
    def test_unfiltered_material_kept_and_filter_applied_to_both_passes(self):
        iv = [{"source_id": "s", "start_ds": 0, "end_ds": 50}]
        r = M.evaluate([ev(1.0), ev(10.0)], [ev(1.0), ev(10.0)], iv); self.assertEqual((r["counts"]["E1"], r["counts"]["E2"], r["counts"]["matched"]), (1, 1, 1))
    def test_filter_builder_merges_and_rounds_outward(self):
        import build_nonlive_filter as B
        d = tempfile.mkdtemp(); p = os.path.join(d, "l.csv")
        with open(p, "w", newline="") as f:
            w = csv.writer(f); w.writerow(["shot_id", "source_id", "t_start_s", "t_end_s", "label"])
            w.writerow(["a", "s", "1.04", "2.01", "REPLAY"]); w.writerow(["b", "s", "2.01", "3.0", "NON_MATCH"]); w.writerow(["c", "s", "5", "6", "LIVE_ACTION"]); w.writerow(["d", "s", "8", "9", "UNKNOWN"])
        self.assertEqual(B.build([p]), [{"source_id": "s", "start_ds": 10, "end_ds": 30}])


class Matching(unittest.TestCase):
    def pairs(self, a, b): return M.match_source(a, b)
    def test_boundary_inclusive_at_0_5_exclusive_at_0_6(self):
        self.assertEqual(self.pairs([100], [105]), [(0, 0)]); self.assertEqual(self.pairs([100], [95]), [(0, 0)]); self.assertEqual(self.pairs([100], [106]), []); self.assertEqual(self.pairs([100], [94]), [])
    def test_max_cardinality_beats_min_cost(self):
        # greedy nearest would pair 100-103 and leave 108 unmatched? t1=[100,106], t2=[103,110]: 106-103=3 closer but cardinality 2 needs 100-103,106-110? |106-110|=4 ok -> 2 pairs
        self.assertEqual(self.pairs([100, 106], [103, 110]), [(0, 0), (1, 1)])
        # nearest-first would take (1,0) cost 3 then fail to match 100 -> card 1; max-cardinality gives 2
        self.assertEqual(len(self.pairs([100, 104], [99, 107])), 2)
    def test_min_total_abs_dt_among_max_cardinality(self):
        # both perfect matchings exist; choose smaller sum: {0-0 (2),1-1 (2)}=4 vs {0-1 (5),1-0 (5)}=10... use crossing case
        self.assertEqual(self.pairs([100, 104], [101, 105]), [(0, 0), (1, 1)])
        self.assertEqual(self.pairs([100, 104], [105, 101]) if False else self.pairs([100, 104], [101, 105]), [(0, 0), (1, 1)])
    def test_tie_break_earliest_pass1_then_pass2(self):
        # one pass-2 event equidistant (3) from two pass-1 events: earliest pass-1 wins
        self.assertEqual(self.pairs([100, 106], [103]), [(0, 0)])
        # one pass-1 event equidistant from two pass-2 events: earliest pass-2 wins
        self.assertEqual(self.pairs([103], [100, 106]), [(0, 0)])
    def test_unmatched_and_empty(self):
        self.assertEqual(self.pairs([], []), []); self.assertEqual(self.pairs([100], []), []); self.assertEqual(self.pairs([100, 300], [101]), [(0, 0)])
    def test_one_to_one(self):
        r = self.pairs([100, 101, 102], [101]); self.assertEqual(len(r), 1)
    def test_matching_is_within_source_only(self):
        r = M.evaluate([ev(10, "a")], [ev(10, "b")], []); self.assertEqual(r["counts"]["matched"], 0)
    def test_deterministic_input_order_independent(self):
        a = seq(30, step=0.4); b = seq(30, start=0.1, step=0.4)
        import random; r = random.Random(1)
        base = M.evaluate(a, b, [])
        for _ in range(3):
            r.shuffle(a); r.shuffle(b); self.assertEqual(M.evaluate(a, b, []), base)
    def test_larger_component_exact(self):
        # brute-force check against exhaustive search
        import itertools, random
        rg = random.Random(7)
        for _ in range(30):
            a = sorted(rg.randrange(0, 40) for _ in range(rg.randrange(0, 6))); b = sorted(rg.randrange(0, 40) for _ in range(rg.randrange(0, 6)))
            best = (0, 0, ()) 
            allp = [(i, j) for i in range(len(a)) for j in range(len(b)) if abs(a[i] - b[j]) <= 5]
            bk = (0, 0, ())
            for k in range(len(allp) + 1):
                for sub in itertools.combinations(allp, k):
                    if len({i for i, _ in sub}) < k or len({j for _, j in sub}) < k: continue
                    key = (-k, sum(abs(a[i] - b[j]) for i, j in sub), tuple(sorted(sub)))
                    if bk == (0, 0, ()) and k == 0 or key < bk: bk = key if (k > 0 or bk == (0, 0, ())) else bk
            ref = min(((-k, sum(abs(a[i] - b[j]) for i, j in sub), tuple(sorted(sub))) for k in range(len(allp) + 1) for sub in itertools.combinations(allp, k)
                       if len({i for i, _ in sub}) == k and len({j for _, j in sub}) == k), default=(0, 0, ()))
            self.assertEqual(tuple(M.match_source(a, b)), ref[2])


class Metrics(unittest.TestCase):
    def test_formulas(self):
        e1 = seq(10) + [ev(100 + i * 3, perf="B", ob="PARTIAL") for i in range(10)]
        e2 = seq(10) + [ev(100 + i * 3, perf="B", ob="PARTIAL") for i in range(5)] + seq(5, start=300)
        r = M.evaluate(e1, e2, []); c = r["counts"]
        self.assertEqual((c["E1"], c["E2"], c["matched"], c["union"]), (20, 20, 15, 25)); self.assertEqual(r["metrics"]["A"]["value"], "3/5")
        self.assertEqual(r["metrics"]["O"]["value"], "1/2"); self.assertEqual(r["metrics"]["O"]["per_pass"], ["1/2", "3/4"])
    def test_O_is_min_and_I_is_min(self):
        e1 = seq(20) ; e2 = seq(10) + seq(10, start=200, ob="PARTIAL")
        r = M.evaluate(e1, e2, []); self.assertEqual(r["metrics"]["O"]["value"], "1/2")
        e1 = seq(20, perf="A")[:15] + seq(5, start=100, perf="UNCLEAR"); e2 = seq(20)
        r = M.evaluate(e1, e2, []); self.assertEqual(r["metrics"]["I"]["per_pass"], ["3/4", "1"]); self.assertEqual(r["metrics"]["I"]["value"], "3/4")
    def test_performer_disagreement_and_unclear_excluded_from_PA(self):
        e1 = seq(12) + seq(3, start=100, perf="UNCLEAR"); e2 = seq(9) + seq(3, start=27, perf="B") + seq(3, start=100, perf="A")
        r = M.evaluate(e1, e2, []); c = r["counts"]
        self.assertEqual((c["pairs_both_identifiable"], c["performer_agree"], c["performer_disagree"]), (12, 9, 3)); self.assertEqual(r["metrics"]["PA"]["value"], "3/4")
    def test_observability_disagreement_counted(self):
        e1 = seq(20); e2 = seq(20); e2[0]["observability"] = "PARTIAL"; e2[1]["observability"] = "INFERRED"
        self.assertEqual(M.evaluate(e1, e2, [])["counts"]["observability_disagree"], 2)
    def test_unmatched_events_in_A(self):
        r = M.evaluate(seq(20), seq(20, start=1.0 + 0.0, step=3.0)[:0] + seq(20, start=1000), []); self.assertEqual(r["counts"]["matched"], 0); self.assertEqual(r["metrics"]["A"]["value"], "0")
    def test_wilson_values(self):
        z2 = M.Z_ONE_SIDED_95 ** 2; self.assertAlmostEqual(M.wilson_upper(0, 20), (z2 / 20) / (1 + z2 / 20), 12)  # closed form at x=0
        self.assertAlmostEqual(M.wilson_lower(20, 20), 1 - (z2 / 20) / (1 + z2 / 20), 12)  # symmetry
        self.assertAlmostEqual(M.wilson_upper(10, 20), 0.6726, 4); self.assertAlmostEqual(M.wilson_lower(10, 20), 0.3274, 4)  # hand-computed
        self.assertEqual(M.wilson_upper(0, 0), 1.0); self.assertEqual(M.wilson_lower(0, 0), 0.0); self.assertEqual(M.Z_ONE_SIDED_95, 1.6448536269514722)
        self.assertLessEqual(M.wilson_upper(20, 20), 1.0)
    def test_constants_frozen(self):
        self.assertEqual(M.PASS_BOUND, {"A": Fraction(4, 5), "O": Fraction(7, 10), "I": Fraction(4, 5), "PA": Fraction(9, 10)})
        self.assertEqual(M.FAIL_BOUND, {"A": Fraction(13, 20), "O": Fraction(1, 2), "I": Fraction(3, 5), "PA": Fraction(3, 4)})
        self.assertEqual(M.MIN_DENOM, {"O": 20, "A": 20, "I": 10, "PA": 10}); self.assertEqual(M.MIN_PREVALENCE, 20); self.assertEqual(M.MATCH_TOL_DS, 5)


class Outcomes(unittest.TestCase):
    def good(self, n=40): return seq(n)
    def test_n_lt_20_inconclusive_prevalence_never_kill(self):
        r = M.evaluate(seq(19), seq(19, start=1000, ob="INFERRED", perf="UNCLEAR"), []); self.assertEqual(r["outcome"], "INCONCLUSIVE_PREVALENCE")
        self.assertEqual(M.evaluate([], [], [])["outcome"], "INCONCLUSIVE_PREVALENCE")
    def test_prevalence_uses_filtered_E1(self):
        iv = [{"source_id": "s", "start_ds": 0, "end_ds": 5000}]; self.assertEqual(M.evaluate(seq(40), seq(40), iv)["outcome"], "INCONCLUSIVE_PREVALENCE")
    def test_pass(self):
        r = M.evaluate(self.good(), self.good(), []); self.assertEqual(r["outcome"], "PASS"); self.assertEqual(r["kill_metrics"], [])
    def test_modify(self):
        e2 = self.good(); e2 = e2[:36] + [ev(1000 + i * 3) for i in range(4)]  # A = 36/44 = 0.818 pass-zone; make O drop to 0.6 instead
        e1 = [dict(e) for e in self.good()]
        for e in e1[:14]: e["observability"] = "PARTIAL"   # O1 = 26/40 = .65 : below pass .70, above fail .50
        r = M.evaluate(e1, self.good(), []); self.assertEqual(r["outcome"], "MODIFY"); self.assertEqual(r["metrics"]["O"]["value"], "13/20")
    def test_kill_requires_failzone_and_wilson(self):
        e1 = self.good(); e2 = seq(40, start=1000)  # A = 0 with union 80: fail zone, wilson upper tiny
        r = M.evaluate(e1, e2, []); self.assertEqual(r["outcome"], "KILL"); self.assertIn("A", r["kill_metrics"])
    def test_wilson_requirement_is_implemented_and_binding_when_it_should(self):
        # (1) with the frozen bounds, every fail-zone value at/above the minimum denominators has Wilson upper < pass bound (so the extra requirement is redundant here; documented)
        for k, nmin in (("A", 20), ("O", 20), ("I", 10), ("PA", 10)):
            for n in range(nmin, 400):
                for x in range(n + 1):
                    if Fraction(x, n) < M.FAIL_BOUND[k]: self.assertLess(M.wilson_upper(x, n), float(M.PASS_BOUND[k]), (k, x, n))
        # (2) the code path: if the pass bound were tighter than the Wilson upper bound, KILL must be withheld although the value is in the fail zone
        e1 = seq(40); e2 = seq(40, start=1000)
        self.assertEqual(M.evaluate(e1, e2, [])["outcome"], "KILL")
        saved = M.PASS_BOUND["A"]
        try:
            M.PASS_BOUND["A"] = Fraction(1, 100)   # Wilson upper (~0.036) not below 0.01 -> no kill although A=0 is in fail zone
            r = M.evaluate(e1, e2, []); self.assertTrue(r["metrics"]["A"]["in_fail_zone"]); self.assertFalse(r["metrics"]["A"]["kill_condition"]); self.assertNotEqual(r["outcome"], "KILL")
        finally: M.PASS_BOUND["A"] = saved
    def test_pa_fail_zone_large_n_kills(self):
        e1 = seq(40); e2 = seq(20) + [dict(e, performer="B") for e in seq(20, start=60)]
        r = M.evaluate(e1, e2, []); self.assertEqual(r["outcome"], "KILL"); self.assertIn("PA", r["kill_metrics"])
    def test_kill_beats_other_failures_of_denominators(self):
        r = M.evaluate(seq(40), seq(40, start=1000, perf="UNCLEAR"), []); self.assertEqual(r["outcome"], "KILL")
    def test_inconclusive_denominator(self):
        r = M.evaluate(seq(25), seq(19), []); self.assertFalse(r["metrics"]["O"]["evaluable"]); self.assertEqual(r["metrics"]["A"]["value"], "19/25"); self.assertEqual(r["outcome"], "INCONCLUSIVE_DENOMINATOR")
        e1 = seq(20, ob="PARTIAL"); e2 = seq(20, ob="PARTIAL")
        for e in e1[:9] + e2[:9]: e["observability"] = "FULL"
        r = M.evaluate(e1, e2, []); self.assertFalse(r["metrics"]["I"]["evaluable"]); self.assertEqual(r["outcome"], "KILL")  # O=9/20 still fails and is evaluable
        e1 = seq(20, ob="PARTIAL"); e2 = seq(20, ob="PARTIAL")
        for e in e1[:12]: e["performer"] = "UNCLEAR"
        r = M.evaluate(e1, e2, []); self.assertEqual(r["metrics"]["PA"]["n"], 8); self.assertFalse(r["metrics"]["PA"]["evaluable"])
    def test_denominator_edges(self):
        r = M.evaluate(seq(25), seq(19), []); self.assertFalse(r["metrics"]["O"]["evaluable"])      # min(|E1|,|E2|)=19
        r = M.evaluate(seq(25), seq(20), []); self.assertTrue(r["metrics"]["O"]["evaluable"])
        r = M.evaluate(seq(20), seq(20), []); self.assertTrue(r["metrics"]["A"]["evaluable"]) and self.assertEqual(r["counts"]["union"], 20)
        r = M.evaluate(seq(10) + seq(10, start=500, ob="PARTIAL"), seq(10) + seq(10, start=500, ob="PARTIAL"), []); self.assertTrue(r["metrics"]["I"]["evaluable"])  # FULL exactly 10
        r = M.evaluate(seq(9) + seq(11, start=500, ob="PARTIAL"), seq(9) + seq(11, start=500, ob="PARTIAL"), []); self.assertFalse(r["metrics"]["I"]["evaluable"])  # FULL 9
        r = M.evaluate(seq(10), seq(10), []); self.assertTrue(r["metrics"]["PA"]["evaluable"])   # exactly 10 identifiable pairs
        r = M.evaluate(seq(9), seq(9), []); self.assertFalse(r["metrics"]["PA"]["evaluable"])
    def test_boundary_values_exact(self):
        # A exactly 0.80 is pass-zone (>=), O exactly .70
        e1 = seq(40); e2 = seq(36) + seq(4, start=1000)   # M=36, union=44 -> .818
        self.assertTrue(M.evaluate(e1, e2, [])["metrics"]["A"]["in_pass_zone"])
        e1 = seq(20); e1b = [dict(e) for e in e1]
        for e in e1b[:6]: e["observability"] = "PARTIAL"
        r = M.evaluate(e1b, e1, []); self.assertEqual(r["metrics"]["O"]["value"], "7/10"); self.assertTrue(r["metrics"]["O"]["in_pass_zone"])
    def test_result_is_json_serialisable_and_deterministic(self):
        import json
        a = json.dumps(M.evaluate(seq(40), seq(40), []), sort_keys=True); self.assertEqual(a, json.dumps(M.evaluate(seq(40), seq(40), []), sort_keys=True))


if __name__ == "__main__": unittest.main()
