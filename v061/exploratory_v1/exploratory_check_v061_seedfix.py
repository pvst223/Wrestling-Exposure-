"""SEED-FIX VERSION of exploratory_check_v061.py (reviewer-authorised single defect correction, ledger PL8): only the seed input hash and the ledger/result bookkeeping differ; all computation is identical.
V0.6.1 DEVELOPMENT / HYPOTHESIS CHECK ONLY (spec_v3 file 09). Executed exactly once. Descriptive; no outcome class; not validation.
Frozen V0.6 L1 seed-0 MobileCLIP-B head + V0.6.1 two-stage rule; thresholds selected on old DEV only; evaluated once on old TEST.
Imports frozen V0.6 functions read-only; modifies nothing frozen."""
import sys,os,json,hashlib,collections,time
import numpy as np
LABEL="V0.6.1 DEVELOPMENT / HYPOTHESIS CHECK ONLY"
GRID_L1=[(t,d) for t in (0.5,0.6,0.7,0.8,0.9) for d in (0.05,0.10,0.20,0.30)]
CSTARS=(0.5,0.4,0.3,0.2,0.1)
def two_stage_label(pA,pB,pN,tau_g,delta):
    """Returns 'A','B','REJECT' (gate fail) or 'ABSTAIN' (A/B ambiguous). Fail-closed on non-finite or degenerate input."""
    if not (np.isfinite(pA) and np.isfinite(pB) and np.isfinite(pN)): return "REJECT"
    g=pA+pB
    if g<1e-12 or g<tau_g: return "REJECT"
    q=pA/g
    if q>=0.5+delta: return "A"
    if q<=0.5-delta: return "B"
    return "ABSTAIN"
def sel_point(points,cstar):
    el=[p for p in points if (-1.0 if p["coverage"] is None else p["coverage"])>=cstar]
    if not el: return None
    return min(el,key=lambda p:(p["fta"] if p["fta"] is not None else 9.0,-(p["coverage"] if p["coverage"] is not None else -1.0),p["param"]))
def auroc(pos,neg):
    from scipy.stats import rankdata
    pos=np.asarray(pos);neg=np.asarray(neg)
    if len(pos)==0 or len(neg)==0: return float("nan")
    r=rankdata(np.concatenate([pos,neg])); return float((r[:len(pos)].sum()-len(pos)*(len(pos)+1)/2)/(len(pos)*len(neg)))
def run(RUN,M,cp,eps_dev,eps_test,probs,seed,frozen_ref=None):
    """eps_*: episode dicts; probs: {episode_id: (m,3) array of frozen-head softmax (pA,pB,pN)}. Pure given inputs."""
    def l1_rows(ep,tau_g,delta):
        P=probs[ep["id"]]; rows=[]
        for i in range(len(ep["meta"])):
            lab=two_stage_label(P[i,0],P[i,1],P[i,2],tau_g,delta)
            rows.append(RUN._row(ep,i,lab,"A" if P[i,0]>=P[i,1] else "B",P[i,0]+P[i,1]))
        return rows
    def table(eps,fn): return RUN.unit_table([(ep,fn(ep)) for ep in eps])
    dev={"B0":[],"L1":[]}
    for tau,mg in RUN.GRID_B0: dev["B0"].append(dict(param=(tau,mg),**RUN.table_metrics(table(eps_dev,lambda e:RUN.b0_rows(e,tau,mg)))))
    for tg,dl in GRID_L1: dev["L1"].append(dict(param=(tg,dl),**RUN.table_metrics(table(eps_dev,lambda e:l1_rows(e,tg,dl)))))
    cov=lambda p:-1.0 if p["coverage"] is None else p["coverage"]
    joint=[c for c in CSTARS if any(cov(p)>=c for p in dev["B0"]) and any(cov(p)>=c for p in dev["L1"])]
    res=dict(label=LABEL,seed=seed,dev_grids=dev,joint_levels=joint)
    if not joint: res["status"]="no feasible operating point"; return res
    cstar=joint[0]; pb=sel_point(dev["B0"],cstar); pl=sel_point(dev["L1"],cstar); res.update(status="OK",cstar=cstar,selected_B0=pb,selected_L1=pl)
    Tb=table(eps_test,lambda e:RUN.b0_rows(e,*pb["param"])); Tl=table(eps_test,lambda e:l1_rows(e,*pl["param"]))
    Db=table(eps_dev,lambda e:RUN.b0_rows(e,*pb["param"])); Dl=table(eps_dev,lambda e:l1_rows(e,*pl["param"]))
    def withci(T):
        m=RUN.table_metrics(T); n,k=m["n_units"],m["fa_units"]; lo,hi=cp(k,n); m["fta_ci95_exact"]=[lo,hi]; return m
    rng=np.random.default_rng(seed)
    def cov_ci(T):
        v=np.array([sum(u["cov"])/len(u["cov"]) for u in T.values() if u["cov"]]); b=[v[rng.integers(0,len(v),len(v))].mean() for _ in range(2000)]; return [float(np.quantile(b,.025)),float(np.quantile(b,.975))]
    mb,ml=withci(Tb),withci(Tl); mb["coverage_ci95_bootstrap"]=cov_ci(Tb); ml["coverage_ci95_bootstrap"]=cov_ci(Tl)
    res.update(test_B0=mb,test_L1=ml,test_paired=RUN.paired(Tb,Tl),dev_insample_B0=RUN.table_metrics(Db),dev_insample_L1=RUN.table_metrics(Dl))
    # candidate-level diagnostics on TEST with unit-clustered bootstrap
    rows=[]
    for ep in eps_test:
        P=probs[ep["id"]]
        for i,m in enumerate(ep["meta"]):
            tgt=m["truth"] in (ep["A"],ep["B"]); g=float(P[i,0]+P[i,1]); q=float(P[i,0]/g) if g>1e-12 else 0.5
            lab=two_stage_label(P[i,0],P[i,1],P[i,2],*pl["param"]); neg_cls=m["truth"] in M.NEG_CLASSES
            rows.append(dict(unit=(ep["clip"],str(m["shot"]),M._norm_truth(m["truth"])),tgt=tgt,isA=(m["truth"]==ep["A"]),g=g,q=q,lab=lab,strat=("TARGET" if tgt else ("OTHER_NAMED_WRESTLER" if not neg_cls else M._norm_truth(m["truth"])))))
    U=collections.defaultdict(list)
    for r in rows: U[r["unit"]].append(r)
    keys=sorted(U)
    def stats(R):
        gate=auroc([r["g"] for r in R if r["tgt"]],[r["g"] for r in R if not r["tgt"]])
        T=[r for r in R if r["tgt"]]; ab=auroc([r["q"] for r in T if r["isA"]],[r["q"] for r in T if not r["isA"]]); return gate,ab
    gate,ab=stats(rows); bg=[];ba=[]
    for _ in range(2000):
        flat=[r for j in rng.integers(0,len(keys),len(keys)) for r in U[keys[j]]]; x,y=stats(flat)
        if x==x: bg.append(x)
        if y==y: ba.append(y)
    ci=lambda a:[float(np.quantile(a,.025)),float(np.quantile(a,.975))] if a else None
    dec=collections.defaultdict(collections.Counter)
    for r in rows: dec[r["strat"]][r["lab"] if r["lab"] in("REJECT","ABSTAIN") else "ACCEPT"]+=1
    wrong=sum(1 for r in rows if r["tgt"] and r["lab"] in("A","B") and ((r["lab"]=="A")!=r["isA"])); acc_t=sum(1 for r in rows if r["tgt"] and r["lab"] in("A","B"))
    res["test_gate_auroc"]=dict(auroc=gate,ci95=ci(bg)); res["test_assignment_auroc"]=dict(auroc=ab,ci95=ci(ba)); res["test_decision_decomposition_candidates"]={k:dict(v) for k,v in dec.items()}
    res["test_target_candidates_accepted"]=acc_t; res["test_target_candidates_accepted_as_wrong_wrestler"]=wrong
    res["diagnostic_flags_descriptive_only"]=dict(D_GATE_lower_ci_below_0_70=(res["test_gate_auroc"]["ci95"] or [1])[0]<0.70,F_ASSIGN_interval_includes_0_5=(res["test_assignment_auroc"]["ci95"] or [0,1])[0]<=0.5<=(res["test_assignment_auroc"]["ci95"] or [0,1])[1])
    if frozen_ref: res["frozen_V0.6_reference"]=frozen_ref
    return res
