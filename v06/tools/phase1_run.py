"""Phase 1 runner (PHASE1_IMPLEMENTATION_CLOSURE_V1, B6/B7). Pure functions over episode tensors; selftested on synthetic fixtures only (selftest6.py).
NOT RUN on experimental data: main() calls the fail-closed authorization guard first. No threshold, seed, grid or rule is a parameter.
Episode dict: id, clip, split, A, B (identity names), seed_A, seed_B, seed_N (np float32 (n,d); seed_N may have 0 rows), cand (m,d), y (m,) in {0:A,1:B,2:NON-TARGET}, meta (list of dict tid, frame, shot, truth).
Closure decisions implemented here (all recorded in PHASE1_IMPLEMENTATION_CLOSURE_V1.md, none performance-informed):
 R1 B0 grid tau x margin (5x4); L1 grid = softmax floor (5), L1 margin fixed 0.0; L1 acceptance = heads.decide (argmax over A/B/NON-TARGET with floor); L1 score = max(pA,pB) before the floor; B0 score = max(sA,sB).
 R2 c* per backbone = largest of {.5,.4,.3,.2,.1} with >=1 DEV point of BOTH methods at coverage >= c; none -> NO_JOINT_COVERAGE (INCONCLUSIVE-DATA for that backbone).
 R3 backbone selection (V3 'lowest B0 dev FTA at matched c*'): a COMMON c* = largest c jointly reachable for every backbone that has any joint coverage; backbone = lowest B0 dev unit-FTA at that c*; ties by fixed order osnet_x1_0, dinov2_vits14, mobileclip_b.
 R4 operating point per method at c*: lowest dev unit-FTA among points with dev coverage >= c*; tie highest coverage; tie lexicographic parameters ascending.
 R5 unit tables aggregate pairwise episodes: unit false-accept = OR across episodes; target coverage of a unit = mean over episodes in which it is a target of its accepted-as-own fraction; non-target episodes contribute only to false-accept.
 R6 (D6 as amended by the reviewer) precedence INCONCLUSIVE-DATA > KEEP/KILL/MODIFY; two fields: uncapped_methodological_outcome and reportable_status; a KEEP is reported ANNOTATION-PROVISIONAL (no stronger than MODIFY for advancement); a KILL stays KILL.
 R7 If there is no evaluable TRAIN episode (or no dev/test episode), nothing is trained or evaluated and the result is INCONCLUSIVE-DATA (analysis cannot be completed)."""
import sys,os,json,collections,math
import numpy as np,torch
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import heads,phase1_metrics as M
from scipy.stats import binom
GRID_B0=[(t,m) for t in (0.30,0.40,0.50,0.60,0.70) for m in (0.00,0.02,0.05,0.10)]
GRID_L1=(0.4,0.5,0.6,0.7,0.8)
CSTAR_LIST=(0.50,0.40,0.30,0.20,0.10)
BACKBONE_ORDER=("osnet_x1_0","dinov2_vits14","mobileclip_b")
L1_MARGIN=0.0; ANNOTATION_GATE_SATISFIED=False   # study status: ANNOTATION-PROVISIONAL (deviation X1)
# ---------------- rows / unit tables ----------------
def _row(ep,i,acc_label,best_label,score):
    m=ep["meta"][i]; ident={"A":ep["A"],"B":ep["B"]}
    return dict(clip_id=ep["clip"],shot=m["shot"],tracklet_id=m["tid"],frame=m["frame"],truth_id=m["truth"],accepted_role=ident.get(acc_label,""),best_role=ident[best_label],score=float(score))
def b0_rows(ep,tau,margin):
    labs,(sa,sb,sn)=heads.NonLearnedBaseline(tau,margin).decide(ep)
    return [_row(ep,i,l,"A" if sa[i]>=sb[i] else "B",max(sa[i],sb[i])) for i,l in enumerate(labs)]
