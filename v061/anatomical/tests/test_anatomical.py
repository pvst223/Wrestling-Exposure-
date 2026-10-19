import unittest
import copy, inspect, json, os, sys, unittest
import numpy as np
try:
    import cv2, scipy  # noqa
except ImportError as e: raise unittest.SkipTest(f"cv2/scipy required: {e}")
HERE = os.path.dirname(os.path.abspath(__file__)); ANAT = os.path.dirname(HERE); sys.path[:0] = [HERE, os.path.join(ANAT, "impl")]
import synth, adapter, merge_guard, carry, pipeline, metrics, render_anat, preflight, run_anat, record_class as RC, ownership_stage
CUT = []
def one_person_clip(code="ACCEPT_A", frames=(0, 3, 6, 9, 12), masks=True, g=0.9, q=0.9):
    dets = {f: synth.det_frame([(60, 100)]) for f in frames}
    seg = {f: synth.seg_frame([synth.person_rect(60)]) for f in frames} if masks else {}
    tr = [synth.tracklet("c:s0:t0", "c", 0, dets, 0, frames)]; dec = synth.decisions("c:s0:t0", frames, code, g, q)
    return tr, dets, dec, seg
def run(tr, dets, dec, seg, cuts=()): return pipeline.run_clip(tr, dets, dec, seg, cuts, 200, 200)
class TRecord(unittest.TestCase):
    def test_truth_table(self):
        import itertools
        for i, nf, o, p in itertools.product(RC.ID_STATES, (False, True), RC.OWN_STATES, ("MEASURED", "NONE")):
            r = RC.classify(i, nf, o, p); ok = i in ("ACCEPT_A", "ACCEPT_B") and not nf and o == "SINGLE_BODY_SUPPORTED" and p == "MEASURED"
            self.assertEqual(r["assigned_label"] is not None, ok); self.assertEqual(r["identity_state_passthrough"], i); self.assertEqual(r["ownership_state_passthrough"], o)
    def test_merge_guard_is_not_a_classifier_input(self):
        self.assertEqual(list(inspect.signature(RC.classify).parameters), ["identity", "numeric_failure", "ownership", "pose_status"])
class TAdapter(unittest.TestCase):
    def test_blinding_and_mapping(self):
        tr, dets, dec, seg = one_person_clip(); rows = adapter.build(tr, dets, dec)
        self.assertTrue(all(r["det"] == 0 and r["identity_code"] == "ACCEPT_A" for r in rows)); self.assertTrue(all("truth" not in r and "b0_decision" not in r for r in rows))
        self.assertEqual(set(adapter.blind_rows(dec)[0]), set(adapter.ALLOWED_COLS))
    def test_missing_identity_and_numeric_failure_and_unmatched(self):
        tr, dets, dec, seg = one_person_clip(); dec = [d for d in dec if d["frame"] != 3]; dec[0]["q"] = float("nan"); dec[1]["g"] = "x"
        rows = {r["frame"]: r for r in adapter.build(tr, dets, dec)}
        self.assertEqual(rows[3]["identity_code"], "NO_IDENTITY_EVAL"); self.assertTrue(rows[0]["numeric_failure"]); self.assertEqual(rows[0]["identity_code"], "REJECT_NONTARGET"); self.assertTrue(rows[6]["numeric_failure"])
        tr2, d2, dec2, _ = one_person_clip(); del d2[6]; self.assertIsNone({r["frame"]: r for r in adapter.build(tr2, d2, dec2)}[6]["det"])
    def test_missing_column_raises(self):
        with self.assertRaises(KeyError): adapter.blind_rows([dict(tracklet="t", frame=0, decision="ACCEPT_A", g=1)])
