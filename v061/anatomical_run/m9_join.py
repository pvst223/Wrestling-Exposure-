#!/usr/bin/env python3
"""M9 join + descriptive analysis. Run exactly ONCE, after verdicts are frozen. Joins frozen verdicts with the hidden key and (for withheld frames) ownership state/reason from the private ROWS pickles."""
import collections, csv, json, os, pickle, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..")); sys.path.insert(0, os.path.join(REPO, "v061", "anatomical", "impl")); import metrics
V = ("CORRECT", "PARTIAL_BUT_USABLE", "CONTAMINATED", "NOT_JUDGEABLE")
def main(priv, verdicts_json, out, expect=60):
    if os.path.exists(out): raise SystemExit("write-once")
    ver = json.load(open(verdicts_json)); key = list(csv.DictReader(open(os.path.join(priv, "M9_HIDDEN_KEY.csv"), newline=""))); assert len(ver) == len(key) == int(expect) and all(v["verdict"] in V for v in ver.values())
    cache = {}; rows = []
    for k in key:
        c = k["clip"]
        if c not in cache: cache[c] = {(r["tracklet"], int(r["frame"])): r for r in pickle.load(open(os.path.join(priv, f"ROWS_{c}.pkl"), "rb"))["rows"]}
        r = cache[c][(k["tracklet"], int(k["frame"]))]
        rows.append(dict(review_id=k["review_id"], clip=c, tracklet=k["tracklet"], frame=int(k["frame"]), stratum=k["stratum"], record_class=r["record_class"], ownership_state=r["ownership_state"], own_reasons=r["own_reasons"], merge_guard_would_trigger=r["merge_guard_would_trigger"], verdict=ver[k["review_id"]]["verdict"], note=ver[k["review_id"]].get("note", "")))
    cnt = lambda rs: dict(collections.Counter(r["verdict"] for r in rs))
    A = [r for r in rows if r["stratum"] == "ASSIGNED"]; W = [r for r in rows if r["stratum"] == "WITHHELD"]
    byreason = collections.defaultdict(list)
    for r in W: byreason[r["ownership_state"]].append(r)
    jw = [r for r in W if r["verdict"] != "NOT_JUDGEABLE"]; ja = [r for r in A if r["verdict"] != "NOT_JUDGEABLE"]
    uw = sum(1 for r in jw if r["verdict"] in ("CORRECT", "PARTIAL_BUT_USABLE")); ca = sum(1 for r in ja if r["verdict"] == "CONTAMINATED")
    res = dict(label="M9 single-reviewer (Claude, non-independent) ANNOTATION-PROVISIONAL; exploratory; NOT validated accuracy", n=len(rows), overall=cnt(rows), assigned=cnt(A), withheld=cnt(W),
               withheld_by_ownership_state={k: cnt(v) for k, v in byreason.items()}, withheld_items=[dict(review_id=r["review_id"], clip=r["clip"], frame=r["frame"], record_class=r["record_class"], ownership_state=r["ownership_state"], reasons=r["own_reasons"], verdict=r["verdict"], note=r["note"]) for r in W],
               contaminated_assigned=[dict(r) for r in A if r["verdict"] == "CONTAMINATED"],
               withheld_usable=dict(k=uw, n_judgeable=len(jw), frac=(uw / len(jw) if jw else None), ci95=list(metrics.cp_ci(uw, len(jw))), not_judgeable=len(W) - len(jw)),
               assigned_contaminated=dict(k=ca, n_judgeable=len(ja), frac=(ca / len(ja) if ja else None), ci95=list(metrics.cp_ci(ca, len(ja))), not_judgeable=len(A) - len(ja)),
               merge_guard_flagged_items=[dict(review_id=r["review_id"], stratum=r["stratum"], verdict=r["verdict"]) for r in rows if r["merge_guard_would_trigger"]], all_items=rows)
    json.dump(res, open(out, "w"), indent=1, sort_keys=True, default=str); print(json.dumps({k: res[k] for k in ("overall", "assigned", "withheld", "withheld_by_ownership_state", "withheld_usable", "assigned_contaminated")}, indent=1))
if __name__ == "__main__": main(*sys.argv[1:5])
