#!/usr/bin/env python3
"""Thin command-line wrappers around the APPROVED labeller_core API (no new logic): open sets, record match marks,
complete, correct (clerical), seal/freeze/unseal/export, status. Run from this directory. Labels themselves are entered
only through labeller_ui.py. `status` prints counts of submitted labels only (never label values)."""
import argparse, json, sys
import labeller_core as C


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--root", required=True); sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("open-set"); p.add_argument("set", choices=C.SETS); p.add_argument("manifest")
    p = sp.add_parser("set-marks"); p.add_argument("set", choices=C.SETS); p.add_argument("source_id")
    p.add_argument("--start", type=float); p.add_argument("--end", type=float); p.add_argument("--evidence", default="")
    p.add_argument("--flags", default="")
    p = sp.add_parser("complete"); p.add_argument("set", choices=C.SETS)
    p = sp.add_parser("correct"); p.add_argument("set", choices=C.SETS); p.add_argument("shot_id"); p.add_argument("--reason", required=True)
    p.add_argument("--explanation", required=True); p.add_argument("--label", required=True); p.add_argument("--confidence", required=True)
    p.add_argument("--unknown_reason", default=""); p.add_argument("--flags", default=""); p.add_argument("--note", default="")
    sp.add_parser("seal-check"); p = sp.add_parser("freeze-rule"); p.add_argument("rule_sha256")
    sp.add_parser("unseal-check"); p = sp.add_parser("export"); p.add_argument("set", choices=C.SETS); p.add_argument("dest")
    p = sp.add_parser("summary"); p.add_argument("set", choices=C.SETS)
    sp.add_parser("status"); sp.add_parser("verify-chain")
    a = ap.parse_args(argv); ws = C.Workspace(a.root); fl = lambda s: [x for x in s.split(";") if x]
    out = {
        "open-set": lambda: ws.open_set(a.set, a.manifest), "complete": lambda: ws.complete_set(a.set),
        "set-marks": lambda: ws.set_marks(a.set, a.source_id, a.start, a.end, a.evidence, fl(a.flags)),
        "correct": lambda: ws.apply_correction(a.set, a.shot_id, a.reason, a.explanation, a.label, a.confidence, a.unknown_reason, fl(a.flags), a.note),
        "seal-check": ws.seal_check, "freeze-rule": lambda: ws.freeze_rule(a.rule_sha256), "unseal-check": ws.unseal_check,
        "export": lambda: ws.export_for_rule_builder(a.set, a.dest), "summary": lambda: ws.reference_summary(a.set),
        "verify-chain": lambda: {"events": ws.verify_chain()},
        "status": lambda: {s: {"opened": ws._has("SET_OPEN", s), "labels_submitted": len(ws._label_rows(s)) if ws._has("SET_OPEN", s) else 0,
                               "total_shots": len(ws.manifest(s)) if ws._has("SET_OPEN", s) else 0, "complete": ws._has("SET_COMPLETE", s)} for s in C.SETS},
    }[a.cmd]()
    print(json.dumps(out, indent=1, sort_keys=True, default=str)); return 0


if __name__ == "__main__":
    try: sys.exit(main())
    except C.ToolError as e: print(f"REFUSED: {type(e).__name__}: {e}", file=sys.stderr); sys.exit(2)
