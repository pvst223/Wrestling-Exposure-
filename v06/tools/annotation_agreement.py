"""Deterministic reconciliation/agreement for the independent annotation (implements PREREGISTRATION_V3 section 2; no tuning, nothing auto-resolved).
usage: annotation_agreement.py returned.csv annotation_template.csv annotation_key.json firstpass_labels.csv reserve.json out.json out_disagreements.csv
Steps: (1) record SHA-256 of the returned CSV BEFORE anything else (and refuse if the original file is modified later: the hash is written to out.json); (2) validate against the template: identical item_ids and order, one permitted label each (TARGET_A, TARGET_B, REFEREE, STAFF, SPECTATOR, UNLABELABLE), clip_code/image unchanged; (3) map first-pass labels to the same vocabulary through the key; (4) report tracklet-level raw agreement, Cohen's kappa including UNLABELABLE, kappa excluding items either annotator marked UNLABELABLE, unit-level agreement on reserved units, per-label confusion counts, governing gate = kappa INCLUDING UNLABELABLE (>= 0.60 means only that the gate is passed, NOT validation); kappa excluding is a required secondary diagnostic; (5) write every disagreement to a CSV with an empty 'classification' column."""
import csv,json,hashlib,sys,collections
PERMITTED=("TARGET_A","TARGET_B","REFEREE","STAFF","SPECTATOR","UNLABELABLE")
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
def kappa(a,b):
    n=len(a)
    if n==0: return None
    po=sum(x==y for x,y in zip(a,b))/n; ca,cb=collections.Counter(a),collections.Counter(b); pe=sum(ca[k]*cb[k] for k in set(ca)|set(cb))/(n*n)
    return None if pe==1 else (po-pe)/(1-pe)
def run(returned,template,key,firstpass,reserve,out_json,out_dis):
    h=sha(returned); T=list(csv.DictReader(open(template))); Rt=list(csv.DictReader(open(returned)))
    if [r["item_id"] for r in T]!=[r["item_id"] for r in Rt]: raise SystemExit("ITEM IDS/ORDER CHANGED: reject")
    for a,b in zip(T,Rt):
        if a["clip_code"]!=b["clip_code"] or a["image"]!=b["image"]: raise SystemExit("clip_code/image changed for "+a["item_id"])
        if b["label"] not in PERMITTED: raise SystemExit(f"invalid/missing label for {b['item_id']}: {b['label']!r}")
    K=json.load(open(key)); gal=K["gallery"]; i2t=K["item_to_tracklet"]; fp={r["tid"]:r for r in csv.DictReader(open(firstpass))}
    def fp_label(tid):
        r=fp[tid]; c=r["person_class"]; clip=tid.split(":")[0]
        if c=="UNLABELABLE": return "UNLABELABLE"
        if c=="WRESTLER": return "TARGET_A" if r["wrestler_id"]==gal[clip]["A"] else ("TARGET_B" if r["wrestler_id"]==gal[clip]["B"] else "UNLABELABLE")
        return {"REFEREE":"REFEREE","RINGSIDE_STAFF":"STAFF","SPECTATOR":"SPECTATOR"}.get(c,"UNLABELABLE")
    ind=[r["label"] for r in Rt]; dev=[fp_label(i2t[r["item_id"]]) for r in Rt]
    n=len(ind); raw=sum(x==y for x,y in zip(ind,dev))/n
    keep=[i for i in range(n) if ind[i]!="UNLABELABLE" and dev[i]!="UNLABELABLE"]
    k_in=kappa(ind,dev); k_ex=kappa([ind[i] for i in keep],[dev[i] for i in keep])
    conf=collections.Counter(zip(dev,ind))
    # unit-level: units = (clip, shot, label-as-identity/class) built from each labelling; reserve units must be present with the same unit key
    tr={}
    import glob
    for p in glob.glob("frozen/tracklets/*.json"):
        for t in json.load(open(p)): tr[t["tid"]]=t
    def units(labels):
        U=collections.defaultdict(set)
        for r,l in zip(Rt,labels):
            if l=="UNLABELABLE": continue
            t=tr[i2t[r["item_id"]]]; U[(t["clip"],t["shot"],l)].add(r["item_id"])
        return U
    Ui,Ud=units(ind),units(dev); res=json.load(open(reserve)); agree=0; rows=[]
    for u in res:
        clip=u["clip"]; lab=u["key"]
        l={gal[clip]["A"]:"TARGET_A",gal[clip]["B"]:"TARGET_B","REFEREE":"REFEREE","RINGSIDE_STAFF":"STAFF","STAFF":"STAFF","SPECTATOR":"SPECTATOR"}.get(lab)
        ok=l is not None and (clip,u["shot"],l) in Ui; agree+=ok; rows.append((clip,u["shot"],lab,ok))
    out={"returned_csv_sha256":h,"n_items":n,"raw_agreement_tracklet_level":raw,"kappa_including_unlabelable":k_in,"kappa_excluding_unlabelable_either":k_ex,"n_items_excluding_unlabelable_either":len(keep),
      "unit_level_agreement_on_reserved_units":{"n_reserved_units":len(res),"units_present_in_independent_labels":agree,"fraction":agree/len(res) if res else None},
      "confusion_firstpass_rows_vs_independent_cols":{f"{a}|{b}":v for (a,b),v in sorted(conf.items())},
      "reliability_gate":{"governing_statistic":"tracklet-level Cohen's kappa INCLUDING UNLABELABLE (clarification C1, AUDIT_LEDGER.jsonl)","kappa_including_unlabelable":k_in,"governing_gate_passed_kappa_ge_0.60":(k_in is not None and k_in>=0.60),"status_if_not_passed":"PROVISIONAL: primary outcome cannot exceed MODIFY","secondary_required_diagnostic_kappa_excluding_unlabelable_either":k_ex,"note":"passing the gate only means the prespecified reliability gate was passed; it is NOT validation of the annotation"}}
    json.dump(out,open(out_json,"w"),indent=1)
    with open(out_dis,"w",newline="") as f:
        w=csv.writer(f); w.writerow(["item_id","clip_code","firstpass_label","independent_label","classification"])
        for r,d,i in zip(Rt,dev,ind):
            if d!=i: w.writerow([r["item_id"],r["clip_code"],d,i,""])
    return out
if __name__=="__main__": print(json.dumps(run(*sys.argv[1:8]),indent=1))
