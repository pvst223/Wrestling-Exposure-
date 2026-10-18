#!/usr/bin/env python3
"""Repo hygiene scan (tooling only): media/weights denylist, 30 MB cap, secret patterns."""
import os, re, subprocess, sys
CAP = 30 * 1024 * 1024
DENY_EXT = {".mp4",".mov",".avi",".mkv",".webm",".m4v",".jpg",".jpeg",".png",".gif",".bmp",".tif",".tiff",".webp",
            ".pt",".pth",".ckpt",".onnx",".safetensors",".h5",".npz",".npy",".pkl",".pickle",".zip",".tar",".gz",".7z"}
SECRET = [re.compile(p) for p in (
    "gh" + r"[pousr]_[A-Za-z0-9]{30,}", "github_" + r"pat_[A-Za-z0-9_]{30,}",
    "AK" + r"IA[0-9A-Z]{16}", "sk" + r"-[A-Za-z0-9]{32,}",
    "-----BEGIN " + r"(RSA |EC |OPENSSH )?PRIVATE KEY-----")]
def main():
    files = subprocess.check_output(["git","ls-files","-z"]).decode().split("\0")
    bad = []
    for f in filter(None, files):
        if not os.path.isfile(f): continue
        if os.path.splitext(f)[1].lower() in DENY_EXT: bad.append(f"denied extension: {f}")
        if os.path.getsize(f) > CAP: bad.append(f"over 30 MB: {f}")
        if os.path.getsize(f) < 5_000_000:
            try: t = open(f, encoding="utf-8", errors="ignore").read()
            except OSError: continue
            for p in SECRET:
                if p.search(t): bad.append(f"secret pattern in: {f}")
    for b in bad: print("FAIL", b)
    print("hygiene scan:", "FAIL" if bad else "OK", f"({len(files)-1} tracked files)")
    sys.exit(1 if bad else 0)
main()
