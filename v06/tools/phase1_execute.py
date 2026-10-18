"""Staged execution driver for the AUTHORIZED Phase 1 bake-off (AUTH1). Uses ONLY the frozen functions of phase1_run.py (train_l1, grid_eval, select_backbone, select_point, b0_rows, l1_rows, unit_table, decide_outcome, loco, variance_seeds); it adds file staging, freezing, hashing and ledger entries, and enforces the order:
  load -> train L1 (seed 0, TRAIN only) -> DEV grids + selection -> FREEZE DEV_SELECTION_RECORD (ledger DS1) -> TEST opened ONCE (ledger TST0 written first, refuses a second opening) -> FREEZE primary result (ledger PR1) -> secondary (LOCO, seeds 1-3) -> FREEZE (ledger SE1).
No parameter of this driver can change a grid, threshold, seed, rule or data. It does not retry with changed settings."""
import sys,os,json,hashlib,time,csv,collections
import numpy as np,torch
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import phase1_run as RUN
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()
def ledger_append(ledger,rec):
    rows=[json.loads(l) for l in open(ledger)]; rec=dict(rec,prev_entry_sha256=hashlib.sha256(json.dumps(rows[-1],sort_keys=True).encode()).hexdigest() if rows else "GENESIS",ts_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())); open(ledger,"a").write(json.dumps(rec)+"\n"); return rec
def jdump(obj,path):
    json.dump(obj,open(path,"w"),indent=1,sort_keys=True,default=lambda o:o.tolist() if hasattr(o,"tolist") else str(o)); os.chmod(path,0o444); return sha(path)
