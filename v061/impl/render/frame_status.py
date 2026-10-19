"""Renderer frame-status logic (04_VIDEO_RENDERER_PLAN). Pure; imports nothing from inference/training/selection code.
Per tracklet and source frame: EVALUATED (a frozen decision exists on this exact frame), CARRIED-FORWARD (no decision; the most recent EVALUATED frame of the same tracklet is at most MAX_CARRY source frames earlier; visualization only, box held, never interpolated), NO-EVAL otherwise."""
EVALUATED, CARRIED, NOEVAL = "EVALUATED", "CARRIED-FORWARD", "NO-EVAL"
MAX_CARRY = 3
def tracklet_status(evaluated_frames, first_frame, last_frame, max_carry=MAX_CARRY):
    """Returns list of dicts, one per source frame in [first_frame,last_frame]: frame, status, source_eval_frame (or None), age (frames since eval)."""
    ev = sorted(set(int(f) for f in evaluated_frames)); out = []; j = -1
    for f in range(int(first_frame), int(last_frame) + 1):
        while j + 1 < len(ev) and ev[j + 1] <= f: j += 1
        if j >= 0 and ev[j] == f: out.append(dict(frame=f, status=EVALUATED, source_eval_frame=f, age=0))
        elif j >= 0 and 0 < f - ev[j] <= max_carry: out.append(dict(frame=f, status=CARRIED, source_eval_frame=ev[j], age=f - ev[j]))
        else: out.append(dict(frame=f, status=NOEVAL, source_eval_frame=None, age=None))
    return out
def counts(status_rows):
    c = {EVALUATED: 0, CARRIED: 0, NOEVAL: 0}
    for r in status_rows: c[r["status"]] += 1
    return c