class TPipeline(unittest.TestCase):
    def test_single_body_accept_is_assigned_and_flagged(self):
        rows, src = run(*one_person_clip()); self.assertTrue(all(r["record_class"] == "ASSIGNED_A" and r["identity_unvalidated_flag"] for r in rows), [r["record_class"] for r in rows])
    def test_abstain_never_assigned(self):
        rows, _ = run(*one_person_clip("ABSTAIN_AMBIGUOUS", q=0.5)); self.assertTrue(all(r["record_class"] == "UNASSIGNED_IDENTITY_AMBIGUOUS" and r["assigned_label"] is None for r in rows))
    def test_no_masks_not_evaluated_withheld(self):
        rows, _ = run(*one_person_clip(masks=False)); self.assertTrue(all(r["record_class"] == "WITHHELD_OWNERSHIP_NOT_EVALUATED" for r in rows))
    def test_numeric_failure_invalid(self):
        tr, dets, dec, seg = one_person_clip(q=float("nan")); rows, _ = run(tr, dets, dec, seg); self.assertTrue(all(r["record_class"] == "INVALID_NUMERIC" for r in rows))
    def test_nontarget_no_landmarks(self):
        rows, _ = run(*one_person_clip("REJECT_NONTARGET")); self.assertTrue(all(not r["landmarks_emitted"] for r in rows))
    def test_two_people_merged_mask_not_assigned(self):
        frames = (0, 3, 6); dets = {f: synth.det_frame([(75, 100), (105, 100)]) for f in frames}; seg = {f: synth.seg_frame([(40, 15, 140, 185)]) for f in frames}
        tr = [synth.tracklet("c:s0:t0", "c", 0, dets, 0, frames)]; rows, _ = run(tr, dets, synth.decisions("c:s0:t0", frames, "ACCEPT_A"), seg)
        self.assertTrue(all(r["record_class"] != "ASSIGNED_A" for r in rows), [r["record_class"] for r in rows])
    def test_skeleton_straddling_two_masks_withheld(self):
        frames = (0, 3); dets = {f: synth.det_frame([(60, 100)]) for f in frames}; seg = {f: synth.seg_frame([(30, 15, 90, 95), (30, 105, 90, 185)]) for f in frames}
        tr = [synth.tracklet("c:s0:t0", "c", 0, dets, 0, frames)]; rows, _ = run(tr, dets, synth.decisions("c:s0:t0", frames, "ACCEPT_B"), seg)
        self.assertTrue(all(r["record_class"] in RC.WITHHELD for r in rows))
    def test_cross_body_cue_forces_mixed_even_without_masks(self):
        dets = {0: synth.det_frame([(60, 100)])}; kp = dets[0]["kp"][0]; kp[9] = kp[9] + np.array([400, 0]); dets[0]["box"][0, 2] += 0
        tr = [synth.tracklet("c:s0:t0", "c", 0, dets, 0, (0,))]; rows, _ = run(tr, dets, synth.decisions("c:s0:t0", (0,), "ACCEPT_A"), {})
        self.assertEqual(rows[0]["record_class"], "WITHHELD_MIXED_BODY")
class TGuardDiagnosticOnly(unittest.TestCase):
    def merged_clip(self):
        frames = (0, 3, 6, 9, 12); dets = {0: synth.det_frame([(60, 100), (110, 100)]), 3: synth.det_frame([(60, 100), (110, 100)]), 6: synth.det_frame([(85, 100)]), 9: synth.det_frame([(85, 100)]), 12: synth.det_frame([(85, 100)])}
        seg = {f: synth.seg_frame([synth.person_rect(85, hw=60)]) for f in frames}; tr = [synth.tracklet("c:s0:t0", "c", 0, dets, 0, frames)]
        return tr, dets, synth.decisions("c:s0:t0", frames, "ACCEPT_A"), seg
    def test_guard_logs_trigger(self):
        rows, _ = run(*self.merged_clip()); self.assertTrue(any(r["merge_guard_would_trigger"] for r in rows)); self.assertTrue(any(not r["merge_guard_would_trigger"] for r in rows))
    def test_guard_changes_nothing_else(self):
        a_rows, a_src = run(*self.merged_clip())
        orig = merge_guard.log_shot; merge_guard.log_shot = lambda fb: {f: dict(merge_guard_would_trigger=False, merge_guard_reason="", merge_guard_since_frame=None) for f in fb}
        try: b_rows, b_src = run(*self.merged_clip())
        finally: merge_guard.log_shot = orig
        strip = lambda rs: [{k: v for k, v in r.items() if not k.startswith("merge_guard")} for r in rs]
        self.assertEqual(json.dumps(strip(a_rows), sort_keys=True, default=str), json.dumps(strip(b_rows), sort_keys=True, default=str)); self.assertEqual(json.dumps(strip(a_src), sort_keys=True, default=str), json.dumps(strip(b_src), sort_keys=True, default=str))
        for f in (metrics.m1_joint_table, metrics.m2_withholding, metrics.m3_disagreements, metrics.m6_coverage): self.assertEqual(f(a_rows), f(b_rows))
    def test_no_trigger_for_stable_two_people(self):
        g = merge_guard.log_shot({0: [(0, 0, 50, 100), (200, 0, 250, 100)], 3: [(0, 0, 50, 100), (200, 0, 250, 100)]}); self.assertFalse(any(v["merge_guard_would_trigger"] for v in g.values()))
