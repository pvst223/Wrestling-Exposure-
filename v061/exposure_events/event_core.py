"""Exposure-construct audit V1.1 - event-coding core (LANDING only; human coding; no CV of any kind).
Tamper-evident hash-chained audit log; append-only submissions; clerical corrections as records; Pass-2 time lock enforced here
(not by owner memory); Pass-2 reads only Pass-2 records. No function returns event counts, candidate times or any CV output."""
import csv, datetime, hashlib, io, json, math, os, re
from decimal import Decimal, InvalidOperation

DESIGN_SHA256 = "c82971641c0a5c618604455e454d982716670966059958a807e6e86c7f8599a0"
HERE = os.path.dirname(os.path.abspath(__file__))
OBSERVABILITY = ("FULL", "PARTIAL", "INFERRED")
CORRECTION_REASONS = ("TOOL_ERROR", "TRANSCRIPTION_ERROR")
UNCLEAR = "UNCLEAR"
EXPORT_COLUMNS = ("source_id", "event_time_s", "performer", "observability", "evidence", "note")


class ToolError(Exception): pass
class ValidationError(ToolError): pass
class StateError(ToolError): pass
class LockError(ToolError): pass
class ChainError(ToolError): pass


def _read_bytes(p):
    with open(p, "rb") as f: return f.read()
def sha(b): return hashlib.sha256(b).hexdigest()
def _utc_now(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def _parse_ts(s): return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)


def load_source_table(path):
    with open(path, "rb") as f: raw = f.read()
    t = json.loads(raw)
    srcs = sorted(t["sources"], key=lambda s: s["order"])
    for s in srcs:
        s["ds_max"] = int(math.floor(s["t_max_s"] * 10 + 1e-9))
    return {"table": t, "sources": srcs, "by_id": {s["source_id"]: s for s in srcs}, "sha256": sha(raw)}


def ds_from_time(x):
    """Event time -> integer deciseconds. Accepts only values with at most one decimal place (0.1 s precision)."""
    try: d = Decimal(str(x).strip())
    except InvalidOperation: raise ValidationError("event time is not a number")
    if not d.is_finite() or d < 0: raise ValidationError("event time must be a non-negative number")
    q = d * 10
    if q != q.to_integral_value(): raise ValidationError("event time must be coded to 0.1 s (one decimal place)")
    return int(q)


