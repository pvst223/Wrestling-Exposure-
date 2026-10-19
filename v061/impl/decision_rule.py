"""V0.6.1 two-stage decision rule (spec_v4 01_SPEC_decision_rule.md). Heuristic scores, NOT probabilities of anything validated.
Stage 1 gate g = pA + pB (= 1 - pN); reject if g < tau_g.  Stage 2 q = pA/g; accept A if q >= 0.5+delta, B if q <= 0.5-delta, else ABSTAIN.
Fail-closed: non-finite input, g < 1e-12 -> REJECT_NONTARGET with numeric_failure=True (clarification C1/C2, see IMPLEMENTATION_CLARIFICATIONS.md)."""
import numpy as np
GRID_L1 = [(t, d) for t in (0.5, 0.6, 0.7, 0.8, 0.9) for d in (0.05, 0.10, 0.20, 0.30)]   # 20 points, fixed by spec_v4
GRID_B0 = [(t, m) for t in (0.30, 0.40, 0.50, 0.60, 0.70) for m in (0.00, 0.02, 0.05, 0.10)]  # original frozen Phase-1 grid
ACCEPT_A, ACCEPT_B, REJECT_NONTARGET, ABSTAIN_AMBIGUOUS = 0, 1, 2, 3
NAMES = ("ACCEPT_A", "ACCEPT_B", "REJECT_NONTARGET", "ABSTAIN_AMBIGUOUS")
EPS_G = 1e-12
RANGE_TOL = 1e-6   # clarification C2: probabilities outside [0,1] by more than this are a numerical failure
SUM_TOL = 1e-4     # clarification C2: |pA+pB+pN-1| above this is a numerical failure
def decide(p, tau_g, delta):
    """p: (n,3) array of (pA,pB,pN). Returns (code int8 (n,), numeric_failure bool (n,), g (n,), q (n,)); q is NaN when undefined."""
    if not (0.0 < tau_g <= 1.0): raise ValueError("tau_g must be in (0,1]")
    if not (0.0 <= delta < 0.5): raise ValueError("delta must be in [0,0.5)")
    p = np.asarray(p, dtype=np.float64)
    if p.ndim != 2 or p.shape[1] != 3: raise ValueError("p must have shape (n,3)")
    pA, pB, pN = p[:, 0], p[:, 1], p[:, 2]
    with np.errstate(all="ignore"):
        finite = np.isfinite(p).all(1)
        in_range = ((p >= -RANGE_TOL) & (p <= 1 + RANGE_TOL)).all(1)
        sums = np.abs(p.sum(1) - 1.0) <= SUM_TOL
        g = pA + pB
        bad = ~(finite & in_range & sums) | ~(g >= EPS_G)
        g_safe = np.where(bad, 1.0, g)
        q = np.where(bad, np.nan, pA / g_safe)
        code = np.full(len(p), ABSTAIN_AMBIGUOUS, dtype=np.int8)
        code[(q >= 0.5 + delta)] = ACCEPT_A
        code[(q <= 0.5 - delta)] = ACCEPT_B
        code[bad | (g < tau_g)] = REJECT_NONTARGET
    g_out = np.where(bad, np.nan, g)
    return code, bad, g_out, q
def decide_one(pA, pB, pN, tau_g, delta):
    code, _, _, _ = decide(np.array([[pA, pB, pN]]), tau_g, delta)
    return NAMES[int(code[0])]