def main():
    T="/home/claude/proj/v06_phase1/tools"; sys.path.insert(0,T)
    import torch,phase1_run as RUN,phase1_execute as X,heads,phase1_metrics as M
    FZ="/home/claude/proj/v06_phase1/frozen"; OUT=os.path.dirname(os.path.abspath(__file__)); RES=os.path.join(OUT,"EXPLORATORY_RESULT_V1_SEEDFIX.json")
    if os.path.exists(RES): raise SystemExit("EXECUTED ALREADY: exactly-once rule")
    led=[json.loads(l) for l in open(os.path.join(FZ,"AUDIT_LEDGER.jsonl"))]
    pre=[r for r in led if r.get("id")=="PL8"]
    if not pre: raise SystemExit("no PL8 pre-run ledger entry")
    if pre[-1]["script_sha256"]!=X.sha(os.path.abspath(__file__)): raise SystemExit("script hash differs from PL8")
    if any(r.get("id")=="EXR2" for r in led): raise SystemExit("EXR2 already recorded")
    seed=int(pre[-1]["corrected_spec_freeze_hash_for_seed_derivation"][:8],16)%2**31
    data=X.load_real(FZ,os.path.join(FZ,"features")); v=data["mobileclip_b"]
    head=heads.LearnedHead(v["d"]); head.load_state_dict(torch.load(os.path.join(FZ,"phase1_results","L1_seed0_mobileclip_b.pt"))); head.eval()
    assert X.sha(os.path.join(FZ,"phase1_results","L1_seed0_mobileclip_b.pt"))==pre[-1]["head_sha256"]
    probs={}
    for ep in v["dev"]+v["test"]:
        e=RUN._tt(ep); e2=dict(e)
        if len(e2["seed_N"])==0: e2.pop("seed_N")
        with torch.no_grad(): probs[ep["id"]]=torch.softmax(head.logits(e2),1).numpy()
    prim=json.load(open(os.path.join(FZ,"phase1_results","primary_result.json")))
    ref=dict(reportable_status=prim["reportable_status"],B0_fta=prim["decision"]["fta_b0"],B0_coverage=prim["decision"]["coverage_b0"],L1_fta=prim["decision"]["fta_l1"],L1_coverage=prim["decision"]["coverage_l1"],paired=prim["decision"]["paired"])
    res=run(RUN,M,M.cp,v["dev"],v["test"],probs,seed,ref); res["test_episodes"]=[e["id"] for e in v["test"]]; res["dev_episodes"]=[e["id"] for e in v["dev"]]; res["head_sha256"]=pre[-1]["head_sha256"]
    json.dump(res,open(RES,"w"),indent=1,sort_keys=True,default=lambda o:o.tolist() if hasattr(o,"tolist") else str(o)); os.chmod(RES,0o444)
    print(json.dumps({k:res.get(k) for k in ("status","cstar","selected_B0","selected_L1")},default=str)[:600]); print("result sha256",X.sha(RES))
if __name__=="__main__": main()
