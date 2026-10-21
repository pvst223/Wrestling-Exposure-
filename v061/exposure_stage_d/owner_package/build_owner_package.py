#!/usr/bin/env python3
"""Assemble the owner package zip from repo files + the private BUILD manifest. Usage: build_owner_package.py <manifest_build.csv> <out.zip>"""
import os, sys, zipfile, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TOP = "STAGE_D_OWNER_PACKAGE_V1"
TOOL = ["labeller_core.py", "labeller_ui.py", "stage_d_cli.py", "build_return_report.py"]
OWNER = ["setup_owner.py", "step3_set_marks.sh", "README_OWNER.md"]
MANIFEST_SHA = "d0c73ca106c9cef5e34766aaabfdceaf039e2735e58c76a52362c0a7d3a99aaf"
PROTO = os.path.join(REPO, "v061", "exposure_design", "EXPOSURE_V1_STAGE_D_LABELLING_PROTOCOL_V1_1.md")


def main(man, out):
    assert hashlib.sha256(open(man, "rb").read()).hexdigest() == MANIFEST_SHA, "manifest hash mismatch"
    files = [(os.path.join(HERE, f), f"{TOP}/{f}") for f in OWNER] + [(man, f"{TOP}/manifest_build.csv"), (PROTO, f"{TOP}/v061/exposure_design/{os.path.basename(PROTO)}")]
    files += [(os.path.join(HERE, "..", f), f"{TOP}/v061/exposure_stage_d/{f}") for f in TOOL]
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for src, arc in files:
            zi = zipfile.ZipInfo(arc, (2026, 10, 21, 0, 0, 0)); zi.external_attr = (0o755 if arc.endswith((".sh", ".py")) else 0o644) << 16
            zi.compress_type = zipfile.ZIP_DEFLATED; z.writestr(zi, open(src, "rb").read())
    print(out, hashlib.sha256(open(out, "rb").read()).hexdigest())


if __name__ == "__main__": main(sys.argv[1], sys.argv[2])
