#!/usr/bin/env python3
"""Stage-D owner shot-labelling tool: core (Protocol V1.1, frozen). Standard library only.

Private by design: label files, marks, logs and clips live under an owner-chosen root that is never
committed. This module contains no classifier, detection, identity, pose, anatomy or ownership code and
reads no such data; the manifest schema whitelists the only fields the labeller can ever see."""
import csv, hashlib, io, json, math, os, random, re
from datetime import datetime, timezone, timedelta

PROTOCOL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "exposure_design",
                             "EXPOSURE_V1_STAGE_D_LABELLING_PROTOCOL_V1_1.md")
PROTOCOL_SHA256 = "0b6c87405aa5c32d1dffd60bc54634835fb4afe710217b506ad508a1a8c3dad9"
CATEGORIES = ("LIVE_ACTION", "REPLAY", "CLOSE_UP", "NON_MATCH", "UNKNOWN")
UNKNOWN_REASONS = ("PIP_AMBIGUOUS", "CLOSEUP_BORDERLINE", "REPLAY_AMBIGUOUS", "UNREADABLE", "MIXED_SHOT",
                   "OUT_OF_WINDOW_AMBIGUOUS", "OTHER")
CONFIDENCES = ("HIGH", "MEDIUM", "LOW")
FLAGS = ("BOUNDARY_ISSUE", "EDIT_DISCONTINUITY", "PIP_AMBIGUOUS", "START_AMBIGUOUS", "END_AMBIGUOUS", "NO_D", "NOTE")
MARK_FLAGS = ("START_AMBIGUOUS", "END_AMBIGUOUS", "NO_D")
LABEL_COLUMNS = ("shot_id", "source_id", "t_start_s", "t_end_s", "label", "unknown_reason", "confidence",
                 "flags", "note", "labelled_at_utc", "protocol_version")
MARK_COLUMNS = ("source_id", "start_s", "end_s", "evidence_note", "flags", "marked_at_utc", "protocol_version")
MANIFEST_COLUMNS = ("shot_id", "source_id", "set", "t_start_s", "t_end_s")   # the ONLY fields the labeller can see
VIEW_KEYS = ("shot_id", "source_id", "t_start_s", "t_end_s", "context_start_s", "context_end_s",
             "index", "total", "protocol_version")
CORRECTION_REASONS = ("TOOL_ERROR", "TRANSCRIPTION_ERROR")
SETS = ("build", "check")
CONTEXT_S = 5.0
NOTE_MAX = 200
RELIABILITY_SEED = 20261021
RELIABILITY_MIN_DAYS = 7
REF_INCONCLUSIVE_FRAC = 0.10


class ToolError(Exception): pass
class ProtocolMismatch(ToolError): pass
class ManifestError(ToolError): pass
class ManifestTamper(ToolError): pass
class ValidationError(ToolError): pass
class FinalOnSubmit(ToolError): pass
class StateError(ToolError): pass
class SealedError(ToolError): pass
class ChainError(ToolError): pass


def sha(b): return hashlib.sha256(b).hexdigest()
def _line(o): return json.dumps(o, sort_keys=True, separators=(",", ":"))
def default_clock(): return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def verify_protocol(path=PROTOCOL_FILE):
    h = sha(open(path, "rb").read())
    if h != PROTOCOL_SHA256:
        raise ProtocolMismatch(f"protocol file hash {h} != frozen {PROTOCOL_SHA256}")
    return h


def _csv_text(columns, rows):
    b = io.StringIO(); w = csv.writer(b, lineterminator="\n"); w.writerow(columns)
    for r in rows: w.writerow([r[c] for c in columns])
    return b.getvalue()


def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as f: return list(csv.DictReader(f))


