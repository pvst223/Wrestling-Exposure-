#!/usr/bin/env python3
"""Frozen-hash check (tooling only). Verifies:
 1. every file in FROZEN_MANIFEST.txt still has its recorded SHA-256 and no extra files exist under frozen dirs;
 2. spec_v4 MANIFEST_SHA256.txt hash is efb2a797... and spec_v4 files match their manifest;
 3. AUDIT_LEDGER.jsonl hash chain is intact and its first N lines equal the anchored prefix (append-only).
Usage: frozen_hash_check.py [--write-manifest]"""
import hashlib, json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
TOOL = "v061/tooling"
FROZEN_DIRS = ["v06/frozen","v06/posthoc_v1","v06/tools","v061/spec_v4","v061/exploratory_v1","v061/gemini_procedure_frozen_v1"]
LEDGER = "v06/frozen/AUDIT_LEDGER.jsonl"
SPEC4_MANIFEST_SHA = "efb2a797c358cdcad73bc933ccc5a80d95979610179240daf6229b4ba86c88af"
def sha(p):
    return hashlib.sha256(open(p,"rb").read()).hexdigest()
def tracked(dirs):
    out = subprocess.check_output(["git","ls-files","-z"]+dirs).decode().split("\0")
    return sorted(f for f in out if f and f != LEDGER)
def main():
    mpath = f"{TOOL}/FROZEN_MANIFEST.txt"; apath = f"{TOOL}/LEDGER_ANCHOR.json"
    if "--write-manifest" in sys.argv:
        open(mpath,"w").write("".join(f"{sha(f)}  {f}\n" for f in tracked(FROZEN_DIRS)))
        lines = open(LEDGER,"rb").read().splitlines(keepends=True)
        json.dump({"n_lines":len(lines),"prefix_sha256":hashlib.sha256(b"".join(lines)).hexdigest()}, open(apath,"w"), indent=1)
        print("wrote", mpath, apath); return 0
    err = []
    rec = {}
    for l in open(mpath):
        h, f = l.rstrip("\n").split("  ",1); rec[f]=h
    cur = set(tracked(FROZEN_DIRS))
    for f in sorted(set(rec)-cur): err.append(f"missing/removed: {f}")
    for f in sorted(cur-set(rec)): err.append(f"unrecorded file in frozen dir: {f}")
    for f in sorted(cur & set(rec)):
        if sha(f)!=rec[f]: err.append(f"modified: {f}")
    if sha("v061/spec_v4/MANIFEST_SHA256.txt")!=SPEC4_MANIFEST_SHA: err.append("spec_v4 manifest hash changed")
    prev=None; n=0
    raw = open(LEDGER,"rb").read().splitlines(keepends=True)
    for ln in raw:
        e = json.loads(ln); n+=1
        if e.get("prev_entry_sha256")!=prev: err.append(f"ledger chain broken at entry {e.get('id')}")
        prev = hashlib.sha256(json.dumps(e, sort_keys=True).encode()).hexdigest()
    a = json.load(open(apath))
    if len(raw)<a["n_lines"] or hashlib.sha256(b"".join(raw[:a["n_lines"]])).hexdigest()!=a["prefix_sha256"]:
        err.append("ledger anchored prefix altered or truncated")
    for e in err: print("FAIL", e)
    print("frozen-hash check:", "FAIL" if err else "OK", f"({len(cur)} files, {n} ledger entries)")
    return 1 if err else 0
sys.exit(main())
