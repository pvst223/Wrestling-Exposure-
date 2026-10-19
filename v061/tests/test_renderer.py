import unittest, json, os, csv, tempfile, hashlib
import _path
from v061.impl.render import frame_status as F, render_video as RV
class T(unittest.TestCase):
    def test_status_rules(self):
        rows = F.tracklet_status([10, 13, 20], 10, 25); st = {r["frame"]: r for r in rows}
        for f in (10, 13, 20): self.assertEqual(st[f]["status"], F.EVALUATED)
        for f, age in ((11, 1), (12, 2), (14, 1), (15, 2), (16, 3), (21, 1), (22, 2), (23, 3)): self.assertEqual((st[f]["status"], st[f]["age"]), (F.CARRIED, age), f)
        for f in (17, 18, 19, 24, 25): self.assertEqual(st[f]["status"], F.NOEVAL, f)
        self.assertTrue(all(r["age"] <= 3 for r in rows if r["status"] == F.CARRIED)); self.assertEqual(len(rows), 16)
    def test_before_first_eval_is_noeval(self): self.assertEqual({r["status"] for r in F.tracklet_status([10], 5, 9)}, {F.NOEVAL})
    def test_counts_and_unique_eval(self):
        dec = [dict(clip="c", tracklet="t1", frame=str(f), truth="a", decision="ACCEPT_A", reason="") for f in (0, 3, 6)] + [dict(clip="c", tracklet="t2", frame="3", truth="b", decision="REJECT_NONTARGET", reason="")]
        bx = [dict(tracklet=t, frame=str(f), x1=1, y1=1, x2=5, y2=5) for t, f in (("t1", 0), ("t1", 3), ("t1", 6), ("t2", 3))]
        rows = RV.build_status(dec, bx); c = F.counts(rows); self.assertEqual(c[F.EVALUATED], 4); self.assertEqual(c[F.EVALUATED], len({(d["clip"], int(d["frame"]), d["tracklet"]) for d in dec}))
        self.assertTrue(all(r["box"] == (1.0, 1.0, 5.0, 5.0) for r in rows if r["status"] != F.NOEVAL))   # held, never interpolated
        self.assertEqual(max(r["age"] for r in rows if r["status"] == F.CARRIED), 3)
    def test_perturbed_decisions_change_hash(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x.csv"); open(p, "w").write("a,b\n1,2\n"); h1 = RV.sha256_file(p); open(p, "w").write("a,b\n1,3\n"); self.assertNotEqual(h1, RV.sha256_file(p))
    def test_render_synthetic_video(self):
        try: import cv2, numpy as np
        except Exception: self.skipTest("opencv unavailable")
        with tempfile.TemporaryDirectory() as d:
            v = os.path.join(d, "in.mp4"); w = cv2.VideoWriter(v, cv2.VideoWriter_fourcc(*"mp4v"), 30, (64, 48))
            for i in range(20): w.write(np.full((48, 64, 3), i * 5, np.uint8))
            w.release()
            dec = os.path.join(d, "d.csv"); bx = os.path.join(d, "b.csv")
            with open(dec, "w", newline="") as f: cw = csv.writer(f); cw.writerow(["clip", "tracklet", "frame", "truth", "decision", "reason", "g", "q"]); [cw.writerow(["c", "t", fr, "a", "ACCEPT_A", "", .9, .9]) for fr in (2, 5, 12)]
            with open(bx, "w", newline="") as f: cw = csv.writer(f); cw.writerow(["tracklet", "frame", "x1", "y1", "x2", "y2"]); [cw.writerow(["t", fr, 5, 5, 30, 40]) for fr in (2, 5, 12)]
            s = RV.render(v, dec, bx, os.path.join(d, "o.mp4"), os.path.join(d, "o.json"))
            self.assertEqual(s["n_source_frames"], 20); self.assertEqual(s["status_counts"]["EVALUATED"], 3); self.assertEqual(s["status_counts"]["CARRIED-FORWARD"], 8)
            self.assertEqual(s["n_unique_evaluated_clip_frames"], 3); self.assertEqual(s["decisions_sha256"], RV.sha256_file(dec)); self.assertTrue(os.path.getsize(os.path.join(d, "o.mp4")) > 0)
if __name__ == "__main__": unittest.main()