class TCarry(unittest.TestCase):
    def meas(self, cls="ASSIGNED_A", frames=(0, 3, 6)): return [dict(tracklet="t", frame=f, record_class=cls, clip="c", shot=0) for f in frames]
    def test_stride3(self):
        s = carry.source_rate(self.meas(), []); self.assertEqual([r["frame"] for r in s], list(range(0, 10))); st = {r["frame"]: r["pose_status"] for r in s}
        self.assertEqual([st[f] for f in range(10)], ["MEASURED", "CARRIED", "CARRIED", "MEASURED", "CARRIED", "CARRIED", "MEASURED", "CARRIED", "CARRIED", "CARRIED"])
        self.assertTrue(all(not r["measurement"] and r["carry_age"] <= 3 for r in s if r["pose_status"] == "CARRIED"))
    def test_cut_resets(self):
        s = carry.source_rate(self.meas(frames=(0, 6)), [2]); self.assertEqual({r["frame"]: r["pose_status"] for r in s}[1], "CARRIED"); self.assertNotIn(2, [r["frame"] for r in s if r["pose_status"] == "CARRIED"]); self.assertNotIn(3, [r["frame"] for r in s])
    def test_no_carry_from_non_assigned(self):
        for c in ("UNASSIGNED_IDENTITY_AMBIGUOUS", "WITHHELD_MIXED_BODY", "NONTARGET", "INVALID_NUMERIC", "WITHHELD_OWNERSHIP_UNCERTAIN"): self.assertTrue(all(r["pose_status"] == "MEASURED" for r in carry.source_rate(self.meas(c), [])))
    def test_carried_never_in_metrics(self):
        rows, src = run(*one_person_clip()); self.assertEqual(len(metrics.m1_joint_table(src)), len(metrics.m1_joint_table(rows))); self.assertEqual(sum(x["n"] for x in metrics.m1_joint_table(src)), len(rows)); self.assertGreater(metrics.m8_carry(src)["carried_share"], 0)
