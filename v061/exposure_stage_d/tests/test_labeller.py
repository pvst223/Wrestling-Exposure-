import csv, json, os, re, shutil, subprocess, sys, tempfile, threading, unittest, urllib.parse, urllib.request, urllib.error
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import labeller_core as C, labeller_ui as UI, make_synthetic as MS

FORBIDDEN = re.compile(r"classif|detect|feature|threshold|metric|performance|identity|pose|skeleton|anatomy|ownership|"
                       r"keypoint|confidence_score|accuracy|auroc|p[1-5]\b", re.I)


class Clock:
    def __init__(self, t="2026-10-22T10:00:00Z"): self.t = t
    def __call__(self): return self.t


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(); self.clock = Clock()
        self.ws = C.Workspace(os.path.join(self.tmp, "w"), clock=self.clock)
        self.mb = MS.write_manifest(os.path.join(self.tmp, "mb.csv"), "build", "B", 5)
        self.mc = MS.write_manifest(os.path.join(self.tmp, "mc.csv"), "check", "C", 4, source="SYN_SRC_B")
    def tearDown(self): shutil.rmtree(self.tmp, ignore_errors=True)
    def label_all(self, s, lab="LIVE_ACTION"):
        for r in self.ws.manifest(s): self.ws.submit_label(s, r["shot_id"], lab, "HIGH")
        for src in {r["source_id"] for r in self.ws.manifest(s)}:
            self.ws.set_marks(s, src, 0.04, 99.96, "synthetic evidence note")
    def full(self, s, lab="LIVE_ACTION"):
        self.ws.open_set(s, self.mb if s == "build" else self.mc); self.label_all(s, lab); return self.ws.complete_set(s)


class T01_Protocol(Base):
    def test_hash_pin_and_mismatch(self):
        self.assertEqual(C.verify_protocol(), C.PROTOCOL_SHA256)
        bad = os.path.join(self.tmp, "p.md"); open(bad, "w").write(open(C.PROTOCOL_FILE).read() + " ")
        with self.assertRaises(C.ProtocolMismatch): C.Workspace(os.path.join(self.tmp, "w2"), protocol_path=bad)
    def test_categories_reasons_flags_exact_vs_protocol_text(self):
        t = open(C.PROTOCOL_FILE, encoding="utf-8").read()
        for c in C.CATEGORIES[:4]: self.assertIn(f"**{c}**", t)
        self.assertEqual(C.CATEGORIES, ("LIVE_ACTION", "REPLAY", "CLOSE_UP", "NON_MATCH", "UNKNOWN"))
        for u in C.UNKNOWN_REASONS: self.assertIn(f"`{u}`", t)
        self.assertEqual(len(C.UNKNOWN_REASONS), 7)
        fl = re.search(r"\| `flags` \| semicolon list from \{([^}]*)\}", t).group(1)
        self.assertEqual(tuple(x.strip() for x in fl.split(",")), C.FLAGS)
    def test_schema_matches_section8(self):
        t = open(C.PROTOCOL_FILE, encoding="utf-8").read()
        sec = t[t.index("Private label table"):t.index("Separate files")]
        fields = tuple(x for row in re.findall(r"^\| ((?:`\w+`(?:, )?)+) \|", sec, re.M) for x in re.findall(r"`(\w+)`", row))
        self.assertEqual(fields, C.LABEL_COLUMNS)
        self.ws.open_set("build", self.mb); self.ws.submit_label("build", "B000", "REPLAY", "LOW")
        with open(self.ws._p("build", "labels_build.csv")) as f: self.assertEqual(tuple(next(csv.reader(f))), fields)


