"""Unit tables and metrics (same definitions as frozen V0.6 phase1_run.unit_table/table_metrics/paired), standalone and numpy/scipy only.
Candidate row: dict(clip, shot, truth, accepted) where accepted is None/'' (not accepted) or the accepted identity string; targets = (A,B) of the episode."""
import collections
import numpy as np
from scipy.stats import beta, binom, rankdata
NEG_CLASSES = ("REFEREE", "STAFF", "SPECTATOR", "OTHER_WRESTLER_UNNAMED")
def norm_truth(t): return "STAFF" if t == "RINGSIDE_STAFF" else t
def unit_table(ep_rows):
    """ep_rows: list of (targets:(A,B), rows). Unit = (clip, shot, truth). Returns dict key -> dict(false, cov list, named)."""
    U = {}
    for targets, rows in ep_rows:
        per = collections.OrderedDict()
        for r in rows:
            k = (r["clip"], str(r["shot"]), norm_truth(r["truth"])); u = per.setdefault(k, dict(n=0, correct=0, false=0)); u["n"] += 1
            acc = r.get("accepted") or ""
            if acc:
                if k[2] in targets and acc == k[2]: u["correct"] += 1
                else: u["false"] += 1
        for k, u in per.items():
            g = U.setdefault(k, dict(false=False, cov=[], named=k[2] not in NEG_CLASSES)); g["false"] = g["false"] or u["false"] > 0
            if k[2] in targets: g["cov"].append(u["correct"] / u["n"])
    return U
def table_metrics(U):
    n = len(U); fa = sum(1 for u in U.values() if u["false"]); tg = [sum(u["cov"]) / len(u["cov"]) for u in U.values() if u["cov"]]
    st = collections.defaultdict(lambda: [0, 0])
    for k, u in U.items():
        s = "OTHER_NAMED_WRESTLER" if u["named"] else k[2]; st[s][0] += 1; st[s][1] += int(u["false"])
    return dict(n_units=n, fa_units=fa, fta=(fa / n if n else None), n_target_units=len(tg), coverage=(sum(tg) / len(tg) if tg else None), strata={s: dict(n=a, fa=b) for s, (a, b) in sorted(st.items())})
def clopper_pearson(k, n, a=0.05):
    if n == 0: return (None, None)
    lo = 0.0 if k == 0 else beta.ppf(a / 2, k, n - k + 1); hi = 1.0 if k == n else beta.ppf(1 - a / 2, k + 1, n - k); return (float(lo), float(hi))
def paired_sign(Tb, Tl):
    if set(Tb) != set(Tl): raise ValueError("unit sets differ between methods")
    b = sum(1 for k in Tb if Tb[k]["false"] and not Tl[k]["false"]); c = sum(1 for k in Tb if Tl[k]["false"] and not Tb[k]["false"]); both = sum(1 for k in Tb if Tb[k]["false"] and Tl[k]["false"]); n = b + c
    p = 1.0 if n == 0 else (float(binom.sf(b - 1, n, 0.5)) if b > 0 else 1.0)
    return dict(n_units=len(Tb), b_baseline_only=b, c_learned_only=c, both=both, discordant=n, one_sided_p_b_gt_c=p)
def auroc(pos, neg):
    pos = np.asarray(pos, float); neg = np.asarray(neg, float)
    if len(pos) == 0 or len(neg) == 0: return float("nan")
    r = rankdata(np.concatenate([pos, neg])); return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))
