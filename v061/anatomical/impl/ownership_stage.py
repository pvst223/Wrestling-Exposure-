"""Per-detection ownership using the UNCHANGED V0.5 modules (reused_v05/src). Identity is not an input. Appearance votes/parts are disabled (votes={}, parts conflict False).
Rules: cross-body geometric cues (integrity_v05) -> MIXED_BODY_SUSPECTED; ownership_v05.decide() state otherwise; plain plausibility failure on an otherwise SINGLE_BODY -> OWNERSHIP_UNCERTAIN;
no masks for the frame -> OWNERSHIP_NOT_EVALUATED (unless a cross-body cue already forces MIXED)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); RV = os.path.join(os.path.dirname(HERE), "reused_v05", "src")
def _mods():
    if RV not in sys.path: sys.path.insert(0, RV)
    import ownership_v05 as own, integrity_v05 as integ, integrity_v03 as i3, config as cfgm
    return own, integ, i3, cfgm
def load_cfg():
    import json, types
    own, integ, i3, cfgm = _mods()
    cfgm._PATH = os.path.join(os.path.dirname(HERE), "reused_v05", "config", "config_v05.json")
    return cfgm.load()
def evaluate(j, d, fs, cfg, prev=None):
    """j: detection index in frame dict d; fs: ownership_v05.FrameSeg or None; prev: temporal anchor dict(kp,obs,S,frame_gap) or None.
    -> dict(ownership_state, reasons, n_landmarks, S, temporal, own_metrics_summary)."""
    own, integ, i3, _ = _mods(); P = cfg.pose; kpc_min = P.KP_CONF
    ev = integ.evaluate(j, d, kpc_min, cfg.integrity, prev, {}, {"conflict": False})
    kp, kc = d["kp"][j], d["kpc"][j]; n_lm = sum(1 for i in own.LMS if kc[i] >= kpc_min)
    base = dict(S=ev["S"], temporal=ev["temporal"], n_landmarks=n_lm, integrity_reasons=ev["reasons"])
    if ev["cross_body"]: return dict(base, ownership_state="MIXED_BODY_SUSPECTED", reasons=ev["cross_body"])
    if fs is None: return dict(base, ownership_state="OWNERSHIP_NOT_EVALUATED", reasons=["NO_SEG_MASKS_FOR_FRAME"])
    dup = {o["det"] for o in ev["overlap_info"] if o["kind"] == "duplicate_ignored"}
    others = [(d["kp"][o], d["kpc"][o]) for o in range(len(d["conf"])) if o != j and o not in dup]
    M = own.metrics(fs, kp, kc, others, ev["S"], kpc_min, cfg.ownership); state, reasons = own.decide(M, cfg.ownership)
    if state == "SINGLE_BODY_SUPPORTED" and ev["plain"]: state, reasons = "OWNERSHIP_UNCERTAIN", ev["plain"]
    return dict(base, ownership_state=state, reasons=reasons, own_summary={k: M.get(k) for k in ("owner", "cover", "own_only_frac", "contested_frac", "other_only_frac", "unexplained_frac")})
