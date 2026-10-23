"""Local (127.0.0.1) event-coding UI for Experiment V1.1 LANDING. Shows only: the current source video, exact time, the frozen manual,
the entry form. NEVER shows event lists, counts, summaries, candidate times, other-pass data or any CV output."""
import json, os, re, sys, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import event_core as C

PAGE = r"""<!doctype html><meta charset=utf-8><title>LANDING coding tool V1.1</title>
<style>body{font-family:sans-serif;margin:12px;max-width:1100px}video{width:100%;max-height:60vh;background:#000}
.row{margin:6px 0}button{margin-right:4px}#msg{color:#a00;min-height:1.2em}#man{display:none;white-space:pre-wrap;border:1px solid #888;padding:8px;max-height:50vh;overflow:auto;font-size:13px}
input[type=text]{width:60%}</style>
<h3>LANDING coding &mdash; Pass <span id=pn></span> &mdash; source <span id=src></span> (<span id=prog></span>)</h3>
<video id=v controls preload=auto></video>
<div class=row><b>Time <span id=t>0.000</span> s</b> / <span id=tm></span> s &nbsp;
<button onclick="step(-1)">&larr; frame</button><button onclick="step(1)">frame &rarr;</button>
<button onclick="seek(-5)">-5 s</button><button onclick="seek(-1)">-1 s</button><button onclick="seek(1)">+1 s</button><button onclick="seek(5)">+5 s</button>
<button onclick="pp()">play / pause</button> speed <select id=rate onchange="v.playbackRate=parseFloat(rate.value)"><option>0.25<option>0.5<option selected>1<option>1.5<option>2</select></div>
<div class=row><b>Record event</b> (first foot contact): time <input id=et size=8> <button onclick="useNow()">use current time (0.1 s)</button>
performer <select id=pf></select> observability <select id=ob><option>FULL<option>PARTIAL<option>INFERRED</select></div>
<div class=row>evidence (required for PARTIAL / INFERRED) <input type=text id=ev maxlength=500></div>
<div class=row>note (optional, &le;200) <input type=text id=nt maxlength=200> <button onclick="submitEv()"><b>Submit event</b></button></div>
<div id=msg></div>
<div class=row><button onclick="toggleMan()">Show / hide coding manual (frozen definitions)</button>
<button onclick="srcDone()">I have watched this whole source &mdash; finish source</button> <button id=cmp onclick="complete()" style="display:none">Complete and freeze this pass</button></div>
<div id=man></div>
<script>
const v=document.getElementById('v');let S=null,FPS=30;
const $=id=>document.getElementById(id),q=(u,b)=>fetch(u,b?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)}:{}).then(r=>r.json());
function fmt(x){return x.toFixed(3)}
async function load(){S=await q('/api/state');$('pn').textContent=S.pass;
 if(S.complete){document.body.innerHTML='<h3>Pass '+S.pass+' is complete and frozen.</h3>';return}
 if(!S.current_source){$('src').textContent='(all sources finished)';$('prog').textContent='';$('cmp').style.display='';v.removeAttribute('src');return}
 $('src').textContent=S.current_source.source_id;$('prog').textContent='source '+S.sources_finished+'+1 of '+S.sources_total;$('tm').textContent=S.current_source.t_max_s;
 const pf=$('pf');pf.innerHTML='';for(const [k,n] of Object.entries(S.current_source.wrestlers)){pf.add(new Option(k+' = '+n,k))}pf.add(new Option('UNCLEAR','UNCLEAR'));
 v.src='/video/'+S.current_source.source_id;v.onloadedmetadata=()=>{v.currentTime=0}}
v.addEventListener('timeupdate',()=>{if(!S||!S.current_source)return;const tm=S.current_source.t_max_s;if(v.currentTime>tm){v.pause();v.currentTime=tm}$('t').textContent=fmt(v.currentTime)});
setInterval(()=>{if(S&&S.current_source)q('/api/hb',{source_id:S.current_source.source_id,t:v.currentTime,playing:!v.paused&&!v.seeking,rate:v.playbackRate})},500);
function step(n){v.pause();v.currentTime=Math.max(0,v.currentTime+n/FPS)}
function seek(d){v.currentTime=Math.max(0,v.currentTime+d)}function pp(){v.paused?v.play():v.pause()}
function useNow(){$('et').value=(Math.round(v.currentTime*10)/10).toFixed(1)}
function msg(m){$('msg').textContent=m}
async function submitEv(){const r=await q('/api/event',{source_id:S.current_source.source_id,event_time_s:$('et').value,performer:$('pf').value,observability:$('ob').value,evidence:$('ev').value,note:$('nt').value});
 if(r.ok){msg('Event recorded (final). Reference id '+r.event_id+' (only needed if you must make a clerical correction).');$('et').value='';$('ev').value='';$('nt').value=''}else msg(r.error)}
async function srcDone(){if(!confirm('Finish this source? You cannot add events to it afterwards.'))return;const r=await q('/api/source_done',{source_id:S.current_source.source_id});if(r.ok){msg('');load()}else msg(r.error)}
async function complete(){if(!confirm('Complete and freeze this pass? This cannot be undone.'))return;const r=await q('/api/complete',{});if(r.ok)load();else msg(r.error)}
async function toggleMan(){const m=$('man');if(!m.dataset.l){m.textContent=await (await fetch('/manual')).text();m.dataset.l=1}m.style.display=m.style.display=='block'?'none':'block'}
load();
</script>"""


