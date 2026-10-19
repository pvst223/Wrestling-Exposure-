"""Deterministic operating-point selection (spec_v4 03 section 3; 09 for the single-DEV-episode case). Same procedure for both methods."""
CSTARS = (0.5, 0.4, 0.3, 0.2, 0.1)
def _cov(p): return -1.0 if p.get("coverage") is None else p["coverage"]
def joint_cstar(points_by_method, cstars=CSTARS, fold_key="fold_coverages"):
    """Largest c* reached by at least one point of EVERY method (pooled), and, where fold coverages are given, by a point whose every fold >= c*."""
    def reach(pts, c): return any(_cov(p) >= c and all(v is not None and v >= c for v in p.get(fold_key, [])) for p in pts)
    ok = [c for c in cstars if all(reach(pts, c) for pts in points_by_method.values())]
    return ok[0] if ok else None
def select_point(points, cstar, fold_key="fold_coverages"):
    """Among points with pooled coverage >= c* (and every fold coverage >= c*): lowest FTA; ties highest coverage; ties lexicographically smallest param."""
    el = [p for p in points if _cov(p) >= cstar and all(v is not None and v >= cstar for v in p.get(fold_key, []))]
    if not el: return None
    return min(el, key=lambda p: (p["fta"] if p["fta"] is not None else 9.0, -_cov(p), tuple(p["param"])))
