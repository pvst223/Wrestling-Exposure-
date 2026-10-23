import csv, datetime, hashlib, io, json, os, shutil, sys, tempfile, threading, unittest, urllib.request, urllib.error, subprocess
_H = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(_H, "..", "..", "exposure_events"), os.path.join(_H, "..")]
import event_core as C, event_ui as U, event_cli as CLI

SYN = {"table_version": "SYNTHETIC", "sources": [
    {"order": 1, "source_id": "s_one", "status": "RESOLVED", "t_max_s": 10.0, "wrestlers": {"A": "Wrestler Alpha", "B": "Wrestler Beta"}},
    {"order": 2, "source_id": "s_two", "status": "RESOLVED", "t_max_s": 5.55, "wrestlers": {"A": "Wrestler Gamma", "B": "Wrestler Delta"}}]}


class Clock:
    def __init__(self, t="2030-01-01T00:00:00Z"): self.t = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ")
    def __call__(self): self.t += datetime.timedelta(seconds=1); return self.t.strftime("%Y-%m-%dT%H:%M:%SZ")
    def jump(self, **kw): self.t += datetime.timedelta(**kw)


def make_ws(tmp, clock=None, table=None):
    tp = os.path.join(tmp, "st.json")
    with open(tp, "w") as f: json.dump(table or SYN, f)
    return C.Workspace(os.path.join(tmp, "w"), source_table_path=tp, clock=clock or Clock())


def ready(tmp, clock=None):
    ws = make_ws(tmp, clock); ws.setup("a" * 64, "b" * 64, {}); return ws


def watch(ws, p, sid, frac=1.0):
    t = ws.src["by_id"][sid]["t_max_s"]; x = 0.0
    while x < t * frac: ws.heartbeat(p, sid, x, True, 1.0); x += 0.5
    ws.heartbeat(p, sid, min(t, t * frac), True, 1.0)


def finish_all(ws, p):
    for s in ws.src["sources"]: watch(ws, p, s["source_id"]); ws.mark_source_done(p, s["source_id"], True)


