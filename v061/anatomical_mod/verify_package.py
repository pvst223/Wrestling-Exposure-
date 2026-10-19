#!/usr/bin/env python3
"""Verify a clean unzip of the readiness package: every vendored dependency file under v061/anatomical and v061/anatomical_plan is byte-identical (sha256) to DEPENDENCY_HASHES.txt,
which was generated from the frozen repository commit; the anatomical implementation manifest hash and the reused V0.5 hashes also match. Run from the package root: python v061/anatomical_mod/verify_package.py"""
import hashlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
EXPECT_ANAT_MANIFEST = "f5936ce8bee667f15eaa55c2545a15ecf060afa06b1539abd3e824a8351b7dfb"; EXPECT_LOCKED_IMPL_MANIFEST = "eb99beb359ee28dca883d7976ede4385f8dafb2e739d729f89a3358cd3ea073d"
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def main():
    lst = [l.split("  ", 1) for l in open(os.path.join(HERE, "DEPENDENCY_HASHES.txt")).read().splitlines() if l.strip() and not l.startswith("#")]; bad = []; seen = set()
    for h, f in lst:
        p = os.path.join(ROOT, f); seen.add(f)
        if not os.path.exists(p): bad.append(("MISSING", f))
        elif sha(p) != h: bad.append(("HASH_MISMATCH", f))
    extra = []
    for d in ("v061/anatomical", "v061/anatomical_plan", "v061/impl", "v061/tests"):
        for dp, dn, fn in os.walk(os.path.join(ROOT, d)):
            dn[:] = [x for x in dn if x != "__pycache__"]
            for x in fn:
                rel = os.path.relpath(os.path.join(dp, x), ROOT).replace(os.sep, "/")
                if rel not in seen and not x.endswith(".pyc"): extra.append(rel)
    am = sha(os.path.join(ROOT, "v061/anatomical/ANATOMICAL_IMPLEMENTATION_MANIFEST.txt")); ok_m = am == EXPECT_ANAT_MANIFEST and sha(os.path.join(ROOT, "v061/impl/IMPLEMENTATION_MANIFEST.txt")) == EXPECT_LOCKED_IMPL_MANIFEST
    rv = json.load(open(os.path.join(ROOT, "v061/anatomical/REUSED_V05_HASHES.json"))); rbad = []
    for k, v in (rv.get("files") or rv).items():
        p = os.path.join(ROOT, "v061/anatomical", k)
        if not isinstance(v, str) or not os.path.exists(p) or sha(p) != v: rbad.append(k)
    print(f"dependency files listed: {len(lst)}; mismatches: {len(bad)}; unlisted extra files: {len(extra)}; anatomical + locked-implementation manifests {'OK' if ok_m else 'MISMATCH'}; reused-v05 hash mismatches: {len(rbad)}")
    for b in bad[:20]: print(" ", b)
    for b in extra[:20]: print("  EXTRA", b)
    sys.exit(0 if not bad and not extra and ok_m and not rbad else 1)
if __name__ == "__main__": main()
