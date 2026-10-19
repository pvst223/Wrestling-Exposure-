#!/usr/bin/env python3
"""M9B join + descriptive analysis. Run once after verdicts are frozen."""
import collections, csv, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "anatomical", "impl")); import metrics
V = ("CORRECT", "PARTIAL_BUT_USABLE", "CONTAMINATED", "NOT_JUDGEABLE")
FAM = {"mask_overlap_ownership": ("OPPONENT_LANDMARKS_IN_MASK", "CONTESTED_LANDMARKS", "TOO_FEW_OWN_ONLY_LANDMARKS", "MASK_NOT_EXPLAINED_BY_SKELETON"), "mask_span_other_instance": ("BONE_SPANS_INSTANCES", "LANDMARKS_IN_OTHER_INSTANCE", "SOME_LANDMARK_IN_OTHER_INSTANCE"),
       "mask_support_missing": ("NO_OWNER_MASK", "FEW_LANDMARKS", "BONES_LEAVE_MASK"), "geometry_cross_body": ("LIMB_TOO_LONG", "TORSO_SIDES_ASYMMETRIC", "SHARED_JOINT_CONFLICT", "TEMPORAL_JOINT_JUMP")}
def fams(reasons):
    out = set()
    for r in reasons:
        for f, ms in FAM.items():
            if any(r == m or r.startswith(m + ":") for m in ms): out.add(f); break
        else: out.add("plausibility_other")
    return out
def cnt(rs): return dict(collections.Counter(r["verdict"] for r in rs))
def usable(rs):
    j = [r for r in rs if r["verdict"] != "NOT_JUDGEABLE"]; k = sum(1 for r in j if r["verdict"] in ("CORRECT", "PARTIAL_BUT_USABLE")); c = sum(1 for r in j if r["verdict"] == "CONTAMINATED")
    return dict(n=len(rs), judgeable=len(j), usable=k, usable_frac=(k / len(j) if j else None), usable_ci95=list(metrics.cp_ci(k, len(j))), contaminated=c, contaminated_frac=(c / len(j) if j else None), contaminated_ci95=list(metrics.cp_ci(c, len(j))), not_judgeable=len(rs) - len(j))
def main(priv, verdicts_json, out, pop_cells_json, expect=60):
    if os.path.exists(out): raise SystemExit("write-once")
    ver = json.load(open(verdicts_json)); key = list(csv.DictReader(open(os.path.join(priv, "M9B_HIDDEN_KEY.csv"), newline=""))); assert len(ver) == len(key) == int(expect) and all(v["verdict"] in V for v in ver.values())
    cells = json.load(open(pop_cells_json))["population_cells"]; rows = []
    for k in key: rows.append(dict(k, own_reasons=json.loads(k["own_reasons"]), verdict=ver[k["review_id"]]["verdict"], note=ver[k["review_id"]].get("note", "")))
    by = lambda f: {a: [r for r in rows if f(r) == a] for a in sorted({f(r) for r in rows})}
    byrs = collections.defaultdict(list); byfam = collections.defaultdict(list)
    for r in rows:
        for x in set(r["own_reasons"]): byrs[x].append(r)
        for f in fams(r["own_reasons"]): byfam[f].append(r)
    # population-weighted descriptive proportions (weight = N_cell / n_cell), judgeable items only
    num = den = cnum = 0.0
    for cell, rs in by(lambda r: f"{r['clip']}|{r['ownership_state']}").items():
        j = [r for r in rs if r["verdict"] != "NOT_JUDGEABLE"]
        if not j: continue
        w = cells[cell] / len(j); den += w * len(j); num += w * sum(1 for r in j if r["verdict"] in ("CORRECT", "PARTIAL_BUT_USABLE")); cnum += w * sum(1 for r in j if r["verdict"] == "CONTAMINATED")
    res = dict(label="M9B single-reviewer (Claude, non-independent) ANNOTATION-PROVISIONAL; exploratory diagnostic; NOT validated accuracy; no rule change", n=len(rows), overall=cnt(rows), overall_usable_contaminated=usable(rows),
               by_ownership_state={a: dict(counts=cnt(v), **usable(v)) for a, v in by(lambda r: r["ownership_state"]).items()}, by_clip={a: dict(counts=cnt(v), **usable(v)) for a, v in by(lambda r: r["clip"]).items()},
               by_reason={a: dict(counts=cnt(v), n_items=len(v)) for a, v in sorted(byrs.items())}, by_reason_family={a: dict(counts=cnt(v), **usable(v)) for a, v in sorted(byfam.items())},
               population_weighted=dict(usable_frac=(num / den if den else None), contaminated_frac=(cnum / den if den else None), note="descriptive, cell weights N_cell/n_judgeable; no CI"),
               by_identity=({a: cnt(v) for a, v in by(lambda r: r["identity"]).items()}), merge_guard_flagged=[dict(review_id=r["review_id"], verdict=r["verdict"], ownership_state=r["ownership_state"]) for r in rows if r["merge_guard"] in ("True", True)],
               contaminated_cases=[dict(review_id=r["review_id"], clip=r["clip"], frame=int(r["frame"]), shot=r["shot"], identity=r["identity"], ownership_state=r["ownership_state"], reasons=r["own_reasons"], note=r["note"]) for r in rows if r["verdict"] == "CONTAMINATED"], all_items=rows)
    json.dump(res, open(out, "w"), indent=1, sort_keys=True, default=str); print(json.dumps({k: res[k] for k in ("overall", "overall_usable_contaminated", "by_ownership_state", "population_weighted")}, indent=1, default=str))
if __name__ == "__main__": main(*sys.argv[1:6])