class T02_Validation(Base):
    def setUp(self): super().setUp(); self.ws.open_set("build", self.mb)
    def sub(self, **k):
        d = dict(label="LIVE_ACTION", confidence="HIGH"); d.update(k); return self.ws.submit_label("build", "B000", **d)
    def test_category_enforced(self):
        for bad in ("live_action", "LIVE", "", "OTHER"):
            with self.assertRaises(C.ValidationError): self.sub(label=bad)
        for i, c in enumerate(C.CATEGORIES[:4]):
            r = self.ws.submit_label("build", f"B00{i}", c, "MEDIUM"); self.assertEqual(r["label"], c)
    def test_unknown_reason_enforced(self):
        with self.assertRaises(C.ValidationError): self.sub(label="UNKNOWN")
        with self.assertRaises(C.ValidationError): self.sub(label="UNKNOWN", unknown_reason="BOGUS")
        with self.assertRaises(C.ValidationError): self.sub(label="UNKNOWN", unknown_reason="OTHER")
        with self.assertRaises(C.ValidationError): self.sub(unknown_reason="UNREADABLE")
        self.assertEqual(self.sub(label="UNKNOWN", unknown_reason="OTHER", note="free text")["unknown_reason"], "OTHER")
    def test_confidence_flags_note(self):
        with self.assertRaises(C.ValidationError): self.sub(confidence="")
        with self.assertRaises(C.ValidationError): self.sub(confidence="VERY")
        with self.assertRaises(C.ValidationError): self.sub(flags=["NOPE"])
        with self.assertRaises(C.ValidationError): self.sub(flags=["NOTE", "NOTE"])
        with self.assertRaises(C.ValidationError): self.sub(note="x" * 201)
        with self.assertRaises(C.ValidationError): self.sub(note="a\nb")
        r = self.sub(flags=["NOTE", "BOUNDARY_ISSUE"], note="n"); self.assertEqual(r["flags"], "BOUNDARY_ISSUE;NOTE")
    def test_final_on_submit(self):
        self.sub()
        with self.assertRaises(C.FinalOnSubmit): self.sub(label="REPLAY")
        self.assertEqual(len(self.ws._label_rows("build")), 1)
        self.assertFalse(hasattr(self.ws, "edit_label") or hasattr(self.ws, "update_label"))
    def test_protocol_hash_timestamp_recorded(self):
        r = self.sub(); self.assertEqual(r["protocol_version"], C.PROTOCOL_SHA256); self.assertEqual(r["labelled_at_utc"], self.clock.t)
    def test_marks(self):
        with self.assertRaises(C.ValidationError): self.ws.set_marks("build", "SYN_SRC_A", 1, 2, " ")
        with self.assertRaises(C.ValidationError): self.ws.set_marks("build", "SYN_SRC_A", 5, 2, "e")
        with self.assertRaises(C.ValidationError): self.ws.set_marks("build", "NOPE", 1, 2, "e")
        r = self.ws.set_marks("build", "SYN_SRC_A", 1.04, 12.26, "bell heard", ["START_AMBIGUOUS"])
        self.assertEqual((r["start_s"], r["end_s"], r["flags"]), ("1.0", "12.3", "START_AMBIGUOUS"))
        with self.assertRaises(C.FinalOnSubmit): self.ws.set_marks("build", "SYN_SRC_A", 1, 2, "e")
    def test_no_d(self):
        r = self.ws.set_marks("build", "SYN_SRC_A", None, None, "", ["NO_D"]); self.assertEqual((r["start_s"], r["end_s"]), ("", ""))


class T03_ContextAndBoundaries(Base):
    def test_context_window(self):
        self.ws.open_set("build", self.mb); v = self.ws.view("build", "B000")
        self.assertEqual((v["context_start_s"], v["context_end_s"]), (0.0, 7.5))
        v = self.ws.view("build", "B002"); self.assertEqual((v["context_start_s"], v["context_end_s"]), (1.0, 13.5))
        self.assertEqual(tuple(v), C.VIEW_KEYS)
    def test_boundaries_immutable(self):
        self.ws.open_set("build", self.mb)
        with self.assertRaises(TypeError): self.ws.submit_label("build", "B000", "REPLAY", "HIGH", t_start_s="1.0")
        r = self.ws.submit_label("build", "B001", "REPLAY", "HIGH")
        m = {x["shot_id"]: x for x in self.ws.manifest("build")}["B001"]
        self.assertEqual((r["t_start_s"], r["t_end_s"]), (m["t_start_s"], m["t_end_s"]))
        p = self.ws._p("build", "manifest.csv"); t = open(p).read().replace("B002,SYN_SRC_A,build,6.000", "B002,SYN_SRC_A,build,6.500")
        open(p, "w").write(t)
        with self.assertRaises(C.ManifestTamper): self.ws.view("build", "B000")
    def test_manifest_whitelist(self):
        for extra in ("score", "detections", "threshold", "identity", "pose", "classifier_output"):
            p = os.path.join(self.tmp, f"x_{extra}.csv")
            rows = list(csv.reader(open(self.mb))); rows[0].append(extra); [r.append("0.9") for r in rows[1:]]
            csv.writer(open(p, "w", newline="")).writerows(rows)
            with self.assertRaises(C.ManifestError): C.Workspace(os.path.join(self.tmp, "w_" + extra)).open_set("build", p)
    def test_sets_disjoint_and_order(self):
        self.ws.open_set("build", self.mb)
        dup = MS.write_manifest(os.path.join(self.tmp, "d.csv"), "check", "B", 2, source="SYN_SRC_B")
        with self.assertRaises(C.ManifestError): self.ws.open_set("check", dup)
        wrong = MS.write_manifest(os.path.join(self.tmp, "w.csv"), "build", "Z", 2)
        with self.assertRaises(C.ManifestError): self.ws.open_set("check", wrong)
        self.assertEqual(self.ws.next_unlabelled("build"), "B000")
        self.ws.submit_label("build", "B000", "REPLAY", "HIGH"); self.assertEqual(self.ws.next_unlabelled("build"), "B001")
    @unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg missing")
    def test_ffmpeg_clip_is_context_window_only(self):
        vid = MS.make_test_video(os.path.join(self.tmp, "s.mp4"), 40); json.dump({"SYN_SRC_A": vid}, open(os.path.join(self.tmp, "src.json"), "w"))
        m = MS.write_manifest(os.path.join(self.tmp, "m2.csv"), "build", "K", 3, t0=10.0)
        ws = C.Workspace(os.path.join(self.tmp, "w3")); ws.open_set("build", m)
        out = UI.ffmpeg_clip_provider(ws.root, os.path.join(self.tmp, "src.json"))(ws.view("build", "K001"))
        d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out]))
        self.assertAlmostEqual(d, (2.5 + 10), delta=0.6)   # shot 2.5 s + 5 s either side


