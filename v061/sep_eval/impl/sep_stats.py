"""Statistics and mechanical decision for the SEPARATED-BODY EVALUATION V1 (frozen; reviewer rulings D4/D6). Governing KEEP statistic: upper limit of the exact (Clopper-Pearson) two-sided 95% CI of the WRONG_BODY frame proportion."""
from scipy.stats import beta
KEEP_UPPER = 0.05; KILL_POINT = 0.10; KILL_SHOTS = 3; KEEP_MAX_SHOTS = 1; AUDIT_KEEP = 0.05; AUDIT_KILL = 0.10; NJ_MAX = 0.20; MIN_JUDGEABLE = 100; MIN_SHOTS = 20; MIN_CLIPS = 3
def cp(k, n, a=0.05):
    if n == 0: return (None, None)
    return (0.0 if k == 0 else float(beta.ppf(a / 2, k, n - k + 1)), 1.0 if k == n else float(beta.ppf(1 - a / 2, k + 1, n - k)))
def cp_upper_onesided(k, n, a=0.05): return 1.0 if k == n else float(beta.ppf(1 - a, k + 1, n - k))
def max_events_keep(n, thr=KEEP_UPPER):
    """Largest k with upper two-sided exact 95% bound <= thr (None if even 0 events exceeds thr)."""
    best = None
    for k in range(0, n + 1):
        if cp(k, n)[1] <= thr: best = k
        else: break
    return best
def event_table(ns): return {n: dict(max_events=max_events_keep(n), upper_at_max=(cp(max_events_keep(n), n)[1] if max_events_keep(n) is not None else None)) for n in ns}
def decide_reviewer(judgeable, wrong, n_reviewed, not_judgeable, shots_with_judgeable, clips_with_judgeable, shots_with_wrong, audit_answered, audit_other):
    gates = {}; ub = cp(wrong, judgeable)[1] if judgeable else None; pt = wrong / judgeable if judgeable else None; nj = not_judgeable / n_reviewed if n_reviewed else None; au = audit_other / audit_answered if audit_answered else None
    enough = judgeable >= MIN_JUDGEABLE and shots_with_judgeable >= MIN_SHOTS and clips_with_judgeable >= MIN_CLIPS
    gates.update(min_data=enough, upper_le_5pct=(ub is not None and ub <= KEEP_UPPER), wrong_shots_le_1=shots_with_wrong <= KEEP_MAX_SHOTS, audit_false_elig_le_5pct=(au is not None and au <= AUDIT_KEEP), not_judgeable_le_20pct=(nj is not None and nj <= NJ_MAX))
    kill = []
    if pt is not None and pt >= KILL_POINT: kill.append("WRONG_BODY_POINT_ESTIMATE_GE_10PCT")
    if shots_with_wrong >= KILL_SHOTS: kill.append("WRONG_BODY_IN_GE_3_SHOTS")
    if au is not None and au > AUDIT_KILL: kill.append("AUDIT_FALSE_ELIGIBILITY_GT_10PCT")
    if not enough: out = "INCONCLUSIVE_DATA"
    elif kill: out = "KILL"
    elif all(gates.values()): out = "KEEP"
    else: out = "NOT_KEEP_NEEDS_REVIEWER_INTERPRETATION"
    return dict(outcome=out, gates=gates, kill_triggers=kill, wrong_body_point=pt, wrong_body_ci95=cp(wrong, judgeable), wrong_body_upper_onesided95=(cp_upper_onesided(wrong, judgeable) if judgeable else None),
                allowable_events_at_realized_n=max_events_keep(judgeable) if judgeable else None, not_judgeable_frac=nj, audit_false_eligibility=au)
_RANK = {"INCONCLUSIVE_DATA": 0, "KILL": 1, "NOT_KEEP_NEEDS_REVIEWER_INTERPRETATION": 2, "KEEP": 3}
def combine_humans(a, b):
    """Less favourable binds (D6); reviewers are never pooled or averaged. Minimum-data failure in either gives INCONCLUSIVE_DATA (approved rule)."""
    return min((a, b), key=lambda o: _RANK[o])
