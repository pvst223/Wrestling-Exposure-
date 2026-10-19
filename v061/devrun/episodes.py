"""Training-episode construction for the V0.6.1 development cross-fit (spec_v4 02 section 2.4: relaxed TRAIN-only seed rule, K resamples). Pure functions; no features, no model.
Clarifications D3-D5 are recorded in the ledger (DR0) BEFORE execution. Strict rule first (4 seeds, >=2 shots, <=2/shot, >=60 frames apart, box_h >= median); only if infeasible the relaxed fallback m in (3, 2) with >=1 shot (still <=2/shot, >=60 frames)."""
import random, statistics
MIN_GAP = 60; MAX_PER_SHOT = 2
def _gap_ok(frame, chosen): return all(abs(frame - c["frame"]) >= MIN_GAP for c in chosen)
def _order(q, rng):
    shots = sorted({c["shot"] for c in q}); rng.shuffle(shots); per = {}
    for s in shots:
        pool = [c for c in q if c["shot"] == s]; rng.shuffle(pool); per[s] = pool
    order = []; r = 0
    while any(r < len(per[s]) for s in shots):
        order += [per[s][r] for s in shots if r < len(per[s])]; r += 1
    return order
def _dfs(order, m, min_shots):
    best = [None]
    def go(start, chosen):
        if len(chosen) == m:
            if len({c["shot"] for c in chosen}) >= min_shots: best[0] = list(chosen); return True
            return False
        for i in range(start, len(order)):
            c = order[i]
            if sum(1 for x in chosen if x["shot"] == c["shot"]) >= MAX_PER_SHOT or not _gap_ok(c["frame"], chosen): continue
            chosen.append(c)
            if go(i + 1, chosen): return True
            chosen.pop()
        return False
    return best[0] if go(0, []) else None
def select_seeds(rng_key, cands):
    """cands: dicts(frame, det, tid, shot, box_h) of eligible detections. rng_key: string for random.Random (caller fixes it, e.g. f'{ep_seed}|{clip}|{identity}|target|k{k}').
    Returns dict(status, rule, seeds). Deterministic."""
    if not cands: return dict(status="NO_ELIGIBLE", rule=None, seeds=[])
    med = statistics.median(c["box_h"] for c in cands); q = sorted([c for c in cands if c["box_h"] >= med], key=lambda c: (c["frame"], c["det"]))
    for m, min_shots, rule in ((4, 2, "STRICT_4"), (3, 1, "RELAXED_3"), (2, 1, "RELAXED_2")):
        order = _order(q, random.Random(rng_key))   # fresh identical stream per attempt
        got = _dfs(order, m, min_shots)
        if got: return dict(status="OK", rule=rule, seeds=sorted(got, key=lambda c: (c["frame"], c["det"])))
    return dict(status="INSUFFICIENT_SEEDS", rule=None, seeds=[])
NEG_MAP = {"REFEREE": "REFEREE", "RINGSIDE_STAFF": "STAFF", "SPECTATOR": "SPECTATOR", "OTHER_WRESTLER_UNNAMED": "OTHER_WRESTLER_UNNAMED"}
def candidate_structure(lab, tr, A, B, used_tids):
    """Mirror of frozen build_clip candidate logic: every labelled (non-UNLABELABLE) tracklet except seed tracklets; y=0 A, 1 B, 2 otherwise."""
    out = []
    for tid, l in sorted(lab.items()):
        if tid in used_tids: continue
        c = l["person_class"]; truth = l["wrestler_id"] if c == "WRESTLER" else NEG_MAP.get(c)
        if truth is None: continue
        out.append(dict(tid=tid, shot=tr[tid]["shot"], truth=truth, y=0 if truth == A else (1 if truth == B else 2)))
    return out
