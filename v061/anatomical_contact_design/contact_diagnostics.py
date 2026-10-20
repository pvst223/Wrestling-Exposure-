"""COUNTS-ONLY descriptive diagnostics on the burned M9C frames (development diagnosis; never confirmatory; nothing tuned, no classifier, no threshold chosen from it).
Question: how much information that already exists in the frozen pipeline rows could distinguish the contaminated frames? Reads private rows/keys/verdicts (not committed); writes aggregate counts only.
usage: python contact_diagnostics.py <private_dir> <out.json>   (private_dir = v061_anat_private with ROWS_*.pkl, M9C_VERDICTS_FROZEN_V1.json, m9c/M9C_HIDDEN_KEY.csv)"""
import json, csv, pickle, collections, sys, os
P, OUT = sys.argv[1], sys.argv[2]
V = json.load(open(os.path.join(P, "M9C_VERDICTS_FROZEN_V1.json"))); K = list(csv.DictReader(open(os.path.join(P, "m9c", "M9C_HIDDEN_KEY.csv"))))
R = {c: pickle.load(open(os.path.join(P, f"ROWS_{c}.pkl"), "rb"))["rows"] for c in {k["clip"] for k in K}}
def iou(a, b):
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]); i = max(0, x2 - x1) * max(0, y2 - y1)
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i; return i / u if u > 0 else 0.0
byf = {c: collections.defaultdict(list) for c in R}; bytr = {c: collections.defaultdict(list) for c in R}
for c, rs in R.items():
    for r in rs: byf[c][r["frame"]].append(r); bytr[c][r["tracklet"]].append(r)
rows = []
for k in K:
    c, f, t = k["clip"], int(k["frame"]), k["tracklet"]; v = V[k["review_id"]]
    me = [r for r in byf[c][f] if r["tracklet"] == t][0]; oth = [r for r in byf[c][f] if r["tracklet"] != t]
    mi = max([iou(me["box"], o["box"]) for o in oth], default=0.0); gap = None
    for r in sorted(bytr[c][t], key=lambda r: -r["frame"]):
        if r["frame"] >= f or r["ownership_state"] != "SINGLE_BODY_SUPPORTED": continue
        if any(iou(r["box"], o["box"]) > 0.05 for o in byf[c][r["frame"]] if o["tracklet"] != t): continue
        gap = f - r["frame"]; break
    rows.append(dict(stratum=k["stratum"], verdict=v["verdict"], contact=v["contact"], n_other=len(oth), max_iou=mi, gap=gap, guard=bool(me["merge_guard_would_trigger"])))
def summ(S):
    return dict(n=len(S), other_person_box_in_frame=sum(o["n_other"] > 0 for o in S), max_box_iou_ge_0_1=sum(o["max_iou"] >= 0.1 for o in S), max_box_iou_ge_0_3=sum(o["max_iou"] >= 0.3 for o in S),
                clean_anchor_exists=sum(o["gap"] is not None for o in S), clean_anchor_within_30_src_frames=sum(o["gap"] is not None and o["gap"] <= 30 for o in S),
                clean_anchor_within_90_src_frames=sum(o["gap"] is not None and o["gap"] <= 90 for o in S), merge_guard_diagnostic_flag=sum(o["guard"] for o in S))
cont = [o for o in rows if o["verdict"] == "CONTAMINATED"]; ok = [o for o in rows if o["verdict"] in ("CORRECT", "PARTIAL_BUT_USABLE")]
res = dict(label="burned M9C frames, descriptive counts only, development diagnosis; NOT confirmatory; no rule derived",
           definitions=dict(clean_anchor="an earlier stride-3 row of the SAME tracklet with ownership SINGLE_BODY_SUPPORTED and no other tracklet box with IoU>0.05 in that frame; gap in source frames",
                            caveat="rows only contain tracklets of the frozen pipeline (>=5 detections); other persons not tracked are invisible here, so n_other undercounts; 'contact' is Claude's subjective flag"),
           contaminated_all=summ(cont), contaminated_by_stratum={s: summ([o for o in cont if o["stratum"] == s]) for s in ("CONTROL_ASSIGNED", "RELEASED", "CONTROL_HARDVETO")},
           correct_or_partial_all=summ(ok), correct_or_partial_contact_yes=summ([o for o in ok if o["contact"] == "YES"]), correct_or_partial_contact_no=summ([o for o in ok if o["contact"] == "NO"]))
json.dump(res, open(OUT, "w"), indent=1, sort_keys=True); print(json.dumps(res["contaminated_all"]))
