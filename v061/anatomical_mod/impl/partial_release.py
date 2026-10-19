"""RELEASED_PARTIAL_ANATOMY machinery (readiness candidate; design ANATOMICAL_MODIFICATION_DESIGN_V1 + AMENDMENT_1).
Pure functions. The locked record classifier (v061/anatomical/impl/record_class.py), the V0.5 ownership modules and the merge guard are NOT modified.
apply_release() has NO merge-guard parameter and NO identity-score parameter by construction; it only reads base-record fields.
No exposure / COM / distance / speed / impact / workload quantity is computed or stored here."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ANAT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "anatomical")
sys.path.insert(0, os.path.join(ANAT, "impl"))
import ownership_stage
TIER_A = frozenset({"CONTESTED_LANDMARKS", "TOO_FEW_OWN_ONLY_LANDMARKS", "MASK_NOT_EXPLAINED_BY_SKELETON"})
PARTIAL_CLASSES = ("RELEASED_PARTIAL_ANATOMY_A", "RELEASED_PARTIAL_ANATOMY_B")
MIN_BONE_ENDPOINTS = 2     # structural constant (design sec. 4): >=1 bone with both endpoints released; otherwise the frame stays withheld
def _own():
    return ownership_stage._mods()[0]
def landmark_classes(j, d, fs, cfg):
    """Per-landmark V0.5 class {landmark_index: OWN_ONLY|CONTESTED|OTHER_ONLY|OUTSIDE} for detection j, recomputed with the UNCHANGED V0.5 modules from the frozen pose dets d and
    frozen segmentation FrameSeg fs. Mirrors ownership_stage.evaluate (same inputs). -> (cls dict | None, M dict | None, S)."""
    own, integ, i3, _ = ownership_stage._mods(); P = cfg.pose; kpc_min = P.KP_CONF
    ev = integ.evaluate(j, d, kpc_min, cfg.integrity, None, {}, {"conflict": False})
    if fs is None: return None, None, ev["S"]
    dup = {o["det"] for o in ev["overlap_info"] if o["kind"] == "duplicate_ignored"}
    others = [(d["kp"][o], d["kpc"][o]) for o in range(len(d["conf"])) if o != j and o not in dup]
    M = own.metrics(fs, d["kp"][j], d["kpc"][j], others, ev["S"], kpc_min, cfg.ownership)
    return dict(M.get("cls", {})), M, ev["S"]
def released_landmarks(cls):
    """Only OWN_ONLY landmarks. Everything else stays missing."""
    return sorted(int(i) for i, c in (cls or {}).items() if c == "OWN_ONLY")
def released_bones(lms):
    own = _own(); s = set(lms); return [(a, b) for a, b in own.BONES if a in s and b in s]
def eligible(rec):
    """Design eligibility (reasons all inside Tier A, UNCERTAIN only). Reads base-record fields only."""
    reasons = rec.get("own_reasons") or []
    return (rec.get("record_class") == "WITHHELD_OWNERSHIP_UNCERTAIN" and rec.get("ownership_state_passthrough", rec.get("ownership_state")) == "OWNERSHIP_UNCERTAIN"
            and rec.get("pose_status") == "MEASURED" and not rec.get("numeric_failure") and rec.get("identity_state_passthrough") in ("ACCEPT_A", "ACCEPT_B")
            and len(reasons) > 0 and all(r in TIER_A for r in reasons))
def apply_release(rec, cls):
    """rec: base record dict from the locked pipeline; cls: per-landmark classes (or None). Returns a NEW dict. Non-eligible records are returned as an equal copy, unchanged."""
    out = dict(rec)
    if not eligible(rec): return out
    lms = released_landmarks(cls); bones = released_bones(lms)
    if len(lms) < MIN_BONE_ENDPOINTS or not bones: return out     # stays WITHHELD_OWNERSHIP_UNCERTAIN
    lab = "A" if rec["identity_state_passthrough"] == "ACCEPT_A" else "B"
    out.update(record_class="RELEASED_PARTIAL_ANATOMY_" + lab, assigned_label=None, landmarks_emitted=False,      # landmarks_emitted stays False: PARTIAL can never pass an ASSIGNED gate
               anatomy_completeness="PARTIAL", partial_landmarks_emitted=True, released_landmarks=lms, n_released=len(lms), released_bones=[list(b) for b in bones],
               release_basis=sorted(rec["own_reasons"]), identity_unvalidated_flag=True)
    return out
def mask_unreleased(rec):
    """Keypoint view for downstream/rendering: only released landmarks keep coordinates; the rest are None (never zero-filled, never interpolated)."""
    if rec.get("record_class") not in PARTIAL_CLASSES: raise ValueError("not a PARTIAL record")
    s = set(rec["released_landmarks"]); return {i: (rec["kp"][i] if i in s else None) for i in range(len(rec["kp"]))}
def coverage_report(rows, n_identity_accept_measured=None):
    """Counts only (no per-frame geometry, no exposure quantity)."""
    import collections
    c = collections.Counter(r["record_class"] for r in rows if r.get("pose_status") == "MEASURED")
    part = [r for r in rows if r.get("record_class") in PARTIAL_CLASSES]
    rep = dict(class_counts=dict(c), n_partial=len(part), n_released_hist=dict(collections.Counter(r["n_released"] for r in part)), clips=dict(collections.Counter(r["clip"] for r in part)))
    if n_identity_accept_measured: rep["coverage_gain_points_of_identity_accept_measured"] = 100.0 * len(part) / n_identity_accept_measured
    return rep
