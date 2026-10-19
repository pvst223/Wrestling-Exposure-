#!/usr/bin/env python3
"""M9C join + analysis (frozen at registration; run ONCE after BOTH reviewers' verdict files are frozen and hashed). Mechanical KEEP/MODIFY/KILL per design sec. 6 + Amendment 1.
Primary reviewer (Claude) decides the pre-registered outcome; the owner's verdicts are an independent reproducibility/sensitivity analysis reported separately."""
import collections, csv, json, os, sys
V4 = ("CORRECT", "PARTIAL_BUT_USABLE", "CONTAMINATED", "NOT_JUDGEABLE")
def cp(k, n, a=0.05):
    from scipy.stats import beta
    return (0.0 if k == 0 else float(beta.ppf(a / 2, k, n - k + 1)), 1.0 if k == n else float(beta.ppf(1 - a / 2, k + 1, n - k))) if n else (None, None)
def summ(rs):
    j = [r for r in rs if r["verdict"] != "NOT_JUDGEABLE"]; u = sum(1 for r in j if r["verdict"] in ("CORRECT", "PARTIAL_BUT_USABLE")); c = sum(1 for r in j if r["verdict"] == "CONTAMINATED"); n = len(rs)
    return dict(n=n, counts=dict(collections.Counter(r["verdict"] for r in rs)), judgeable=len(j), usable=u, usable_frac=u / len(j) if j else None, usable_ci95=cp(u, len(j)), contaminated=c, contaminated_frac=c / len(j) if j else None,
                contaminated_ci95=cp(c, len(j)), not_judgeable=n - len(j), not_judgeable_frac=(n - len(j)) / n if n else None)
def kappa(pairs):
    n = len(pairs)
    if not n: return None
    po = sum(1 for a, b in pairs if a == b) / n; ca = collections.Counter(a for a, _ in pairs); cb = collections.Counter(b for _, b in pairs); pe = sum(ca[k] * cb[k] for k in V4) / n ** 2
    return dict(n=n, raw_agreement=po, cohen_kappa=(1.0 if pe == 1 else (po - pe) / (1 - pe)), table={a: {b: sum(1 for x, y in pairs if x == a and y == b) for b in V4} for a in V4})
def decide(rel, clip_contam, ctrl_h, coverage_pts, structural_shots, pending=False):
    """Amendment-1 gates + reviewer clarifications 5a/5b/5c (final authorization). structural_shots = number of distinct shots in which localized inspection established that an emitted OWN_ONLY landmark
    (or a released bone built from them) belongs to the wrong body; a frame-level CONTAMINATED label alone never counts. pending = some contaminated released frame has no recorded determination yet."""
    cf = ctrl_h["contaminated_frac"]; uninformative = (cf is None) or cf == 0
    g = dict(judgeable_ge_50=rel["judgeable"] >= 50, contamination_le_5pct=rel["contaminated_frac"] is not None and rel["contaminated_frac"] <= 0.05, coverage_ge_5pts=coverage_pts >= 5.0,
             no_clip_ge_3_contaminated=all(v < 3 for v in clip_contam.values()), hardveto_ge_2x_released=(not uninformative) and rel["contaminated_frac"] is not None and cf >= 2 * rel["contaminated_frac"], not_judgeable_le_25pct=rel["not_judgeable_frac"] <= 0.25)
    kill = (rel["contaminated_frac"] is not None and rel["contaminated_frac"] >= 0.10) or structural_shots >= 2
    modify = (not kill) and (rel["contaminated_frac"] is not None and rel["contaminated_frac"] > 0.05 or not g["coverage_ge_5pts"] or not g["no_clip_ge_3_contaminated"] or not g["not_judgeable_le_25pct"])
    unmet = [k for k, v in g.items() if not v]
    if kill: out = "KILL"
    elif modify: out = "MODIFY"
    elif pending: out = "PENDING_STRUCTURAL_DETERMINATION"
    elif not unmet: out = "KEEP"
    elif unmet == ["hardveto_ge_2x_released"] and uninformative: out = "NOT_KEEP_CRITERION_UNINFORMATIVE_CONTROL_NEEDS_REVIEWER_INTERPRETATION"
    else: out = "NOT_KEEP_CRITERION_UNMET_NEEDS_REVIEWER_INTERPRETATION"
    return dict(gates=g, unmet_gates=unmet, outcome=out, control_uninformative=uninformative,
                structural_clause=dict(distinct_shots_with_established_wrong_body_released_landmark=structural_shots, kill_triggered=structural_shots >= 2, pending_determinations=pending,
                                       rule="KILL only if localized inspection establishes an emitted OWN_ONLY landmark or released bone belongs to the wrong body in >=2 distinct shots; a CONTAMINATED label alone does not count; independent of the 5% gate"))
