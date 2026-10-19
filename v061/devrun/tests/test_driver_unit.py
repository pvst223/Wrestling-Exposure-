import os, sys, unittest, json, tempfile, csv
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, REPO)
try:
    from v061.devrun import crossfit_run as C, render_dev as RD
    IMPORT_ERR = None
except Exception as e:   # torch-dependent frozen imports are lazy; module import itself needs only numpy
    IMPORT_ERR = e
@unittest.skipIf(IMPORT_ERR is not None, f"driver import failed: {IMPORT_ERR}")
class T(unittest.TestCase):
    def test_components_link_shared_identity(self):
        c = C.components({"c1": ["andrade", "rey"], "c2": ["andrade", "omega"], "c3": ["orton", "rollins"]})
        self.assertEqual(c["c1"], c["c2"]); self.assertNotEqual(c["c1"], c["c3"])
    def test_ep_seed_matches_spec_derivation(self):
        self.assertEqual(C.EP_SEED, int("efb2a797", 16) % 2**31); self.assertLess(C.EP_SEED, 2**31)
    def test_preflight_refuses_without_ledger_entry(self):
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, "AUDIT_LEDGER.jsonl"), "w").write(json.dumps({"id": "X"}) + "\n")
            with self.assertRaises(SystemExit): C.preflight(d, d, os.path.join(d, "r.json"))
    def test_preflight_refuses_when_result_exists_or_hash_differs(self):
        ms, _ = C.devrun_manifest_sha()
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, "AUDIT_LEDGER.jsonl"), "w").write(json.dumps({"id": "DR0", "devrun_code_manifest_sha256": "0" * 64}) + "\n")
            with self.assertRaises(SystemExit): C.preflight(d, d, os.path.join(d, "r.json"))
            open(os.path.join(d, "AUDIT_LEDGER.jsonl"), "w").write(json.dumps({"id": "DR0", "devrun_code_manifest_sha256": ms}) + "\n"); open(os.path.join(d, "r.json"), "w").write("{}")
            with self.assertRaises(SystemExit): C.preflight(d, d, os.path.join(d, "r.json"))
    def test_render_inputs_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            oof = os.path.join(d, "o.csv")
            with open(oof, "w", newline="") as f:
                w = csv.writer(f); w.writerow(["clip", "tracklet", "frame", "shot", "truth", "decision", "reason", "g", "q", "b0_decision"]); w.writerow(["c", "t1", 3, 0, "a", "ACCEPT_A", "OK", .9, .9, "A"]); w.writerow(["x", "t9", 3, 0, "a", "ACCEPT_A", "OK", .9, .9, "A"])
            tj = os.path.join(d, "t.json"); json.dump([dict(tid="t1", frames=[0, 3], boxes=[[1, 2, 3, 4], [5, 6, 7, 8]])], open(tj, "w"))
            dp, bp, n = RD.build_inputs(oof, tj, "c", d); self.assertEqual(n, 1); rows = list(csv.DictReader(open(bp))); self.assertEqual((rows[0]["x1"], rows[0]["y2"]), ("5", "8"))
if __name__ == "__main__": unittest.main()