class TMetrics(unittest.TestCase):
    def rows(self, per_clip=None):
        out = []
        for c in ("c1", "c2", "c3", "c4"):
            for i in range(24):
                cls = "ASSIGNED_A" if i < 10 else ("WITHHELD_MIXED_BODY" if i < 18 else "UNASSIGNED_IDENTITY_AMBIGUOUS")
                ident = "ACCEPT_A" if i < 18 else "ABSTAIN_AMBIGUOUS"; own = "SINGLE_BODY_SUPPORTED" if cls in ("ASSIGNED_A", "UNASSIGNED_IDENTITY_AMBIGUOUS") else "MIXED_BODY_SUSPECTED"
                out.append(dict(clip=c, shot=0, tracklet=f"{c}:s0:t0", frame=i * 3, record_class=cls, identity_state_passthrough=ident, ownership_state_passthrough=own, numeric_failure=False, pose_status="MEASURED", measurement=True, n_landmarks=13, box=[0, 0, 1, 1], assigned_label="A" if cls == "ASSIGNED_A" else None))
        return out
    def test_m2_flag_and_ci(self):
        m = {(x["clip"], x["shot"]): x for x in metrics.m2_withholding(self.rows())}; x = m[("c1", 0)]
        self.assertEqual((x["withheld"], x["accept_measured"]), (8, 18)); self.assertTrue(x["diagnostic_flag_ge_20pct"]); self.assertTrue(x["ci95"][0] < 0.44 < x["ci95"][1]); self.assertEqual(m[("ALL", "ALL")]["accept_measured"], 72)
    def test_m2_flag_off_below_20(self):
        rs = self.rows(); [r.update(record_class="ASSIGNED_A", ownership_state_passthrough="SINGLE_BODY_SUPPORTED") for r in rs if r["record_class"] == "WITHHELD_MIXED_BODY"]; self.assertFalse(any(x["diagnostic_flag_ge_20pct"] for x in metrics.m2_withholding(rs)))
    def test_m3_m4(self):
        rs = self.rows(); self.assertEqual(metrics.m3_disagreements(rs)["ACCEPT_but_ownership_not_single"], 32); self.assertEqual(metrics.m3_disagreements(rs)["ABSTAIN_with_single_body"], 24)
        rs[1]["record_class"] = "ASSIGNED_B"; rs[1]["assigned_label"] = "B"; self.assertEqual(metrics.m4_label_flips(rs)["n_flips"], 2)
    def test_m7(self): r = metrics.m7_cut_crosscheck([0, 100, 200], [101, 300]); self.assertEqual((r["frozen_only"], r["classifier_only"], r["agree"]), ([200], [300], 1))
    def test_m9_selection_and_summary(self):
        sheet, key, short = metrics.m9_select(self.rows(), 1234); self.assertEqual(short, {}); n = {s: sum(1 for k in key if k["stratum"] == s) for s in ("ASSIGNED", "WITHHELD")}; self.assertEqual(n, {"ASSIGNED": 30, "WITHHELD": 30})
        for s in ("ASSIGNED", "WITHHELD"): self.assertEqual({k["clip"] for k in key if k["stratum"] == s}, {"c1", "c2", "c3", "c4"})
        self.assertTrue(all(set(x) == {"review_id", "clip", "tracklet", "frame", "box"} for x in sheet))   # status-blind
        self.assertEqual((sheet, key, short), metrics.m9_select(self.rows(), 1234))
        v = [dict(review_id=k["review_id"], verdict="MIXED_OR_WRONG_BODY" if i == 0 and k["stratum"] == "ASSIGNED" else "SINGLE_PERSON") for i, k in enumerate(key)]
        s = metrics.m9_summarise(key, v); self.assertEqual(s["ASSIGNED"]["reviewed"], 30); self.assertEqual(len(s["contaminated_emitted_skeletons_individually"]), sum(1 for x in v if x["verdict"] == "MIXED_OR_WRONG_BODY" and any(k["review_id"] == x["review_id"] and k["stratum"] == "ASSIGNED" for k in key))); self.assertIn("ANNOTATION-PROVISIONAL", s["label"])
    def test_m9_shortfall(self):
        rs = [r for r in self.rows() if r["clip"] == "c1"][:8]; _, key, short = metrics.m9_select(rs, 1); self.assertIn("ASSIGNED", short); self.assertEqual(short["ASSIGNED"]["reviewed"], short["ASSIGNED"]["available"])
    def test_no_exposure_keys(self):
        rep, _, _ = metrics.report(self.rows(), [dict(pose_status="MEASURED")], [0], [], 1); txt = json.dumps(rep).lower()
        for w in ("distance", "impact", "workload", "fatigue", "injury", "intensity", "com_"): self.assertNotIn(w, txt)
class TRender(unittest.TestCase):
    def rec(self, cls):
        kp, kc = synth.skel(100, 100); return dict(record_class=cls, box=[60, 10, 140, 190], kp=kp.tolist(), kpc=kc.tolist(), tracklet="c:s0:t0", pose_status="CARRIED" if cls.startswith("CARRIED") else "MEASURED", q=0.8)
    def test_class_coverage_distinct(self):
        imgs = {}
        for c in RC.CLASSES:
            f = np.full((200, 200, 3), 60, np.uint8); r = self.rec(c); render_anat.draw_record(f, r) if c != "NO_POSE" else None; imgs[c] = f
        blank = np.full((200, 200, 3), 60, np.uint8); self.assertTrue((imgs["NO_POSE"] == blank).all())
        for c in RC.CLASSES:
            if c != "NO_POSE": self.assertGreater(int((imgs[c] != blank).any(2).sum()), 20, c)
        cl = list(RC.CLASSES)
        for i in range(len(cl)):
            for j in range(i + 1, len(cl)): self.assertFalse((imgs[cl[i]] == imgs[cl[j]]).all(), (cl[i], cl[j]))
    def test_compose_deterministic_and_panel(self):
        fr = np.full((200, 200, 3), 60, np.uint8); rows = [dict(self.rec("ASSIGNED_A"), merge_guard_would_trigger=True)]; ctx = dict(frame=3, fps=30.0, cut_banner=False)
        a = render_anat.compose(fr, rows, ctx); b = render_anat.compose(fr, rows, ctx); self.assertTrue((a == b).all()); self.assertEqual(a.shape, (200, 200 + render_anat.PANEL_W, 3))
    def test_sidecar_matches_rows_and_has_no_exposure_fields(self):
        _, src = run(*one_person_clip()); sc = render_anat.sidecar_rows(src); self.assertEqual(len(sc), len(src)); self.assertEqual([s["record_class"] for s in sc], [r["record_class"] for r in sorted(src, key=lambda r: (r["frame"], r["tracklet"]))])
        self.assertTrue(all("merge_guard_would_trigger" in s and "identity_state_passthrough" in s and "ownership_state_passthrough" in s for s in sc))
        for w in ("distance", "impact", "workload", "com", "speed"): self.assertFalse(any(w in k for s in sc for k in s))
