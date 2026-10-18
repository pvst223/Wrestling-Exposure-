import csv,random,json,subprocess,os,sys
sys.path.insert(0,".")
import phase1_metrics as M, leakage_audit as L
random.seed(0); rows=[]
for i in range(40):
    t=random.choice(["w1","w2"]) if i<10 else random.choice(["REFEREE","SPECTATOR"])
    for f in range(20):
        sc=random.gauss(1.0 if t.startswith("w") else -0.5,0.6); rows.append(dict(clip_id="c",shot=i,tracklet_id=f"t{i}",frame=f,truth_id=t,accepted_role=(t if t.startswith("w") else "w1") if sc>0.5 else "",best_role=t if t.startswith("w") else "w1",score=sc))
m=M.metrics(rows); assert 0<=m["target_coverage"]["coverage_mean_of_unit_fractions"]<=1; assert M.cp(0,300)[1]<0.0125 and M.cp(0,300)[1]>0.0095
print("metrics ok; cp(0,300)=",M.cp(0,300))
open("/tmp/man.csv","w").write("clip_id,tracklet_id,wrestler_id,match_id,promotion_id,split,person_class\nc1,t1,w1,m1,p1,train,WRESTLER\nc2,t2,w1,m2,p1,test,WRESTLER\nc3,t3,w9,m3,p2,dev,WRESTLER\n")
bad,h=L.audit("/tmp/man.csv",{"wrestler_id":["w9"]}); assert any(b[0]=="wrestler_id" for b in bad) and any(b[0].startswith("EXCLUDED") for b in bad); print("leakage audit detects planted leaks:",len(bad))
