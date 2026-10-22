"""BUILD-only diagnostics for Rule V1 (private inputs, aggregates out). Reads: BUILD manifest, shot_frames (BUILD ids only), effective BUILD labels, frozen detections (box/conf/shape only).
Refuses to read any CHECK id. Usage: build_diagnostics.py --priv DIR --labels labels_build.csv --dets_clips DIR --dets_match PKL --out OUT.json"""
import argparse,csv,json,pickle,hashlib,collections,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import rule_v1
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
def main():
    ap=argparse.ArgumentParser(); [ap.add_argument("--"+k,required=True) for k in ("priv","labels","dets_clips","dets_match","out")]; ap.add_argument("--per_shot_private",default=None); a=ap.parse_args()
    man=list(csv.DictReader(open(os.path.join(a.priv,"inputs/manifest_build.csv"))))
    assert all(r["set"]=="build" for r in man) and len(man)==169
    ids={r["shot_id"]:r for r in man}
    fr={r["shot_id"]:(int(r["frame_start"]),int(r["frame_end"])) for r in csv.DictReader(open(os.path.join(a.priv,"inputs/shot_frames_private.csv"))) if r["shot_id"] in ids}
    assert len(fr)==169
    lab={r["shot_id"]:r for r in csv.DictReader(open(a.labels))}; assert set(lab)==set(ids)
    dets={}
    for s in sorted({r["source_id"] for r in man}):
        if s=="rr_balor_full":
            raw=pickle.load(open(a.dets_match,"rb"))
        else:
            raw=pickle.load(open(os.path.join(a.dets_clips,f"dets_{s}.pkl"),"rb"))
        dets[s]={f:(d["box"],d["conf"],d["shape"]) for f,d in raw.items()}
    cfg=rule_v1.load_cfg(); shots=[(sid,ids[sid]["source_id"],*fr[sid]) for sid in ids]
    res=rule_v1.classify_shots(shots,dets,cfg); dur={sid:float(ids[sid]["t_end_s"])-float(ids[sid]["t_start_s"]) for sid in ids}
    # P1 under the prospective calculation
    def p1(pred):
        num=den=0.0
        for r in res:
            ref=lab[r["shot_id"]]["label"]
            if ref=="UNKNOWN": continue
            d=dur[r["shot_id"]]; den+=d; num+=d*((pred(r)=="LIVE")!=(ref=="LIVE_ACTION"))
        return num,den,(num/den if den else None)
    n,d,p=p1(lambda r:r["rule_class"]); nb,db,pb=p1(lambda r:"LIVE")
    conf=collections.defaultdict(lambda:[0,0.0])
    for r in res:
        k=(lab[r["shot_id"]]["label"],r["rule_class"]); conf[k][0]+=1; conf[k][1]+=dur[r["shot_id"]]
    bysrc={}
    for s in sorted({r["source_id"] for r in man}):
        nn=dd=0.0
        for r in res:
            if r["source_id"]!=s: continue
            ref=lab[r["shot_id"]]["label"]
            if ref=="UNKNOWN": continue
            dsh=dur[r["shot_id"]]; dd+=dsh; nn+=dsh*((r["rule_class"]=="LIVE")!=(ref=="LIVE_ACTION"))
        bysrc[s]={"disagree_s":round(nn,3),"decidable_s":round(dd,3)}
    cls_dur=collections.Counter(); cls_n=collections.Counter()
    for r in res: cls_dur[r["rule_class"]]+=dur[r["shot_id"]]; cls_n[r["rule_class"]]+=1
    out={"set":"build","n_shots":len(res),"rule_config_sha256":sha(os.path.join(rule_v1.HERE,"rule_v1_config.json")),
     "rule_class_counts":dict(cls_n),"rule_class_duration_s":{k:round(v,3) for k,v in cls_dur.items()},
     "confusion_ref_by_rule":{f"{k[0]}|{k[1]}":{"n":v[0],"s":round(v[1],3)} for k,v in sorted(conf.items())},
     "P1_rule_V1":{"disagree_s":round(n,3),"decidable_s":round(d,3),"fraction":p},
     "P1_all_LIVE_baseline":{"disagree_s":round(nb,3),"decidable_s":round(db,3),"fraction":pb},
     "P1_by_source_rule_V1":bysrc,
     "no_feature_shots":sum(1 for r in res if r["features"] is None)}
    json.dump(out,open(a.out,"w"),indent=1,sort_keys=True)
    if a.per_shot_private:
        with open(a.per_shot_private,"w",newline="") as f:
            w=csv.writer(f); w.writerow(["shot_id","dur_s","ref","rule","why","n_sampled","F1","F2"])
            for r in res:
                ft=r["features"] or {}
                w.writerow([r["shot_id"],round(dur[r["shot_id"]],3),lab[r["shot_id"]]["label"],r["rule_class"],r["why"],ft.get("n_sampled"),ft.get("F1_frac_ge2"),ft.get("F2_h_max_med")])
    print(json.dumps(out,indent=1,sort_keys=True))
if __name__=="__main__": main()
