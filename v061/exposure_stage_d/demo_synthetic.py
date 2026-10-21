#!/usr/bin/env python3
"""Synthetic-only demonstration: drives the whole workflow on dummy data (lavfi test pattern, SYN_* ids) and
prints a JSON evidence record. No real footage exists anywhere in this run."""
import json, os, sys, tempfile, shutil, subprocess
import labeller_core as C, labeller_ui as UI, make_synthetic as MS


def run():
    tmp = tempfile.mkdtemp(); t = ["2026-10-22T10:00:00Z"]; clock = lambda: t[0]
    ws = C.Workspace(os.path.join(tmp, "w"), clock=clock); ev = {"protocol_sha256": ws.protocol_version, "steps": []}
    st = lambda k, v: ev["steps"].append({k: v})
    vid = MS.make_test_video(os.path.join(tmp, "syn.mp4"), 40); json.dump({"SYN_SRC_A": vid, "SYN_SRC_B": vid}, open(os.path.join(tmp, "src.json"), "w"))
    mb = MS.write_manifest(os.path.join(tmp, "mb.csv"), "build", "B", 5, t0=10.0); mc = MS.write_manifest(os.path.join(tmp, "mc.csv"), "check", "C", 4, source="SYN_SRC_B", t0=10.0)
    st("open_build", ws.open_set("build", mb)["data"]); st("open_check", ws.open_set("check", mc)["data"])
    prov = UI.ffmpeg_clip_provider(ws.root, os.path.join(tmp, "src.json"))
    clips = {}
    for sid in ("B000", "C001"):
        s = "build" if sid[0] == "B" else "check"; v = ws.view(s, sid); out = prov(v)
        d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out]))
        clips[sid] = {"view": v, "clip_duration_s": round(d, 2), "expected_s": round(float(v["context_end_s"]) - float(v["context_start_s"]), 2)}
    st("context_clips", clips)
    rej = {}
    def tryit(name, f):
        try: f(); rej[name] = "ACCEPTED (unexpected)"
        except C.ToolError as e: rej[name] = f"{type(e).__name__}: {e}"
    tryit("UNKNOWN_without_reason", lambda: ws.submit_label("build", "B000", "UNKNOWN", "HIGH"))
    tryit("invalid_category", lambda: ws.submit_label("build", "B000", "LIVE", "HIGH"))
    tryit("OTHER_without_note", lambda: ws.submit_label("build", "B000", "UNKNOWN", "LOW", "OTHER"))
    ws.submit_label("build", "B000", "LIVE_ACTION", "HIGH"); tryit("resubmit_final", lambda: ws.submit_label("build", "B000", "REPLAY", "HIGH"))
    tryit("check_export_before_unseal", lambda: ws.export_for_rule_builder("check", os.path.join(tmp, "x")))
    for r in ws.manifest("build")[1:]: ws.submit_label("build", r["shot_id"], "CLOSE_UP", "MEDIUM")
    ws.set_marks("build", "SYN_SRC_A", 10.04, 22.96, "synthetic evidence"); st("complete_build", ws.complete_set("build")["data"])
    st("correction", ws.apply_correction("build", "B002", "TOOL_ERROR", "synthetic mis-click", "REPLAY", "MEDIUM")["reason"])
    for i, r in enumerate(ws.manifest("check")):
        if i == 0: ws.submit_label("check", r["shot_id"], "UNKNOWN", "LOW", "REPLAY_AMBIGUOUS")
        else: ws.submit_label("check", r["shot_id"], "LIVE_ACTION", "HIGH")
    ws.set_marks("check", "SYN_SRC_B", 10, 20, "synthetic evidence"); ws.complete_set("check"); st("seal_check", ws.seal_check()["data"])
    tryit("check_export_while_sealed", lambda: ws.export_for_rule_builder("check", os.path.join(tmp, "x"))); tryit("unseal_before_rule_frozen", ws.unseal_check); st("freeze_rule", ws.freeze_rule("0" * 63 + "1")["data"])
    tryit("build_correction_after_freeze", lambda: ws.apply_correction("build", "B000", "TOOL_ERROR", "x", "REPLAY", "HIGH"))
    st("unseal_check", ws.unseal_check()["data"]); st("reference_summary_check", ws.reference_summary("check"))
    ev["rejections"] = rej; ev["chain_events"] = ws.verify_chain(); ev["event_types"] = [e["type"] for e in ws.events()]
    ev["reliability_sample_build"] = ws.reliability_sample("build"); ev["relabel_opens_utc"] = ws.relabel_available_from("build")
    ev["label_file_columns"] = list(C.LABEL_COLUMNS)
    shutil.rmtree(tmp); return ev


if __name__ == "__main__": print(json.dumps(run(), indent=1, sort_keys=True))
