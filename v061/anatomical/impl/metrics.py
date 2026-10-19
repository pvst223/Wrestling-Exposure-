"""M1-M9 reporting machinery (descriptive only; no thresholds; no exposure/COM/distance/impact/workload quantity). Measured rows only unless stated; CARRIED rows are excluded from every numerator/denominator (M8 reports their share)."""
import collections, csv, hashlib, io, json, random
from record_class import ASSIGNED, WITHHELD
def cp_ci(k, n, alpha=0.05):
    if n == 0: return (None, None)
    from scipy.stats import beta
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1)); hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return (lo, hi)
def _meas(rows): return [r for r in rows if r.get("pose_status") == "MEASURED" and r.get("measurement", True)]
def m1_joint_table(rows):
    t = collections.Counter(); 
    for r in _meas(rows): t[(r["clip"], r["shot"], r["identity_state_passthrough"], r["ownership_state_passthrough"], r["record_class"])] += 1
    return [dict(clip=k[0], shot=k[1], identity=k[2], ownership=k[3], record_class=k[4], n=v) for k, v in sorted(t.items())]
def m2_withholding(rows, flag=0.20):
    """numerator: identity-ACCEPT measured-pose frames withheld by ownership (any WITHHELD_*); denominator: identity-ACCEPT measured-pose frames. Diagnostic flag only."""
    out = []; g = collections.defaultdict(lambda: [0, 0, 0])
    for r in _meas(rows):
        if r["identity_state_passthrough"] in ("ACCEPT_A", "ACCEPT_B") and not r["numeric_failure"]:
            for key in ((r["clip"], r["shot"]), (r["clip"], "ALL"), ("ALL", "ALL")):
                g[key][1] += 1
                if r["record_class"] in WITHHELD: g[key][0] += 1
                if r["record_class"] == "WITHHELD_OWNERSHIP_NOT_EVALUATED": g[key][2] += 1
    for k, (num, den, ne) in sorted(g.items(), key=lambda x: (str(x[0][0]), str(x[0][1]))):
        lo, hi = cp_ci(num, den); out.append(dict(clip=k[0], shot=k[1], withheld=num, accept_measured=den, of_which_not_evaluated=ne, frac=(num / den if den else None), ci95=[lo, hi], diagnostic_flag_ge_20pct=bool(den and num / den >= flag)))
    return out
def m3_disagreements(rows):
    c = collections.Counter()
    for r in _meas(rows):
        a, o = r["identity_state_passthrough"], r["ownership_state_passthrough"]
        if a in ("ACCEPT_A", "ACCEPT_B") and o != "SINGLE_BODY_SUPPORTED": c["ACCEPT_but_ownership_not_single"] += 1
        if a == "ABSTAIN_AMBIGUOUS" and o == "SINGLE_BODY_SUPPORTED": c["ABSTAIN_with_single_body"] += 1
        if a == "REJECT_NONTARGET" and o == "SINGLE_BODY_SUPPORTED": c["NONTARGET_with_single_body"] += 1
    return dict(c)
def m4_label_flips(rows):
    flips = []; by = collections.defaultdict(list)
    for r in _meas(rows):
        if r["record_class"] in ASSIGNED: by[r["tracklet"]].append(r)
    for t, rs in by.items():
        rs.sort(key=lambda r: r["frame"])
        for a, b in zip(rs, rs[1:]):
            if a["record_class"] != b["record_class"]: flips.append(dict(tracklet=t, from_frame=a["frame"], to_frame=b["frame"], frm=a["assigned_label"], to=b["assigned_label"]))
    dup = collections.Counter((r["clip"], r["frame"], r["record_class"]) for r in _meas(rows) if r["record_class"] in ASSIGNED)
    return dict(flips=flips, n_flips=len(flips), same_label_on_two_detections=[dict(clip=k[0], frame=k[1], label=k[2]) for k, v in dup.items() if v > 1])
