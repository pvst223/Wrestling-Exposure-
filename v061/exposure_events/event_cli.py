#!/usr/bin/env python3
"""Command line for the V1.1 LANDING event tool. Commands never print event lists or counts."""
import argparse, hashlib, json, os, sys, webbrowser
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import event_core as C, event_ui as U

TOOL_FILES = ["event_core.py", "event_ui.py", "event_cli.py", "landing_metrics.py", "source_table_v1_1.json", "config_v1_1.json"]


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def tool_hashes(): return {n: sha_file(os.path.join(HERE, n)) for n in TOOL_FILES}


def find_sources(ws, search_dirs, manual):
    found = dict(manual)
    want = {s["source_id"]: s for s in ws.src["sources"]}
    for d in search_dirs:
        for dp, dn, fn in os.walk(os.path.expanduser(d)):
            dn[:] = [x for x in dn if not x.startswith(".") and x != "Library"]
            for n in fn:
                p = os.path.join(dp, n)
                try: sz = os.path.getsize(p)
                except OSError: continue
                for sid, s in want.items():
                    if sid not in found and s["bytes"] == sz and sha_file(p) == s["file_sha256"]: found[sid] = p
    return found


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--root", default="~/landing_events_private")
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("setup"); a.add_argument("--search", action="append", default=[]); a.add_argument("--path", action="append", default=[])
    for n in ("status", "verify-chain"): sp.add_parser(n)
    r = sp.add_parser("run"); r.add_argument("--pass", dest="p", type=int, required=True); r.add_argument("--port", type=int, default=8765)
    c = sp.add_parser("correct"); c.add_argument("--pass", dest="p", type=int, required=True); c.add_argument("--event-id", required=True)
    c.add_argument("--reason", required=True); c.add_argument("--explanation", required=True); c.add_argument("--retract", action="store_true")
    for k in ("event_time_s", "performer", "observability", "evidence", "note"): c.add_argument("--" + k.replace("_", "-"))
    e = sp.add_parser("export"); e.add_argument("--pass", dest="p", type=int, required=True); e.add_argument("--out", default=None)
    o = sp.add_parser("open-pass"); o.add_argument("--pass", dest="p", type=int, required=True)
    x = ap.parse_args(argv); ws = C.Workspace(x.root)
    try:
        if x.cmd == "setup":
            paths = dict(kv.split("=", 1) for kv in x.path); paths = find_sources(ws, x.search, paths)
            miss = [s["source_id"] for s in ws.src["sources"] if s["source_id"] not in paths]
            if miss: print("MISSING source files (matched by SHA-256):", miss); return 2
            h = tool_hashes()
            ws.setup(sha_file(os.path.join(HERE, "source_table_v1_1.json")), h["landing_metrics.py"], h)
            json.dump(paths, open(os.path.join(ws.root, "sources_local.json"), "w")); print("setup complete; chain records:", ws.verify_chain()); return 0
        if x.cmd == "verify-chain": print("chain OK, records:", ws.verify_chain()); return 0
        if x.cmd == "status": print(json.dumps({p: ws.status(p) for p in (1, 2)}, indent=1)); return 0
        if x.cmd == "open-pass": ws.open_pass(x.p); print("pass", x.p, "opened"); return 0
        if x.cmd == "run":
            if not ws._pass_state(x.p)["opened"]: ws.open_pass(x.p)
            paths = json.load(open(os.path.join(ws.root, "sources_local.json")))
            srv = U.serve(ws, x.p, paths, x.port); url = f"http://127.0.0.1:{srv.server_address[1]}/"
            print("Coding tool at", url, "(Ctrl-C to pause; resume with the same command)")
            try: webbrowser.open(url)
            except Exception: pass
            try: srv.serve_forever()
            except KeyboardInterrupt: ws._save_cov(x.p); print("paused")
            return 0
        if x.cmd == "correct":
            new = {k: getattr(x, k) for k in ("event_time_s", "performer", "observability", "evidence", "note") if getattr(x, k) is not None}
            ws.correct(x.p, x.event_id, x.reason, x.explanation, "RETRACT" if x.retract else "EDIT", **new); print("correction recorded"); return 0
        if x.cmd == "export":
            res = ws.export(x.p, x.out or os.path.join(ws.root, "export")); print(json.dumps(res)); return 0
    except C.ToolError as err:
        print("REFUSED:", err); return 1


if __name__ == "__main__": sys.exit(main())