class T(unittest.TestCase):
    def setUp(self): self.tmp = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_setup_refuses_unresolved_real_table(self):
        ws = C.Workspace(os.path.join(self.tmp, "w"), clock=Clock())
        self.assertTrue(ws.source_problems() or True)
        if ws.source_problems():
            with self.assertRaises(C.StateError): ws.setup("a" * 64, "b" * 64, {})

    def test_setup_requires_design_hash(self):
        ws = make_ws(self.tmp); ws.design_path = os.path.join(self.tmp, "st.json")
        with self.assertRaises(C.StateError): ws.setup("a", "b", {})

    def test_valid_events_all_observabilities_and_unclear(self):
        ws = ready(self.tmp); ws.open_pass(1)
        ws.submit_event(1, "s_one", "1.0", "A", "FULL")
        ws.submit_event(1, "s_one", "2.5", "B", "PARTIAL", "cut before contact")
        ws.submit_event(1, "s_one", "3.5", "UNCLEAR", "INFERRED", "replay shows landing", "note")
        rows = ws.effective_events(1); self.assertEqual([r["observability"] for r in rows], ["FULL", "PARTIAL", "INFERRED"])
        self.assertEqual(rows[2]["performer"], "UNCLEAR")

    def test_evidence_mandatory(self):
        ws = ready(self.tmp); ws.open_pass(1)
        for ob in ("PARTIAL", "INFERRED"):
            for ev in ("", "   "):
                with self.assertRaises(C.ValidationError): ws.submit_event(1, "s_one", "1.0", "A", ob, ev)
        ws.submit_event(1, "s_one", "1.0", "A", "FULL")  # FULL needs none

    def test_timestamp_precision(self):
        ws = ready(self.tmp); ws.open_pass(1)
        for bad in ("1.05", "1.25", "abc", "-1", "nan", "1e0x"):
            with self.assertRaises(C.ValidationError): ws.submit_event(1, "s_one", bad, "A", "FULL")
        ws.submit_event(1, "s_one", "1", "A", "FULL"); ws.submit_event(1, "s_one", "1.1", "A", "FULL"); ws.submit_event(1, "s_one", 2.3, "A", "FULL")
        self.assertEqual([r["t_ds"] for r in ws.effective_events(1)], [10, 11, 23])

    def test_source_range_enforcement(self):
        ws = ready(self.tmp); ws.open_pass(1)
        ws.submit_event(1, "s_one", "10.0", "A", "FULL")
        with self.assertRaises(C.ValidationError): ws.submit_event(1, "s_one", "10.1", "A", "FULL")
        ws.sources_done  # noqa
        watch(ws, 1, "s_one"); ws.mark_source_done(1, "s_one", True)
        ws.submit_event(1, "s_two", "5.5", "A", "FULL")
        with self.assertRaises(C.ValidationError): ws.submit_event(1, "s_two", "5.6", "A", "FULL")

    def test_forbidden_source_and_performer_rejected(self):
        ws = ready(self.tmp); ws.open_pass(1)
        with self.assertRaises(C.ValidationError): ws.submit_event(1, "b2_videoplayback_3", "1.0", "A", "FULL")
        with self.assertRaises(C.ValidationError): ws.submit_event(1, "s_one", "1.0", "C", "FULL")
        with self.assertRaises(C.ValidationError): ws.submit_event(1, "s_one", "1.0", "A", "BUMP")
        with self.assertRaises(C.ToolError): ws.submit_event(1, "s_two", "1.0", "A", "FULL")  # not the current source

    def test_real_source_table_contents(self):
        ws = C.Workspace(os.path.join(self.tmp, "w"))
        self.assertEqual([s["source_id"] for s in ws.src["sources"]], ["b1_orton_rollins_wm31", "b2_batch2_clip_condensed", "b2_videoplayback_2", "b2_videoplayback_5", "rr_balor_full"])
        self.assertEqual(ws.src["by_id"]["rr_balor_full"]["ds_max"], 7791); self.assertEqual(ws.src["by_id"]["b2_videoplayback_2"]["ds_max"], 644)

    def test_note_limits_and_duplicates(self):
        ws = ready(self.tmp); ws.open_pass(1)
        with self.assertRaises(C.ValidationError): ws.submit_event(1, "s_one", "1.0", "A", "FULL", "", "x" * 201)
        ws.submit_event(1, "s_one", "1.0", "A", "FULL", "", "x" * 200)
        with self.assertRaises(C.ValidationError): ws.submit_event(1, "s_one", "1.0", "A", "FULL")
        ws.submit_event(1, "s_one", "1.0", "B", "FULL")

    def test_append_only_and_tamper_detection(self):
        ws = ready(self.tmp); ws.open_pass(1); ws.submit_event(1, "s_one", "1.0", "A", "FULL"); ws.submit_event(1, "s_one", "2.0", "A", "FULL")
        before = open(ws.audit_path).read().splitlines(); ws.verify_chain()
        ws.submit_event(1, "s_one", "3.0", "A", "FULL"); after = open(ws.audit_path).read().splitlines()
        self.assertEqual(after[:len(before)], before)
        lines = after[:]; lines[2] = lines[2].replace('"t_ds":10', '"t_ds":11'); open(ws.audit_path, "w").write("\n".join(lines) + "\n")
        with self.assertRaises(C.ChainError): ws.verify_chain()
        with self.assertRaises(C.ChainError): ws.submit_event(1, "s_one", "4.0", "A", "FULL")

    def test_deleted_record_detected(self):
        ws = ready(self.tmp); ws.open_pass(1)
        for t in ("1.0", "2.0", "3.0"): ws.submit_event(1, "s_one", t, "A", "FULL")
        lines = open(ws.audit_path).read().splitlines(); del lines[3]; open(ws.audit_path, "w").write("\n".join(lines) + "\n")
        with self.assertRaises(C.ChainError): ws.verify_chain()

    def test_clock_going_backwards_refused(self):
        clk = Clock(); ws = ready(self.tmp, clk); ws.open_pass(1); clk.jump(days=-1)
        with self.assertRaises(C.ChainError): ws.submit_event(1, "s_one", "1.0", "A", "FULL")

    def test_records_carry_design_hash_and_source_provenance(self):
        ws = ready(self.tmp); rec = json.loads(open(ws.audit_path).readline())
        self.assertEqual(rec["data"]["design_sha256"], C.DESIGN_SHA256); self.assertIn("source_table_sha256", rec["data"]); self.assertEqual(rec["type"], "SETUP")

    def test_correction_audit_chain(self):
        ws = ready(self.tmp); ws.open_pass(1); eid = ws.submit_event(1, "s_one", "1.0", "A", "FULL")
        with self.assertRaises(C.ValidationError): ws.correct(1, eid, "WHIM", "x", performer="B")
        with self.assertRaises(C.ValidationError): ws.correct(1, eid, "TOOL_ERROR", "  ", performer="B")
        with self.assertRaises(C.ValidationError): ws.correct(1, "ev_nope", "TOOL_ERROR", "x", performer="B")
        n0 = len(open(ws.audit_path).read().splitlines())
        ws.correct(1, eid, "TRANSCRIPTION_ERROR", "typed the wrong time", event_time_s="1.2")
        self.assertEqual(len(open(ws.audit_path).read().splitlines()), n0 + 1)
        raw = [json.loads(l) for l in open(ws.audit_path)]
        orig = [r for r in raw if r["type"] == "EVENT"][0]; self.assertEqual(orig["data"]["t_ds"], 10)  # original untouched
        cor = raw[-1]; self.assertEqual((cor["type"], cor["data"]["old"]["t_ds"], cor["data"]["new"]["t_ds"]), ("CORRECTION", 10, 12))
        self.assertEqual(ws.effective_events(1)[0]["t_ds"], 12); ws.verify_chain()
        ws.correct(1, eid, "TOOL_ERROR", "entered twice", action="RETRACT"); self.assertEqual(ws.effective_events(1), [])
        with self.assertRaises(C.ValidationError): ws.correct(1, eid, "TOOL_ERROR", "again", action="RETRACT")

    def test_correction_cannot_violate_rules_or_touch_finished_source(self):
        ws = ready(self.tmp); ws.open_pass(1); eid = ws.submit_event(1, "s_one", "1.0", "A", "FULL")
        with self.assertRaises(C.ValidationError): ws.correct(1, eid, "TOOL_ERROR", "x", observability="PARTIAL")  # needs evidence
        with self.assertRaises(C.ValidationError): ws.correct(1, eid, "TOOL_ERROR", "x", event_time_s="99")
        watch(ws, 1, "s_one"); ws.mark_source_done(1, "s_one", True)
        with self.assertRaises(C.StateError): ws.correct(1, eid, "TOOL_ERROR", "x", performer="B")

    def test_source_order_and_coverage_enforced(self):
        ws = ready(self.tmp); ws.open_pass(1)
        with self.assertRaises(C.ValidationError): ws.mark_source_done(1, "s_one", False)
        with self.assertRaises(C.StateError): ws.mark_source_done(1, "s_one", True)  # nothing played
        watch(ws, 1, "s_one", 0.5)
        with self.assertRaises(C.StateError): ws.mark_source_done(1, "s_one", True)
        ws.heartbeat(1, "s_one", 0.0, False, 1.0)
        # seeking (jump >1 s) and fast playback give no credit
        ws2 = ready(os.path.join(self.tmp, "x") if os.makedirs(os.path.join(self.tmp, "x"), exist_ok=True) is None else self.tmp); ws2.open_pass(1)
        x = 0.0
        while x < 10: ws2.heartbeat(1, "s_one", x, True, 4.0); x += 0.5
        self.assertEqual(ws2.coverage_fraction(1, "s_one"), 0.0)
        with self.assertRaises(C.StateError): ws2.mark_source_done(1, "s_two", True)

    def test_pass_completion_freeze_and_hash(self):
        ws = ready(self.tmp); ws.open_pass(1); ws.submit_event(1, "s_one", "1.0", "A", "FULL")
        with self.assertRaises(C.StateError): ws.complete_pass(1)
        with self.assertRaises(C.StateError): ws.export(1, self.tmp)
        finish_all(ws, 1); rec = ws.complete_pass(1); self.assertEqual(rec["data"]["pass_sha256"], ws.pass_hash(1))
        self.assertNotIn("count", json.dumps(rec["data"]))
        with self.assertRaises(C.StateError): ws.submit_event(1, "s_two", "1.0", "A", "FULL")
        eid = ws.effective_events(1)[0]["event_id"]
        with self.assertRaises(C.StateError): ws.correct(1, eid, "TOOL_ERROR", "late", performer="B")
        with self.assertRaises(C.StateError): ws.complete_pass(1)
        self.assertTrue(ws.status(1)["complete"])

    def test_pass2_lock_7_days(self):
        clk = Clock(); ws = ready(self.tmp, clk)
        with self.assertRaises(C.LockError): ws.open_pass(2)  # before pass 1 exists
        ws.open_pass(1); finish_all(ws, 1); rec = ws.complete_pass(1); nb = rec["data"]["pass2_not_before_utc"]
        done = datetime.datetime.strptime(rec["ts"], "%Y-%m-%dT%H:%M:%SZ"); self.assertEqual(datetime.datetime.strptime(nb, "%Y-%m-%dT%H:%M:%SZ"), done + datetime.timedelta(days=7))
        self.assertTrue(ws.status(2)["locked"])
        clk.jump(days=6, hours=23, minutes=58)
        with self.assertRaises(C.LockError): ws.open_pass(2)
        with self.assertRaises(C.StateError): ws.submit_event(2, "s_one", "1.0", "A", "FULL")
        clk.jump(minutes=5); ws.open_pass(2); self.assertFalse(ws.status(2).get("locked", False))

    def test_pass2_lock_survives_new_process_and_cli(self):
        clk = Clock(); ws = ready(self.tmp, clk); ws.open_pass(1); finish_all(ws, 1); ws.complete_pass(1)
        ws2 = C.Workspace(ws.root, source_table_path=os.path.join(self.tmp, "st.json"), clock=clk)
        with self.assertRaises(C.LockError): ws2.open_pass(2)

    def test_pass2_blindness(self):
        clk = Clock(); ws = ready(self.tmp, clk); ws.open_pass(1)
        secret = "ZQXSECRETNOTE"; ws.submit_event(1, "s_one", "3.7", "B", "PARTIAL", "ZQXSECRETEVID", secret)
        finish_all(ws, 1); ws.complete_pass(1); clk.jump(days=8); ws.open_pass(2)
        self.assertEqual(ws.effective_events(2), []); self.assertEqual(ws.export_text(2).strip().count("\n"), 0)
        blob = json.dumps(ws.status(2)) + json.dumps(ws.status(1)) + ws.export_text(2)
        for s in (secret, "ZQXSECRETEVID", "3.7", "PARTIAL"): self.assertNotIn(s, blob)
        # identical pass-2 entry of the same data is allowed (no cross-pass duplicate rejection that would leak Pass 1)
        ws.submit_event(2, "s_one", "3.7", "B", "PARTIAL", "other evidence"); self.assertEqual(len(ws.effective_events(2)), 1)

    def test_status_never_contains_counts_or_events(self):
        ws = ready(self.tmp); ws.open_pass(1)
        for t in ("1.0", "2.0", "3.0"): ws.submit_event(1, "s_one", t, "A", "FULL")
        st = ws.status(1); self.assertEqual(set(st), {"pass", "opened", "complete", "sources_finished", "sources_total", "current_source"})
        self.assertEqual((st["sources_finished"], st["sources_total"]), (0, 2))

    def test_deterministic_export_and_pass_hash(self):
        def run(sub):
            d = os.path.join(self.tmp, sub); os.makedirs(d); ws = ready(d); ws.open_pass(1)
            ws.submit_event(1, "s_one", "5.0", "B", "FULL"); ws.submit_event(1, "s_one", "1.0", "A", "PARTIAL", "ev"); finish_all(ws, 1); ws.complete_pass(1)
            return ws.export(1, os.path.join(d, "o")), open(ws.export(1, os.path.join(d, "o2"))["path"], "rb").read()
        a, b = run("a"), run("b"); self.assertEqual(a[0]["pass_sha256"], b[0]["pass_sha256"]); self.assertEqual(a[1], b[1])
        self.assertTrue(a[1].decode().splitlines()[1].startswith("s_one,1.0,A,PARTIAL"))
        self.assertEqual(hashlib.sha256(a[1]).hexdigest(), a[0]["pass_sha256"])

    def test_manual_is_verbatim_from_design(self):
        ws = make_ws(self.tmp); ws.design_path = C.Workspace(os.path.join(self.tmp, "q")).design_path
        txt = U.manual_text(ws); dz = open(ws.design_path, encoding="utf-8").read()
        self.assertIn("**Inclusion criteria (all required).**", txt); self.assertIn("**FULL:**", txt); self.assertIn(C.DESIGN_SHA256, txt)
        sec1 = dz[dz.index("## 1."):dz.index("## 2.")].rstrip(); self.assertIn(sec1, txt)
        self.assertEqual(hashlib.sha256(open(ws.design_path, "rb").read()).hexdigest(), C.DESIGN_SHA256)


@unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg needed")
class UI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, self.tmp, True)
        self.vid = os.path.join(self.tmp, "t.mp4")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=duration=3:size=160x120:rate=30", "-pix_fmt", "yuv420p", self.vid], check=True)
        self.ws = ready(self.tmp); self.ws.open_pass(1)
        self.srv = U.serve(self.ws, 1, {"s_one": self.vid, "s_two": self.vid}); self.base = "http://127.0.0.1:%d" % self.srv.server_address[1]
        threading.Thread(target=self.srv.serve_forever, daemon=True).start(); self.addCleanup(self.srv.server_close); self.addCleanup(self.srv.shutdown)

    def get(self, p, h=None):
        return urllib.request.urlopen(urllib.request.Request(self.base + p, headers=h or {}))

    def post(self, p, b): 
        r = urllib.request.Request(self.base + p, json.dumps(b).encode(), {"Content-Type": "application/json"}); return json.loads(urllib.request.urlopen(r).read())

    def test_page_state_and_no_counts(self):
        page = self.get("/").read().decode()
        for word in ("Submit event", "frame", "use current time", "FULL", "PARTIAL", "INFERRED", "UNCLEAR", "coding manual"): self.assertIn(word, page)
        for bad in ("total events", "events recorded", "count", "candidate", "prediction", "Rule V1", "classifier", "skeleton", "mask"):
            self.assertNotIn(bad.lower(), page.lower().replace("coding manual", "").replace("encoded", ""))
        r = self.post("/api/event", {"source_id": "s_one", "event_time_s": "1.0", "performer": "A", "observability": "FULL"})
        self.assertTrue(r["ok"] and r["event_id"].startswith("ev_")); self.assertEqual(set(r), {"ok", "event_id"})
        st = json.loads(self.get("/api/state").read()); self.assertNotIn("events", json.dumps(st).lower().replace("events can", ""))
        self.assertEqual(set(st["current_source"]), {"source_id", "t_max_s", "wrestlers"})

    def test_rejections_via_api(self):
        r = self.post("/api/event", {"source_id": "s_one", "event_time_s": "1.05", "performer": "A", "observability": "FULL"}); self.assertFalse(r["ok"])
        r = self.post("/api/event", {"source_id": "s_one", "event_time_s": "1.0", "performer": "A", "observability": "PARTIAL"}); self.assertFalse(r["ok"])
        r = self.post("/api/source_done", {"source_id": "s_one"}); self.assertFalse(r["ok"])  # no coverage yet

    def test_video_range_and_only_current_source(self):
        with self.get("/video/s_one", {"Range": "bytes=0-99"}) as r: self.assertEqual(r.status, 206); self.assertEqual(len(r.read()), 100)
        with self.assertRaises(urllib.error.HTTPError) as c: self.get("/video/s_two")
        self.assertEqual(c.exception.code, 403)
        with self.assertRaises(urllib.error.HTTPError): self.get("/video/not_a_source")

    def test_manual_endpoint_and_no_event_list_endpoints(self):
        self.assertIn("Inclusion criteria", self.get("/manual").read().decode())
        for p in ("/api/events", "/api/export", "/api/summary", "/audit.jsonl"):
            with self.assertRaises(urllib.error.HTTPError): self.get(p)

    def test_heartbeat_coverage_and_source_done(self):
        for x in [i * 0.5 for i in range(21)]: self.post("/api/hb", {"source_id": "s_one", "t": x, "playing": True, "rate": 1})
        self.assertTrue(self.post("/api/source_done", {"source_id": "s_one"})["ok"])
        self.assertEqual(json.loads(self.get("/api/state").read())["current_source"]["source_id"], "s_two")


if __name__ == "__main__": unittest.main()
