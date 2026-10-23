"""Frozen metric/evaluation code for Experiment V1.1 (LANDING). Synthetic-fixture testing only until Pass 1 and Pass 2 are both frozen.
Pure python, exact integer/Fraction arithmetic except the Wilson square root. No dependence on any CV component."""
import csv, math, sys
from decimal import Decimal
from fractions import Fraction
from functools import lru_cache

Z_ONE_SIDED_95 = 1.6448536269514722
MATCH_TOL_DS = 5
MIN_PREVALENCE = 20
MIN_DENOM = {"O": 20, "A": 20, "I": 10, "PA": 10}
PASS_BOUND = {"A": Fraction(8, 10), "O": Fraction(7, 10), "I": Fraction(8, 10), "PA": Fraction(9, 10)}
FAIL_BOUND = {"A": Fraction(65, 100), "O": Fraction(5, 10), "I": Fraction(6, 10), "PA": Fraction(75, 100)}
UNCLEAR = "UNCLEAR"
MAX_DP_STATES = 2_000_000


def _ev_sort_key(e): return (e["source_id"], e["t_ds"], e["performer"], e["observability"])


def load_events_csv(path):
    out = []
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            q = Decimal(r["event_time_s"]) * 10
            assert q == q.to_integral_value()
            out.append({"source_id": r["source_id"], "t_ds": int(q), "performer": r["performer"], "observability": r["observability"]})
    return out


def filter_events(events, intervals):
    """Remove events inside frozen REPLAY/NON_MATCH intervals [start_ds, end_ds). Unlabelled material is kept."""
    by = {}
    for iv in intervals: by.setdefault(iv["source_id"], []).append((iv["start_ds"], iv["end_ds"]))
    return [e for e in events if not any(a <= e["t_ds"] < b for a, b in by.get(e["source_id"], ()))]


def wilson_upper(x, n, z=Z_ONE_SIDED_95):
    if n == 0: return 1.0
    p = x / n; z2 = z * z
    return min(1.0, (p + z2 / (2 * n) + z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n))) / (1 + z2 / n))


def wilson_lower(x, n, z=Z_ONE_SIDED_95):
    if n == 0: return 0.0
    p = x / n; z2 = z * z
    return max(0.0, (p + z2 / (2 * n) - z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n))) / (1 + z2 / n))


def match_source(t1, t2):
    """t1,t2: sorted lists of deciseconds (ties broken by list order) for ONE source.
    Pairs allowed iff |d|<=5. Result maximises cardinality, then minimises sum|d|, then picks the lexicographically smallest
    sorted tuple of (index1,index2) (i.e. earliest Pass-1 then earliest Pass-2 event). Returns list of (i,j)."""
    n1, n2 = len(t1), len(t2)
    adj = [[j for j in range(n2) if abs(t1[i] - t2[j]) <= MATCH_TOL_DS] for i in range(n1)]
    seen1 = [False] * n1; seen2 = [False] * n2; pairs = []
    for s in range(n1):
        if seen1[s] or not adj[s]: continue
        c1, c2, stack = set(), set(), [("a", s)]
        while stack:
            side, k = stack.pop()
            if side == "a":
                if k in c1: continue
                c1.add(k); stack += [("b", j) for j in adj[k]]
            else:
                if k in c2: continue
                c2.add(k); stack += [("a", i) for i in range(n1) if k in adj[i]]
        for i in c1: seen1[i] = True
        a = sorted(c1); b = sorted(c2)
        pairs += _solve_component(t1, t2, a, b)
    return sorted(pairs)


def _solve_component(t1, t2, a, b):
    """Exact DP over side-1 events in time order; the used-mask is restricted to side-2 events still adjacent to a later side-1 event,
    so chains of closely spaced events stay tractable. Key minimised: (-cardinality, total |dt|, sorted pair-index tuple)."""
    pos = {j: k for k, j in enumerate(b)}
    rel = []
    for ii in range(len(a) + 1):
        m = 0
        for i in a[ii:]:
            for j in b:
                if abs(t1[i] - t2[j]) <= MATCH_TOL_DS: m |= 1 << pos[j]
        rel.append(m)
    memo = {}
    def best(ii, mask):
        if ii == len(a): return (0, 0, ())
        key = (ii, mask & rel[ii])
        if key in memo: return memo[key]
        if len(memo) > MAX_DP_STATES: raise ValueError("matching component too large for the exact solver")
        i = a[ii]
        r = best(ii + 1, mask); cands = [(-r[0], r[1], r[2])]
        for j in b:
            if mask >> pos[j] & 1 or abs(t1[i] - t2[j]) > MATCH_TOL_DS: continue
            r = best(ii + 1, mask | (1 << pos[j]))
            cands.append((-(r[0] + 1), r[1] + abs(t1[i] - t2[j]), ((i, j),) + r[2]))
        k = min(cands); memo[key] = (-k[0], k[1], k[2]); return memo[key]
    import sys
    old = sys.getrecursionlimit(); sys.setrecursionlimit(max(old, 10000))
    try: return list(best(0, 0)[2])
    finally: sys.setrecursionlimit(old)


