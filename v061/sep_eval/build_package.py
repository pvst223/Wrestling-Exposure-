#!/usr/bin/env python3
"""Build the self-contained reviewer package from the repository: regenerates DEPENDENCY_HASHES.txt from git HEAD blobs (byte-identity proof) and zips the dependency trees + new code. Usage: build_package.py <out.zip> [extra files...]"""
import hashlib, os, subprocess, sys, zipfile
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEP_DIRS = ["v061/anatomical", "v061/anatomical_plan", "v061/impl", "v061/tests"]; DEP_FILES = ["v061/requirements.lock", "v061/ENVIRONMENT.md", "v061/tooling/impl_manifest.py"]; NEW_DIRS = ["v061/sep_eval", "v061/anatomical_separated_eval_design"]
def git(*a): return subprocess.check_output(["git", *a], cwd=ROOT)
def main(out, extra):
    deps = sorted(git("ls-files", *DEP_DIRS, *DEP_FILES).decode().split()); lines = ["# sha256 of each vendored dependency file = git HEAD blob (byte-identical to the frozen repository)"]
    for f in deps:
        b = git("show", "HEAD:" + f); assert hashlib.sha256(b).hexdigest() == hashlib.sha256(open(os.path.join(ROOT, f), "rb").read()).hexdigest(), f; lines.append(f"{hashlib.sha256(b).hexdigest()}  {f}")
    open(os.path.join(ROOT, "v061/sep_eval/DEPENDENCY_HASHES.txt"), "w").write("\n".join(lines) + "\n")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in deps: z.write(os.path.join(ROOT, f), f)
        for d in NEW_DIRS:
            for dp, dn, fn in os.walk(os.path.join(ROOT, d)):
                dn[:] = [x for x in dn if x != "__pycache__"]
                for x in sorted(fn):
                    if not x.endswith(".pyc"): p = os.path.join(dp, x); z.write(p, os.path.relpath(p, ROOT))
        for e in extra: z.write(e, os.path.basename(e))
    print(len(deps), "dependency files;", out)
main(sys.argv[1], sys.argv[2:])