def _grid_json(g): return {m:[dict(p) for p in pts] for m,pts in g.items()}
def execute(data,out_dir,ledger,comp_of_clip_fn=None):
    os.makedirs(out_dir,exist_ok=True); res={}
    for b,v in data.items():
        if not v["train"] or not v["dev"] or not v["test"]:
            r=dict(status="INCONCLUSIVE-DATA: analysis cannot be completed",backbone=b); h=jdump(r,os.path.join(out_dir,"primary_result.json")); ledger_append(ledger,dict(id="PR1",kind="PRIMARY_RESULT_FROZEN",result=r,sha256=h)); return r
    # ---- L1 training, TRAIN only, seed 0 ----
    heads_={}; trainrec={}
    for b in RUN.BACKBONE_ORDER:
        v=data[b]; head,hist=RUN.train_l1(v["train"],v["d"],0); heads_[b]=head
        pth=os.path.join(out_dir,f"L1_seed0_{b}.pt"); torch.save(head.state_dict(),pth); os.chmod(pth,0o444)
        trainrec[b]=dict(train_episode_ids=[e["id"] for e in v["train"]],d_in=v["d"],epochs=30,lr=0.01,seed=0,loss_history=hist,state_dict_sha256=sha(pth))
    th=jdump(trainrec,os.path.join(out_dir,"TRAIN_RECORD.json")); ledger_append(ledger,dict(id="TR1",kind="L1_TRAINED_SEED0_TRAIN_ONLY",sha256=th,state_dicts={b:trainrec[b]["state_dict_sha256"] for b in trainrec}))
    # ---- DEV only ----
    grids={b:RUN.grid_eval(data[b]["dev"],heads_[b]) for b in RUN.BACKBONE_ORDER}; sel=RUN.select_backbone(grids)
    rec=dict(record="DEV_SELECTION_RECORD",dev_episodes={b:[e["id"] for e in data[b]["dev"]] for b in grids},grids={b:_grid_json(g) for b,g in grids.items()},joint_levels={b:RUN.joint_levels(g) for b,g in grids.items()},backbone_selection=sel)
    if sel["status"]=="OK":
        b=sel["backbone"]; cs=sel["cstar"]; pb=RUN.select_point(grids[b]["B0"],cs); pl=RUN.select_point(grids[b]["L1"],cs)
        rec["selected_backbone"]=b; rec["selected_B0_point"]=pb; rec["selected_L1_point"]=pl
        rec["selected_points_at_cstar_all_eligible_backbones"]={x:dict(B0=RUN.select_point(grids[x]["B0"],cs),L1=RUN.select_point(grids[x]["L1"],cs)) for x in grids if RUN.joint_levels(grids[x])}
    dh=jdump(rec,os.path.join(out_dir,"DEV_SELECTION_RECORD.json")); ledger_append(ledger,dict(id="DS1",kind="DEV_SELECTION_RECORD_FROZEN_BEFORE_TEST",sha256=dh,status=sel["status"],selected_backbone=sel.get("backbone"),cstar=sel.get("cstar")))
    if sel["status"]!="OK":
        r=dict(status=sel["status"],reported_class="INCONCLUSIVE-DATA",uncapped_methodological_outcome="INCONCLUSIVE-DATA",reportable_status="INCONCLUSIVE-DATA",backbone_selection=sel,test_opened=False)
        h=jdump(r,os.path.join(out_dir,"primary_result.json")); ledger_append(ledger,dict(id="PR1",kind="PRIMARY_RESULT_FROZEN",sha256=h,reportable_status="INCONCLUSIVE-DATA",test_opened=False)); return r
    # ---- TEST exactly once ----
    if any(json.loads(l).get("id")=="TST0" for l in open(ledger)): raise SystemExit("TEST ALREADY OPENED: single-use violation")
    ledger_append(ledger,dict(id="TST0",kind="TEST_OPENED_SINGLE_USE",dev_selection_record_sha256=dh,note="TEST opened once for the primary analysis with DEV-selected backbone and operating points"))
    pb0=pb["param"]; pl1=pl["param"]; eps=data[b]["test"]; head=heads_[b]
    rb=[(ep,RUN.b0_rows(ep,*pb0)) for ep in eps]; rl=[(ep,RUN.l1_rows(head,ep,pl1[0])) for ep in eps]; Tb=RUN.unit_table(rb); Tl=RUN.unit_table(rl); dec=RUN.decide_outcome(Tb,Tl)
    with open(os.path.join(out_dir,"test_decisions.csv"),"w",newline="") as f:
        w=csv.writer(f); w.writerow(["method","episode","clip_id","shot","tracklet_id","frame","truth_id","accepted_role","best_role","score"])
        for name,rr in (("B0",rb),("L1",rl)):
            for ep,rows in rr:
                for r in rows: w.writerow([name,ep["id"],r["clip_id"],r["shot"],r["tracklet_id"],r["frame"],r["truth_id"],r["accepted_role"],r["best_role"],f'{r["score"]:.8f}'])
    with open(os.path.join(out_dir,"test_unit_table.csv"),"w",newline="") as f:
        w=csv.writer(f); w.writerow(["clip","shot","truth","stratum","B0_false_accept","L1_false_accept","B0_target_cov","L1_target_cov"])
        for k in sorted(Tb): w.writerow([k[0],k[1],k[2],"OTHER_NAMED_WRESTLER" if Tb[k]["named"] else k[2],int(Tb[k]["false"]),int(Tl[k]["false"]),(sum(Tb[k]["cov"])/len(Tb[k]["cov"]) if Tb[k]["cov"] else ""),(sum(Tl[k]["cov"])/len(Tl[k]["cov"]) if Tl[k]["cov"] else "")])
    for fn in ("test_decisions.csv","test_unit_table.csv"): os.chmod(os.path.join(out_dir,fn),0o444)
    prim=dict(record="PRIMARY_RESULT",backbone=b,cstar=sel["cstar"],B0_point=pb0,L1_point=pl1,dev_selection_record_sha256=dh,test_episodes=[e["id"] for e in eps],decision=dec,B0_metrics=RUN.table_metrics(Tb),L1_metrics=RUN.table_metrics(Tl),
              test_decisions_csv_sha256=sha(os.path.join(out_dir,"test_decisions.csv")),test_unit_table_csv_sha256=sha(os.path.join(out_dir,"test_unit_table.csv")),
              uncapped_methodological_outcome=dec["uncapped_methodological_outcome"],reportable_status=dec["reportable_status"],annotation_status="ANNOTATION-PROVISIONAL",human_reliability_gate="NOT SATISFIED AS SPECIFIED")
    ph=jdump(prim,os.path.join(out_dir,"primary_result.json")); ledger_append(ledger,dict(id="PR1",kind="PRIMARY_RESULT_FROZEN",sha256=ph,uncapped_methodological_outcome=prim["uncapped_methodological_outcome"],reportable_status=prim["reportable_status"]))
    res.update(primary=prim)
    # ---- consistency cross-check of the frozen pure pipeline (after freezing; cannot change anything) ----
    chk=RUN.run_primary(data); cc=dict(run_primary_status=chk.get("status"),run_primary_reported_class=chk.get("reported_class"),matches_driver=(chk.get("reported_class")==dec["reported_class"] and chk.get("operating_points",{}).get("B0")==pb0 and chk.get("operating_points",{}).get("L1")==pl1 and chk["backbone_selection"]["backbone"]==b))
    jdump(cc,os.path.join(out_dir,"consistency_check.json"))
    # ---- secondary, after primary is frozen ----
    v=data[b]; allep=v["train"]+v["dev"]+v["test"]; ids={}
    for e in allep: ids.setdefault(e["clip"],[]).extend([e["A"],e["B"]])
    comp=RUN.components({c:sorted(set(x)) for c,x in ids.items()})
    sec=dict(record="SECONDARY_DESCRIPTIVE_ONLY",note="cannot change the primary backbone, operating points, outcome or interpretation",loco=RUN.loco(allep,comp,v["d"]),variance_seeds_1_3=RUN.variance_seeds(v["train"],v["dev"],v["test"],v["d"],sel["cstar"],pb0))
    sh=jdump(sec,os.path.join(out_dir,"secondary_descriptive.json")); ledger_append(ledger,dict(id="SE1",kind="SECONDARY_DESCRIPTIVE_FROZEN",sha256=sh))
    res.update(secondary=sec,consistency=cc); return res
def load_real(frozen_dir,feat_dir):
    sm=os.path.join(frozen_dir,"SEED_EPISODE_MANIFEST_V2.json"); ex=os.path.join(frozen_dir,"EXTRACTION_FRAME_MANIFEST_V1.csv"); data={}
    for b in RUN.BACKBONE_ORDER:
        t=RUN.load_episode_tensors(frozen_dir,feat_dir,b,sm,ex); allc=t["train"]+t["dev"]+t["test"]; data[b]=dict(d=allc[0]["cand"].shape[1] if allc else 0,train=t["train"],dev=t["dev"],test=t["test"])
    return data
def main():
    import argparse; ap=argparse.ArgumentParser(); [ap.add_argument(x) for x in ("--frozen_dir","--feat_dir","--out_dir")]; a=ap.parse_args()
    from authorization_guard import require_bakeoff_authorization; require_bakeoff_authorization(a.frozen_dir)
    data=load_real(a.frozen_dir,a.feat_dir); r=execute(data,a.out_dir,os.path.join(a.frozen_dir,"AUDIT_LEDGER.jsonl"))
    print(json.dumps({k:r.get(k) for k in ("status",)} if "primary" not in r else {"uncapped":r["primary"]["uncapped_methodological_outcome"],"reportable":r["primary"]["reportable_status"]},default=str))
if __name__=="__main__": main()
