#!/usr/bin/env python3
"""Narrow re-verification of the owner package V1.1 (no labels submitted; scratch workspace deleted).
Usage: verify_package_v1_1.py <new.zip> <previous_v1.zip> <search_dir>... -> JSON on stdout."""
import hashlib, json, os, shutil, subprocess, sys, tempfile, zipfile
new_zip, old_zip, *search = sys.argv[1:]
MAN = "d0c73ca106c9cef5e34766aaabfdceaf039e2735e58c76a52362c0a7d3a99aaf"; PROTO = "0b6c87405aa5c32d1dffd60bc54634835fb4afe710217b506ad508a1a8c3dad9"
sh = lambda b: hashlib.sha256(b).hexdigest()
zn, zo = zipfile.ZipFile(new_zip), zipfile.ZipFile(old_zip)
rel = lambda z, n: n.split("/", 1)[1]
hn = {rel(zn, n): sh(zn.read(n)) for n in zn.namelist()}; ho = {rel(zo, n): sh(zo.read(n)) for n in zo.namelist()}
rep = {"new_zip_sha256": sh(open(new_zip, "rb").read()), "files": sorted(hn),
       "manifest_build_sha256": hn["manifest_build.csv"], "manifest_matches_frozen": hn["manifest_build.csv"] == MAN,
       "protocol_sha256": hn["v061/exposure_design/EXPOSURE_V1_STAGE_D_LABELLING_PROTOCOL_V1_1.md"],
       "protocol_matches_frozen": hn["v061/exposure_design/EXPOSURE_V1_STAGE_D_LABELLING_PROTOCOL_V1_1.md"] == PROTO,
       "files_changed_vs_V1": sorted(k for k in hn if ho.get(k) != hn[k]), "files_unchanged_vs_V1": sorted(k for k in hn if ho.get(k) == hn[k]),
       "no_check_or_classifier_material": not any(w in n.lower() for n in hn for w in ("check", "classif", "result", "preflight"))}
# diff of the only code file expected to change
rep["labeller_ui_diff"] = [l for l in subprocess.run(["diff", "-u", "/dev/stdin", "/dev/null"], input=b"", capture_output=True).stdout.decode().splitlines()][:0]
import difflib
a = zo.read("STAGE_D_OWNER_PACKAGE_V1/v061/exposure_stage_d/labeller_ui.py").decode().splitlines(); b = zn.read("STAGE_D_OWNER_PACKAGE_V1_1/v061/exposure_stage_d/labeller_ui.py").decode().splitlines()
rep["labeller_ui_diff"] = [l for l in difflib.unified_diff(a, b, "V1", "V1_1", lineterm="", n=0) if not l.startswith("@@")]
tmp = tempfile.mkdtemp()
try:
    zn.extractall(tmp); pk = os.path.join(tmp, "STAGE_D_OWNER_PACKAGE_V1_1"); priv = os.path.join(tmp, "priv")
    cmd = ["python3", os.path.join(pk, "setup_owner.py"), "--root", priv] + [x for d in search for x in ("--search", d)]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=pk); rep["setup_owner_exit"] = r.returncode
    rep["setup_owner_found_all_five"] = r.stdout.count("FOUND") == 5 and "BUILD set opened: 169 shots" in r.stdout
    m = subprocess.run(["bash", os.path.join(pk, "step3_set_marks.sh"), priv], capture_output=True, text=True); rep["marks_set"] = m.stdout.count("mark set:")
    sys.path.insert(0, os.path.join(pk, "v061", "exposure_stage_d")); import labeller_core as C, labeller_ui as UI
    ws = C.Workspace(priv); prov = UI.ffmpeg_clip_provider(priv, os.path.join(priv, "sources.json")); src = json.load(open(os.path.join(priv, "sources.json")))
    probe = lambda p, e: subprocess.check_output(["ffprobe", "-v", "error", *e, "-of", "csv=p=0", p]).decode().split()
    rep["source_audio_streams"] = {k: len(probe(v, ["-select_streams", "a", "-show_entries", "stream=codec_type"])) for k, v in src.items()}
    rows = {}
    for sid, shot in (("rr_balor_full", None), ("b1_orton_rollins_wm31", None)):
        rowsm = [x for x in ws.manifest("build") if x["source_id"] == sid]; sh_ = rowsm[len(rowsm) // 2]["shot_id"]; v = ws.view("build", sh_)
        clip = prov(v); exp = v["context_end_s"] - v["context_start_s"]
        rows[sid] = {"shot_id_index_only": rowsm.index(next(x for x in rowsm if x["shot_id"] == sh_)), "expected_context_s": round(exp, 2),
                     "clip_duration_s": round(float(probe(clip, ["-show_entries", "format=duration"])[0]), 2),
                     "clip_streams": sorted(probe(clip, ["-show_entries", "stream=codec_type"])), "context_start_s": v["context_start_s"],
                     "context_end_s": v["context_end_s"], "t_start_s": v["t_start_s"], "t_end_s": v["t_end_s"]}
    rep["real_source_context_clips"] = rows
    rep["labels_submitted_build"] = len(ws._label_rows("build")); rep["labels_submitted_check"] = len(ws._label_rows("check"))
    rep["manifest_in_workspace_verified"] = bool(ws.manifest("build")) and len(ws.manifest("build")) == 169
finally: shutil.rmtree(tmp, ignore_errors=True)
rep["scratch_deleted"] = not os.path.exists(tmp)
print(json.dumps(rep, indent=1, sort_keys=True))