def main(priv, claude_json, owner_json, out, parity_json, wrongbody_json=None, n_idacc=2179):
    key = list(csv.DictReader(open(os.path.join(priv, "M9C_HIDDEN_KEY.csv"), newline=""))); ver = json.load(open(claude_json)); assert set(ver) == {k["review_id"] for k in key} and all(v["verdict"] in V4 for v in ver.values())
    rows = [dict(k, verdict=ver[k["review_id"]]["verdict"], contact=ver[k["review_id"]].get("contact", ""), note=ver[k["review_id"]].get("note", ""), reasons=json.loads(k["reasons"])) for k in key]
    rel = [r for r in rows if r["stratum"] == "RELEASED"]; ca = [r for r in rows if r["stratum"] == "CONTROL_ASSIGNED"]; ch = [r for r in rows if r["stratum"] == "CONTROL_HARDVETO"]
    P = json.load(open(parity_json)); n_rel_total = sum(sum(v.get("released", {}).values()) for v in P["per_clip"].values()); cov = 100.0 * n_rel_total / n_idacc
    S = summ(rel); clip_c = {c: sum(1 for r in rel if r["clip"] == c and r["verdict"] == "CONTAMINATED") for c in sorted({r["clip"] for r in rel})}
    wb = json.load(open(wrongbody_json)) if wrongbody_json else {}; contam = [r for r in rel if r["verdict"] == "CONTAMINATED"]
    for v in wb.values(): assert v["wrong_body_landmark"] in ("YES", "NO", "UNDETERMINED")
    assert set(wb) <= {r["review_id"] for r in contam}, "determinations only for contaminated RELEASED frames"
    pending = any(r["review_id"] not in wb for r in contam); shots_c = {(r["clip"], r["shot"]) for r in contam if wb.get(r["review_id"], {}).get("wrong_body_landmark") == "YES"}; D = decide(S, clip_c, summ(ch), cov, len(shots_c), pending)
    res = dict(label="M9C primary reviewer Claude (non-independent), development-only, ANNOTATION-PROVISIONAL; no validation claim", released=S, control_assigned=summ(ca), control_hardveto=summ(ch),
               by_clip={c: summ([r for r in rel if r["clip"] == c]) for c in clip_c}, by_shot={f"{c}|{s}": summ([r for r in rel if (r["clip"], r["shot"]) == (c, s)]) for c, s in sorted({(r["clip"], r["shot"]) for r in rel})},
               by_contact={k: summ([r for r in rel if r["contact"] == k]) for k in ("YES", "NO", "")}, by_identity={k: summ([r for r in rel if r["identity"] == k]) for k in ("ACCEPT_A", "ACCEPT_B")},
               by_n_released=None, recovered=dict(structural_released_total=n_rel_total, coverage_gain_points_of_identity_accept_measured=cov, net_contaminated_per_100_identity_accept=(S["contaminated_frac"] or 0) * cov),
               decision=D, contaminated_released=[{k: r[k] for k in ("review_id", "clip", "frame", "shot", "identity", "reasons", "note")} for r in rel if r["verdict"] == "CONTAMINATED"], wrong_body_determinations=wb,
               merge_guard_flagged=[dict(review_id=r["review_id"], stratum=r["stratum"], verdict=r["verdict"]) for r in rows if r["merge_guard"] in ("True", True)], all_items=rows)
    if owner_json:
        ow = json.load(open(owner_json)); okey = {r["owner_id"]: r for r in csv.DictReader(open(os.path.join(priv, "M9C_OWNER_KEY.csv"), newline=""))}; assert set(ow) == set(okey) and all(v["verdict"] in V4 for v in ow.values())
        byid = {r["review_id"]: r for r in rows}; pairs = [(byid[okey[o]["review_id"]]["verdict"], ow[o]["verdict"]) for o in sorted(ow)]; rp = [(byid[okey[o]["review_id"]]["verdict"], ow[o]["verdict"]) for o in sorted(ow) if okey[o]["stratum"] == "RELEASED"]
        ov = {okey[o]["review_id"]: ow[o]["verdict"] for o in ow}; sub = [dict(r, verdict=ov.get(r["review_id"], r["verdict"])) for r in rel]; subown = [dict(r, verdict=ov[r["review_id"]]) for r in rel if r["review_id"] in ov]; subcl = [r for r in rel if r["review_id"] in ov]
        res["second_reviewer"] = dict(label="independent reproducibility/sensitivity analysis; reported separately; does not decide KEEP/MODIFY/KILL", all_overlap=kappa(pairs), released_overlap=kappa(rp),
                                      overlap_released_claude=summ(subcl), overlap_released_owner=summ(subown), main_released_with_owner_substituted_on_overlap=summ(sub),
                                      decision_under_owner_substitution=decide(summ(sub), {c: sum(1 for r in sub if r["clip"] == c and r["verdict"] == "CONTAMINATED") for c in clip_c}, summ(ch), cov, len(shots_c), True)["outcome"] + " (structural determinations not re-made for owner-only contaminations)")
    json.dump(res, open(out, "w"), indent=1, sort_keys=True, default=str); print(json.dumps(dict(released=S, decision=D["outcome"]), indent=1, default=str)[:1200])
if __name__ == "__main__": main(sys.argv[1], sys.argv[2], sys.argv[3] if sys.argv[3] != "-" else None, sys.argv[4], sys.argv[5], sys.argv[6] if len(sys.argv) > 6 else None)
