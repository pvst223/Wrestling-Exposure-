"""Builds the frozen REPLAY/NON_MATCH post-coding filter table from the existing Stage-D reference shot labels (private inputs).
Usage: python build_nonlive_filter.py OUT.json LABELS1.csv [LABELS2.csv ...]
Intervals [start_ds, end_ds) in deciseconds (start rounded down, end rounded up so no part of a labelled shot escapes);
adjacent/overlapping intervals of the same source are merged. Material with no label (e.g. first ~151 s of the match, straddler shots) is NOT filtered.
Only shot-class labels are read; no event of any kind. The table itself stays private; only its sha256 and aggregate counts are recorded."""
import csv, hashlib, json, math, sys

def build(paths):
    iv = {}
    for p in paths:
        for r in csv.DictReader(open(p, encoding="utf-8", newline="")):
            if r["label"] in ("REPLAY", "NON_MATCH"):
                iv.setdefault(r["source_id"], []).append((int(math.floor(float(r["t_start_s"]) * 10 + 1e-9)), int(math.ceil(float(r["t_end_s"]) * 10 - 1e-9))))
    out = []
    for sid in sorted(iv):
        cur = None
        for a, b in sorted(iv[sid]):
            if cur and a <= cur[1]: cur[1] = max(cur[1], b)
            else:
                if cur: out.append({"source_id": sid, "start_ds": cur[0], "end_ds": cur[1]})
                cur = [a, b]
        out.append({"source_id": sid, "start_ds": cur[0], "end_ds": cur[1]})
    return out

if __name__ == "__main__":
    out = build(sys.argv[2:]); txt = json.dumps(out, sort_keys=True, separators=(",", ":"))
    open(sys.argv[1], "w").write(txt)
    print(json.dumps({"filter_sha256": hashlib.sha256(txt.encode()).hexdigest(), "n_intervals": len(out),
                      "total_filtered_seconds": sum(i["end_ds"] - i["start_ds"] for i in out) / 10}))
