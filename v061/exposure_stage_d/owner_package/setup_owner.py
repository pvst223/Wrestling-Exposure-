#!/usr/bin/env python3
"""Owner setup for Stage-D BUILD labelling (Mac/Linux). Verifies the frozen protocol and BUILD manifest, finds your five
existing source videos by SHA-256 (nothing is copied or altered), writes sources.json, and opens the BUILD set once.
It assigns no labels."""
import argparse, hashlib, json, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "v061", "exposure_stage_d"))
import labeller_core as C

MANIFEST_SHA = "d0c73ca106c9cef5e34766aaabfdceaf039e2735e58c76a52362c0a7d3a99aaf"
SOURCES = {   # source_id: (bytes, sha256, name of the file the project holds)
    "b1_orton_rollins_wm31": (19786272, "eb9625d30eef49670fdb6d469f77d549ec364005f95e73c207150320c16b3723", "orton_rollins_wm31.mp4"),
    "b2_batch2_clip_condensed": (20652610, "e89e92c71690d2e7285ebce6e0877d74b9c685cb3ca504e83644fc2814bb5486", "b2_batch2_clip_condensed.mp4"),
    "b2_videoplayback_2": (5156110, "d6728cb914fd0bbd2e4efdb14a4e1a08a8c8dfbaa387db3b6535417008136319", "b2_videoplayback_2.mp4"),
    "b2_videoplayback_5": (11023849, "e72c5561b15de92fc5c34f24ad54097111c753ce49c12603cbaccc5265fcb575", "b2_videoplayback_5.mp4"),
    "rr_balor_full": (385742414, "7d718d6c82fd893c62634a5b62ec48178543bfec95164d80c344614057ee26ee",
                      "FULL_MATCH_-_Roman_Reigns_vs__Finn_Bálor_Raw__July_25__2016_-_WWE__1080p_.mp4"),
}
EXTS = {".mp4", ".mov", ".m4v", ".mkv"}


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def find(search_dirs, mapping):
    by_size = {}
    for sid, (sz, h, _) in SOURCES.items(): by_size.setdefault(sz, []).append(sid)
    found = dict(mapping)
    for d in search_dirs:
        for dp, dn, fn in os.walk(os.path.expanduser(d)):
            dn[:] = [x for x in dn if not x.startswith(".") and x != "Library"]
            for n in fn:
                if os.path.splitext(n)[1].lower() not in EXTS: continue
                p = os.path.join(dp, n)
                try: sz = os.path.getsize(p)
                except OSError: continue
                for sid in by_size.get(sz, []):
                    if sid in found: continue
                    try:
                        if sha_file(p) == SOURCES[sid][1]: found[sid] = p
                    except OSError: pass
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="~/stage_d_private"); ap.add_argument("--search", action="append", default=[])
    ap.add_argument("--path", action="append", default=[], help="source_id=/full/path (optional manual mapping)")
    a = ap.parse_args(); root = os.path.expanduser(a.root); ok = True
    print("== checks")
    print("python", sys.version.split()[0])
    for t in ("ffmpeg", "ffprobe"):
        w = shutil.which(t); print(t, w or "MISSING  -> install with: brew install ffmpeg"); ok &= bool(w)
    try: print("protocol V1.1 sha256 OK", C.verify_protocol()[:12])
    except C.ToolError as e: print("PROTOCOL PROBLEM:", e); ok = False
    mp = os.path.join(HERE, "manifest_build.csv"); mh = C.sha(open(mp, "rb").read())
    print("manifest_build.csv sha256", "OK" if mh == MANIFEST_SHA else f"MISMATCH {mh}"); ok &= mh == MANIFEST_SHA
    manual = {}
    for s in a.path:
        k, v = s.split("=", 1); manual[k] = os.path.expanduser(v)
    dirs = a.search or ["~/Downloads", "~/Movies", "~/Desktop", "~/Documents"]
    print("== searching for your source videos in", dirs, "(this can take a minute)")
    found = find(dirs, {k: v for k, v in manual.items() if os.path.exists(v) and sha_file(v) == SOURCES.get(k, (0, ""))[1]})
    for sid, (sz, h, name) in SOURCES.items():
        print(f"  {sid:28s}", ("FOUND " + found[sid]) if sid in found else f"MISSING  need sha256 {h}  (project file name {name}, {sz} bytes)")
    if len(found) != len(SOURCES):
        print("\nSome sources were not found. Put them anywhere under your home folder, or re-run with --search <folder> "
              "or --path source_id=/full/path/to/file. Nothing else was changed."); sys.exit(1)
    if not ok: print("\nFix the items above, then re-run."); sys.exit(1)
    os.makedirs(root, exist_ok=True)
    json.dump({k: found[k] for k in SOURCES}, open(os.path.join(root, "sources.json"), "w"), indent=1)
    ws = C.Workspace(root)
    if ws._has("SET_OPEN", "build"): print("BUILD set already open (kept as is).")
    else: print("BUILD set opened:", ws.open_set("build", mp)["data"]["n_shots"], "shots")
    print("\nREADY. private folder:", root, "\nNext: bash step3_set_marks.sh   (once), then launch the labelling page (see README_OWNER.md).")


if __name__ == "__main__": main()