def _tt(ep):
    d={k:torch.as_tensor(np.asarray(ep[k],np.float32)) for k in ("seed_A","seed_B","seed_N","cand")}; d["y"]=torch.as_tensor(np.asarray(ep["y"]),dtype=torch.long); return d
def l1_rows(head,ep,floor):
    e=_tt(ep)
    if len(e["seed_N"])==0: e.pop("seed_N")
    labs,p=heads.decide(head,e,tau=floor,margin=L1_MARGIN)
    return [_row(ep,i,l,"A" if p[i,0]>=p[i,1] else "B",max(p[i,0],p[i,1])) for i,l in enumerate(labs)]
def unit_table(ep_rows):
    U={}
    for ep,rows in ep_rows:
        per=collections.OrderedDict()
        for r in rows:
            k=(r["clip_id"],str(r["shot"]),M._norm_truth(r["truth_id"])); u=per.setdefault(k,dict(n=0,correct=0,false=0)); u["n"]+=1; acc=r["accepted_role"]
            if acc!="":
                if k[2] in (ep["A"],ep["B"]) and acc==k[2]: u["correct"]+=1
                else: u["false"]+=1
        for k,u in per.items():
            g=U.setdefault(k,dict(false=False,cov=[],named=k[2] not in M.NEG_CLASSES)); g["false"]=g["false"] or u["false"]>0
            if k[2] in (ep["A"],ep["B"]): g["cov"].append(u["correct"]/u["n"])
    return U
def table_metrics(U):
    n=len(U); fa=sum(1 for u in U.values() if u["false"]); tg=[sum(u["cov"])/len(u["cov"]) for u in U.values() if u["cov"]]
    st=collections.defaultdict(lambda:[0,0])
    for k,u in U.items():
        s="OTHER_NAMED_WRESTLER" if u["named"] else k[2]; st[s][0]+=1; st[s][1]+=int(u["false"])
    return dict(n_units=n,fa_units=fa,fta=(fa/n if n else None),n_target_units=len(tg),coverage=(sum(tg)/len(tg) if tg else None),strata={s:dict(n=a,fa=b) for s,(a,b) in sorted(st.items())})
def paired(Tb,Tl):
    if set(Tb)!=set(Tl): raise ValueError("unit sets differ between methods")
    b=sum(1 for k in Tb if Tb[k]["false"] and not Tl[k]["false"]); c=sum(1 for k in Tb if Tl[k]["false"] and not Tb[k]["false"]); both=sum(1 for k in Tb if Tb[k]["false"] and Tl[k]["false"]); n=b+c
    p=1.0 if n==0 else (float(binom.sf(b-1,n,0.5)) if b>0 else 1.0)
    return dict(n_units=len(Tb),b_baseline_only=b,c_learned_only=c,both=both,discordant=n,one_sided_p_b_gt_c=p)
# ---------------- L1 training ----------------
def train_l1(train_eps,d_in,seed=0):
    eps=[]
    for ep in sorted(train_eps,key=lambda e:e["id"]):
        e=_tt(ep)
        if len(e["seed_N"])==0: e.pop("seed_N")
        eps.append(e)
    head=heads.LearnedHead(d_in,128,seed=seed); hist=heads.train(head,eps,epochs=30,lr=1e-2,seed=seed); return head,hist
# ---------------- grids / selection ----------------
def grid_eval(eps,head):
    out=dict(B0=[],L1=[])
    for tau,mg in GRID_B0:
        T=unit_table([(ep,b0_rows(ep,tau,mg)) for ep in eps]); out["B0"].append(dict(param=(tau,mg),**table_metrics(T)))
    for fl in GRID_L1:
        T=unit_table([(ep,l1_rows(head,ep,fl)) for ep in eps]); out["L1"].append(dict(param=(fl,),**table_metrics(T)))
    return out
