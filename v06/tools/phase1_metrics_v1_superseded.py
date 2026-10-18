"""Phase 1 deterministic metric computation (no training code, no LLM-written numbers in reports).
Input: decisions CSV with columns: unit_id (tracklet id = independent unit), wrestler_id, truth_class (TARGET/OTHER_WRESTLER/REFEREE/STAFF/SPECTATOR/MULTI/OTHER), accepted (0/1), score (higher = more target-like).
Reports false-target-acceptance (FTA) by negative type with exact CIs over units, coverage on true targets, and a risk-coverage curve. Report writers must quote metrics.json only."""
import csv,json,sys,hashlib,collections
from scipy.stats import beta
def cp(k,n,a=0.05):
    if n==0: return (None,None)
    lo=0.0 if k==0 else beta.ppf(a/2,k,n-k+1); hi=1.0 if k==n else beta.ppf(1-a/2,k+1,n-k); return (float(lo),float(hi))
def unit_collapse(rows):
    """collapse frames to units: a unit counts as accepted-wrong if ANY of its frames is accepted (conservative); fraction accepted also reported"""
    u=collections.OrderedDict()
    for r in rows:
        k=r["unit_id"]; u.setdefault(k,{"truth":r["truth_class"],"wid":r["wrestler_id"],"n":0,"acc":0}); u[k]["n"]+=1; u[k]["acc"]+=int(r["accepted"])
    return u
def metrics(rows):
    out={"n_frames":len(rows)}; U=unit_collapse(rows); neg=collections.defaultdict(list); tgt=[]
    for k,v in U.items(): (tgt if v["truth"]=="TARGET" else neg[v["truth"]]).append(v)
    out["fta_by_negative_type"]={}
    for t,L in sorted(neg.items()):
        fr_n=sum(x["n"] for x in L); fr_a=sum(x["acc"] for x in L); ua=sum(1 for x in L if x["acc"]>0)
        out["fta_by_negative_type"][t]={"units":len(L),"units_with_any_accept":ua,"unit_FTA_95CI":cp(ua,len(L)),"frames":fr_n,"frames_accepted":fr_a,"frame_FTA":fr_a/fr_n if fr_n else None}
    allneg=[x for L in neg.values() for x in L]; ua=sum(1 for x in allneg if x["acc"]>0)
    out["fta_all_negatives_unit"]={"units":len(allneg),"units_with_any_accept":ua,"CI":cp(ua,len(allneg))}
    tf=sum(x["n"] for x in tgt); ta=sum(x["acc"] for x in tgt); out["target_coverage_frames"]={"frames":tf,"accepted":ta,"coverage":ta/tf if tf else None,"CI":cp(ta,tf)}
    # per-wrestler coverage (worst wrestler)
    pw=collections.defaultdict(lambda:[0,0])
    for x in tgt: pw[x["wid"]][0]+=x["n"]; pw[x["wid"]][1]+=x["acc"]
    out["per_wrestler_coverage"]={w:(a/n if n else None) for w,(n,a) in sorted(pw.items())}; out["worst_wrestler_coverage"]=min((v for v in out["per_wrestler_coverage"].values() if v is not None),default=None)
    # risk-coverage over score thresholds
    sc=sorted({float(r["score"]) for r in rows},reverse=True); rc=[]
    P=sum(1 for r in rows if r["truth_class"]=="TARGET"); 
    for th in sc[::max(1,len(sc)//50)]:
        acc=[r for r in rows if float(r["score"])>=th]; tp=sum(1 for r in acc if r["truth_class"]=="TARGET"); fp=len(acc)-tp
        rc.append({"threshold":th,"coverage":tp/P if P else None,"false_accepts":fp,"accepted":len(acc),"risk":fp/len(acc) if acc else 0.0})
    out["risk_coverage"]=rc; return out
def main(p,o):
    rows=list(csv.DictReader(open(p))); m=metrics(rows); m["input_sha256"]=hashlib.sha256(open(p,"rb").read()).hexdigest(); json.dump(m,open(o,"w"),indent=1); print("wrote",o)
if __name__=="__main__": main(sys.argv[1],sys.argv[2])
