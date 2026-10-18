"""Synthetic test of the staged execution driver (temp dir, temp ledger; no real data)."""
import os,sys,json,tempfile
import numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import phase1_execute as EX,phase1_run as RUN
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"selftest6.py")).read().split("# ---- B6/B7")[0].split("# ---- B5: no dev/test contamination in training ----")[1].split("rng=np.random.RandomState(3)")[0])
rng=np.random.RandomState(3)
tr=[mk_ep(0,"train",rng,A="a",B="b")]; dv=[mk_ep(0,"dev",rng,A="c",B="d")]; te=[mk_ep(0,"test",rng,A="e",B="f"),mk_ep(1,"test",rng,A="e",B="g")]
data={b:dict(d=6,train=tr,dev=dv,test=te) for b in RUN.BACKBONE_ORDER}
td=tempfile.mkdtemp(); L=os.path.join(td,"ledger.jsonl"); open(L,"w").write(json.dumps({"id":"G"})+"\n")
r=EX.execute(data,os.path.join(td,"out"),L)
ids=[json.loads(l)["id"] for l in open(L)]; assert ids==["G","TR1","DS1","TST0","PR1","SE1"],ids
assert r["consistency"]["matches_driver"],r["consistency"]
assert os.path.exists(os.path.join(td,"out","test_decisions.csv"))
try: EX.execute(data,os.path.join(td,"out2"),L); raise AssertionError("second test opening allowed")
except SystemExit as e: assert "TEST ALREADY OPENED" in str(e)
r2=EX.execute({b:dict(d=6,train=[],dev=dv,test=te) for b in RUN.BACKBONE_ORDER},os.path.join(td,"out3"),L); assert r2["status"].startswith("INCONCLUSIVE-DATA")
print("selftest7 ok: driver staging order, single-use TEST, consistency with run_primary, fail-closed inconclusive (synthetic only)")