class TDeterminismAndPreflight(unittest.TestCase):
    def test_pipeline_deterministic(self):
        a = run(*one_person_clip()); b = run(*one_person_clip()); self.assertEqual(json.dumps(a, sort_keys=True, default=str), json.dumps(b, sort_keys=True, default=str))
    def test_reused_files_present_and_hashes(self): self.assertTrue(preflight.check_reused())
    def test_reused_tamper_detected(self):
        j = json.load(open(os.path.join(ANAT, "REUSED_V05_HASHES.json"))); k = sorted(j["files"])[0]; orig = preflight.sha
        preflight.sha = lambda p: "0" * 64 if p.endswith(k) else orig(p)
        try:
            with self.assertRaises(preflight.Blocked): preflight.check_reused()
        finally: preflight.sha = orig
    def test_reused_hashes_equal_provenance(self):
        prov = json.load(open(os.path.join(os.path.dirname(ANAT), "anatomical_plan", "REUSE_PROVENANCE.json")))["sha256"]; j = json.load(open(os.path.join(ANAT, "REUSED_V05_HASHES.json")))
        for p, h in j["files"].items(): self.assertEqual(prov[os.path.basename(p)], h)
        self.assertEqual(j["models"]["yolov8m-pose.pt"], preflight.POSE_SHA256); self.assertEqual(j["models"]["yolov8m-seg.pt"], preflight.SEG_SHA256)
    def test_locked_impl_unchanged(self): self.assertTrue(preflight.check_locked_impl())
    def test_authorization_absent_blocks_run(self):
        with self.assertRaises(preflight.Blocked): preflight.check_authorization(os.path.join(ANAT, "AUTHORIZATION_RECORD.json"), os.path.join(preflight.REPO, "v06", "frozen", "AUDIT_LEDGER.jsonl"))
        with self.assertRaises(preflight.Blocked): run_anat.main(os.path.join(ANAT, "AUTHORIZATION_RECORD.json"), os.path.join(preflight.REPO, "v06", "frozen", "AUDIT_LEDGER.jsonl"), "", "", "")
    def test_clip_set_and_exactly_once(self):
        with self.assertRaises(preflight.Blocked): preflight.check_clips(list(preflight.CLIPS[:3]) + ["b1_hbk_raw_20050502"])
        self.assertTrue(preflight.check_clips(preflight.CLIPS))
        with self.assertRaises(preflight.Blocked): preflight.check_exactly_once(__file__)
    def test_model_hash_check_blocks_wrong_weights(self):
        with self.assertRaises(preflight.Blocked): preflight.check_models(__file__, __file__)
    def test_self_contained_no_external_repo_paths(self):
        for fn in ("test_anatomical.py", "synth.py"): self.assertNotIn("versions/", open(os.path.join(HERE, fn)).read().replace('"versions/"', ""))
class TSegWrapper(unittest.TestCase):
    def test_pack_equals_original_expression(self):
        import cv2, seg_posegrid as sp
        rng = np.random.RandomState(0); m = rng.rand(2, 180, 320).astype(np.float32); bx = rng.rand(2, 4) * 100; cf = rng.rand(2)
        orig_ms = np.stack([cv2.resize((x > 0.5).astype(np.uint8), (320, 180), interpolation=cv2.INTER_NEAREST) for x in m]); got = sp.pack(bx, cf, m)
        self.assertTrue((got["mask"] == np.packbits(orig_ms, axis=-1)).all()); self.assertEqual(got["shape"], (180, 320)); self.assertEqual(got["box"].dtype, np.float32)
        e = sp.pack(np.zeros((0, 4)), np.zeros(0), None); self.assertEqual(e["mask"].shape, (0, 180, 40))
    def test_settings_match_original_source(self):
        src = open(os.path.join(ANAT, "reused_v05", "src", "seg_extract.py")).read(); self.assertIn("IMGSZ, CONF = 960, 0.10", src); self.assertIn("MW, MH = 320, 180", src)
        import seg_posegrid as sp; self.assertEqual((sp.IMGSZ, sp.CONF, sp.MW, sp.MH), (960, 0.10, 320, 180))
if __name__ == "__main__": unittest.main(verbosity=1)
