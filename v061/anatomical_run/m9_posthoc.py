#!/usr/bin/env python3
"""Post-hoc descriptive breakdown of the M9 join (NOT pre-registered): identity-state composition of the withheld stratum, reason x verdict, non-wrestler (by reviewer note) counts. Reads the join result and private ROWS pickles; writes a write-once JSON."""
import collections, json, os, pickle, sys
P = "/home/claude/proj/v061_anat_private/"; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "anatomical", "impl")); import metrics
R = json.load(open(P + "M9_JOIN_RESULT.json")); cache = {}
def row(i):
    c = i["clip"]
    if c not in cache: cache[c] = {(r["tracklet"], r["frame"]): r for r in pickle.load(open(P + f"ROWS_{c}.pkl", "rb"))["rows"]}
    return cache[c][(i["tracklet"], i["frame"])]
W = [i for i in R["all_items"] if i["stratum"] == "WITHHELD"]; A = [i for i in R["all_items"] if i["stratum"] == "ASSIGNED"]
by_id = collections.defaultdict(collections.Counter)
for i in W: by_id[row(i)["identity_state_passthrough"]][i["verdict"]] += 1
acc = [i for i in W if row(i)["identity_state_passthrough"] in ("ACCEPT_A", "ACCEPT_B")]; ju = [i for i in acc if i["verdict"] != "NOT_JUDGEABLE"]; u = sum(1 for i in ju if i["verdict"] in ("CORRECT", "PARTIAL_BUT_USABLE"))
rv = collections.defaultdict(collections.Counter)
for i in W:
    for r in i["own_reasons"]: rv[r][i["verdict"]] += 1
sp = lambda n: any(w in n.lower() for w in ("spectator", "woman", "referee", "crowd"))
out = dict(label="POST-HOC descriptive; not pre-registered; single non-independent reviewer; ANNOTATION-PROVISIONAL", withheld_by_identity_state={k: dict(v) for k, v in by_id.items()},
           withheld_identity_ACCEPT=dict(n=len(acc), usable=u, n_judgeable=len(ju), ci95=list(metrics.cp_ci(u, len(ju))), contaminated=sum(1 for i in acc if i["verdict"] == "CONTAMINATED")),
           reason_x_verdict={k: dict(v) for k, v in sorted(rv.items())}, non_wrestler_by_reviewer_note=dict(total=sum(1 for i in R["all_items"] if sp(i["note"])), withheld=sum(1 for i in W if sp(i["note"])), assigned=sum(1 for i in A if sp(i["note"]))),
           per_clip_stratum={f"{k[0]}|{k[1]}": v for k, v in collections.Counter((i["clip"], i["stratum"]) for i in R["all_items"]).items()},
           assigned_by_class_verdict={f"{k[0]}|{k[1]}": v for k, v in collections.Counter((i["record_class"], i["verdict"]) for i in A).items()})
p = os.path.join(HERE, "M9_POSTHOC_V1.json")
if os.path.exists(p): raise SystemExit("write-once")
json.dump(out, open(p, "w"), indent=1, sort_keys=True); print(json.dumps({k: out[k] for k in ("withheld_by_identity_state", "withheld_identity_ACCEPT", "non_wrestler_by_reviewer_note")}, indent=1))