def _cov(p): return -1.0 if p["coverage"] is None else p["coverage"]
def joint_levels(g): return [c for c in CSTAR_LIST if any(_cov(p)>=c for p in g["B0"]) and any(_cov(p)>=c for p in g["L1"])]
def select_point(points,cstar):
    el=[p for p in points if _cov(p)>=cstar]
    if not el: return None
    return min(el,key=lambda p:(p["fta"] if p["fta"] is not None else 9.0,-_cov(p),p["param"]))
def select_backbone(grids):
    """grids: {backbone: grid_eval on DEV}. Returns dict(status, cstar, backbone, per_backbone)."""
    per={b:joint_levels(g) for b,g in grids.items()}; ok=[b for b in BACKBONE_ORDER if b in grids and per[b]]
    if not ok: return dict(status="INCONCLUSIVE-DATA: NO JOINT COVERAGE OPERATING POINT",cstar=None,backbone=None,per_backbone_joint_levels=per)
    cstar=max(c for c in CSTAR_LIST if all(c in per[b] for b in ok)); best=None
    for b in ok:                                    # fixed order = tie-break
        p=select_point(grids[b]["B0"],cstar); key=p["fta"]
        if best is None or key<best[0]: best=(key,b)
    return dict(status="OK",cstar=cstar,backbone=best[1],b0_dev_fta_at_cstar={b:select_point(grids[b]["B0"],cstar)["fta"] for b in ok},per_backbone_joint_levels=per)
# ---------------- decision ----------------
def decide_outcome(Tb,Tl,annotation_gate_satisfied=ANNOTATION_GATE_SATISFIED):
    pw=paired(Tb,Tl); mb,ml=table_metrics(Tb),table_metrics(Tl); b,c,p=pw["b_baseline_only"],pw["c_learned_only"],pw["one_sided_p_b_gt_c"]
    crit1=(b+c>=4 and b>c and p<=0.10)
    crit2=(ml["coverage"] is not None and mb["coverage"] is not None and ml["coverage"]>=mb["coverage"]-0.10)
    strata={}
    for s in set(mb["strata"])|set(ml["strata"]):
        sb,sl=mb["strata"].get(s,dict(n=0,fa=0)),ml["strata"].get(s,dict(n=0,fa=0)); strata[s]=dict(n=sb["n"],fa_b0=sb["fa"],fa_l1=sl["fa"],eligible=sb["n"]>=15,violates=(sb["n"]>=15 and sl["fa"]-sb["fa"]>=3))
    crit3=not any(v["violates"] for v in strata.values())
    inconclusive=(mb["fa_units"]<5) or (mb["n_target_units"]<15)
    keep=crit1 and crit2 and crit3; kill=(b<=c) and mb["fa_units"]>=5   # D6 (amended): KILL does not require the annotation gate; annotation uncertainty never rescues a failing method
    uncapped="INCONCLUSIVE-DATA" if inconclusive else ("KEEP" if keep else ("KILL" if kill else "MODIFY"))
    if uncapped=="INCONCLUSIVE-DATA": status="INCONCLUSIVE-DATA"
    elif annotation_gate_satisfied: status=uncapped
    elif uncapped=="KEEP": status="KEEP, ANNOTATION-PROVISIONAL (no stronger than MODIFY for advancement)"
    else: status=uncapped+" (ANNOTATION-PROVISIONAL)"
    return dict(paired=pw,crit1_sign_test=crit1,crit2_coverage=crit2,crit3_strata=crit3,strata=strata,inconclusive_data=inconclusive,baseline_fa_units=mb["fa_units"],n_post_seed_target_units=mb["n_target_units"],coverage_b0=mb["coverage"],coverage_l1=ml["coverage"],fta_b0=mb["fta"],fta_l1=ml["fta"],
                uncapped_methodological_outcome=uncapped,annotation_gate_satisfied=annotation_gate_satisfied,reportable_status=status,reported_class=status)