def m5_temporal(rows):
    d = [r["temporal"]["median_rel"] for r in _meas(rows) if r.get("temporal") and r["temporal"].get("applicable") and r["temporal"].get("median_rel") is not None]
    jumps = sum(1 for r in _meas(rows) if "TEMPORAL_JOINT_JUMP" in (r.get("own_reasons") or []) or r.get("temporal") and r["temporal"].get("applicable") and r["temporal"]["fail_joints"] >= 2)
    d.sort(); return dict(n_pairs=len(d), median_of_median_rel=(d[len(d) // 2] if d else None), max_median_rel=(d[-1] if d else None), n_joint_jump_rows=jumps)
def m6_coverage(rows, min_lm=4):
    m = _meas(rows); n = len(m); k = sum(1 for r in m if r["n_landmarks"] >= min_lm); return dict(measured=n, with_min_landmarks=k, frac=(k / n if n else None), ci95=list(cp_ci(k, n)))
def m7_cut_crosscheck(frozen_shot_starts, classifier_cuts, tol=2):
    a = sorted(int(x) for x in frozen_shot_starts if int(x) > 0); b = sorted(int(x) for x in classifier_cuts)
    ma = [x for x in a if any(abs(x - y) <= tol for y in b)]; mb = [y for y in b if any(abs(x - y) <= tol for x in a)]
    return dict(frozen_only=[x for x in a if x not in ma], classifier_only=[y for y in b if y not in mb], agree=len(ma), note="disagreements are reported, not reconciled")
def m8_carry(source_rows):
    c = collections.Counter(r["pose_status"] for r in source_rows); n = sum(c.values()); return dict(counts=dict(c), carried_share=(c["CARRIED"] / n if n else None), note="visualization only; excluded from all metrics")
def m9_select(rows, seed, n_min=30):
    """Deterministic stratified selection of MEASURED rows: ASSIGNED_* and WITHHELD_* separately, spread over clips (round-robin), >= n_min each if available (else all + shortfall).
    Returns (status-blind review sheet rows with shuffled review_id, hidden key rows, shortfall dict)."""
    rng = random.Random(seed); sheet = []; key = []; short = {}
    for name, classes in (("ASSIGNED", ASSIGNED), ("WITHHELD", WITHHELD)):
        pool = collections.defaultdict(list)
        for r in _meas(rows):
            if r["record_class"] in classes: pool[r["clip"]].append(r)
        for v in pool.values(): v.sort(key=lambda r: (r["tracklet"], r["frame"])); rng.shuffle(v)
        pick = []; clips = sorted(pool)
        while len(pick) < n_min and any(pool[c] for c in clips):
            for c in clips:
                if pool[c] and len(pick) < n_min: pick.append(pool[c].pop())
        total = sum(1 for r in _meas(rows) if r["record_class"] in classes)
        if len(pick) < n_min: short[name] = dict(requested=n_min, available=total, reviewed=len(pick))
        for r in pick: key.append(dict(clip=r["clip"], tracklet=r["tracklet"], frame=r["frame"], record_class=r["record_class"], stratum=name)); sheet.append(dict(clip=r["clip"], tracklet=r["tracklet"], frame=r["frame"], box=r["box"]))
    order = list(range(len(sheet))); rng.shuffle(order)
    sheet2 = [dict(review_id=f"R{n:03d}", **sheet[i]) for n, i in enumerate(order)]; key2 = [dict(review_id=f"R{n:03d}", **key[i]) for n, i in enumerate(order)]
    return sheet2, key2, short
VERDICTS = ("SINGLE_PERSON", "MIXED_OR_WRONG_BODY", "UNSURE")
def m9_summarise(key_rows, verdict_rows):
    v = {r["review_id"]: r["verdict"] for r in verdict_rows}; assert all(x in VERDICTS for x in v.values())
    out = {}; contaminated = []
    for stratum in ("ASSIGNED", "WITHHELD"):
        ks = [k for k in key_rows if k["stratum"] == stratum and k["review_id"] in v]; c = collections.Counter(v[k["review_id"]] for k in ks)
        out[stratum] = dict(reviewed=len(ks), counts=dict(c))
        if stratum == "ASSIGNED": contaminated += [dict(k, verdict=v[k["review_id"]]) for k in ks if v[k["review_id"]] == "MIXED_OR_WRONG_BODY"]
    out["contaminated_emitted_skeletons_individually"] = contaminated; out["label"] = "ANNOTATION-PROVISIONAL single reviewer; not accuracy or validation"; return out
def report(rows, source_rows, frozen_shot_starts, classifier_cuts, seed):
    sheet, key, short = m9_select(rows, seed)
    return dict(M1=m1_joint_table(rows), M2=m2_withholding(rows), M3=m3_disagreements(rows), M4=m4_label_flips(rows), M5=m5_temporal(rows), M6=m6_coverage(rows), M7=m7_cut_crosscheck(frozen_shot_starts, classifier_cuts),
                M8=m8_carry(source_rows), M9=dict(n_sheet=len(sheet), shortfall=short)), sheet, key