class T04_Corrections(Base):
    def test_correction_flow_and_retention(self):
        self.full("build")
        e = self.ws.apply_correction("build", "B001", "TOOL_ERROR", "mis-click", "REPLAY", "HIGH")
        self.assertEqual(e["old"]["label"], "LIVE_ACTION"); self.assertEqual(e["new"]["label"], "REPLAY")
        orig = {r["shot_id"]: r for r in self.ws._label_rows("build")}["B001"]; self.assertEqual(orig["label"], "LIVE_ACTION")
        self.assertEqual({r["shot_id"]: r for r in self.ws.effective_labels("build")}["B001"]["label"], "REPLAY")
        self.assertTrue(self.ws._has("SET_HASH_UPDATED", "build")); self.assertEqual(self.ws.verify_chain(self.ws._corr_path("build")), 1)
    def test_reasons_required(self):
        self.full("build")
        with self.assertRaises(C.ValidationError): self.ws.apply_correction("build", "B001", "DISAGREE", "x", "REPLAY", "HIGH")
        with self.assertRaises(C.ValidationError): self.ws.apply_correction("build", "B001", "TOOL_ERROR", " ", "REPLAY", "HIGH")
        with self.assertRaises(C.ValidationError): self.ws.apply_correction("build", "B001", "TOOL_ERROR", "x", "UNKNOWN", "HIGH")
    def test_build_closed_after_freeze_and_check_after_unseal(self):
        self.full("build"); self.full("check")
        self.ws.seal_check(); self.ws.apply_correction("check", "C000", "TRANSCRIPTION_ERROR", "typo", "CLOSE_UP", "LOW")
        self.assertEqual(self.ws._has("SEAL_UPDATED", "check", last=True)["data"]["set_sha256"], self.ws.set_hash("check"))
        self.ws.freeze_rule("a" * 64)
        with self.assertRaises(C.SealedError): self.ws.apply_correction("build", "B000", "TOOL_ERROR", "x", "REPLAY", "HIGH")
        self.ws.unseal_check()
        with self.assertRaises(C.SealedError): self.ws.apply_correction("check", "C000", "TOOL_ERROR", "x", "REPLAY", "HIGH")
    def test_chain_tamper_detected(self):
        self.full("build"); self.ws.apply_correction("build", "B000", "TOOL_ERROR", "x", "REPLAY", "HIGH")
        p = self.ws._corr_path("build"); open(p, "w").write(open(p).read().replace("mis", "xx").replace("REPLAY", "CLOSE_UP", 1))
        self.ws.verify_chain(p)   # content edit with intact prev link is caught by the next append's chain only if prev altered
        self.ws.apply_correction("build", "B001", "TOOL_ERROR", "y", "REPLAY", "HIGH")
        ev = open(self.ws.events_path).read().replace("SET_COMPLETE", "SET_COMPLET_", 1); open(self.ws.events_path, "w").write(ev)
        with self.assertRaises(C.ChainError): self.ws.verify_chain()


