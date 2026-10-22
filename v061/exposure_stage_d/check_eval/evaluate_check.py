"""Frozen Stage-D CHECK evaluation of Rule V1.1. Inputs: exported CHECK labels + marks, private predictions CSV, CHECK manifest.
Reference adequacy FIRST: if reference-UNKNOWN > 10% of CHECK duration (strict >) the output contains reference distributions ONLY (REFERENCE_INCONCLUSIVE).
Integer-millisecond arithmetic. No tuning, no alternative metrics. Usage: evaluate_check.py --labels L --marks M --pred P --manifest MAN --out OUT.json"""
import argparse,csv,json,hashlib,collections
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
def ms(a,b): return round((float(b)-float(a))*1000)
def s(x): return round(x/1000,3)
def main():
    ap=argparse.ArgumentParser(); [ap.add_argument("--"+k,required=True) for k in ("labels","marks","pred","manifest","out")]; ap.add_argument("--expect_pred_sha256",default=""); ap.add_argument("--manifest_sha256",default="f1b8664e0238a87c2e8a0eee34f50be5f0ebdb62e78852b5f1c9bf8d43a5517e"); a=ap.parse_args()
    assert sha(a.manifest)==a.manifest_sha256,"CHECK manifest hash mismatch"
    if a.expect_pred_sha256: assert sha(a.pred)==a.expect_pred_sha256,"predictions file differs from the pre-committed hash"
    man={r["shot_id"]:r for r in csv.DictReader(open(a.manifest))}; lab={r["shot_id"]:r for r in csv.DictReader(open(a.labels))}
    assert set(lab)==set(man)
    dur={k:ms(m["t_start_s"],m["t_end_s"]) for k,m in man.items()}; tot=sum(dur.values())
    out={"n_shots":len(man),"total_s":s(tot),"input_sha256":{"manifest":sha(a.manifest),"labels":sha(a.labels),"marks":sha(a.marks),"predictions":sha(a.pred)}}
    cnt=collections.Counter(); d=collections.Counter(); ur=collections.Counter(); urd=collections.Counter(); fl=collections.Counter()
    for k,r in lab.items():
        cnt[r["label"]]+=1; d[r["label"]]+=dur[k]
        if r["label"]=="UNKNOWN": ur[r["unknown_reason"]]+=1; urd[r["unknown_reason"]]+=dur[k]
        for f in filter(None,r.get("flags","").split(";")): fl[f]+=1
    unk=d["UNKNOWN"]; out["reference"]={"count_by_label":dict(cnt),"duration_s_by_label":{k:s(v) for k,v in d.items()},"unknown_by_reason_count":dict(ur),"unknown_by_reason_s":{k:s(v) for k,v in urd.items()},"flags":dict(fl),"match_marks":list(csv.DictReader(open(a.marks)))}
    out["reference_unknown_fraction_exact"]=f"{unk}/{tot} ms"; out["U_ref_CHECK"]=unk/tot
    if unk*10>tot:
        out["decision"]="REFERENCE_INCONCLUSIVE"; out["note"]="reference UNKNOWN > 10% of CHECK duration (frozen rule). No classifier result computed or reported."
        json.dump(out,open(a.out,"w"),indent=1,sort_keys=True); print(json.dumps(out,indent=1,sort_keys=True)); return
    pred={r["shot_id"]:r for r in csv.DictReader(open(a.pred))}; assert set(pred)==set(man)
    rc=collections.Counter(); rd=collections.Counter()
    for k,r in pred.items(): rc[r["rule_class"]]+=1; rd[r["rule_class"]]+=dur[k]
    out["classifier"]={"count_by_class":dict(rc),"duration_s_by_class":{k:s(v) for k,v in rd.items()},"no_features_cases":sum(1 for r in pred.values() if r["why"]=="NO_FEATURES")}
    conf={}
    for k in man: c=(lab[k]["label"],pred[k]["rule_class"]); conf.setdefault(c,[0,0]); conf[c][0]+=1; conf[c][1]+=dur[k]
    out["confusion_ref_by_rule"]={f"{a_}|{b_}":{"n":v[0],"s":s(v[1])} for (a_,b_),v in sorted(conf.items())}
    den=num=base=0; err=collections.Counter()
    for k in man:
        ref=lab[k]["label"]
        if ref=="UNKNOWN": continue
        den+=dur[k]; live_ref=ref=="LIVE_ACTION"; live_rule=pred[k]["rule_class"]=="LIVE"
        if live_ref!=live_rule: num+=dur[k]; err[f"ref {ref} -> rule {pred[k]['rule_class']}"]+=dur[k]
        if not live_ref: base+=dur[k]
    out["P1"]={"numerator_s":s(num),"denominator_s":s(den),"fraction":num/den,"exceeds_20pct":num*5>den,"error_contribution_s":{k:s(v) for k,v in err.items()}}
    out["all_LIVE_comparator"]={"numerator_s":s(base),"denominator_s":s(den),"fraction":base/den}
    lo=rd["LIVE"]; hi=lo+rd["UNKNOWN"]; tref=d["LIVE_ACTION"]
    out["P2_descriptive_single_segment"]={"T_live_ref_s":s(tref),"T_live_lo_s":s(lo),"T_live_hi_s":s(hi),"inside_interval":lo<=tref<=hi,"numerator":int(lo<=tref<=hi),"denominator":1,
        "note":"design P2 is match-level (>=90% of evaluable matches); CHECK is one partial segment so match-level P2 is NOT_EVALUABLE; interval inclusion on the CHECK set is reported descriptively"}
    leak=sum(dur[k] for k in man if lab[k]["label"]=="REPLAY" and pred[k]["rule_class"] in ("LIVE","UNKNOWN"))
    if d["REPLAY"]==0: out["P3"]={"status":"NOT_EVALUABLE","reason":"no reference REPLAY material in CHECK","replay_in_T_live_hi_s":0.0,"T_live_hi_s":s(hi)}
    else: out["P3"]={"numerator_s":s(leak),"denominator_s":s(hi),"fraction":(leak/hi if hi else None),"exceeds_15pct":(leak*100>15*hi if hi else None)}
    out["P4_descriptive_single_segment"]={"classifier_unknown_s":s(rd["UNKNOWN"]),"check_total_s":s(tot),"fraction":rd["UNKNOWN"]/tot,"within_15pct":rd["UNKNOWN"]*100<=15*tot,
        "note":"design P4 is match-level (>=80% of matches); CHECK is one partial segment; classifier UNKNOWN is distinct from reference UNKNOWN"}
    p3=out["P3"]
    if out["P1"]["exceeds_20pct"] or (p3.get("exceeds_15pct") is True): out["decision"]="STOP"; out["decision_reason"]="P1>20%" if out["P1"]["exceeds_20pct"] else "P3>15%"
    elif p3.get("status")=="NOT_EVALUABLE": out["decision"]="NO_STOP_TRIGGER_P3_NOT_EVALUABLE"; out["decision_reason"]="P1<=20% and P3 not evaluable: CONTINUE determination returned to the reviewer"
    else: out["decision"]="CONTINUE"; out["decision_reason"]="P1<=20% and P3<=15% (futility gate survived; not validation)"
    json.dump(out,open(a.out,"w"),indent=1,sort_keys=True); print(json.dumps(out,indent=1,sort_keys=True))
if __name__=="__main__": main()
