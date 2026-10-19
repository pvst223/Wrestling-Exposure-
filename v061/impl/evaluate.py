"""Grid evaluation and development-only diagnostics for the V0.6.1 rule. Pure functions of (probabilities, labels, parameters, seed).
Episode dict: id, targets=(A,B), clip, rows=[dict(clip, shot, truth)], P=(n,3) array of (pA,pB,pN)."""
import collections
import numpy as np
from . import decision_rule as R, units as U
LABEL = "V0.6.1 DEVELOPMENT / HYPOTHESIS CHECK ONLY"
def rows_for(ep, tau_g, delta):
    code, bad, g, q = R.decide(ep["P"], tau_g, delta); A, B = ep["targets"]; out = []
    for r, c in zip(ep["rows"], code):
        out.append(dict(clip=r["clip"], shot=r["shot"], truth=r["truth"], accepted=(A if c == R.ACCEPT_A else B if c == R.ACCEPT_B else "")))
    return out
def unit_table_for(eps, tau_g, delta): return U.unit_table([(ep["targets"], rows_for(ep, tau_g, delta)) for ep in eps])
def grid_points(eps, grid=R.GRID_L1):
    pts = []
    for tg, dl in grid:
        m = U.table_metrics(unit_table_for(eps, tg, dl)); m["param"] = (tg, dl)
        m["fold_coverages"] = [(U.table_metrics(unit_table_for([e], tg, dl))["coverage"]) for e in eps] if len(eps) > 1 else []
        pts.append(m)
    return pts
def _stratum(truth, targets):
    t = U.norm_truth(truth)
    return "TARGET" if t in targets else ("OTHER_NAMED_WRESTLER" if t not in U.NEG_CLASSES else t)
def diagnostics(eps, tau_g, delta, seed, B=2000):
    """Development-only: target-gate behaviour, A/B assignment behaviour, abstention reason, coverage, false-target acceptance."""
    cand = []
    for ep in eps:
        code, bad, g, q = R.decide(ep["P"], tau_g, delta); A, Bn = ep["targets"]
        for i, r in enumerate(ep["rows"]):
            s = _stratum(r["truth"], ep["targets"])
            cand.append(dict(unit=(r["clip"], str(r["shot"]), U.norm_truth(r["truth"])), strat=s, tgt=s == "TARGET", isA=U.norm_truth(r["truth"]) == A,
                             g=float(g[i]), q=float(q[i]), code=int(code[i]), bad=bool(bad[i]),
                             wrong=bool(s == "TARGET" and ((code[i] == R.ACCEPT_A and U.norm_truth(r["truth"]) != A) or (code[i] == R.ACCEPT_B and U.norm_truth(r["truth"]) != Bn)))))
    dec = collections.defaultdict(collections.Counter)
    for c in cand: dec[c["strat"]][R.NAMES[c["code"]]] += 1
    acc = [c for c in cand if c["code"] in (R.ACCEPT_A, R.ACCEPT_B)]; acc_t = [c for c in acc if c["tgt"]]
    def stats(rows):
        T = [r for r in rows if r["tgt"] and np.isfinite(r["g"])]
        gate = U.auroc([r["g"] for r in rows if r["tgt"] and np.isfinite(r["g"])], [r["g"] for r in rows if not r["tgt"] and np.isfinite(r["g"])])
        ab = U.auroc([r["q"] for r in T if r["isA"] and np.isfinite(r["q"])], [r["q"] for r in T if not r["isA"] and np.isfinite(r["q"])])
        return gate, ab
    gate, ab = stats(cand)
    byu = collections.defaultdict(list)
    for c in cand: byu[c["unit"]].append(c)
    keys = sorted(byu); rng = np.random.default_rng(seed); bg, ba = [], []
    for _ in range(B):
        flat = [r for j in rng.integers(0, len(keys), len(keys)) for r in byu[keys[j]]]; x, y = stats(flat)
        if x == x: bg.append(x)
        if y == y: ba.append(y)
    ci = lambda a: [float(np.quantile(a, .025)), float(np.quantile(a, .975))] if a else None
    tab = U.table_metrics(unit_table_for(eps, tau_g, delta)); n, k = tab["n_units"], tab["fa_units"]
    out = dict(label=LABEL, param=dict(tau_g=tau_g, delta=delta), seed=seed, unit_metrics=tab, fta_ci95_exact=list(U.clopper_pearson(k, n)),
               decision_decomposition_candidates={s: dict(v) for s, v in sorted(dec.items())},
               n_numeric_failures=int(sum(c["bad"] for c in cand)),
               target_gate=dict(auroc=gate, ci95=ci(bg), target_candidates_rejected=sum(1 for c in cand if c["tgt"] and c["code"] == R.REJECT_NONTARGET), target_candidates=sum(1 for c in cand if c["tgt"])),
               ab_assignment=dict(auroc=ab, ci95=ci(ba), target_candidates_abstained=sum(1 for c in cand if c["tgt"] and c["code"] == R.ABSTAIN_AMBIGUOUS), accepted_target_candidates=len(acc_t), accepted_as_wrong_target=sum(c["wrong"] for c in acc_t)),
               false_target_acceptance=dict(nontarget_candidates_accepted=len(acc) - len(acc_t), by_stratum_units=tab["strata"]),
               coverage=tab["coverage"],
               flags_descriptive_only=dict(D_GATE_lower_ci_below_0_70=(ci(bg) or [1.0])[0] < 0.70, F_ASSIGN_interval_includes_0_5=(ci(ba) or [0.0, 1.0])[0] <= 0.5 <= (ci(ba) or [0.0, 1.0])[1]))
    return out