class T05_SealingSeparation(Base):
    def test_sequence(self):
        self.ws.open_set("build", self.mb); self.ws.open_set("check", self.mc)
        with self.assertRaises(C.StateError): self.ws.complete_set("build")                      # unlabelled
        with self.assertRaises(C.StateError): self.ws.freeze_rule("b" * 64)                       # build not complete
        self.label_all("build"); self.ws.complete_set("build")
        with self.assertRaises(C.StateError): self.ws.submit_label("build", "B000", "REPLAY", "HIGH")   # complete => final
        d = os.path.join(self.tmp, "export"); self.assertIn("labels", self.ws.export_for_rule_builder("build", d))
        self.label_all("check"); self.ws.complete_set("check")
        with self.assertRaises(C.SealedError): self.ws.export_for_rule_builder("check", d)       # not sealed/unsealed
        with self.assertRaises(C.StateError): self.ws.unseal_check()                             # not sealed
        self.ws.seal_check(); h = self.ws.sealed_hash()
        with self.assertRaises(C.SealedError): self.ws.export_for_rule_builder("check", d)
        with self.assertRaises(C.SealedError): self.ws.reference_summary("check")
        with self.assertRaises(C.SealedError): self.ws.unseal_check()                            # rule not frozen
        with self.assertRaises(C.ValidationError): self.ws.freeze_rule("zz")
        self.ws.freeze_rule("c" * 64)
        with self.assertRaises(C.StateError): self.ws.freeze_rule("d" * 64)
        self.ws.unseal_check(); out = self.ws.export_for_rule_builder("check", d); self.assertEqual(out["set_sha256"], h)
        ev = [e["type"] for e in self.ws.events()]
        self.assertLess(ev.index("RULE_FROZEN"), ev.index("CHECK_UNSEALED")); self.assertLess(ev.index("CHECK_SEALED"), ev.index("CHECK_UNSEALED"))
    def test_summary_and_reference_inconclusive(self):
        self.ws.open_set("build", self.mb); self.label_all("build"); self.ws.complete_set("build")
        self.ws.open_set("check", self.mc)
        for i, r in enumerate(self.ws.manifest("check")):   # 4 equal shots (2.5 s): 1 UNKNOWN of 4 => 25%
            if i == 0: self.ws.submit_label("check", r["shot_id"], "UNKNOWN", "LOW", "REPLAY_AMBIGUOUS")
            else: self.ws.submit_label("check", r["shot_id"], "LIVE_ACTION", "HIGH")
        self.ws.set_marks("check", "SYN_SRC_B", 0, 10, "e"); self.ws.complete_set("check"); self.ws.seal_check()
        self.ws.freeze_rule("e" * 64); self.ws.unseal_check()
        s = self.ws.reference_summary("check"); self.assertAlmostEqual(s["U_ref_fraction"], 0.25)
        self.assertTrue(s["REFERENCE_INCONCLUSIVE"]); self.assertEqual(s["unknown_count_by_reason"]["REPLAY_AMBIGUOUS"], 1)
        self.assertIsNone(self.ws.reference_summary("build")["REFERENCE_INCONCLUSIVE"])         # build is descriptive only
    def test_boundary_exactly_10_percent_is_not_inconclusive(self):
        m = MS.write_manifest(os.path.join(self.tmp, "m10.csv"), "check", "Q", 10)
        self.ws.open_set("build", self.mb); self.label_all("build"); self.ws.complete_set("build"); self.ws.open_set("check", m)
        for i, r in enumerate(self.ws.manifest("check")):
            if i == 0: self.ws.submit_label("check", r["shot_id"], "UNKNOWN", "LOW", "UNREADABLE")
            else: self.ws.submit_label("check", r["shot_id"], "LIVE_ACTION", "HIGH")
        self.ws.set_marks("check", "SYN_SRC_A", 0, 10, "e"); self.ws.complete_set("check"); self.ws.seal_check()
        self.ws.freeze_rule("f" * 64); self.ws.unseal_check()
        s = self.ws.reference_summary("check"); self.assertAlmostEqual(s["U_ref_fraction"], 0.10); self.assertFalse(s["REFERENCE_INCONCLUSIVE"])


