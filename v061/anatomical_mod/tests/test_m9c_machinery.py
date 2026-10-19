"""Synthetic tests of the M9C sampler / pack / join machinery (no real data, no images of real footage)."""
import collections, csv, json, os, random, sys, tempfile, unittest
import numpy as np
try:
    import cv2, scipy  # noqa
except ImportError as e: raise unittest.SkipTest(f"cv2/scipy required: {e}")
HERE = os.path.dirname(os.path.abspath(__file__)); MOD = os.path.dirname(HERE); V = os.path.dirname(MOD)
sys.path[:0] = [os.path.join(V, "anatomical", "tests"), os.path.join(V, "anatomical", "impl"), os.path.join(MOD, "impl"), os.path.join(MOD, "m9c")]
import synth, m9c_sample as S, m9c_join as J, m9c_review_pack as RP
C = S.CLIPS
def pop(n_per_clip, step=7, shots=4, st=0):
    return [dict(clip=c, frame=100 * (k + 1) + st + i * step, shot=i % shots, tracklet=f"{c}:t{i % 2}", box=[0, 0, 10, 10], identity="ACCEPT_A", own_state="OWNERSHIP_UNCERTAIN", reasons=["CONTESTED_LANDMARKS"], record_class="X", merge_guard=False, draw_landmarks=[5, 6, 11, 12])
            for k, c in enumerate(C) for i in range(n_per_clip)]
def pops(n=40, step=40): return {"RELEASED": pop(n, step), "CONTROL_ASSIGNED": [dict(r, draw_landmarks=None, frame=r["frame"] + 1) for r in pop(n, step)], "CONTROL_HARDVETO": [dict(r, draw_landmarks=None, frame=r["frame"] + 2) for r in pop(n, step)]}
class TSample(unittest.TestCase):
    def test_deterministic_and_targets(self):
        P = pops(); a = S.build(P, {}); b = S.build(P, {}); self.assertEqual(json.dumps(a["log"], sort_keys=True, default=str), json.dumps(b["log"], sort_keys=True, default=str))
        self.assertEqual([i["review_id"] for i in a["items"]], [i["review_id"] for i in b["items"]]); self.assertEqual([(i["clip"], i["frame"]) for i in a["items"]], [(i["clip"], i["frame"]) for i in b["items"]])
        c = collections.Counter(i["stratum"] for i in a["items"]); self.assertEqual(dict(c), S.TARGETS); self.assertEqual(len({(i["clip"], i["frame"]) for i in a["items"]}), 120)
    def test_exclusion_radius_15_and_burned(self):
        P = pops(); reviewed = {c: {P["RELEASED"][k * 40 + 5]["frame"]} for k, c in enumerate(C)}; r = S.build(P, reviewed)
        for i in r["items"]:
            for g in reviewed[i["clip"]]: self.assertGreater(abs(i["frame"] - g), 15)
        self.assertTrue(S.is_excluded({"a": {100}}, "a", 115)); self.assertTrue(S.is_excluded({"a": {100}}, "a", 100)); self.assertFalse(S.is_excluded({"a": {100}}, "a", 116)); self.assertFalse(S.is_excluded({"a": {100}}, "b", 100))
    def test_spacing_ladder_relaxes_only_as_needed(self):
        P = pops(n=40, step=40); r = S.build(P, {}); self.assertEqual(r["log"]["strata"]["RELEASED"]["picked_at_gap"], {30: 60})          # ample frames: no relaxation
        dense = pops(n=20, step=7); r2 = S.build(dense, {}); st = r2["log"]["strata"]["RELEASED"]; self.assertEqual(st["n"], 60); self.assertIn(15, st["picked_at_gap"]); self.assertGreaterEqual(st["adjacent_gap_min"], 7)
        tiny = pops(n=20, step=3); r3 = S.build(tiny, {}); self.assertIn(0, r3["log"]["strata"]["RELEASED"]["picked_at_gap"]); self.assertEqual(r3["log"]["strata"]["RELEASED"]["n"], 60)
        for it in r2["items"]:      # gap_level is the strictest level that admitted the pick relative to earlier picks in its clip
            self.assertIn(it["gap_level"], (30, 15, 0))
    def test_clip_imbalance_when_a_clip_is_short(self):
        P = pops(); P["RELEASED"] = [r for r in P["RELEASED"] if not (r["clip"] == C[0] and r["frame"] > 100 + 3 * 40)]; r = S.build(P, {}); st = r["log"]["strata"]["RELEASED"]
        self.assertEqual(st["n"], 60); self.assertLess(st["per_clip"][C[0]], 15); self.assertGreater(st["clip_imbalance"], 0)
    def test_owner_subset(self):
        r = S.build(pops(), {}); ids = {i["review_id"] for i in r["items"]}; oi = r["owner_items"]
        self.assertGreaterEqual(r["log"]["owner_released_n"], 30); self.assertTrue({o["review_id"] for o in oi} <= ids); self.assertEqual(len({o["owner_id"] for o in oi}), len(oi))
        self.assertTrue(all(o["owner_id"] != o["review_id"] for o in oi)); self.assertEqual(collections.Counter(o["stratum"] for o in oi), collections.Counter(S.OWNER_N))
        self.assertNotEqual([o["owner_id"][1:] for o in oi], [o["review_id"][1:] for o in oi])
    def test_big_shortfall_reported_not_hidden(self):
        P = pops(n=5); r = S.build(P, {}); self.assertLess(r["log"]["strata"]["RELEASED"]["n"], 60); self.assertEqual(r["log"]["strata"]["RELEASED"]["target"], 60)