class Workspace:
    def __init__(self, root, source_table_path=None, design_path=None, clock=None):
        self.root = os.path.abspath(os.path.expanduser(root)); os.makedirs(self.root, exist_ok=True)
        self.audit_path = os.path.join(self.root, "audit.jsonl")
        self.clock = clock or _utc_now
        self.src = load_source_table(source_table_path or os.path.join(HERE, "source_table_v1_1.json"))
        _dn = "EXPOSURE_CONSTRUCT_AUDIT_EXPERIMENT_V1_1_DESIGN.md"
        self.design_path = design_path or (os.path.join(HERE, _dn) if os.path.exists(os.path.join(HERE, _dn)) else os.path.join(HERE, "..", "exposure_design", _dn))
        self.cfg = json.loads(_read_bytes(os.path.join(HERE, "config_v1_1.json")))
        self._last = {}; self._hb_n = 0; self._cov = {}

    # ---------- audit chain ----------
    def _records(self):
        if not os.path.exists(self.audit_path): return []
        return [json.loads(l) for l in self._lines()]

    def _lines(self):
        if not os.path.exists(self.audit_path): return []
        with open(self.audit_path, encoding="utf-8") as f: return [l for l in f.read().splitlines() if l.strip()]

    def verify_chain(self):
        prev = "0" * 64; n = 0; last_ts = ""
        for l in self._lines():
            o = json.loads(l)
            if o.get("prev") != prev: raise ChainError(f"chain broken at record {n + 1}")
            if o["ts"] < last_ts: raise ChainError(f"timestamps go backwards at record {n + 1}")
            prev = sha(l.encode()); last_ts = o["ts"]; n += 1
        return n

    def _append(self, typ, p, data, derive=None):
        self.verify_chain()
        recs = self._records(); prev = "0" * 64
        if recs:
            prev = sha(self._lines()[-1].encode())
        ts = self.clock()
        if recs and ts < recs[-1]["ts"]: raise ChainError("system clock moved backwards; refusing to write")
        if derive: data = dict(data, **derive(ts))
        rec = {"seq": len(recs), "ts": ts, "type": typ, "pass": p, "data": data, "prev": prev}
        line = json.dumps(rec, sort_keys=True, separators=(",", ":"))
        with open(self.audit_path, "a", encoding="utf-8") as f: f.write(line + "\n"); f.flush(); os.fsync(f.fileno())
        rec["_line_sha"] = sha(line.encode()); return rec

    def _has(self, typ, p=None):
        return [r for r in self._records() if r["type"] == typ and (p is None or r["pass"] == p)]

    # ---------- setup ----------
    def source_problems(self):
        return [s["source_id"] for s in self.src["sources"] if s["status"] != "RESOLVED" or not s.get("wrestlers")]

    def setup(self, sources_json_sha256, metrics_code_sha256, tool_files_sha256):
        if self._has("SETUP"): raise StateError("already set up")
        if sha(_read_bytes(self.design_path)) != DESIGN_SHA256: raise StateError("design file does not match the approved design hash")
        bad = self.source_problems()
        if bad: raise StateError(f"source table has unresolved provenance (reviewer resolution required): {bad}")
        return self._append("SETUP", 0, {"design_sha256": DESIGN_SHA256, "source_table_sha256": self.src["sha256"],
                                          "sources_json_sha256": sources_json_sha256, "metrics_code_sha256": metrics_code_sha256,
                                          "tool_files_sha256": tool_files_sha256, "tool_version": self.cfg["tool_version"]})

    # ---------- passes ----------
    def _pass_state(self, p):
        return {"opened": bool(self._has("PASS_OPEN", p)), "complete": bool(self._has("PASS_COMPLETE", p))}

    def open_pass(self, p):
        if p not in (1, 2): raise ValidationError("pass must be 1 or 2")
        if not self._has("SETUP"): raise StateError("tool not set up")
        if self._has("PASS_OPEN", p): raise StateError(f"pass {p} already opened")
        data = {}
        if p == 2:
            c = self._has("PASS_COMPLETE", 1)
            if not c: raise LockError("Pass 2 cannot open before Pass 1 is complete")
            nb = c[0]["data"]["pass2_not_before_utc"]
            if _parse_ts(self.clock()) < _parse_ts(nb):
                raise LockError(f"Pass 2 is locked until {nb} (7 full days after Pass 1 completion)")
            data["not_before_utc"] = nb
        return self._append("PASS_OPEN", p, data)

    def _require_open(self, p):
        st = self._pass_state(p)
        if not st["opened"]: raise StateError(f"pass {p} is not open")
        if st["complete"]: raise StateError(f"pass {p} is complete and frozen")

    def sources_done(self, p):
        return [r["data"]["source_id"] for r in self._has("SOURCE_DONE", p)]

    def current_source(self, p):
        done = set(self.sources_done(p))
        for s in self.src["sources"]:
            if s["source_id"] not in done: return s
        return None

    # ---------- events ----------
    def _validate_fields(self, source_id, event_time_s, performer, observability, evidence, note):
        s = self.src["by_id"].get(source_id)
        if s is None: raise ValidationError("source is not in the allowed source table")
        ds = ds_from_time(event_time_s)
        if ds > s["ds_max"]: raise ValidationError("event time is outside the allowed range of this source")
        if performer not in (list(s["wrestlers"].keys()) + [UNCLEAR]): raise ValidationError("performer must be one of this source's wrestlers or UNCLEAR")
        if observability not in OBSERVABILITY: raise ValidationError("observability must be FULL, PARTIAL or INFERRED")
        evidence = (evidence or "").strip(); note = (note or "").strip()
        if observability in ("PARTIAL", "INFERRED") and not evidence: raise ValidationError("evidence is mandatory for PARTIAL and INFERRED events")
        if len(evidence) > self.cfg["evidence_max_chars"]: raise ValidationError("evidence too long")
        if len(note) > self.cfg["note_max_chars"]: raise ValidationError("note must be at most 200 characters")
        return {"source_id": source_id, "t_ds": ds, "performer": performer, "observability": observability, "evidence": evidence, "note": note}

    def submit_event(self, p, source_id, event_time_s, performer, observability, evidence="", note=""):
        self._require_open(p)
        if source_id not in self.src["by_id"]: raise ValidationError("source is not in the allowed source table")
        cur = self.current_source(p)
        if cur is None or cur["source_id"] != source_id: raise StateError("events can only be submitted for the current (first unfinished) source")
        f = self._validate_fields(source_id, event_time_s, performer, observability, evidence, note)
        for e in self.effective_events(p):
            if e["source_id"] == source_id and e["t_ds"] == f["t_ds"] and e["performer"] == f["performer"]:
                raise ValidationError("an event with the same source, time and performer already exists")
        rec = self._append("EVENT", p, f)
        return "ev_" + rec["_line_sha"][:10]

    def _events_raw(self, p):
        """Original submitted events with ids (id = first 10 hex of the sha256 of the stored record line)."""
        out = {}; order = []
        for l in self._lines():
            r = json.loads(l)
            if r["pass"] == p and r["type"] == "EVENT":
                eid = "ev_" + sha(l.encode())[:10]; out[eid] = dict(r["data"]); order.append(eid)
        return out, order

    def effective_events(self, p):
        ev, order = self._events_raw(p); retracted = set()
        for r in self._records():
            if r["pass"] == p and r["type"] == "CORRECTION":
                d = r["data"]
                if d["action"] == "RETRACT": retracted.add(d["event_id"])
                elif d["action"] == "EDIT": ev[d["event_id"]].update(d["new"])
        rows = [dict(ev[i], event_id=i) for i in order if i not in retracted]
        so = {s["source_id"]: s["order"] for s in self.src["sources"]}
        rows.sort(key=lambda e: (so[e["source_id"]], e["t_ds"], e["performer"], e["observability"], e["event_id"]))
        return rows

    def correct(self, p, event_id, reason, explanation, action="EDIT", **new):
        self._require_open(p)
        if reason not in CORRECTION_REASONS: raise ValidationError(f"correction reason must be one of {CORRECTION_REASONS}")
        if not (explanation or "").strip(): raise ValidationError("explanation required")
        ev, _ = self._events_raw(p)
        if event_id not in ev: raise ValidationError("unknown event id in this pass")
        if event_id not in {e["event_id"] for e in self.effective_events(p)}: raise ValidationError("event already retracted")
        if action not in ("EDIT", "RETRACT"): raise ValidationError("action must be EDIT or RETRACT")
        data = {"event_id": event_id, "reason": reason, "explanation": explanation.strip(), "action": action}
        if action == "EDIT":
            cur = next(e for e in self.effective_events(p) if e["event_id"] == event_id)
            if cur["source_id"] in self.sources_done(p): raise StateError("source already finished; correction not possible")
            merged = {"event_time_s": new.get("event_time_s", cur["t_ds"] / 10), "performer": new.get("performer", cur["performer"]),
                      "observability": new.get("observability", cur["observability"]), "evidence": new.get("evidence", cur["evidence"]),
                      "note": new.get("note", cur["note"])}
            f = self._validate_fields(cur["source_id"], merged["event_time_s"], merged["performer"], merged["observability"], merged["evidence"], merged["note"])
            data["new"] = {k: f[k] for k in ("t_ds", "performer", "observability", "evidence", "note")}
            data["old"] = {k: cur[k] for k in ("t_ds", "performer", "observability", "evidence", "note")}
        else:
            cur = next(e for e in self.effective_events(p) if e["event_id"] == event_id)
            if cur["source_id"] in self.sources_done(p): raise StateError("source already finished; correction not possible")
        self._append("CORRECTION", p, data); return True

    # ---------- coverage (playback evidence that a source was watched through) ----------
    def _cov_path(self, p): return os.path.join(self.root, f"coverage_pass{p}.json")

    def _load_cov(self, p):
        if p not in self._cov:
            self._cov[p] = json.loads(_read_bytes(self._cov_path(p))) if os.path.exists(self._cov_path(p)) else {}
        return self._cov[p]

    def _save_cov(self, p):
        with open(self._cov_path(p) + ".tmp", "w") as f: json.dump(self._load_cov(p), f)
        os.replace(self._cov_path(p) + ".tmp", self._cov_path(p))

    def heartbeat(self, p, source_id, t_s, playing, rate):
        self._require_open(p)
        s = self.src["by_id"].get(source_id)
        if s is None: raise ValidationError("unknown source")
        t = min(max(float(t_s), 0.0), s["t_max_s"]); key = (p, source_id); last = self._last.get(key)
        if playing and last is not None and 0 < t - last <= self.cfg["coverage_max_gap_s"] and float(rate) <= self.cfg["coverage_max_playback_rate"]:
            iv = self._load_cov(p).setdefault(source_id, []); iv.append([round(last, 3), round(t, 3)])
            self._hb_n += 1
            if self._hb_n % 10 == 0: self._save_cov(p)
        self._last[key] = t if playing else None

    def coverage_fraction(self, p, source_id):
        s = self.src["by_id"][source_id]; iv = sorted(self._load_cov(p).get(source_id, [])); tot = 0.0; cur_a = cur_b = None
        for a, b in iv:
            if cur_b is None or a > cur_b:
                if cur_b is not None: tot += cur_b - cur_a
                cur_a, cur_b = a, b
            else: cur_b = max(cur_b, b)
        if cur_b is not None: tot += cur_b - cur_a
        return min(1.0, tot / s["t_max_s"])

    def mark_source_done(self, p, source_id, attested):
        self._require_open(p)
        cur = self.current_source(p)
        if cur is None or cur["source_id"] != source_id: raise StateError("sources must be finished in order")
        if not attested: raise ValidationError("you must attest that you watched the whole source")
        self._save_cov(p); cov = self.coverage_fraction(p, source_id)
        if cov < self.cfg["coverage_required_fraction"]:
            raise StateError(f"playback coverage {cov:.2f} is below the required {self.cfg['coverage_required_fraction']:.2f}; keep playing the unwatched parts at normal speed")
        return self._append("SOURCE_DONE", p, {"source_id": source_id, "coverage": round(cov, 4), "attested": True})

    # ---------- export / completion ----------
    def export_text(self, p):
        b = io.StringIO(); w = csv.writer(b, lineterminator="\n"); w.writerow(EXPORT_COLUMNS)
        for e in self.effective_events(p):
            w.writerow([e["source_id"], f"{e['t_ds'] / 10:.1f}", e["performer"], e["observability"], e["evidence"], e["note"]])
        return b.getvalue()

    def pass_hash(self, p): return sha(self.export_text(p).encode())

    def complete_pass(self, p):
        self._require_open(p)
        if self.current_source(p) is not None: raise StateError("not all sources are finished")
        h = self.pass_hash(p); data = {"pass_sha256": h}
        derive = None
        if p == 1:
            derive = lambda ts: {"pass2_not_before_utc": (_parse_ts(ts) + datetime.timedelta(days=self.cfg["pass2_lock_days"])).strftime("%Y-%m-%dT%H:%M:%SZ")}
        return self._append("PASS_COMPLETE", p, data, derive)

    def export(self, p, dest_dir):
        if not self._has("PASS_COMPLETE", p): raise StateError("pass is not complete")
        os.makedirs(dest_dir, exist_ok=True); path = os.path.join(dest_dir, f"landing_events_pass{p}.csv")
        with open(path, "w", encoding="utf-8", newline="") as f: f.write(self.export_text(p))
        return {"path": path, "pass_sha256": self.pass_hash(p)}

    # ---------- blind status (no counts, no events, no other-pass information) ----------
    def status(self, p):
        st = self._pass_state(p); cur = self.current_source(p) if st["opened"] and not st["complete"] else None
        n_src = len(self.src["sources"]); done = len(self.sources_done(p)) if st["opened"] else 0
        out = {"pass": p, "opened": st["opened"], "complete": st["complete"], "sources_finished": done, "sources_total": n_src,
               "current_source": cur["source_id"] if cur else None}
        if p == 2 and not st["opened"]:
            c = self._has("PASS_COMPLETE", 1)
            out["locked"] = (not c) or _parse_ts(self.clock()) < _parse_ts(c[0]["data"]["pass2_not_before_utc"])
        return out
