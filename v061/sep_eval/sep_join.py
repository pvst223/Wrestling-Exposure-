#!/usr/bin/env python3
"""SEPARATED-BODY EVALUATION V1 join (single hidden-key join AFTER all reviewer files are frozen). Mechanical; no post-hoc rules. Usage: sep_join.py <key.csv> <primary.csv> <owner.csv> <out.json> [claude.csv]
Reviewer file columns: item_id, box_person, separation_audit, judgeable(YES/NO), landmarks_other_person ("5;7"), bones_other_person ("5-7;6-8"), landmarks_off_body, note.
Derived frame verdict (never typed by reviewers): NOT_JUDGEABLE if judgeable=NO or fewer than 3 landmarks drawn; WRONG_BODY if any other-person landmark/bone; OFF_BODY_ONLY if only off-body landmarks; else OWNERSHIP_CORRECT."""
import collections, csv, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "impl"))
import sep_stats as S
BOX = ("WRESTLER", "REFEREE", "SPECTATOR_OTHER", "MULTIPLE_PERSONS_IN_BOX", "CANNOT_TELL"); AUD = ("SEPARATED", "OTHER_BODY_TOUCHING_OVERLAPPING", "CANNOT_TELL")
def _idx(s):
    s = (s or "").strip(); out = [int(x) for x in s.split(";") if x.strip()]; assert all(0 <= i <= 16 for i in out), s; return out
def _bones(s):
    s = (s or "").strip(); out = []
    for x in s.split(";"):
        if x.strip(): a, b = x.strip().split("-"); out.append((int(a), int(b)))
    return out
def load_reviewer(path, ids):
    rows = {r["item_id"]: r for r in csv.DictReader(open(path, newline=""))}; assert set(rows) >= set(ids), "missing items: %s" % sorted(set(ids) - set(rows))[:5]; out = {}
    for i in ids:
        r = rows[i]; assert r["box_person"] in BOX and r["separation_audit"] in AUD and r["judgeable"] in ("YES", "NO"), (i, r); out[i] = dict(r, lo=_idx(r["landmarks_other_person"]), bo=_bones(r["bones_other_person"]), off=_idx(r["landmarks_off_body"]))
    return out
def verdict(rv, n_drawn):
    if rv["judgeable"] == "NO" or n_drawn < 3: return "NOT_JUDGEABLE"
    if rv["lo"] or rv["bo"]: return "WRONG_BODY"
    if rv["off"]: return "OFF_BODY_ONLY"
    return "OWNERSHIP_CORRECT"
def stat_block(items, ver, rv, flt=lambda k: True):
    its = [k for k in items if flt(k)]; V = collections.Counter(ver[k["item_id"]] for k in its); jud = [k for k in its if ver[k["item_id"]] != "NOT_JUDGEABLE"]; wrong = [k for k in jud if ver[k["item_id"]] == "WRONG_BODY"]
    aud = [k for k in its if rv[k["item_id"]]["separation_audit"] != "CANNOT_TELL"]; auo = [k for k in aud if rv[k["item_id"]]["separation_audit"] == "OTHER_BODY_TOUCHING_OVERLAPPING"]
    return dict(n=len(its), counts=dict(V), judgeable=len(jud), wrong_body=len(wrong), wrong_body_frac=(len(wrong) / len(jud) if jud else None), wrong_body_ci95=S.cp(len(wrong), len(jud)), off_body_only=V.get("OFF_BODY_ONLY", 0),
                not_judgeable=V.get("NOT_JUDGEABLE", 0), shots_with_judgeable=len({(k["clip"], k["shot"]) for k in jud}), clips_with_judgeable=len({k["clip"] for k in jud}), shots_with_wrong=len({(k["clip"], k["shot"]) for k in wrong}),
                audit_answered=len(aud), audit_other=len(auo), audit_cannot_tell=len(its) - len(aud), box_person=dict(collections.Counter(rv[k["item_id"]]["box_person"] for k in its)))
def kappa(a, b):
    n = len(a); cats = sorted(set(a) | set(b)); po = sum(x == y for x, y in zip(a, b)) / n if n else None
    if not n: return None, None
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats); return po, ((po - pe) / (1 - pe) if pe < 1 else 1.0)
def main(key_csv, primary, owner, out, claude=None):
    key = list(csv.DictReader(open(key_csv, newline=""))); ids = [k["item_id"] for k in key]; items = [dict(k, n_drawn=int(k["n_drawn"])) for k in key]; res = dict(label="SEPARATED-BODY EVALUATION V1: tests anatomical body ownership of the assigned detection under the pre-specified separated-body condition ONLY. Not validation of joint localization, temporal accuracy, identity, exposure, workload or generalization. Development-only, ANNOTATION-PROVISIONAL.", reviewers={})
    revs = dict(primary=load_reviewer(primary, ids), owner=load_reviewer(owner, ids)); 
    if claude: revs["claude_sensitivity"] = load_reviewer(claude, ids)
    ver = {}
    for name, rv in revs.items():
        ver[name] = {k["item_id"]: verdict(rv[k["item_id"]], k["n_drawn"]) for k in items}; E = lambda k: k["stratum"] == "ELIGIBLE_ASSIGNED"; N = lambda k: k["stratum"] == "INELIGIBLE_ASSIGNED"
        eb = stat_block(items, ver[name], rv, E); dec = S.decide_reviewer(eb["judgeable"], eb["wrong_body"], eb["n"], eb["not_judgeable"], eb["shots_with_judgeable"], eb["clips_with_judgeable"], eb["shots_with_wrong"], eb["audit_answered"], eb["audit_other"])
        res["reviewers"][name] = dict(eligible=eb, decision=dec, contrast_ineligible=stat_block(items, ver[name], rv, N), sensitivity_margin25_eligible=stat_block(items, ver[name], rv, lambda k: E(k) and k["eligible25"] == "1"),
                                      sensitivity_margin10_eligible=stat_block(items, ver[name], rv, lambda k: E(k) and k["eligible10"] == "1"), by_clip={c: stat_block(items, ver[name], rv, lambda k, c=c: E(k) and k["clip"] == c) for c in sorted({k["clip"] for k in items})},
                                      identity_secondary_ANNOTATION_PROVISIONAL=dict(box_person_eligible=eb["box_person"], non_wrestler_emission=sum(1 for k in items if E(k) and rv[k["item_id"]]["box_person"] in ("REFEREE", "SPECTATOR_OTHER"))))
    both = [k for k in items if k["stratum"] == "ELIGIBLE_ASSIGNED" and ver["primary"][k["item_id"]] != "NOT_JUDGEABLE" and ver["owner"][k["item_id"]] != "NOT_JUDGEABLE"]
    a = [ver["primary"][k["item_id"]] == "WRONG_BODY" for k in both]; b = [ver["owner"][k["item_id"]] == "WRONG_BODY" for k in both]; po, kap = kappa(a, b)
    res["agreement_primary_vs_owner_eligible_both_judgeable"] = dict(n=len(both), raw=po, kappa_wrong_body=kap)
    res["final"] = dict(outcome=S.combine_humans(res["reviewers"]["primary"]["decision"]["outcome"], res["reviewers"]["owner"]["decision"]["outcome"]), rule="less favourable of the two human reviewers binds; never pooled or averaged; Claude sensitivity never decides")
    json.dump(res, open(out, "w"), indent=1, sort_keys=True, default=str); print(json.dumps(res["final"]))
if __name__ == "__main__": main(*sys.argv[1:5], *(sys.argv[5:6]))
