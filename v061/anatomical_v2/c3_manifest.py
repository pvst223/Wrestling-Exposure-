#!/usr/bin/env python3
"""Manifest tool for the Anatomy V2 (C3) candidate (v061/anatomical_v2/**), excluding the manifest itself. `--write` regenerates; default checks."""
import hashlib, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DIRS = ["v061/anatomical_v2"]; MAN = "v061/anatomical_v2/C3_IMPLEMENTATION_MANIFEST.txt"
def sha(p): return hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest()
def files():
    out = []
    for d in DIRS:
        for dp, dn, fs in os.walk(os.path.join(ROOT, d)):
            dn[:] = [x for x in dn if x not in ("__pycache__", "results")]
            out += [os.path.relpath(os.path.join(dp, f), ROOT).replace(os.sep, "/") for f in fs if not f.endswith(".pyc") and not f.startswith("RESULT_")]
    return sorted(set(out) - {MAN})
cur = {f: sha(f) for f in files()}
if "--write" in sys.argv:
    open(os.path.join(ROOT, MAN), "w").write("".join(f"{h}  {f}\n" for f, h in sorted(cur.items()))); print("written", len(cur)); sys.exit(0)
rec = dict(reversed(l.rstrip("\n").split("  ", 1)) for l in open(os.path.join(ROOT, MAN)) if l.strip())
bad = [f for f in cur if rec.get(f) != cur[f]] + [f for f in rec if f not in cur]
for b in bad: print("MISMATCH", b)
print("C3 manifest:", "FAIL" if bad else "OK", len(cur), "files"); sys.exit(1 if bad else 0)