# ---------------- orchestration (pure; tests inject data) ----------------
def evaluate_at(eps,head,pb0,pl1):
    Tb=unit_table([(ep,b0_rows(ep,*pb0)) for ep in eps]); Tl=unit_table([(ep,l1_rows(head,ep,pl1[0])) for ep in eps]); return Tb,Tl
def run_primary(data):
    """data: {backbone: dict(d=int, train=[eps], dev=[eps], test=[eps])} (only status OK episodes). Returns full result dict. Test is touched only after dev selection."""
    res=dict(status=None)
    for b,v in data.items():
        if not v["train"] or not v["dev"] or not v["test"]:
            return dict(status="INCONCLUSIVE-DATA: analysis cannot be completed (no evaluable %s episodes)"%("/".join(k for k in ("train","dev","test") if not v[k])),reported_class="INCONCLUSIVE-DATA",backbone=b)
    heads_={b:train_l1(v["train"],v["d"],0)[0] for b,v in data.items()}
    grids={b:grid_eval(v["dev"],heads_[b]) for b,v in data.items()}; sel=select_backbone(grids); res["backbone_selection"]=sel
    if sel["status"]!="OK": res.update(status=sel["status"],reported_class="INCONCLUSIVE-DATA"); return res
    b=sel["backbone"]; pb0=select_point(grids[b]["B0"],sel["cstar"])["param"]; pl1=select_point(grids[b]["L1"],sel["cstar"])["param"]
    res["operating_points"]=dict(B0=pb0,L1=pl1); Tb,Tl=evaluate_at(data[b]["test"],heads_[b],pb0,pl1); res["decision"]=decide_outcome(Tb,Tl); res["status"]="OK"; res["reported_class"]=res["decision"]["reported_class"]; return res
def components(clip_identities):
    """Connected components of identities linked across clips (LOCO components)."""
    par={}
    def f(x):
        par.setdefault(x,x)
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for ids in clip_identities.values():
        for i in ids[1:]: par[f(i)]=f(ids[0])
        if ids: f(ids[0])
    comp={c:f(ids[0]) for c,ids in clip_identities.items() if ids}; return comp
def loco(all_eps,comp_of_clip,d_in,seed=0):
    """SECONDARY/DESCRIPTIVE ONLY. Run after the primary result is recorded. Thresholds set on the training fold itself (in-sample), same c*/lowest-FTA rule."""
    out={}
    for comp in sorted(set(comp_of_clip.values())):
        held=[e for e in all_eps if comp_of_clip[e["clip"]]==comp]; fold=[e for e in all_eps if comp_of_clip[e["clip"]]!=comp]
        if not held or not fold: out[comp]=dict(status="UNEVALUABLE"); continue
        head,_=train_l1(fold,d_in,seed); g=grid_eval(fold,head); lv=joint_levels(g)
        if not lv: out[comp]=dict(status="NO_JOINT_COVERAGE"); continue
        cs=lv[0]; pb=select_point(g["B0"],cs)["param"]; pl=select_point(g["L1"],cs)["param"]; Tb,Tl=evaluate_at(held,head,pb,pl)
        out[comp]=dict(status="OK",cstar_train_fold=cs,B0=table_metrics(Tb),L1=table_metrics(Tl),paired=paired(Tb,Tl),n_held_units=len(Tb))
    return out
def variance_seeds(train,dev,test,d_in,cstar,pb0,seeds=(1,2,3)):
    """VARIANCE REPORTING ONLY (does not change any decision): retrain L1 with other seeds, select the L1 floor on dev at the fixed c*, report test metrics."""
    out={}
    for s in seeds:
        head,_=train_l1(train,d_in,s); g=grid_eval(dev,head); pt=select_point(g["L1"],cstar)
        if pt is None: out[s]=dict(status="NO_POINT"); continue
        Tb,Tl=evaluate_at(test,head,pb0,pt["param"]); out[s]=dict(status="OK",L1_param=pt["param"],paired=paired(Tb,Tl),L1=table_metrics(Tl))
    return out
