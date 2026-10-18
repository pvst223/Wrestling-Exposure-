"""POSTHOC_DIAGNOSTIC_V1: read-only diagnostics on frozen Phase-1 artifacts (frozen features, frozen L1 state dict, frozen manifests).
Imports frozen functions; modifies nothing; writes only into this directory. Post-hoc, descriptive, cannot alter Phase 1."""
import sys,os,json,hashlib,collections,csv
import numpy as np,torch
T="/home/claude/proj/v06_phase1/tools"; sys.path.insert(0,T)
import phase1_run as RUN, phase1_execute as X, heads
from scipy.stats import rankdata
FZ="/home/claude/proj/v06_phase1/frozen"; OUT=os.path.dirname(os.path.abspath(__file__)); B="mobileclip_b"
data=X.load_real(FZ,os.path.join(FZ,"features")); v=data[B]
head=heads.LearnedHead(v["d"]); head.load_state_dict(torch.load(os.path.join(FZ,"phase1_results",f"L1_seed0_{B}.pt"))); head.eval()
NEG_PROB=lambda p:p
def auroc(pos,neg):
    pos=np.asarray(pos);neg=np.asarray(neg)
    if len(pos)==0 or len(neg)==0: return float("nan")
    r=rankdata(np.concatenate([pos,neg])); return float((r[:len(pos)].sum()-len(pos)*(len(pos)+1)/2)/(len(pos)*len(neg)))
rows=[]  # per candidate
for split in ("train","dev","test"):
    for ep in v[split]:
        e=RUN._tt(ep); e2=dict(e)
        if len(e2["seed_N"])==0: e2.pop("seed_N")
        with torch.no_grad(): p=torch.softmax(head.logits(e2),1).numpy()
        sa,sb,sn=heads.NonLearnedBaseline().scores(ep)
        for i,m in enumerate(ep["meta"]):
            tr=m["truth"]; role="TARGET" if tr in (ep["A"],ep["B"]) else "NONTARGET"
            rows.append(dict(split=split,ep=ep["id"],clip=ep["clip"],shot=str(m["shot"]),tid=m["tid"],frame=m["frame"],truth=tr,role=role,
              strat=("TARGET" if role=="TARGET" else ("OTHER_NAMED_WRESTLER" if tr not in __import__("phase1_metrics").NEG_CLASSES else tr)),
              pA=p[i,0],pB=p[i,1],pN=p[i,2],l1=max(p[i,0],p[i,1]),l1_arg=int(p[i].argmax()),sA=sa[i],sB=sb[i],sN=sn[i],b0=max(sa[i],sb[i]),
              own_correct=(tr==ep["A"] and p[i,0]>=p[i,1]) or (tr==ep["B"] and p[i,1]>p[i,0]),A=ep["A"],B=ep["B"]))
# consistency with frozen test_decisions.csv
fz={}
for r in csv.DictReader(open(os.path.join(FZ,"phase1_results","test_decisions.csv"))):
    if r["method"]=="L1": fz[(r["clip_id"],r["tracklet_id"],int(r["frame"]))]=float(r["score"])
mx=max(abs(fz[(r["clip"],r["tid"],r["frame"])]-r["l1"]) for r in rows if r["split"]=="test")
res=dict(record="POSTHOC_DIAGNOSTIC_V1",backbone=B,recompute_vs_frozen_L1_test_scores_max_abs_diff=mx)
def q(a): a=np.asarray(a); return dict(n=int(len(a)),min=float(a.min()),q10=float(np.quantile(a,.1)),q25=float(np.quantile(a,.25)),median=float(np.median(a)),q75=float(np.quantile(a,.75)),q90=float(np.quantile(a,.9)),max=float(a.max())) if len(a) else dict(n=0)
def sel(split,**k): return [r for r in rows if r["split"]==split and all(r[a]==b for a,b in k.items())]
# 1 score distributions
dist={}
for s in ("train","dev","test"):
    for role in ("TARGET","NONTARGET"):
        R=sel(s,role=role); dist[f"{s}/{role}"]=dict(L1_max_pA_pB=q([r["l1"] for r in R]),L1_pNONTARGET=q([r["pN"] for r in R]),B0_max_sA_sB=q([r["b0"] for r in R]),B0_sN=q([r["sN"] for r in R]))
