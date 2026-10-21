#!/usr/bin/env python3
"""Synthetic-only fixtures: dummy manifest rows (no real footage, no real timings) and an optional tiny
lavfi test-pattern video, used for tool testing and the demonstration."""
import csv, os, subprocess
import labeller_core as C


def write_manifest(path, set_name, prefix, n=5, source="SYN_SRC_A", t0=0.0, step=3.0):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n"); w.writerow(C.MANIFEST_COLUMNS)
        for i in range(n):
            w.writerow([f"{prefix}{i:03d}", source, set_name, f"{t0 + i * step:.3f}", f"{t0 + (i + 1) * step - 0.5:.3f}"])
    return path


def make_test_video(path, seconds=40):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                    f"testsrc2=size=160x90:rate=10:duration={seconds}", "-c:v", "libx264", "-pix_fmt", "yuv420p", path], check=True)
    return path