def manual_text(ws):
    txt = open(ws.design_path, encoding="utf-8").read()
    m1 = re.search(r"## 1\. Construct review.*?(?=\n## 2\.)", txt, re.S).group(0)
    m3 = re.search(r"## 3\. Coding manual.*?(?=\n## 4\.)", txt, re.S).group(0)
    return ("FROZEN CODING DEFINITIONS (verbatim from the approved design, sha256 %s)\n\n" % C.DESIGN_SHA256) + m1 + "\n\n" + m3 + \
           "\n\nContext rule: you may look up to 5 s before and 5 s after a candidate moment within the same source to name the performer or judge observability."


def make_handler(ws, p, paths):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a): pass
        def _json(self, o, code=200):
            b = json.dumps(o).encode(); self.send_response(code); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
        def do_GET(self):
            if self.path == "/": b = PAGE.encode(); self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
            elif self.path == "/manual": b = manual_text(ws).encode(); self.send_response(200); self.send_header("Content-Type", "text/plain; charset=utf-8"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
            elif self.path == "/api/state":
                st = ws.status(p); cur = ws.current_source(p) if st["opened"] and not st["complete"] else None
                st["current_source"] = {"source_id": cur["source_id"], "t_max_s": cur["t_max_s"], "wrestlers": cur["wrestlers"]} if cur else None
                self._json(st)
            elif self.path.startswith("/video/"): self._video(self.path[7:])
            else: self._json({"error": "not found"}, 404)
        def _video(self, sid):
            cur = ws.current_source(p)
            if cur is None or sid != cur["source_id"] or sid not in paths: return self._json({"error": "not available"}, 403)
            path = paths[sid]; size = os.path.getsize(path); a, b = 0, size - 1
            m = re.match(r"bytes=(\d*)-(\d*)", self.headers.get("Range", ""))
            if m:
                if m.group(1): a = int(m.group(1))
                if m.group(2): b = int(m.group(2))
                if not m.group(1) and m.group(2): a, b = max(0, size - int(m.group(2))), size - 1
                b = min(b, size - 1); self.send_response(206); self.send_header("Content-Range", f"bytes {a}-{b}/{size}")
            else: self.send_response(200)
            self.send_header("Content-Type", "video/mp4"); self.send_header("Accept-Ranges", "bytes"); self.send_header("Content-Length", str(b - a + 1)); self.end_headers()
            try:
                with open(path, "rb") as f:
                    f.seek(a); left = b - a + 1
                    while left > 0:
                        d = f.read(min(1 << 20, left))
                        if not d: break
                        self.wfile.write(d); left -= len(d)
            except (BrokenPipeError, ConnectionResetError): pass
        def do_POST(self):
            try:
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
                if self.path == "/api/hb": ws.heartbeat(p, body["source_id"], body["t"], bool(body["playing"]), body["rate"]); return self._json({"ok": True})
                if self.path == "/api/event":
                    eid = ws.submit_event(p, body["source_id"], body["event_time_s"], body["performer"], body["observability"], body.get("evidence", ""), body.get("note", "")); return self._json({"ok": True, "event_id": eid})
                if self.path == "/api/source_done": ws.mark_source_done(p, body["source_id"], True); return self._json({"ok": True})
                if self.path == "/api/complete": ws.complete_pass(p); return self._json({"ok": True})
                self._json({"error": "not found"}, 404)
            except (C.ToolError, KeyError, ValueError, TypeError) as e:
                self._json({"ok": False, "error": str(e) if isinstance(e, C.ToolError) else "invalid request"})
    return H


def serve(ws, p, paths, port=0):
    srv = ThreadingHTTPServer(("127.0.0.1", port), make_handler(ws, p, paths)); return srv