res["score_distributions"]=dist
# 2 AUROC with unit-clustered bootstrap
rng=np.random.default_rng(20261018)
def unit_key(r): return (r["clip"],r["shot"],r["truth"])
def boot(split,key,nb=2000):
    R=sel(split); U=collections.defaultdict(list)
    for r in R: U[unit_key(r)].append(r)
    keys=sorted(U); pt=auroc([r[key] for r in R if r["role"]=="TARGET"],[r[key] for r in R if r["role"]=="NONTARGET"]); vals=[]
    for _ in range(nb):
        S=[U[keys[j]] for j in rng.integers(0,len(keys),len(keys))]; flat=[r for u in S for r in u]
        a=auroc([r[key] for r in flat if r["role"]=="TARGET"],[r[key] for r in flat if r["role"]=="NONTARGET"])
        if a==a: vals.append(a)
    tu=sum(1 for k in keys if any(r["role"]=="TARGET" for r in U[k])); nu=sum(1 for k in keys if any(r["role"]=="NONTARGET" for r in U[k]))
    return dict(auroc=pt,ci95=[float(np.quantile(vals,.025)),float(np.quantile(vals,.975))] if vals else None,n_units=len(keys),target_units=tu,nontarget_units=nu,n_cand=len(R),n_boot_valid=len(vals))
def unit_auc(split,key):
    U=collections.defaultdict(list)
    for r in sel(split): U[unit_key(r)].append(r)
    pos=[np.mean([r[key] for r in v_]) for v_ in U.values() if v_[0]["role"]=="TARGET"]; neg=[np.mean([r[key] for r in v_]) for v_ in U.values() if v_[0]["role"]=="NONTARGET"]; return auroc(pos,neg),len(pos),len(neg)
disc={}
for s in ("train","dev","test"):
    disc[s]={k:boot(s,k) for k in ("l1","b0")}; disc[s]["unit_level_auroc_l1"]=unit_auc(s,"l1"); disc[s]["unit_level_auroc_b0"]=unit_auc(s,"b0")
    # role-correctness among targets: argmax of pA/pB equals own identity
    T=sel(s,role="TARGET"); disc[s]["target_identity_correct_argmax_AvsB"]=float(np.mean([r["own_correct"] for r in T])) if T else None
    disc[s]["target_identity_correct_argmax_b0_AvsB"]=float(np.mean([((r["sA"]>=r["sB"] and r["truth"]==r["A"]) or (r["sB"]>r["sA"] and r["truth"]==r["B"])) for r in T])) if T else None
# per test episode
for ep in v["test"]:
    R=sel("test",ep=ep["id"]); disc["test_"+ep["id"]]=dict(l1=auroc([r["l1"] for r in R if r["role"]=="TARGET"],[r["l1"] for r in R if r["role"]=="NONTARGET"]),b0=auroc([r["b0"] for r in R if r["role"]=="TARGET"],[r["b0"] for r in R if r["role"]=="NONTARGET"]))
res["threshold_free_discrimination"]=disc
# 3 calibration shift
FLOOR=0.8; cal={}
for s in ("dev","test"):
    T=sel(s,role="TARGET"); N=sel(s,role="NONTARGET")
    cal[s]=dict(frac_target_l1_ge_floor=float(np.mean([r["l1"]>=FLOOR for r in T])),frac_nontarget_l1_ge_floor=float(np.mean([r["l1"]>=FLOOR for r in N])) if N else None,
      frac_target_argmax_nonTARGETclass=float(np.mean([r["l1_arg"]==2 for r in T])),mean_pN_targets=float(np.mean([r["pN"] for r in T])),mean_pN_nontargets=float(np.mean([r["pN"] for r in N])) if N else None,
      frac_target_b0_ge_tau=float(np.mean([r["b0"]>=0.3 for r in T])),frac_nontarget_b0_ge_tau=float(np.mean([r["b0"]>=0.3 for r in N])) if N else None)
    bins=[0,.2,.4,.6,.8,.9,1.0001]; rel=[]
    for lo,hi in zip(bins[:-1],bins[1:]):
        R=[r for r in sel(s) if lo<=r["l1"]<hi]; rel.append(dict(bin=[lo,min(hi,1.0)],n=len(R),frac_target_own_role_correct=(float(np.mean([r["role"]=="TARGET" and r["own_correct"] for r in R])) if R else None)))
    cal[s]["reliability_l1_max_pAB"]=rel
    # all-softmax confident rate overall
    cal[s]["pmax_over_all_three_classes_ge_floor"]=float(np.mean([max(r["pA"],r["pB"],r["pN"])>=FLOOR for r in sel(s)]))