class T06_NoLeakAndDeterminism(Base):
    def test_view_and_pages_expose_nothing_else(self):
        self.full("build", "REPLAY")
        for r in self.ws.manifest("build"):
            v = self.ws.view("build", r["shot_id"]); self.assertEqual(tuple(v), C.VIEW_KEYS)
        ws2 = C.Workspace(os.path.join(self.tmp, "w9"), clock=self.clock); ws2.open_set("build", self.mb)
        ws2.submit_label("build", "B000", "REPLAY", "HIGH")
        page = UI.render_shot(ws2.view("build", "B001"), "tok")
        txt = re.sub(r"<[^>]+>", " ", page)
        self.assertIsNone(FORBIDDEN.search(txt), FORBIDDEN.search(txt))
        for secret in ("B000",): self.assertNotIn(secret, page)          # previous shot/label not shown
        self.assertNotIn("REPLAY</", page.split("<form")[0])             # no label values outside the choice list
    def test_determinism(self):
        outs = []
        for k in range(2):
            ws = C.Workspace(os.path.join(self.tmp, f"d{k}"), clock=Clock()); ws.open_set("build", self.mb)
            for r in ws.manifest("build"): ws.submit_label("build", r["shot_id"], "CLOSE_UP", "LOW", flags=["NOTE"], note="n")
            ws.set_marks("build", "SYN_SRC_A", 1, 9, "e"); ws.complete_set("build")
            outs.append((open(ws._p("build", "labels_build.csv"), "rb").read(), [e["prev"] for e in ws.events()], ws.set_hash("build")))
        self.assertEqual(outs[0], outs[1])
    def test_reliability(self):
        self.full("build")
        s1 = self.ws.reliability_sample("build"); self.assertEqual(s1, self.ws.reliability_sample("build"))
        self.assertEqual(len(s1), 1); self.assertEqual(s1[0], "B002" if s1[0] == "B002" else s1[0])
        with self.assertRaises(C.StateError): self.ws.submit_relabel("build", s1[0], "REPLAY", "HIGH")      # < 7 days
        self.clock.t = "2026-10-29T10:00:00Z"; self.ws.submit_relabel("build", s1[0], "REPLAY", "HIGH")
        with self.assertRaises(C.FinalOnSubmit): self.ws.submit_relabel("build", s1[0], "REPLAY", "HIGH")
        with self.assertRaises(C.ValidationError): self.ws.submit_relabel("build", [i for i in ("B000", "B001", "B002", "B003", "B004") if i != s1[0]][0], "REPLAY", "HIGH")
        self.assertEqual({r["label"] for r in self.ws.effective_labels("build")}, {"LIVE_ACTION"})           # labels untouched
        self.assertEqual(self.ws.reliability_report("build")["raw_agreement"], 0.0)
    def test_kappa(self):
        ws = self.ws; ws.open_set("build", MS.write_manifest(os.path.join(self.tmp, "k.csv"), "build", "K", 10))
        labs = ["LIVE_ACTION"] * 5 + ["REPLAY"] * 5
        for r, l in zip(ws.manifest("build"), labs): ws.submit_label("build", r["shot_id"], l, "HIGH")
        ws.set_marks("build", "SYN_SRC_A", 0, 9, "e"); ws.complete_set("build"); self.clock.t = "2026-11-30T00:00:00Z"
        for sid in ws.reliability_sample("build"): ws.submit_relabel("build", sid, "LIVE_ACTION", "HIGH")
        rep = ws.reliability_report("build"); self.assertEqual(rep["n"], 1)


class T07_HTTPEndToEnd(Base):
    def test_ui(self):
        self.ws.open_set("build", self.mb)
        clip = os.path.join(self.tmp, "dummy.mp4"); open(clip, "wb").write(b"DUMMY")
        srv = UI.make_server(self.ws, "build", lambda v: clip); threading.Thread(target=srv.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{srv.server_address[1]}"
        try:
            page = urllib.request.urlopen(base + "/").read().decode(); self.assertIn("B000", page); self.assertIn("Submission is final", page)
            self.assertEqual(urllib.request.urlopen(base + "/clip/B000.mp4").read(), b"DUMMY")
            with self.assertRaises(urllib.error.HTTPError) as e: urllib.request.urlopen(base + "/clip/NOPE.mp4")
            def post(**f):
                f.setdefault("token", srv.token)
                data = urllib.parse.urlencode(f, doseq=True).encode()
                try: return urllib.request.urlopen(urllib.request.Request(base + "/submit", data=data)).status
                except urllib.error.HTTPError as ex: return ex.code
            self.assertEqual(post(shot_id="B000", label="LIVE_ACTION", confidence="HIGH", token="bad"), 403)
            self.assertEqual(post(shot_id="B000", label="UNKNOWN", confidence="HIGH"), 400)              # reason enforced server-side
            self.assertEqual(post(shot_id="B000", label="UNKNOWN", unknown_reason="MIXED_SHOT", confidence="LOW", flags=["BOUNDARY_ISSUE"]), 200)
            self.assertEqual(post(shot_id="B000", label="REPLAY", confidence="HIGH"), 400)               # final on submit over HTTP
            self.assertIn("B001", urllib.request.urlopen(base + "/").read().decode())                    # advances chronologically
            self.assertEqual(self.ws.effective_labels("build")[0]["unknown_reason"], "MIXED_SHOT")
        finally: srv.shutdown(); srv.server_close()


if __name__ == "__main__": unittest.main()
