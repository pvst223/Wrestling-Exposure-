"""Deterministic adjudication (v2, unit-level schema). Joins committed blind labels to system decisions; writes decisions.csv (input of phase1_metrics v2) and adjudication.csv (one row per UNIT with a false accept, classification left blank for a human: system_error / reviewer_error / ambiguous; nothing is auto-resolved).
Refuses to run unless the label commitment hash verifies.
Blind labels CSV (annotation vocabulary): clip_id,tracklet_id,shot,label ; label in TARGET_A, TARGET_B, REFEREE, STAFF, SPECTATOR, UNLABELABLE. (Legacy first-pass vocabulary person_class/wrestler_id is also accepted via legacy=True.)
System CSV: clip_id,tracklet_id,frame,accepted_role (wrestler id or empty),best_role,score.
gallery_json: {clip_id: {"A": wrestler_id, "B": wrestler_id}}: the key linking anonymous Target A/B to named wrestlers; it is held outside the annotator package.
UNLABELABLE tracklets are excluded and counted."""
import csv,sys,json,collections
sys.path.insert(0,".")
import blind_sample as BS
VOC={"REFEREE":"REFEREE","STAFF":"STAFF","SPECTATOR":"SPECTATOR"}
def truth_of(lab,gal,clip,legacy):
    if legacy:
        pc=lab["person_class"]
        if pc=="UNLABELABLE": return None
        return lab["wrestler_id"] if pc=="WRESTLER" else {"RINGSIDE_STAFF":"STAFF"}.get(pc,pc)
    l=lab["label"]
    if l=="UNLABELABLE": return None
    if l=="TARGET_A": return gal[clip]["A"]
    if l=="TARGET_B": return gal[clip]["B"]
    if l in VOC: return VOC[l]
    raise SystemExit("unknown label "+l)
def run(labels_csv,system_csv,gallery_json,out_decisions,out_adj,legacy=False):
    if not BS.verify_commit(labels_csv): raise SystemExit("LABEL COMMITMENT MISMATCH: labels changed after commitment, HALT")
    gal=json.load(open(gallery_json)); L={(r["clip_id"],r["tracklet_id"]):r for r in csv.DictReader(open(labels_csv))}
    rows=[]; unl=0
    for r in csv.DictReader(open(system_csv)):
        k=(r["clip_id"],r["tracklet_id"]); lab=L.get(k)
        if lab is None: unl+=1; continue
        t=truth_of(lab,gal,r["clip_id"],legacy)
        if t is None: unl+=1; continue
        rows.append(dict(clip_id=r["clip_id"],shot=lab["shot"],tracklet_id=r["tracklet_id"],frame=r["frame"],truth_id=t,accepted_role=r.get("accepted_role",""),best_role=r.get("best_role",""),score=r.get("score","")))
    with open(out_decisions,"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["clip_id","shot","tracklet_id","frame","truth_id","accepted_role","best_role","score"]); w.writeheader(); w.writerows(rows)
    import phase1_metrics as M
    U=M.units_of(rows); dis=[(k,u) for k,u in U.items() if u["n_false"]>0]
    with open(out_adj,"w",newline="") as f:
        w=csv.writer(f); w.writerow(["clip_id","shot","truth_id","n_detections","n_false_accepted","n_tracklets","classification"])
        for (c,s,t),u in dis: w.writerow([c,s,t,u["n_det"],u["n_false"],len(u["tracklets"]),""])
    return len(rows),len(dis),unl