def validate_label_fields(label, unknown_reason, confidence, flags, note):
    """Exact frozen choices; returns canonical (label, reason, confidence, flags_str, note)."""
    if label not in CATEGORIES: raise ValidationError(f"label must be one of {CATEGORIES}")
    unknown_reason = unknown_reason or ""
    if label == "UNKNOWN":
        if unknown_reason not in UNKNOWN_REASONS: raise ValidationError(f"UNKNOWN requires reason in {UNKNOWN_REASONS}")
    elif unknown_reason: raise ValidationError("unknown_reason only allowed with label UNKNOWN")
    if confidence not in CONFIDENCES: raise ValidationError(f"confidence must be one of {CONFIDENCES}")
    flags = list(flags or [])
    bad = [f for f in flags if f not in FLAGS]
    if bad or len(set(flags)) != len(flags): raise ValidationError(f"invalid/duplicate flags {bad or flags}")
    note = note or ""
    if len(note) > NOTE_MAX: raise ValidationError(f"note over {NOTE_MAX} characters")
    if "\n" in note or "\r" in note: raise ValidationError("note must be a single line")
    if label == "UNKNOWN" and unknown_reason == "OTHER" and not note.strip():
        raise ValidationError("reason OTHER requires a free-text note")
    return label, unknown_reason, confidence, ";".join(f for f in FLAGS if f in flags), note