class TPack(unittest.TestCase):
    def test_released_draws_only_listed_landmarks(self):
        d = synth.det_frame([(60, 100)]); fr = np.zeros((200, 200, 3), np.uint8)
        full = RP.render_item(fr, d, d["box"][0].tolist(), None, "M000"); part = RP.render_item(fr, d, d["box"][0].tolist(), [5, 6, 11, 12], "M001")
        self.assertFalse(np.array_equal(full, part)); x, y = [int(v) for v in d["kp"][0][15]]
        win = part[y - 4:y + 5, x - 4:x + 5, :200 - 0]; self.assertFalse(((win[..., 0] == 255) & (win[..., 1] == 255) & (win[..., 2] == 0)).any())     # unreleased ankle: nothing drawn
        x2, y2 = [int(v) for v in d["kp"][0][5]]; w2 = part[y2 - 3:y2 + 4, x2 - 3:x2 + 4]; self.assertTrue(((w2[..., 0] == 255) & (w2[..., 1] == 255) & (w2[..., 2] == 0)).any())    # released shoulder drawn in the same neutral colour
        self.assertFalse(((part[:, :200, 0] == 0) & (part[:, :200, 1] == 140) & (part[:, :200, 2] == 255)).any())                                             # no PARTIAL colour/tag
class TJoin(unittest.TestCase):
    def mk(self, verdicts):
        tmp = tempfile.mkdtemp(); P = pops(); r = S.build(P, {}); rel = [i for i in r["items"] if i["stratum"] == "RELEASED"]
        cols = ["review_id", "owner_id", "stratum", "clip", "tracklet", "frame", "shot", "identity", "own_state", "reasons", "record_class", "merge_guard", "draw_landmarks", "gap_level"]
        own = {o["review_id"]: o["owner_id"] for o in r["owner_items"]}
        with open(os.path.join(tmp, "M9C_HIDDEN_KEY.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
            for i in r["items"]: w.writerow(dict({k: i.get(k, "") for k in cols}, reasons=json.dumps(i["reasons"]), draw_landmarks=json.dumps(i["draw_landmarks"]) if i["draw_landmarks"] else "", owner_id=own.get(i["review_id"], "")))
        with open(os.path.join(tmp, "M9C_OWNER_KEY.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["owner_id", "review_id", "stratum"]); w.writeheader(); [w.writerow(dict(owner_id=o["owner_id"], review_id=o["review_id"], stratum=o["stratum"])) for o in r["owner_items"]]
        ver = {}; relids = [i["review_id"] for i in rel]
        for i in r["items"]:
            ver[i["review_id"]] = dict(verdict="PARTIAL_BUT_USABLE", contact="NO")
        for k, v in verdicts.items(): ver[relids[k]] = dict(verdict=v, contact="YES")
        json.dump(ver, open(os.path.join(tmp, "v.json"), "w")); json.dump(dict(per_clip={c: dict(released=dict(RELEASED_PARTIAL_ANATOMY_A=45)) for c in C}), open(os.path.join(tmp, "p.json"), "w")); return tmp, r, ver
    def test_mechanical_outcomes(self):
        tmp, r, ver = self.mk({}); out = os.path.join(tmp, "o.json"); J.main(tmp, os.path.join(tmp, "v.json"), None, out, os.path.join(tmp, "p.json")); o = json.load(open(out))
        self.assertEqual(o["released"]["contaminated"], 0); self.assertEqual(o["decision"]["outcome"], "KEEP"); self.assertIn("uninformative", o["decision"]["control_note"])   # all-zero case: 2x clause vacuous, flagged for the reviewer
    def test_keep_modify_kill(self):
        base = dict(n=60, judgeable=60, contaminated_frac=0.0, not_judgeable_frac=0.0)
        ctrl = dict(contaminated_frac=0.2)
        self.assertEqual(J.decide(dict(base), {"a": 0}, ctrl, 8.2, 0)["outcome"], "KEEP")
        self.assertEqual(J.decide(dict(base, contaminated_frac=0.05), {"a": 2}, ctrl, 8.2, 2)["outcome"], "KEEP")
        self.assertEqual(J.decide(dict(base, contaminated_frac=0.067), {"a": 2}, ctrl, 8.2, 1)["outcome"], "MODIFY")
        self.assertEqual(J.decide(dict(base, contaminated_frac=0.10), {"a": 2}, ctrl, 8.2, 1)["outcome"], "KILL")
        self.assertEqual(J.decide(dict(base), {"a": 3}, ctrl, 8.2, 1)["outcome"], "MODIFY"); self.assertEqual(J.decide(dict(base), {"a": 0}, ctrl, 4.9, 0)["outcome"], "MODIFY")
        self.assertEqual(J.decide(dict(base, not_judgeable_frac=0.26), {"a": 0}, ctrl, 8.2, 0)["outcome"], "MODIFY")
        self.assertEqual(J.decide(dict(base, judgeable=49), {"a": 0}, ctrl, 8.2, 0)["outcome"], "NOT_KEEP_CRITERION_UNMET_NEEDS_REVIEWER_INTERPRETATION")
        self.assertEqual(J.decide(dict(base, contaminated_frac=0.03), {"a": 1}, dict(contaminated_frac=0.04), 8.2, 1)["outcome"], "NOT_KEEP_CRITERION_UNMET_NEEDS_REVIEWER_INTERPRETATION")   # hard-veto control < 2x released
        d = J.decide(dict(base, contaminated_frac=0.033), {"a": 2}, ctrl, 8.2, 2)["literal_per_landmark_clause"]; self.assertTrue(d["literal_kill_triggered"]); self.assertIn("OPEN INTERPRETATION", d["note"])
    def test_kappa_and_second_reviewer(self):
        pairs = [("CORRECT", "CORRECT")] * 10 + [("CONTAMINATED", "CONTAMINATED")] * 5 + [("PARTIAL_BUT_USABLE", "CONTAMINATED")] * 5; k = J.kappa(pairs)
        self.assertAlmostEqual(k["raw_agreement"], 0.75); po, pe = 0.75, (10 * 10 + 10 * 0 + 5 * 10 + 0) / 400 if False else None
        ca = collections.Counter(a for a, _ in pairs); cb = collections.Counter(b for _, b in pairs); pe = sum(ca[x] * cb[x] for x in J.V4) / 400; self.assertAlmostEqual(k["cohen_kappa"], (0.75 - pe) / (1 - pe)); self.assertEqual(k["table"]["PARTIAL_BUT_USABLE"]["CONTAMINATED"], 5)
        self.assertEqual(J.kappa([("CORRECT", "CORRECT")] * 3)["cohen_kappa"], 1.0)
        tmp, r, ver = self.mk({0: "CONTAMINATED", 1: "CONTAMINATED"}); ow = {}
        for o in r["owner_items"]: ow[o["owner_id"]] = dict(verdict=ver[o["review_id"]]["verdict"])
        any_o = [o for o in r["owner_items"] if o["stratum"] == "RELEASED"][0]; ow[any_o["owner_id"]]["verdict"] = "CONTAMINATED" if ver[any_o["review_id"]]["verdict"] != "CONTAMINATED" else "CORRECT"
        json.dump(ow, open(os.path.join(tmp, "ow.json"), "w")); out = os.path.join(tmp, "o.json"); J.main(tmp, os.path.join(tmp, "v.json"), os.path.join(tmp, "ow.json"), out, os.path.join(tmp, "p.json")); o = json.load(open(out))
        sr = o["second_reviewer"]; self.assertEqual(sr["all_overlap"]["n"], 50); self.assertEqual(sr["released_overlap"]["n"], 30); self.assertIn("separately", sr["label"]); self.assertIn("main_released_with_owner_substituted_on_overlap", sr)
        self.assertEqual(o["released"]["contaminated"], 2)           # primary reviewer's numbers unchanged by owner input
if __name__ == "__main__": unittest.main(verbosity=2)
