#!/usr/bin/env python3
"""Hash manifest of the V0.6.1 implementation tree. --write regenerates v061/impl/IMPLEMENTATION_MANIFEST.txt; default checks it (fails on any mismatch or unrecorded file)."""
import hashlib, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DIRS = ["v061/impl", "v061/tests"]; EXTRA = ["v061/requirements.lock", "v061/ENVIRONMENT.md"]
MAN = "v061/impl/IMPLEMENTATION_MANIFEST.txt"
def sha(p):
    h = hashlib.sha256(); h.update(open(os.path.join(ROOT, p), "rb").read()); return h.hexdigest()
def files():
    out = list(EXTRA)
    for d in DIRS:
        for dp, dn, fs in os.walk(os.path.join(ROOT, d)):
            dn[:] = [x for x in dn if x != "__pycache__"]
            for f in fs:
                if not f.endswith(".pyc"): out.append(os.path.relpath(os.path.join(dp, f), ROOT).replace(os.sep, "/"))
    return sorted(set(out) - {MAN})
def main():
    cur = {f: sha(f) for f in files()}
    if "--write" in sys.argv:
        open(os.path.join(ROOT, MAN), "w").write("".join(f"{h}  {f}\n" for f, h in sorted(cur.items()))); print("manifest written:", len(cur), "files"); return
    rec = dict(reversed(l.rstrip("\n").split("  ", 1)) for l in open(os.path.join(ROOT, MAN)) if l.strip())
    bad = [f for f in cur if rec.get(f) != cur[f]] + [f for f in rec if f not in cur]
    for b in bad: print("MISMATCH", b)
    print("implementation manifest:", "FAIL" if bad else "OK", len(cur), "files"); sys.exit(1 if bad else 0)
main()
