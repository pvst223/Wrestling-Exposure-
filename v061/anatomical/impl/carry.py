"""Source-rate rows with visualization-only carry (stride-3 pose). A pose-evaluated row stays itself; frames after it (<=MAX_CARRY, same tracklet, no camera cut since the anchor)
become CARRIED_ASSIGNED_x only if the anchor was ASSIGNED_x. Never interpolated, never from a non-assigned anchor, never enters metrics (measurement=False)."""
MAX_CARRY = 3   # identical to the locked identity renderer constant
def source_rate(measured_rows, cut_frames, last_pad=MAX_CARRY):
    """measured_rows: rows with tracklet, frame, record_class (+ box, kp, kc...). cut_frames: iterable of source frames where a CUT starts a new shot.
    -> list of rows (one per tracklet x source frame) with pose_status MEASURED | CARRIED | NONE."""
    cuts = sorted(int(c) for c in cut_frames); by = {}
    for r in measured_rows: by.setdefault(r["tracklet"], {})[int(r["frame"])] = r
    out = []
    for t, fr in sorted(by.items()):
        ev = sorted(fr)
        for f in range(ev[0], ev[-1] + last_pad + 1):
            if f in fr: out.append(dict(fr[f], pose_status="MEASURED", measurement=True, carry_age=0)); continue
            prior = [e for e in ev if e < f]
            if not prior: continue
            a = prior[-1]; age = f - a
            if age <= MAX_CARRY and fr[a]["record_class"] in ("ASSIGNED_A", "ASSIGNED_B") and not any(a < c <= f for c in cuts):
                out.append(dict(fr[a], frame=f, record_class="CARRIED_" + fr[a]["record_class"], pose_status="CARRIED", measurement=False, carry_age=age, anchor_frame=a))
    return out