class Workspace:
    def __init__(self, root, clock=None, protocol_path=PROTOCOL_FILE):
        self.root = root; self.clock = clock or default_clock
        self.protocol_version = verify_protocol(protocol_path)
        os.makedirs(root, exist_ok=True)
        self.events_path = os.path.join(root, "events.jsonl")

    # ---------- paths ----------
    def _d(self, s):
        if s not in SETS: raise ValidationError(f"set must be one of {SETS}")
        d = os.path.join(self.root, s); os.makedirs(d, exist_ok=True); return d
    def _p(self, s, name): return os.path.join(self._d(s), name)

    # ---------- event chain ----------
    def events(self):
        if not os.path.exists(self.events_path): return []
        return [json.loads(l) for l in open(self.events_path, encoding="utf-8").read().splitlines() if l.strip()]

    def verify_chain(self, path=None, key="prev"):
        path = path or self.events_path
        if not os.path.exists(path): return 0
        prev = "0" * 64; n = 0
        for l in open(path, encoding="utf-8").read().splitlines():
            if not l.strip(): continue
            o = json.loads(l)
            if o.get(key) != prev: raise ChainError(f"chain broken at line {n + 1} of {os.path.basename(path)}")
            prev = sha(l.encode()); n += 1
        return n

    def _append_chained(self, path, obj):
        self.verify_chain(path)
        prev = "0" * 64
        if os.path.exists(path):
            ls = [l for l in open(path, encoding="utf-8").read().splitlines() if l.strip()]
            if ls: prev = sha(ls[-1].encode())
        obj = dict(obj); obj["prev"] = prev
        with open(path, "a", encoding="utf-8") as f:
            f.write(_line(obj) + "\n"); f.flush(); os.fsync(f.fileno())
        return obj

    def _event(self, typ, s, **data):
        return self._append_chained(self.events_path, {"seq": len(self.events()), "ts": self.clock(), "type": typ,
                                                       "set": s, "data": data})

    def _has(self, typ, s=None, last=False):
        ev = [e for e in self.events() if e["type"] == typ and (s is None or e["set"] == s)]
        return (ev[-1] if ev else None) if last else bool(ev)

    # ---------- manifest ----------
    def open_set(self, s, manifest_path):
        if self._has("SET_OPEN", s): raise StateError(f"set {s} already open")
        with open(manifest_path, newline="", encoding="utf-8") as f:
            rd = csv.DictReader(f); cols = tuple(rd.fieldnames or ()); rows = list(rd)
        if cols != MANIFEST_COLUMNS:
            raise ManifestError(f"manifest columns must be exactly {MANIFEST_COLUMNS} (got {cols}); no other data may enter")
        if not rows: raise ManifestError("empty manifest")
        seen = set(); other = {sid for st in SETS if st != s and self._has("SET_OPEN", st) for sid in self._ids(st)}
        for r in rows:
            if r["set"] != s: raise ManifestError(f"row {r['shot_id']} belongs to set {r['set']}, not {s}")
            if r["shot_id"] in seen: raise ManifestError(f"duplicate shot_id {r['shot_id']}")
            if r["shot_id"] in other: raise ManifestError(f"shot {r['shot_id']} already in the other set (sets must be disjoint)")
            seen.add(r["shot_id"])
            try: a, b = float(r["t_start_s"]), float(r["t_end_s"])
            except ValueError: raise ManifestError("non-numeric boundary")
            if not (a >= 0 and b > a): raise ManifestError(f"bad boundaries for {r['shot_id']}")
        rows.sort(key=lambda r: (r["source_id"], float(r["t_start_s"])))
        by = {}
        for r in rows:
            if r["source_id"] in by and float(r["t_start_s"]) < by[r["source_id"]] - 1e-9:
                raise ManifestError("overlapping shots within a source")
            by[r["source_id"]] = float(r["t_end_s"])
        text = _csv_text(MANIFEST_COLUMNS, rows)
        open(self._p(s, "manifest.csv"), "w", encoding="utf-8", newline="").write(text)
        return self._event("SET_OPEN", s, manifest_sha256=sha(text.encode()), n_shots=len(rows),
                           protocol_sha256=self.protocol_version)

    def _ids(self, s):
        p = self._p(s, "manifest.csv")
        return [r["shot_id"] for r in _read_csv(p)] if os.path.exists(p) else []

    def manifest(self, s):
        ev = self._has("SET_OPEN", s, last=True)
        if not ev: raise StateError(f"set {s} not open")
        p = self._p(s, "manifest.csv")
        if sha(open(p, "rb").read()) != ev["data"]["manifest_sha256"]:
            raise ManifestTamper("manifest (frozen shot ids/boundaries) was modified after SET_OPEN")
        return _read_csv(p)

    def _shot(self, s, shot_id):
        for i, r in enumerate(self.manifest(s)):
            if r["shot_id"] == shot_id: return i, r
        raise ValidationError(f"unknown shot {shot_id} in set {s}")

    # ---------- labeller view (whitelisted) ----------
    def view(self, s, shot_id):
        rows = self.manifest(s); i, r = self._shot(s, shot_id)
        t0, t1 = float(r["t_start_s"]), float(r["t_end_s"])
        v = {"shot_id": r["shot_id"], "source_id": r["source_id"], "t_start_s": r["t_start_s"], "t_end_s": r["t_end_s"],
             "context_start_s": round(max(0.0, t0 - CONTEXT_S), 3), "context_end_s": round(t1 + CONTEXT_S, 3),
             "index": i + 1, "total": len(rows), "protocol_version": self.protocol_version}
        assert tuple(v) == VIEW_KEYS
        return v

    # ---------- state ----------
    def _label_rows(self, s):
        p = self._p(s, f"labels_{s}.csv"); return _read_csv(p) if os.path.exists(p) else []

    def _editable(self, s):
        if not self._has("SET_OPEN", s): raise StateError(f"set {s} not open")
        if self._has("SET_COMPLETE", s): raise StateError(f"set {s} is complete; labels are final")

    def next_unlabelled(self, s):
        done = {r["shot_id"] for r in self._label_rows(s)}
        for r in self.manifest(s):
            if r["shot_id"] not in done: return r["shot_id"]
        return None

    # ---------- labelling (final on submit) ----------
    def submit_label(self, s, shot_id, label, confidence, unknown_reason="", flags=(), note=""):
        self._editable(s); _, r = self._shot(s, shot_id)
        if shot_id in {x["shot_id"] for x in self._label_rows(s)}:
            raise FinalOnSubmit(f"shot {shot_id} already submitted; labels are final on submission")
        lab, rea, con, fl, nt = validate_label_fields(label, unknown_reason, confidence, flags, note)
        row = {"shot_id": shot_id, "source_id": r["source_id"], "t_start_s": r["t_start_s"], "t_end_s": r["t_end_s"],
               "label": lab, "unknown_reason": rea, "confidence": con, "flags": fl, "note": nt,
               "labelled_at_utc": self.clock(), "protocol_version": self.protocol_version}
        self._append_row(self._p(s, f"labels_{s}.csv"), LABEL_COLUMNS, row)
        return row

    def _append_row(self, path, cols, row):
        new = not os.path.exists(path)
        with open(path, "a", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            if new: w.writerow(cols)
            w.writerow([row[c] for c in cols]); f.flush(); os.fsync(f.fileno())

    # ---------- match marks (D) ----------
    def _mark_rows(self, s):
        p = self._p(s, "match_marks.csv"); return _read_csv(p) if os.path.exists(p) else []

    def _validate_mark(self, start, end, evidence, flags):
        flags = list(flags or [])
        if any(f not in MARK_FLAGS for f in flags) or len(set(flags)) != len(flags): raise ValidationError("invalid mark flags")
        if "NO_D" in flags:
            return "", "", (evidence or ""), ";".join(f for f in MARK_FLAGS if f in flags)
        for v in (start, end):
            if v is None or not math.isfinite(float(v)): raise ValidationError("start/end required unless NO_D")
        a, b = round(float(start), 1), round(float(end), 1)
        if b <= a: raise ValidationError("end must be after start")
        if not (evidence or "").strip(): raise ValidationError("evidence note required for start/end marks")
        return f"{a:.1f}", f"{b:.1f}", evidence.strip(), ";".join(f for f in MARK_FLAGS if f in flags)

    def set_marks(self, s, source_id, start_s, end_s, evidence_note, flags=()):
        self._editable(s)
        if source_id not in {r["source_id"] for r in self.manifest(s)}: raise ValidationError("unknown source_id")
        if source_id in {r["source_id"] for r in self._mark_rows(s)}: raise FinalOnSubmit("marks already submitted for source")
        a, b, ev, fl = self._validate_mark(start_s, end_s, evidence_note, flags)
        row = {"source_id": source_id, "start_s": a, "end_s": b, "evidence_note": ev, "flags": fl,
               "marked_at_utc": self.clock(), "protocol_version": self.protocol_version}
        self._append_row(self._p(s, "match_marks.csv"), MARK_COLUMNS, row); return row

    # ---------- completion ----------
    def complete_set(self, s):
        self._editable(s)
        miss = [r["shot_id"] for r in self.manifest(s) if r["shot_id"] not in {x["shot_id"] for x in self._label_rows(s)}]
        if miss: raise StateError(f"{len(miss)} shots unlabelled")
        srcs = {r["source_id"] for r in self.manifest(s)}; ms = {r["source_id"] for r in self._mark_rows(s)}
        if srcs - ms: raise StateError(f"match marks missing for {sorted(srcs - ms)}")
        return self._event("SET_COMPLETE", s, set_sha256=self.set_hash(s))

    # ---------- corrections (clerical only) ----------
    def _corr_path(self, s): return self._p(s, "corrections_log.jsonl")

    def corrections(self, s):
        p = self._corr_path(s)
        return [json.loads(l) for l in open(p, encoding="utf-8").read().splitlines() if l.strip()] if os.path.exists(p) else []

    def apply_correction(self, s, shot_id, reason, explanation, label, confidence, unknown_reason="", flags=(), note=""):
        if reason not in CORRECTION_REASONS: raise ValidationError(f"correction reason must be one of {CORRECTION_REASONS}")
        if not (explanation or "").strip(): raise ValidationError("explanation required")
        if not self._has("SET_OPEN", s): raise StateError("set not open")
        if s == "build" and self._has("RULE_FROZEN"): raise SealedError("rule frozen: build labels can no longer be corrected by the tool")
        if s == "check" and self._has("CHECK_UNSEALED"): raise SealedError("check labels unsealed: they can no longer be corrected")
        cur = {r["shot_id"]: r for r in self.effective_labels(s)}
        if shot_id not in cur: raise ValidationError("shot has no submitted label to correct")
        lab, rea, con, fl, nt = validate_label_fields(label, unknown_reason, confidence, flags, note)
        old = {k: cur[shot_id][k] for k in ("label", "unknown_reason", "confidence", "flags", "note")}
        new = {"label": lab, "unknown_reason": rea, "confidence": con, "flags": fl, "note": nt}
        ent = self._append_chained(self._corr_path(s), {"ts": self.clock(), "set": s, "shot_id": shot_id, "reason": reason,
                                                       "explanation": explanation.strip(), "old": old, "new": new})
        if self._has("SET_COMPLETE", s): self._event("SET_HASH_UPDATED", s, set_sha256=self.set_hash(s))
        if s == "check" and self._has("CHECK_SEALED"): self._event("SEAL_UPDATED", s, set_sha256=self.set_hash(s))
        return ent

    def effective_labels(self, s):
        rows = [dict(r) for r in self._label_rows(s)]; idx = {r["shot_id"]: r for r in rows}
        for c in self.corrections(s): idx[c["shot_id"]].update(c["new"])
        return rows

    def set_hash(self, s):
        lab = _csv_text(LABEL_COLUMNS, self.effective_labels(s)); mk = _csv_text(MARK_COLUMNS, self._mark_rows(s))
        return sha((lab + "\n--MARKS--\n" + mk).encode())

    # ---------- freeze / seal / unseal / export ----------
    def freeze_rule(self, rule_sha256):
        if not re.fullmatch(r"[0-9a-f]{64}", rule_sha256 or ""): raise ValidationError("rule hash must be sha256 hex")
        if not self._has("SET_COMPLETE", "build"): raise StateError("build set must be complete first")
        if self._has("RULE_FROZEN"): raise StateError("rule already frozen")
        return self._event("RULE_FROZEN", "build", rule_sha256=rule_sha256, build_set_sha256=self.set_hash("build"))

    def seal_check(self):
        if not self._has("SET_COMPLETE", "check"): raise StateError("check set must be complete first")
        if self._has("CHECK_SEALED"): raise StateError("already sealed")
        return self._event("CHECK_SEALED", "check", set_sha256=self.set_hash("check"))

    def unseal_check(self):
        if not self._has("CHECK_SEALED"): raise StateError("check set not sealed")
        if not self._has("RULE_FROZEN"): raise SealedError("check labels stay sealed until the frozen rule hash is recorded")
        if self._has("CHECK_UNSEALED"): raise StateError("already unsealed")
        return self._event("CHECK_UNSEALED", "check", set_sha256=self.set_hash("check"))

    def export_for_rule_builder(self, s, dest_dir):
        if not self._has("SET_COMPLETE", s): raise StateError(f"set {s} not complete")
        if s == "check" and not self._has("CHECK_UNSEALED"):
            raise SealedError("check labels are sealed; only their hash is available")
        os.makedirs(dest_dir, exist_ok=True)
        lp = os.path.join(dest_dir, f"labels_{s}.csv"); mp = os.path.join(dest_dir, f"match_marks_{s}.csv")
        open(lp, "w", encoding="utf-8", newline="").write(_csv_text(LABEL_COLUMNS, self.effective_labels(s)))
        open(mp, "w", encoding="utf-8", newline="").write(_csv_text(MARK_COLUMNS, self._mark_rows(s)))
        return {"labels": lp, "marks": mp, "set_sha256": self.set_hash(s)}

    def sealed_hash(self, s="check"):
        e = self._has("SEAL_UPDATED", s, last=True) or self._has("CHECK_SEALED", s, last=True)
        return e["data"]["set_sha256"] if e else None

    # ---------- descriptive reference summary (public, counts/durations only) ----------
    def reference_summary(self, s):
        if not self._has("SET_COMPLETE", s): raise StateError("set not complete")
        if s == "check" and not self._has("CHECK_UNSEALED"): raise SealedError("check summary available only after unsealing")
        dur = {c: 0.0 for c in CATEGORIES}; cnt = {c: 0 for c in CATEGORIES}
        ur_d = {u: 0.0 for u in UNKNOWN_REASONS}; ur_n = {u: 0 for u in UNKNOWN_REASONS}
        for r in self.effective_labels(s):
            d = float(r["t_end_s"]) - float(r["t_start_s"]); dur[r["label"]] += d; cnt[r["label"]] += 1
            if r["label"] == "UNKNOWN": ur_d[r["unknown_reason"]] += d; ur_n[r["unknown_reason"]] += 1
        total = sum(dur.values()); u = dur["UNKNOWN"]
        return {"set": s, "n_shots": sum(cnt.values()), "total_duration_s": round(total, 3),
                "duration_by_label_s": {k: round(v, 3) for k, v in dur.items()}, "count_by_label": cnt,
                "unknown_duration_by_reason_s": {k: round(v, 3) for k, v in ur_d.items()},
                "unknown_count_by_reason": ur_n, "U_ref_fraction": (u / total) if total else None,
                "REFERENCE_INCONCLUSIVE": bool(total and u > REF_INCONCLUSIVE_FRAC * total) if s == "check" else None,
                "set_sha256": self.set_hash(s)}

    # ---------- blind reliability relabel (>= 7 days; never changes labels) ----------
    def reliability_sample(self, s):
        if not self._has("SET_COMPLETE", s): raise StateError("set not complete")
        order = [r["shot_id"] for r in self.manifest(s)]
        k = max(1, int(round(0.10 * len(order))))
        pick = set(random.Random(RELIABILITY_SEED).sample(sorted(order), k))
        return [i for i in order if i in pick]

    def _relabel_path(self, s): return self._p(s, "reliability_relabel.csv")

    def relabel_available_from(self, s):
        t = datetime.strptime(self._has("SET_COMPLETE", s, last=True)["ts"], "%Y-%m-%dT%H:%M:%SZ")
        return (t + timedelta(days=RELIABILITY_MIN_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def submit_relabel(self, s, shot_id, label, confidence, unknown_reason="", flags=(), note=""):
        if shot_id not in self.reliability_sample(s): raise ValidationError("shot not in the reliability sample")
        if self.clock() < self.relabel_available_from(s):
            raise StateError(f"blind relabel opens {self.relabel_available_from(s)} (>= {RELIABILITY_MIN_DAYS} days after completion)")
        p = self._relabel_path(s)
        if os.path.exists(p) and shot_id in {r["shot_id"] for r in _read_csv(p)}: raise FinalOnSubmit("already relabelled")
        _, r = self._shot(s, shot_id)
        lab, rea, con, fl, nt = validate_label_fields(label, unknown_reason, confidence, flags, note)
        row = {"shot_id": shot_id, "source_id": r["source_id"], "t_start_s": r["t_start_s"], "t_end_s": r["t_end_s"],
               "label": lab, "unknown_reason": rea, "confidence": con, "flags": fl, "note": nt,
               "labelled_at_utc": self.clock(), "protocol_version": self.protocol_version}
        self._append_row(p, LABEL_COLUMNS, row); return row

    def reliability_report(self, s):
        p = self._relabel_path(s)
        re_ = {r["shot_id"]: r["label"] for r in _read_csv(p)} if os.path.exists(p) else {}
        orig = {r["shot_id"]: r["label"] for r in self.effective_labels(s)}
        ids = sorted(re_); n = len(ids)
        if not n: return {"n": 0, "raw_agreement": None, "cohen_kappa": None}
        agree = sum(orig[i] == re_[i] for i in ids) / n
        pe = sum((sum(orig[i] == c for i in ids) / n) * (sum(re_[i] == c for i in ids) / n) for c in CATEGORIES)
        kappa = None if abs(1 - pe) < 1e-12 else (agree - pe) / (1 - pe)
        return {"n": n, "raw_agreement": agree, "cohen_kappa": kappa}