# oracle (diagnostic only, NOT an operating point): floor levels on TEST vs DEV: target accept & non-target accept (candidate-level)
sweep={}
for s in ("dev","test"):
    T=sel(s,role="TARGET"); N=sel(s,role="NONTARGET"); sw=[]
    for f in (0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9):
        # frozen decision rule: argmax class in {A,B} and prob>=f
        def acc(r): 
            pr=np.array([r["pA"],r["pB"],r["pN"]]); k=pr.argmax(); return k<2 and pr[k]>=f
        sw.append(dict(floor=f,target_accept_rate=float(np.mean([acc(r) for r in T])),nontarget_candidate_false_accept_rate=float(np.mean([acc(r) for r in N])) if N else None))
    sweep[s]=sw
res["calibration_shift"]=cal; res["floor_sweep_descriptive_NOT_AN_OPERATING_POINT"]=sweep
# 4 abstention/rejection structure (frozen rule: floor .8, margin 0): per truth class
absn={}
for s in ("dev","test"):
    d=collections.defaultdict(lambda:collections.Counter())
    for r in sel(s):
        pr=np.array([r["pA"],r["pB"],r["pN"]]); k=int(pr.argmax()); lab=("A","B","NONTARGET")[k] if pr[k]>=FLOOR else "ABSTAIN"
        d[r["strat"]][lab]+=1; d[r["strat"]]["n"]+=1
        d[r["strat"]]["argmax_"+("A","B","NONTARGET")[k]]+=1
        if lab=="ABSTAIN": d[r["strat"]]["abstain_with_argmax_"+("A","B","NONTARGET")[k]]+=1
    absn[s]={k:dict(c) for k,c in d.items()}
res["abstention_rejection_structure_L1_frozen_rule"]=absn
# 5 B0 false-accept structure at frozen point tau=.3, margin=.02 on TEST (and DEV for reference)
b0f={}
for s in ("dev","test"):
    out=collections.defaultdict(lambda:collections.Counter()); units=collections.defaultdict(lambda:collections.Counter())
    for ep in v[s]:
        rr=RUN.b0_rows(ep,0.3,0.02)
        for r in rr:
            tr=r["truth_id"]; named=tr not in __import__("phase1_metrics").NEG_CLASSES
            tgt=tr in (ep["A"],ep["B"]); strat="TARGET" if tgt else ("OTHER_NAMED_WRESTLER" if named else tr)
            out[strat]["n"]+=1
            if r["accepted_role"]!="":
                out[strat]["accepted"]+=1
                if not (tgt and r["accepted_role"]==tr): out[strat]["false_accept"]+=1; out[strat]["false_accept_as_"+r["accepted_role"]]+=1
                if not (tgt and r["accepted_role"]==tr): units[(ep["clip"],str(r["shot"]),tr)]["false_cand"]+=1
            units[(ep["clip"],str(r["shot"]),tr)]["n"]+=1
    b0f[s]=dict(by_stratum={k:dict(c) for k,c in out.items()},false_accept_units=[dict(clip=k[0],shot=k[1],truth=k[2],false_candidates=c["false_cand"],n=c["n"],frac=c["false_cand"]/c["n"]) for k,c in sorted(units.items()) if c["false_cand"]>0])
    fa=[u for u in b0f[s]["false_accept_units"]]; b0f[s]["summary"]=dict(n_units_with_any_false_accept=len(fa),single_candidate_units=sum(1 for u in fa if u["false_candidates"]==1),median_fraction_of_unit_candidates_false_accepted=float(np.median([u["frac"] for u in fa])) if fa else None)
res["B0_false_accept_structure"]=b0f
# 6 context: candidates/units/seeds by clip/shot
ctx={}
for s in ("train","dev","test"):
    for ep in v[s]:
        R=sel(s,ep=ep["id"]); ctx[ep["id"]]=dict(split=s,n_candidates=len(R),n_seed_A=len(ep["seed_A"]),n_seed_B=len(ep["seed_B"]),n_seed_N=len(ep["seed_N"]),
          by_stratum=dict(collections.Counter(r["strat"] for r in R)),shots=dict(collections.Counter(r["shot"] for r in R)),n_tracklets=len(set(r["tid"] for r in R)))