# ---------------- real-data loading (guarded; not used by selftests) ----------------
def load_episode_tensors(frozen_dir,feat_dir,backbone,manifest_json,extraction_csv):
    import csv,glob
    SM=json.load(open(manifest_json)); rows=collections.defaultdict(lambda:collections.defaultdict(list))
    for r in csv.DictReader(open(extraction_csv)): rows[r["clip"]][r["tid"]].append((int(r["frame"]),int(r["det"])))
    out={"train":[],"dev":[],"test":[]}
    for clip,cv in sorted(SM["clips"].items()):
        fp=glob.glob(os.path.join(feat_dir,f"feat_{backbone}_{clip}_*.npz"))
        if len(fp)!=1: raise SystemExit(f"expected exactly one feature cache for {backbone}/{clip}")
        z=np.load(fp[0]); idx={(int(f),int(d)):i for i,(f,d) in enumerate(zip(z["frame"],z["det"]))}; E=z["emb"]
        def feat(f,d): return E[idx[(f,d)]]
        for e in cv["episodes"]:
            if e["status"]!="OK": continue
            sa=np.stack([feat(s["frame"],s["det"]) for s in e["seed_A"]]); sb=np.stack([feat(s["frame"],s["det"]) for s in e["seed_B"]])
            sn=np.stack([feat(s["frame"],s["det"]) for s in e["seed_N"]]) if e["seed_N"] else np.zeros((0,E.shape[1]),np.float32)
            cand=[];meta=[];y=[]
            for c in sorted(e["candidate_tracklets"],key=lambda c:c["tid"]):
                for f,d in sorted(rows[clip][c["tid"]]):
                    if (f,d) in idx: cand.append(feat(f,d)); meta.append(dict(tid=c["tid"],frame=f,shot=c["shot"],truth=c["truth"])); y.append(c["y"])
            out[e["split"]].append(dict(id=e["id"],clip=clip,split=e["split"],A=e["A"],B=e["B"],seed_A=sa,seed_B=sb,seed_N=sn,cand=np.stack(cand),y=np.array(y),meta=meta))
    return out
def main():
    import argparse; ap=argparse.ArgumentParser(); [ap.add_argument(x) for x in ("--frozen_dir","--feat_dir","--out_dir")]; a=ap.parse_args()
    from authorization_guard import require_bakeoff_authorization; require_bakeoff_authorization(a.frozen_dir)
    sm=os.path.join(a.frozen_dir,"SEED_EPISODE_MANIFEST_V2.json"); ex=os.path.join(a.frozen_dir,"EXTRACTION_FRAME_MANIFEST_V1.csv"); data={}
    for b in BACKBONE_ORDER:
        t=load_episode_tensors(a.frozen_dir,a.feat_dir,b,sm,ex); allc=t["train"]+t["dev"]+t["test"]; d=allc[0]["cand"].shape[1] if allc else 0; data[b]=dict(d=d,train=t["train"],dev=t["dev"],test=t["test"])
    res=run_primary(data); os.makedirs(a.out_dir,exist_ok=True); json.dump(res,open(os.path.join(a.out_dir,"primary_result.json"),"w"),indent=1,default=str); print(res.get("reported_class"))
    # secondary analyses are run only after the primary result file exists
    if res.get("status")=="OK":
        b=res["backbone_selection"]["backbone"]; v=data[b]; ids={}
        for e in v["train"]+v["dev"]+v["test"]: ids.setdefault(e["clip"],[]).extend([e["A"],e["B"]])
        comp=components({c:sorted(set(x)) for c,x in ids.items()})
        json.dump(dict(loco=loco(v["train"]+v["dev"]+v["test"],comp,v["d"]),variance=variance_seeds(v["train"],v["dev"],v["test"],v["d"],res["backbone_selection"]["cstar"],res["operating_points"]["B0"])),open(os.path.join(a.out_dir,"secondary_descriptive.json"),"w"),indent=1,default=str)
if __name__=="__main__": main()