def build_pairs(e1, e2):
    """Per-source matching over filtered event lists. Returns (pairs as (event1, event2) dicts)."""
    out = []
    for sid in sorted({e["source_id"] for e in e1} | {e["source_id"] for e in e2}):
        a = sorted([e for e in e1 if e["source_id"] == sid], key=_ev_sort_key)
        b = sorted([e for e in e2 if e["source_id"] == sid], key=_ev_sort_key)
        for i, j in match_source([e["t_ds"] for e in a], [e["t_ds"] for e in b]): out.append((a[i], b[j]))
    return out


def _prop(num, den): return None if den == 0 else Fraction(num, den)


def evaluate(pass1, pass2, intervals):
    e1 = filter_events(pass1, intervals); e2 = filter_events(pass2, intervals)
    n1, n2 = len(e1), len(e2)
    pairs = build_pairs(e1, e2); m = len(pairs); union = n1 + n2 - m
    full = [sum(e["observability"] == "FULL" for e in e) for e in (e1, e2)]
    full_id = [sum(e["observability"] == "FULL" and e["performer"] != UNCLEAR for e in e) for e in (e1, e2)]
    both_id = [(p, q) for p, q in pairs if p["performer"] != UNCLEAR and q["performer"] != UNCLEAR]
    same = sum(p["performer"] == q["performer"] for p, q in both_id)
    nobs_dis = sum(p["observability"] != q["observability"] for p, q in pairs)
    nperf_dis = len(both_id) - same
    counts = {"E1": n1, "E2": n2, "matched": m, "union": union, "unmatched_1": n1 - m, "unmatched_2": n2 - m,
              "FULL_1": full[0], "FULL_2": full[1], "FULL_identifiable_1": full_id[0], "FULL_identifiable_2": full_id[1],
              "pairs_both_identifiable": len(both_id), "performer_agree": same, "performer_disagree": nperf_dis, "observability_disagree": nobs_dis}
    # metric definitions: (numerator, denominator) per binding side
    O_k = [(full[0], n1), (full[1], n2)]; I_k = [(full_id[0], full[0]), (full_id[1], full[1])]
    def pick(ks):
        vals = [_prop(*k) for k in ks]
        if any(v is None for v in vals): return None, None
        idx = 0 if vals[0] <= vals[1] else 1; return vals[idx], ks[idx]
    metrics = {}
    metrics["A"] = {"value": _prop(m, union), "x": m, "n": union, "evaluable": union >= MIN_DENOM["A"]}
    ov, ok = pick(O_k); metrics["O"] = {"value": ov, "x": ok[0] if ok else 0, "n": ok[1] if ok else 0, "evaluable": min(n1, n2) >= MIN_DENOM["O"] and ov is not None,
                                        "per_pass": [str(_prop(*k)) if _prop(*k) is not None else None for k in O_k]}
    iv, ik = pick(I_k); metrics["I"] = {"value": iv, "x": ik[0] if ik else 0, "n": ik[1] if ik else 0, "evaluable": min(full) >= MIN_DENOM["I"] and iv is not None,
                                        "per_pass": [str(_prop(*k)) if _prop(*k) is not None else None for k in I_k]}
    metrics["PA"] = {"value": _prop(same, len(both_id)), "x": same, "n": len(both_id), "evaluable": len(both_id) >= MIN_DENOM["PA"]}
    for k, d in metrics.items():
        d["pass_bound"] = str(PASS_BOUND[k]); d["fail_bound"] = str(FAIL_BOUND[k])
        d["in_pass_zone"] = bool(d["evaluable"] and d["value"] >= PASS_BOUND[k])
        d["in_fail_zone"] = bool(d["evaluable"] and d["value"] < FAIL_BOUND[k])
        if d["n"] > 0: d["wilson_upper_95_one_sided"] = wilson_upper(d["x"], d["n"]); d["wilson_lower_95_one_sided"] = wilson_lower(d["x"], d["n"])
        else: d["wilson_upper_95_one_sided"] = d["wilson_lower_95_one_sided"] = None
        d["kill_condition"] = bool(d["in_fail_zone"] and d["wilson_upper_95_one_sided"] < float(PASS_BOUND[k]))
    killers = [k for k in ("A", "O", "I", "PA") if metrics[k]["kill_condition"]]
    if n1 < MIN_PREVALENCE: outcome = "INCONCLUSIVE_PREVALENCE"
    elif killers: outcome = "KILL"
    elif all(metrics[k]["evaluable"] for k in metrics):
        outcome = "PASS" if all(metrics[k]["in_pass_zone"] for k in metrics) else "MODIFY"
    else: outcome = "INCONCLUSIVE_DENOMINATOR"
    ser = {k: dict(v, value=None if v["value"] is None else str(v["value"])) for k, v in metrics.items()}
    return {"outcome": outcome, "kill_metrics": killers if outcome == "KILL" else [], "counts": counts, "metrics": ser}
