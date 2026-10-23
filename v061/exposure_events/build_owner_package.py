"""Builds the owner package zip deterministically (fixed timestamps, sorted entries) with MANIFEST.json and verify_package.py."""
import hashlib, json, os, sys, zipfile
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
DESIGN = os.path.join(REPO, "v061", "exposure_design", "EXPOSURE_CONSTRUCT_AUDIT_EXPERIMENT_V1_1_DESIGN.md")
FILES = {  # package path -> source
    "event_core.py": "event_core.py", "event_ui.py": "event_ui.py", "event_cli.py": "event_cli.py", "landing_metrics.py": "landing_metrics.py",
    "source_table_v1_1.json": "source_table_v1_1.json", "config_v1_1.json": "config_v1_1.json", "README_OWNER_EVENTS.md": "README_OWNER_EVENTS.md",
    "TEST_RESULTS_SYNTHETIC.txt": "TEST_RESULTS_SYNTHETIC.txt", "build_nonlive_filter.py": "build_nonlive_filter.py",
}
VERIFY = '''#!/usr/bin/env python3
"""Recomputes every file hash of this package against MANIFEST.json."""
import hashlib, json, os, sys
H = os.path.dirname(os.path.abspath(__file__)); m = json.load(open(os.path.join(H, "MANIFEST.json"))); bad = []
for n, h in sorted(m["files"].items()):
    p = os.path.join(H, n)
    if not os.path.exists(p) or hashlib.sha256(open(p, "rb").read()).hexdigest() != h: bad.append(n)
print("PACKAGE OK" if not bad else "PACKAGE MODIFIED: %s" % bad); sys.exit(1 if bad else 0)
'''
def sha(b): return hashlib.sha256(b).hexdigest()
def build(out):
    content = {k: open(os.path.join(HERE, v), "rb").read() for k, v in FILES.items()}
    content["EXPOSURE_CONSTRUCT_AUDIT_EXPERIMENT_V1_1_DESIGN.md"] = open(DESIGN, "rb").read()
    td = os.path.join(REPO, "v061", "exposure_stage_d", "tests")
    for t in ("test_exposure_events.py", "test_landing_metrics.py"): content["tests/" + t] = open(os.path.join(td, t), "rb").read()
    man = {"design_sha256": sha(content["EXPOSURE_CONSTRUCT_AUDIT_EXPERIMENT_V1_1_DESIGN.md"]), "metrics_code_sha256": sha(content["landing_metrics.py"]),
           "files": {k: sha(v) for k, v in sorted(content.items())}}
    content["MANIFEST.json"] = (json.dumps(man, indent=1, sort_keys=True) + "\n").encode(); content["verify_package.py"] = VERIFY.encode()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for k in sorted(content):
            zi = zipfile.ZipInfo(k, (2030, 1, 1, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED; zi.external_attr = 0o644 << 16; z.writestr(zi, content[k])
    return sha(open(out, "rb").read()), man
if __name__ == "__main__":
    h, m = build(sys.argv[1]); print(json.dumps({"zip_sha256": h, "design_sha256": m["design_sha256"], "metrics_code_sha256": m["metrics_code_sha256"]}))
