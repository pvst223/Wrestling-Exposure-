#!/usr/bin/env python3
"""Local-only (127.0.0.1) labelling interface for Protocol V1.1. Shows one shot at a time, chronological, with the
shot clip restricted to [t_start-5 s, t_end+5 s]. Exposes nothing but the whitelisted view (see labeller_core.VIEW_KEYS).
Never displays prior labels, counts by label, or any computed feature. Standard library only (ffmpeg optional for clips)."""
import html, json, os, secrets, subprocess, sys, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import labeller_core as C


def ffmpeg_clip_provider(root, sources_json):
    """Cut the context window of a shot from a private source video. sources_json maps source_id -> video path."""
    src = json.load(open(sources_json))
    def provide(v):
        out = os.path.join(root, "clips", f"{v['shot_id']}.mp4"); os.makedirs(os.path.dirname(out), exist_ok=True)
        if not os.path.exists(out):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(v["context_start_s"]), "-to",
                            str(v["context_end_s"]), "-i", src[v["source_id"]], "-an", "-c:v", "libx264",
                            "-preset", "veryfast", "-crf", "23", out], check=True)
        return out
    return provide


PAGE = """<!doctype html><meta charset=utf-8><title>Stage-D labelling</title>
<style>body{{font:15px system-ui;max-width:760px;margin:1.5rem auto;padding:0 1rem}}fieldset{{margin:.6rem 0}}
label{{display:block}}.ro{{font-family:monospace;background:#eee;padding:.1rem .4rem}}video{{width:100%;max-height:50vh}}</style>
<h3>Shot {index} / {total}</h3>
<p>shot_id <span class=ro>{shot_id}</span> source <span class=ro>{source_id}</span>
 frozen boundaries <span class=ro>{t_start_s}</span>&ndash;<span class=ro>{t_end_s}</span> s (read-only)</p>
<p>Context window (fixed): {context_start_s}&ndash;{context_end_s} s. The shot occupies the highlighted part of the bar.</p>
<video id=v controls src="/clip/{shot_id}.mp4"></video>
<div style="height:8px;background:#ccc;position:relative"><div style="position:absolute;height:8px;background:#36c;left:{l}%;width:{w}%"></div></div>
<form method=post action=/submit><input type=hidden name=token value="{token}"><input type=hidden name=shot_id value="{shot_id}">
<fieldset><legend>Category (one)</legend>{cats}</fieldset>
<fieldset><legend>UNKNOWN reason (required if UNKNOWN; note required if OTHER)</legend>
<select name=unknown_reason><option value="">&mdash;</option>{reasons}</select></fieldset>
<fieldset><legend>Confidence</legend>{confs}</fieldset>
<fieldset><legend>Flags</legend>{flags}</fieldset>
<label>Note (&le;200 chars) <input name=note maxlength=200 size=60></label>
<p><b>Submission is final.</b> <button>Submit label</button></p></form>"""
DONE = "<!doctype html><meta charset=utf-8><h3>All shots in this set have been submitted.</h3>"


def render_shot(v, token):
    radio = lambda n, xs: "".join(f'<label><input type=radio name={n} value="{x}" required> {x}</label>' for x in xs)
    t0, t1 = float(v["t_start_s"]), float(v["t_end_s"]); c0, c1 = v["context_start_s"], v["context_end_s"]
    span = max(c1 - c0, 1e-9)
    return PAGE.format(**{k: html.escape(str(v[k])) for k in C.VIEW_KEYS}, token=token, l=round(100 * (t0 - c0) / span, 2),
                       w=round(100 * (t1 - t0) / span, 2), cats=radio("label", C.CATEGORIES),
                       reasons="".join(f'<option>{x}</option>' for x in C.UNKNOWN_REASONS),
                       confs=radio("confidence", C.CONFIDENCES),
                       flags="".join(f'<label><input type=checkbox name=flags value="{x}"> {x}</label>' for x in C.FLAGS))


def make_server(ws, set_name, clip_provider, port=0):
    token = secrets.token_hex(8)

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a): pass
        def _send(self, code, body, ctype="text/html; charset=utf-8", extra=()):
            b = body.encode() if isinstance(body, str) else body
            self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(b)))
            for k, v in extra: self.send_header(k, v)
            self.end_headers(); self.wfile.write(b)
        def do_GET(self):
            p = urlparse(self.path).path
            if p == "/":
                sid = ws.next_unlabelled(set_name)
                return self._send(200, DONE if sid is None else render_shot(ws.view(set_name, sid), token))
            if p.startswith("/clip/") and p.endswith(".mp4"):
                sid = p[6:-4]
                try: v = ws.view(set_name, sid)
                except C.ToolError: return self._send(404, "not found")
                with open(clip_provider(v), "rb") as fh: data = fh.read()
                return self._send(200, data, "video/mp4")
            self._send(404, "not found")
        def do_POST(self):
            if urlparse(self.path).path != "/submit": return self._send(404, "not found")
            q = parse_qs(self.rfile.read(int(self.headers.get("Content-Length", 0))).decode())
            g = lambda k: (q.get(k) or [""])[0]
            if g("token") != token: return self._send(403, "bad token")
            try:
                ws.submit_label(set_name, g("shot_id"), g("label"), g("confidence"), g("unknown_reason"),
                                q.get("flags", []), g("note"))
            except C.ToolError as e:
                return self._send(400, f"<!doctype html><meta charset=utf-8><p>Rejected: {html.escape(str(e))}</p><a href=/>back</a>")
            self._send(303, "", extra=[("Location", "/")])

    srv = ThreadingHTTPServer(("127.0.0.1", port), H); srv.token = token; return srv


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--root", required=True); ap.add_argument("--set", required=True, choices=C.SETS)
    ap.add_argument("--sources", required=True, help="private JSON {source_id: video path}"); ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args(argv)
    ws = C.Workspace(a.root); srv = make_server(ws, a.set, ffmpeg_clip_provider(a.root, a.sources), a.port)
    print(f"http://127.0.0.1:{srv.server_address[1]}/  (set={a.set})"); srv.serve_forever()


if __name__ == "__main__": main(sys.argv[1:])
