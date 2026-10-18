import sys,os,csv,json,subprocess,tempfile
sys.path.insert(0,".")
import make_splits as MS, validate_labels as VL, registry as RG
d=tempfile.mkdtemp(); m=os.path.join(d,"meta.csv")
rows=[("c1","p1","m1","w1","w2"),("c2","p1","m2","w3","w4"),("c3","p2","m3","w5","w6"),("c4","p2","m4","w1","w7"),("c5","p3","m5","w8","w9"),("c6","p3","m6","w10","w11"),("c7","p4","m7","w12","w13"),("c8","p4","m8","w14","w15"),("c9","p5","m9","w16","w3")]
open(m,"w").write("clip_id,promotion_id,match_id,wrestler_A,wrestler_B\n"+"".join(",".join(r)+"\n" for r in rows))
out,rep=MS.run(m); 
for s,t in [("train","dev"),("train","test"),("dev","test")]: assert not set(rep[s]["wrestlers"])&set(rep[t]["wrestlers"]),"wrestler leak"
assert out["c1"]==out["c4"] and out["c2"]==out["c9"]
try: MS.run(m,excluded={"wrestler_id":["w16"]}); raise AssertionError
except SystemExit: pass
l=os.path.join(d,"l.csv"); open(l,"w").write(",".join(VL.COLS)+"\nc1,t1,0,10,WRESTLER,,,clear,front,upright,large,0,1,0,dev,ai,v1,0\nc1,t2,0,10,SPECTATOR,w9,,clear,front,upright,large,0,1,0,dev,ai,v1,0\n")
e=VL.validate(l); assert len(e)==2,e
lg=os.path.join(d,"led.jsonl"); RG.log(lg,dict(kind="sealed_test",split_manifest_hash="h",config_hash="c",code_hash="x",seed=0,outputs_sha256="o",note=""))
try: RG.log(lg,dict(kind="sealed_test",split_manifest_hash="h")); raise AssertionError
except SystemExit: pass
print("splits",{k:len(v['wrestlers']) for k,v in rep.items()},"selftest2 ok")
