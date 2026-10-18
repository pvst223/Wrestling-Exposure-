"""Synthetic-only test of exploratory_check_v061.py (no real data, no frozen head)."""
import sys,numpy as np,collections
sys.path.insert(0,"/home/claude/proj/v06_phase1/tools"); sys.path.insert(0,"/home/claude/proj/v06_phase1/exploratory_v1")
import exploratory_check_v061 as E, phase1_run as RUN, phase1_metrics as M
ok=lambda c,m:(c or (_ for _ in ()).throw(AssertionError(m)))
t=E.two_stage_label
ok(t(.45,.45,.1,.5,.05)=="ABSTAIN","tie abstains"); ok(t(.8,.1,.1,.5,.05)=="A","A"); ok(t(.1,.8,.1,.5,.05)=="B","B"); ok(t(.2,.2,.6,.5,.05)=="REJECT","gate")
ok(t(.65,.25,.1,.5,.2)=="A" and t(.55,.35,.1,.5,.2)=="ABSTAIN" and t(.46,.44,.1,.5,.2)=="ABSTAIN","delta boundaries"); ok(t(float("nan"),.5,.5,.5,.05)=="REJECT","nan fail closed"); ok(t(0,0,1,.5,.05)=="REJECT","degenerate")
ok(t(.9,.1,0,.9,.3)=="A" and t(.4,.4,.2,.9,.05)=="REJECT","g exactly at/under tau: g=.8 <.9 rejects")
pts=[dict(param=(1,1),coverage=.5,fta=.2),dict(param=(0,1),coverage=.5,fta=.2),dict(param=(2,0),coverage=.6,fta=.2),dict(param=(3,0),coverage=.3,fta=.0)]
ok(E.sel_point(pts,.5)["param"]==(2,0),"tie -> highest coverage"); ok(E.sel_point(pts[:2],.5)["param"]==(0,1),"tie -> lexicographic"); ok(E.sel_point(pts,.9) is None,"infeasible")
# synthetic end-to-end
rng=np.random.default_rng(1)
def mk(id,clip,n=60):
    meta=[];y=[];P=[]
    for i in range(n):
        shot=i%3; r=i%4
        truth=["a","b","REFEREE","SPECTATOR"][r]; y.append([0,1,2,2][r]); meta.append(dict(tid=f"{clip}:s{shot}:t{r}",frame=3*i,shot=shot,truth=truth))
        base=[[.8,.1,.1],[.1,.8,.1],[.02,.02,.96],[.05,.05,.9]][r]; P.append(np.clip(np.array(base)+rng.normal(0,.03,3),.001,None))
    P=np.array(P); P=P/P.sum(1,keepdims=True)
    pr=np.eye(8)[:4]*5; cand=np.array([pr[[0,1,2,3][i%4]]+rng.normal(0,.2,8) for i in range(n)]).astype(np.float32)
    d=dict(id=id,clip=clip,split="x",A="a",B="b",seed_A=(pr[0]+rng.normal(0,.2,(4,8))).astype(np.float32),seed_B=(pr[1]+rng.normal(0,.2,(4,8))).astype(np.float32),seed_N=(pr[2]+rng.normal(0,.2,(2,8))).astype(np.float32),cand=cand,y=np.array(y),meta=meta); return d,P
d1,P1=mk("e1","c1"); d2,P2=mk("e2","c2"); d3,P3=mk("e3","c3")
res=E.run(RUN,M,M.cp,[d1],[d2,d3],{"e1":P1,"e2":P2,"e3":P3},123)
ok(res["label"]==E.LABEL,"label"); ok(res["status"]=="OK","ran"); ok("class" not in res and "reported_class" not in res,"no outcome class")
ok(res["test_L1"]["fa_units"]==0,"clean synthetic -> no false accept"); ok(res["test_gate_auroc"]["auroc"]>0.99,"gate auroc"); ok(res["test_assignment_auroc"]["auroc"]>0.99,"assign auroc")
res2=E.run(RUN,M,M.cp,[d1],[d2,d3],{"e1":P1,"e2":P2,"e3":P3},123); import json
ok(json.dumps(res,sort_keys=True,default=str)==json.dumps(res2,sort_keys=True,default=str),"deterministic")
# infeasible: all-abstain probabilities
Pab=np.tile([.45,.45,.1],(60,1)); r3=E.run(RUN,M,M.cp,[d1],[d2],{"e1":Pab,"e2":P2},1); ok(r3["status"]=="no feasible operating point" or r3["joint_levels"] is not None,"infeasible handled")
print("selftest_exploratory ok (synthetic only)")