res["context_frozen_variables"]=ctx
# classification per pre-written rule
t=disc["test"]["l1"]; d=disc["dev"]["l1"]; aT=t["auroc"]; aD=d["auroc"]; lo,hi=(t["ci95"] or [float("nan")]*2)
tgt_acc=cal["test"]["frac_target_l1_ge_floor"]
if t["target_units"]<10 or t["nontarget_units"]<10 or (hi-lo)>0.40: cls="D4"; why="insufficient evidence by rule (n units or CI width)"
elif hi<0.65 or (aT<=aD-0.20 and lo<0.60): cls="D1"; why="discrimination failure by rule"
elif lo>=0.70 and aT>=aD-0.10 and tgt_acc<0.05: cls="D2"; why="calibration/operating-point transfer by rule"
else: cls="D3"; why="mixed by rule"
res["classification"]=dict(rule_file="CLASSIFICATION_RULE_V1.md",rule_sha256=X.sha(os.path.join(OUT,"CLASSIFICATION_RULE_V1.md")),class_=cls,reason=why,test_auroc=aT,test_ci=[lo,hi],dev_auroc=aD,test_target_accept_at_frozen_floor=tgt_acc,test_target_units=t["target_units"],test_nontarget_units=t["nontarget_units"])
json.dump(res,open(os.path.join(OUT,"posthoc_numbers.json"),"w"),indent=1,default=lambda o:o.item() if hasattr(o,"item") else str(o))

# ---- SUPPLEMENTARY (added after first inspection of results; disclosed; does not alter the pre-written classification) ----
sup={}
for s_ in ("train","dev","test"):
    T=[r for r in sel(s_,role="TARGET")]
    def ab(R,k):  # AUROC for A-vs-B ordering: score = pA-pB (L1) or sA-sB (B0); positives = truth A
        key=(lambda r:r["pA"]-r["pB"]) if k=="l1" else (lambda r:r["sA"]-r["sB"])
        return auroc([key(r) for r in R if r["truth"]==r["A"]],[key(r) for r in R if r["truth"]==r["B"]])
    U=collections.defaultdict(list)
    for r in T: U[unit_key(r)].append(r)
    keys=sorted(U); out={}
    for k in ("l1","b0"):
        vals=[]
        for _ in range(2000):
            flat=[r for j in rng.integers(0,len(keys),len(keys)) for r in U[keys[j]]]; a=ab(flat,k)
            if a==a: vals.append(a)
        key=(lambda r:r["pA"]-r["pB"]) if k=="l1" else (lambda r:r["sA"]-r["sB"])
        acc=float(np.mean([(key(r)>0)==(r["truth"]==r["A"]) for r in T])) if T else None
        uacc=[np.mean([(key(r)>0)==(r["truth"]==r["A"]) for r in u]) for u in U.values()]
        out[k]=dict(auroc_A_vs_B=ab(T,k),ci95=[float(np.quantile(vals,.025)),float(np.quantile(vals,.975))] if vals else None,candidate_accuracy_A_vs_B=acc,unit_mean_accuracy=float(np.mean(uacc)) if uacc else None,frac_units_majority_correct=float(np.mean([a>0.5 for a in uacc])) if uacc else None,n_target_units=len(keys))
    sup[s_]=out
for ep in v["test"]+v["dev"]:
    T=sel(ep["split"],ep=ep["id"],role="TARGET"); sup["episode_"+ep["id"]]=dict(l1_auroc_A_vs_B=auroc([r["pA"]-r["pB"] for r in T if r["truth"]==r["A"]],[r["pA"]-r["pB"] for r in T if r["truth"]==r["B"]]),b0_auroc_A_vs_B=auroc([r["sA"]-r["sB"] for r in T if r["truth"]==r["A"]],[r["sA"]-r["sB"] for r in T if r["truth"]==r["B"]]),
       l1_mean_pA_pB_sum_targets=float(np.mean([r["pA"]+r["pB"] for r in T])),l1_mean_pA_minus_pB_abs=float(np.mean([abs(r["pA"]-r["pB"]) for r in T])))
res["supplementary_A_vs_B_identity_discrimination"]=sup
json.dump(res,open(os.path.join(OUT,"posthoc_numbers.json"),"w"),indent=1,default=lambda o:o.item() if hasattr(o,"item") else str(o))
# per-candidate table for video rendering and developer inspection (derived only from frozen scores)
with open(os.path.join(OUT,"posthoc_candidate_scores.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(["split","episode","clip","shot","tracklet","frame","truth","stratum","pA","pB","pNONTARGET","l1_max_pAB","sA","sB","sN","b0_max"])
    for r in rows: w.writerow([r["split"],r["ep"],r["clip"],r["shot"],r["tid"],r["frame"],r["truth"],r["strat"],*[f"{r[k]:.6f}" for k in ("pA","pB","pN","l1","sA","sB","sN","b0")]])
print("class",cls,why,"maxdiff",mx)
