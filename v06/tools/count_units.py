"""Measured independent-unit counts from first-pass tracklet labels (non-independent).
labels CSV: tid,person_class,wrestler_id,multi_person_flag,annotator,independent ; person_class in WRESTLER|REFEREE|RINGSIDE_STAFF|SPECTATOR|OTHER_WRESTLER_UNNAMED|UNLABELABLE.
Unit keys: WRESTLER (clip,shot,wrestler_id); others (clip,shot,class). Uses frozen splits and manifest. Seed exclusions are NOT yet applied (seeds are selected at bake-off time). Output JSON + printed table."""
import csv,json,sys,collections
from scipy.stats import beta
def ub(k,n): return None if n==0 else float(1.0 if k==n else beta.ppf(0.975,k+1,n-k))
def run(labels,splits,manifest,tracklet_glob):
    import glob
    T={}
    for p in glob.glob(tracklet_glob):
        for t in json.load(open(p)): T[t["tid"]]=t
    sp={r["clip_id"]:r["split"] for r in csv.DictReader(open(splits))}; roles={r["clip_id"]:(r["wrestler_id_A"],r["wrestler_id_B"]) for r in csv.DictReader(open(manifest))}
    units=collections.defaultdict(set); trk=collections.Counter(); unl=0
    for r in csv.DictReader(open(labels)):
        t=T[r["tid"]]; c=r["person_class"]
        if c=="UNLABELABLE": unl+=1; continue
        key=(t["clip"],t["shot"],r["wrestler_id"] if c=="WRESTLER" else c); units[key].add(r["tid"]); trk[(t["clip"],c if c!="WRESTLER" else "WRESTLER:"+("TARGETROLE" if r["wrestler_id"] in roles[t["clip"]] else "OTHER_NAMED_NOT_A_ROLE"))]+=1
    out={"by_clip":{},"by_split":{}}
    for (clip,shot,k),tids in units.items():
        d=out["by_clip"].setdefault(clip,dict(split=sp[clip],target_units=0,other_named_negative_units=0,unnamed_other_wrestler_units=0,referee_units=0,staff_units=0,spectator_units=0,tracklets=0,shots_with_any_unit=set()))
        d["tracklets"]+=len(tids); d["shots_with_any_unit"].add(shot)
        if k in roles[clip]: d["target_units"]+=1
        elif k=="OTHER_WRESTLER_UNNAMED": d["unnamed_other_wrestler_units"]+=1
        elif k=="REFEREE": d["referee_units"]+=1
        elif k=="RINGSIDE_STAFF": d["staff_units"]+=1
        elif k=="SPECTATOR": d["spectator_units"]+=1
        else: d["other_named_negative_units"]+=1   # named wrestler not among the clip's two roles
    for clip,d in out["by_clip"].items():
        d["shots_with_any_unit"]=len(d["shots_with_any_unit"]); d["other_named_negative_units"]+=d["target_units"]  # each role's unit is the other role's negative (role-relative equivalence)
    for clip,d in out["by_clip"].items():
        s=out["by_split"].setdefault(d["split"],collections.Counter())
        for k,v in d.items():
            if k!="split": s[k]+=v
    out["by_split"]={s:dict(v) for s,v in out["by_split"].items()}
    out["pooled"]={k:sum(v[k] for v in out["by_split"].values()) for k in next(iter(out["by_split"].values()))}
    def bounds(d): return {k:{"n":d[k],"upper95_if_0_errors":ub(0,d[k]),"upper95_if_1_error":ub(1,d[k]),"descriptive_only_n_lt_15":d[k]<15} for k in ("target_units","other_named_negative_units","unnamed_other_wrestler_units","referee_units","staff_units","spectator_units")}
    out["bounds_by_split"]={s:bounds(v) for s,v in out["by_split"].items()}; out["bounds_pooled"]=bounds(out["pooled"]); out["unlabelable_tracklets"]=unl; out["tracklet_class_counts"]={f"{a}|{b}":v for (a,b),v in trk.items()}
    return out
if __name__=="__main__":
    o=run(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]); json.dump(o,open(sys.argv[5],"w"),indent=1); print(json.dumps({"by_split":o["by_split"],"pooled":o["pooled"]},indent=1))
