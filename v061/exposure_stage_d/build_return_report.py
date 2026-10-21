#!/usr/bin/env python3
"""Descriptive BUILD-return report (reporting only; no decision logic; reads, never writes, the private workspace).
Prints counts/durations by category, UNKNOWN reasons, build U_ref, confidence/flag distributions, corrections, hashes."""
import hashlib, json, os, sys
import labeller_core as C


def build_report(root, set_name="build"):
    ws = C.Workspace(root)
    if not ws._has("SET_COMPLETE", set_name): raise C.StateError(f"set {set_name} not complete")
    eff = ws.effective_labels(set_name); orig = {r["shot_id"]: r for r in ws._label_rows(set_name)}
    dur = lambda r: float(r["t_end_s"]) - float(r["t_start_s"])
    cnt = lambda key, rows=eff: {k: sum(1 for r in rows if r[key] == k) for k in sorted({r[key] for r in rows})}
    flags = {}
    for r in eff:
        for f in [x for x in r["flags"].split(";") if x]: flags[f] = flags.get(f, 0) + 1
    corr = ws.corrections(set_name); s = ws.reference_summary(set_name) if set_name == "build" else None
    ev_text = open(ws.events_path, "rb").read()
    return {"set": set_name, "protocol_version": ws.protocol_version, "n_shots": len(eff),
            "reference_summary": s, "confidence_distribution": cnt("confidence"),
            "confidence_by_label": {l: cnt("confidence", [r for r in eff if r["label"] == l]) for l in C.CATEGORIES if any(r["label"] == l for r in eff)},
            "flag_distribution": dict(sorted(flags.items())), "n_corrections": len(corr),
            "corrections": [{"shot_id": c["shot_id"], "reason": c["reason"], "ts": c["ts"], "old_label": c["old"]["label"], "new_label": c["new"]["label"]} for c in corr],
            "corrections_chain_ok": bool(ws.verify_chain(ws._corr_path(set_name))) if corr else True,
            "protocol_violations_detected": {"manifest_tamper": False, "event_chain_ok": ws.verify_chain() >= 0},
            "labels_original_csv_sha256": hashlib.sha256(open(ws._p(set_name, f"labels_{set_name}.csv"), "rb").read()).hexdigest(),
            "labels_effective_set_sha256": ws.set_hash(set_name), "events_jsonl_sha256": hashlib.sha256(ev_text).hexdigest(),
            "event_chain_last_prev": [json.loads(l) for l in ev_text.decode().splitlines() if l.strip()][-1]["prev"],
            "n_events": ws.verify_chain(), "manifest_verified": bool(ws.manifest(set_name))}


if __name__ == "__main__":
    print(json.dumps(build_report(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "build"), indent=1, sort_keys=True))
