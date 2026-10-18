"""Synthetic selftests for PHASE1_IMPLEMENTATION_CLOSURE_V1 (B1-B7). Uses ONLY seeded synthetic arrays/videos (and the pinned weights on seeded random crops for adapter shape/equivalence checks). No experimental footage, features, labels-derived performance or training on real data."""
import os,sys,json,hashlib,tempfile,random,collections,itertools
import numpy as np,torch,cv2
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import phase1_structure as S,phase1_run as RUN,extract_features as X,heads,phase1_metrics as M,authorization_guard as AG
R="/home/claude/proj/v06_phase1/"; ok=lambda c,m: (c or (_ for _ in ()).throw(AssertionError(m)))
# ---- B1: sparse / non-contiguous frame keys ----
dets={0:dict(box=np.array([[10,10,60,110]],np.float32),conf=np.array([.9],np.float32),shape=(360,640)),3:dict(box=np.array([[12,10,62,112],[200,20,230,40]],np.float32),conf=np.array([.9,.9],np.float32),shape=(360,640)),9:dict(box=np.array([[14,12,64,114]],np.float32),conf=np.array([.9],np.float32),shape=(360,640)),30:dict(box=np.array([[16,12,66,114]],np.float32),conf=np.array([.9],np.float32),shape=(360,640))}
trk=[dict(tid="c:s0:t0",clip="c",shot=0,frames=[0,3,9,30],boxes=[[10,10,60,110],[12,10,62,112],[14,12,64,114],[16,12,66,114]])]
keys,rows=S.extraction_rows("c",dets,trk); ok(keys==[0,3,9,30],"keys ascending actual"); ok([r["frame"] for r in rows]==[0,3,9,30] and all(r["det"]==0 for r in rows),"only retained tracklet dets, no synthesis")
ok(S.extraction_rows("c",dets,trk,frame_limit=10)[0]==[0,3,9],"exclusion limit")
tmp=tempfile.mkdtemp(); vp=os.path.join(tmp,"v.mp4"); w=cv2.VideoWriter(vp,cv2.VideoWriter_fourcc(*"mp4v"),30,(640,360)); rng=np.random.RandomState(0)
for i in range(31): w.write(rng.randint(0,255,(360,640,3),dtype=np.uint8))
w.release()
class Dummy(torch.nn.Module):
    def forward(self,x): return x.mean((2,3))
mrows=[(r["frame"],r["det"],r["tid"],r["crop_ok"]) for r in rows]
K,E=X.extract_clip(vp,dets,mrows,Dummy(),"mobileclip_b")
ok(K.tolist()==[[0,0],[3,0],[9,0],[30,0]] and E.shape==(4,3),"extract_clip sparse-safe"); ok(np.allclose(np.linalg.norm(E,axis=1),1,atol=1e-5),"L2 norm")
# ---- B2: adapters (pinned weights, seeded random crops) ----
g=np.random.RandomState(1); crops=[g.randint(0,255,(224,224,3),dtype=np.uint8) for _ in range(2)]
from PIL import Image; import torchvision.transforms as T
ref=torch.stack([T.Compose([T.Resize((256,128)),T.ToTensor(),T.Normalize(X.IMNET_MEAN,X.IMNET_STD)])(Image.fromarray(c)) for c in crops])
ok(torch.equal(ref,X.prep_osnet(crops)),"OSNet preprocessing identical to official torchreid test pipeline (PIL BILINEAR resize + ToTensor + ImageNet norm)")
ok(X.prep_osnet(crops).shape==(2,3,256,128) and X.prep_imagenet(crops).shape==(2,3,224,224),"prep shapes")
W=R+"frozen/artifacts/"
md=X.load_backbone("dinov2_vits14",W+"dinov2_vits14_pretrain.pth",R+"frozen/dep_source/dinov2_code"); e=X.embed(md,"dinov2_vits14",crops); ok(e.shape==(2,384),"dinov2 dim"); ok(np.allclose(e,X.embed(md,"dinov2_vits14",crops)),"dinov2 deterministic")
mo=X.load_backbone("osnet_x1_0",W+"osnet_x1_0_msmt17_combineall_256x128_amsgrad_ep150_stp60_lr0.0015_b64_fb10_softmax_labelsmooth_flip_jitter.pth",R+"frozen/dep_source/deep-person-reid_code"); e=X.embed(mo,"osnet_x1_0",crops); ok(e.shape==(2,512),"osnet dim"); ok(np.allclose(e,X.embed(mo,"osnet_x1_0",crops)),"osnet deterministic")
try:
    mm=X.load_backbone("mobileclip_b","/home/claude/proj/v04/models/mobileclip_blt.ts"); e=X.embed(mm,"mobileclip_b",crops); mc_dim=e.shape[1]; ok(e.shape[0]==2,"mobileclip rows")
except Exception as ex: mc_dim="LOAD_ERROR:"+repr(ex)[:120]
# ---- B4: deterministic seeds, pairwise 3-wrestler episodes, seed removal ----
def synth_clip(ids=("c_wrestler","a_wrestler","b_wrestler"),n_shots=8,seed=0,ndet=6):
    r=random.Random(seed); T_=[];lab={};di={};tid=0
    for wi,w in enumerate(ids):
        for s in range(n_shots):
            f0=s*400+wi*10; fr=[f0+3*k for k in range(ndet)]; h=[r.uniform(60,200) for _ in fr]
            t=f"cl:s{s}:t{tid}"; tid+=1; T_.append(dict(tid=t,clip="cl",shot=s,frames=fr,boxes=[[0,0,50,hh] for hh in h])); lab[t]=dict(tid=t,person_class="WRESTLER",wrestler_id=w,multi_person_flag="0"); di[t]=list(range(len(fr)))
    for s in range(n_shots):
        t=f"cl:s{s}:t{tid}"; tid+=1; T_.append(dict(tid=t,clip="cl",shot=s,frames=[s*400+300+3*k for k in range(6)],boxes=[[0,0,50,100]]*6)); lab[t]=dict(tid=t,person_class="REFEREE",wrestler_id="",multi_person_flag="0"); di[t]=list(range(6))
    t=f"cl:s0:t{tid}"; T_.append(dict(tid=t,clip="cl",shot=0,frames=[1000+3*k for k in range(6)],boxes=[[0,0,50,100]]*6)); lab[t]=dict(tid=t,person_class="SPECTATOR",wrestler_id="",multi_person_flag="0"); di[t]=list(range(6))
    return T_,lab,di
Tt,lab,di=synth_clip(); a=S.build_clip("cl","test",Tt,lab,di); b=S.build_clip("cl","test",Tt,lab,di)
ok(json.dumps(a,sort_keys=True,default=str)==json.dumps(b,sort_keys=True,default=str),"seed selection deterministic")
ok([e["id"] for e in a["episodes"]]==["cl|a_wrestler|b_wrestler","cl|a_wrestler|c_wrestler","cl|b_wrestler|c_wrestler"],"3 named -> 3 unordered pairs, lexicographic A/B")
for w,info in a["target_seed_info"].items():
    ok(info["status"]=="OK" and len(info["seeds"])==4 and len({s["shot"] for s in info["seeds"]})==4,"4 distinct shots")
    fr=sorted(s["frame"] for s in info["seeds"]); ok(all(y-x>=60 for x,y in zip(fr,fr[1:])),">=2 s apart"); ok(all(s["box_h"]>=info["median_h"] for s in info["seeds"]),">= median height")
e0=a["episodes"][0]; ok(e0["online_N"]==[],"online_N empty")
ok(any(s["source"]=="NAMED_NONTARGET:c_wrestler" for s in e0["seed_N"]) and any(s["source"]=="REFEREE" for s in e0["seed_N"]),"seed_N = referee seeds + third wrestler seeds")
ok(e0["seed_A"]==a["episodes"][1]["seed_A"] and e0["seed_B"]==a["episodes"][2]["seed_A"],"same physical seeds reused across pairs")
cands={c["tid"]:c for c in e0["candidate_tracklets"]}; ok(all(s["tid"] not in cands for s in e0["seed_A"]+e0["seed_B"]+e0["seed_N"]),"seed tracklets removed from candidates")
ok({c["truth"]:c["y"] for c in cands.values() if c["truth"] in ("a_wrestler","b_wrestler","c_wrestler")}=={"a_wrestler":0,"b_wrestler":1,"c_wrestler":2},"y: A=0,B=1,third wrestler NON-TARGET=2")
Tt2,lab2,di2=synth_clip(n_shots=1); a2=S.build_clip("cl","train",Tt2,lab2,di2); ok(all(e["status"]=="UNEVALUABLE" for e in a2["episodes"]),"<2 distinct shots -> UNEVALUABLE, rule not relaxed further")
Tt3,lab3,di3=synth_clip(n_shots=2,ndet=30); a3=S.build_clip("cl","train",Tt3,lab3,di3); ok(all(e["status"]=="OK" for e in a3["episodes"]),"2 shots x up to 2 seeds -> amended rule feasible")
for w,info in a3["target_seed_info"].items(): ok(len(info["seeds"])==4 and info["n_represented_shots"]==2 and all(sum(1 for x in info["seeds"] if x["shot"]==s_)<=2 for s_ in (0,1)),"amended: 4 seeds, 2 shots, <=2 per shot")
# explicit capacity limits: one shot with only 1 usable detection and one with 2 -> 3 < 4 -> UNEVALUABLE; two shots with 2 each but gap violation -> UNEVALUABLE
mk=lambda spec:[dict(frame=f,det=0,tid="t%d"%i,shot=s_,box_h=100.0) for i,(s_,f) in enumerate(spec)]
ok(S.select_target_seeds("c","w",mk([(0,0),(0,100),(1,200)]))["status"]=="INSUFFICIENT_SEEDS","3 usable detections -> UNEVALUABLE")
ok(S.select_target_seeds("c","w",mk([(0,0),(0,30),(1,200),(1,500)]))["status"]=="INSUFFICIENT_SEEDS","gap violation inside a shot -> UNEVALUABLE")
ok(S.select_target_seeds("c","w",mk([(0,0),(0,100),(0,200),(1,500),(1,700)]))["status"]=="OK","max 2 per shot but >=2 shots feasible")
ok(S.select_target_seeds("c","w",mk([(0,0),(0,100),(0,200),(0,300)]))["status"]=="INSUFFICIENT_SEEDS","single shot (4 detections) -> UNEVALUABLE")
ok(S.select_target_seeds("c","w",mk([(0,0),(0,100),(0,200),(1,500)]))["status"]=="INSUFFICIENT_SEEDS","cap of 2 seeds per shot prevents a 3+1 split")
# ---- B5: no dev/test contamination in training ----
def mk_ep(i,split,rng,n=12,d=6,A="a",B="b"):
    cand=rng.randn(n,d).astype(np.float32); y=np.array([0,1,2]*(n//3));
    cand[y==0]+=np.eye(d)[0]*3; cand[y==1]+=np.eye(d)[1]*3; cand[y==2]+=np.eye(d)[2]*3
    sh=lambda k,m: (rng.randn(k,d)+np.eye(d)[m]*3).astype(np.float32)
    meta=[dict(tid=f"{i}:t{j}",frame=3*j,shot=j,truth=(A,B,"REFEREE")[y[j]]) for j in range(n)]
    return dict(id=f"{split}{i}",clip=f"{split}{i}",split=split,A=A,B=B,seed_A=sh(4,0),seed_B=sh(4,1),seed_N=sh(2,2),cand=cand,y=y,meta=meta)
rng=np.random.RandomState(3); tr=[mk_ep(i,"train",rng) for i in range(2)]; dv=[mk_ep(i,"dev",rng) for i in range(2)]; te=[mk_ep(i,"test",rng) for i in range(2)]
seen=[]; orig=heads.train
def spy(head,eps,**kw): seen.append(len(eps)); return orig(head,eps,**kw)
heads.train=spy; head,hist=RUN.train_l1(tr,6,0); heads.train=orig; ok(seen==[2],"L1 sees exactly the TRAIN episodes"); ok(hist[-1]<hist[0],"training reduces loss (synthetic)")
h2,_=RUN.train_l1(tr,6,0); ok(all(torch.equal(p,q) for p,q in zip(head.parameters(),h2.parameters())),"training deterministic given seed 0")
# ---- B6/B7: metrics equivalence, rows, margin/score ----
ep=dv[0]; rows_=RUN.b0_rows(ep,0.5,0.05); rowsM=[dict(r) for r in rows_]
Tbl=RUN.unit_table([(ep,rows_)]); mm=M.metrics_core(rowsM); tm=RUN.table_metrics(Tbl); ok(abs(mm["unit_FTA"]-tm["fta"])<1e-12 and abs(mm["coverage_mean_of_unit_fractions"]-tm["coverage"])<1e-12,"unit table == frozen phase1_metrics for single episode")
lr=RUN.l1_rows(head,ep,0.6); e_=RUN._tt(ep);
if len(e_["seed_N"])==0: e_.pop("seed_N")
labs,p=heads.decide(head,e_,tau=0.6,margin=0.0); ok(RUN.L1_MARGIN==0.0,"margin fixed 0.0")
for i,r in enumerate(lr):
    ok(abs(r["score"]-max(p[i,0],p[i,1]))<1e-12,"score = max(pA,pB) before floor")
    if labs[i]=="NONTARGET": ok(r["accepted_role"]=="","NON-TARGET argmax is not acceptance")
    if labs[i] in("A","B"): ok(r["accepted_role"]==ep[labs[i]] and p[i,("A","B").index(labs[i])]>=0.6,"acceptance needs argmax target and floor")
# sign test
def tab(false_idx,n=20,named=True,trunc="x"):
    return {("c",str(i),f"w{i%2}" if named else "REFEREE"):dict(false=(i in false_idx),cov=[0.5] if named else [],named=named) for i in range(n)}
for (b,c,pexp) in ((4,0,0.0625),(5,0,0.03125),(3,0,0.125),(6,1,0.0625),(7,1,0.03515625)):
    pw=RUN.paired(tab(set(range(b))),tab(set(range(b,b+c)))); ok(pw["b_baseline_only"]==b and pw["c_learned_only"]==c and abs(pw["one_sided_p_b_gt_c"]-pexp)<1e-9,f"sign test b={b} c={c}")
# c*, edge, selection, tie-breaking
def G(b0cov,l1cov): return dict(B0=[dict(param=(0.3+0.1*i,0.0),fta=0.1*i,coverage=c) for i,c in enumerate(b0cov)],L1=[dict(param=(0.4+0.1*i,),fta=0.1*i,coverage=c) for i,c in enumerate(l1cov)])
jl=RUN.joint_levels(G([0.35,0.2],[0.6,0.1])); ok(jl==[0.30,0.20,0.10],"c* normal levels"); ok(max(jl)==0.30,"c*=0.30")
ok(RUN.joint_levels(G([0.05],[0.9]))==[],"no joint coverage -> empty (INCONCLUSIVE-DATA)")
s=RUN.select_backbone({"osnet_x1_0":G([0.05],[0.9]),"dinov2_vits14":G([0.05],[0.9]),"mobileclip_b":G([0.0],[0.0])}); ok(s["status"].startswith("INCONCLUSIVE-DATA") and s["cstar"] is None,"no joint coverage anywhere")
g1=G([0.5,0.2],[0.5]); g2=G([0.4,0.3],[0.4]); sb=RUN.select_backbone({"osnet_x1_0":g1,"dinov2_vits14":g2}); ok(sb["cstar"]==0.4,"common c* across backbones")
pts=[dict(param=(0.3,0.0),fta=0.2,coverage=0.5),dict(param=(0.4,0.0),fta=0.2,coverage=0.6),dict(param=(0.5,0.0),fta=0.2,coverage=0.6),dict(param=(0.6,0.0),fta=0.1,coverage=0.1)]
ok(RUN.select_point(pts,0.5)["param"]==(0.4,0.0),"tie: lowest FTA, then highest coverage, then lexicographic params"); ok(RUN.select_point(pts,0.1)["param"]==(0.6,0.0),"lowest FTA wins"); ok(RUN.select_point(pts,0.9) is None,"none reachable")
ta=G([0.3,0.3],[0.3]); tb_=G([0.3,0.3],[0.3]); ok(RUN.select_backbone({"mobileclip_b":ta,"dinov2_vits14":tb_})["backbone"]=="dinov2_vits14","backbone tie -> fixed order (osnet, dinov2, mobileclip)")
# outcome classes (annotation gate True fixtures) and capping
def two(fb,fl,n=20,extra_fl_ref=0,ref_fb=0):
    Tb={};Tl={}
    for i in range(n):
        k=("c",str(i),f"w{i%2}"); Tb[k]=dict(false=i in fb,cov=[0.5],named=True); Tl[k]=dict(false=i in fl,cov=[0.5],named=True)
    for i in range(n):
        k=("c",str(100+i),"REFEREE"); Tb[k]=dict(false=i<ref_fb,cov=[],named=False); Tl[k]=dict(false=i<extra_fl_ref,cov=[],named=False)
    return Tb,Tl
d=RUN.decide_outcome(*two(set(range(6)),set()),annotation_gate_satisfied=True); ok(d["reported_class"]=="KEEP","KEEP")
d=RUN.decide_outcome(*two(set(range(6)),set(range(6))|{6}),annotation_gate_satisfied=True); ok(d["reported_class"]=="KILL","KILL")
d=RUN.decide_outcome(*two({0,1},set()),annotation_gate_satisfied=True); ok(d["reported_class"]=="INCONCLUSIVE-DATA","INCONCLUSIVE (baseline <5 false-accept units)")
d=RUN.decide_outcome(*two(set(range(6)),set(range(3))),annotation_gate_satisfied=True); ok(d["reported_class"]=="MODIFY","MODIFY (insufficient discordance)")
Tb,Tl=two(set(range(15)),set(),extra_fl_ref=3); d=RUN.decide_outcome(Tb,Tl,annotation_gate_satisfied=True)
ok(d["crit1_sign_test"] and not d["crit3_strata"] and d["reported_class"]=="MODIFY" and d["strata"]["REFEREE"]["violates"],"criterion 3: stratum n>=15 with >=3 extra learned false-accept units blocks KEEP")
Tb,Tl=two(set(range(15)),set(),extra_fl_ref=3,n=10); ok(not RUN.decide_outcome(Tb,Tl,True)["strata"]["REFEREE"]["eligible"],"stratum n<15 descriptive only")
d=RUN.decide_outcome(*two(set(range(6)),set()),annotation_gate_satisfied=False); ok(d["uncapped_methodological_outcome"]=="KEEP" and d["reportable_status"].startswith("KEEP, ANNOTATION-PROVISIONAL") and "no stronger than MODIFY" in d["reportable_status"],"D6: favourable KEEP reported provisional, no stronger than MODIFY")
d=RUN.decide_outcome(*two(set(range(6)),set(range(6))|{6}),annotation_gate_satisfied=False); ok(d["uncapped_methodological_outcome"]=="KILL" and d["reportable_status"]=="KILL (ANNOTATION-PROVISIONAL)","D6: KILL stays KILL despite unmet annotation gate")
d=RUN.decide_outcome(*two({0,1},set()),annotation_gate_satisfied=False); ok(d["reportable_status"]=="INCONCLUSIVE-DATA","D6: INCONCLUSIVE-DATA takes precedence")
ok(RUN.ANNOTATION_GATE_SATISFIED is False,"study constant: gate not satisfied")
# coverage criterion
Tb,Tl=two(set(range(6)),set())
for k in Tl:
    if Tl[k]["cov"]: Tl[k]["cov"]=[0.3]
ok(not RUN.decide_outcome(Tb,Tl,True)["crit2_coverage"],"coverage loss > 0.10 fails criterion 2")
# fail-closed: no evaluable train/dev/test episodes
r=RUN.run_primary({"osnet_x1_0":dict(d=6,train=[],dev=dv,test=te)}); ok(r["reported_class"]=="INCONCLUSIVE-DATA" and "train" in r["status"],"no train episodes -> INCONCLUSIVE-DATA, nothing trained")
# end-to-end synthetic run_primary + loco + variance
data={b:dict(d=6,train=tr,dev=dv,test=te) for b in RUN.BACKBONE_ORDER}; r=RUN.run_primary(data); ok(r["status"]=="OK" and ("ANNOTATION-PROVISIONAL" in r["reported_class"] or r["reported_class"]=="INCONCLUSIVE-DATA"),"end-to-end synthetic")
comp=RUN.components({"c1":["a","b"],"c2":["b","c"],"c3":["x","y"]}); ok(comp["c1"]==comp["c2"] and comp["c1"]!=comp["c3"],"LOCO components via shared identities")
lo=RUN.loco(tr+dv+te,{e["clip"]:("g%d"%(i%2)) for i,e in enumerate(tr+dv+te)},6); ok(set(lo)=={"g0","g1"},"loco runs (synthetic)")
vr=RUN.variance_seeds(tr,dv,te,6,r["backbone_selection"]["cstar"],r["operating_points"]["B0"]); ok(set(vr)=={1,2,3},"variance seeds 1-3")
# ---- loader on real structural manifests with RANDOM synthetic feature caches (no real features; run_primary is NOT executed on them) ----
import csv as _csv
td=tempfile.mkdtemp(); rr=collections.defaultdict(list)
for r_ in _csv.DictReader(open(R+"frozen/EXTRACTION_FRAME_MANIFEST_V1.csv")): rr[r_["clip"]].append((int(r_["frame"]),int(r_["det"])))
g_=np.random.RandomState(7)
for clip_,L_ in rr.items(): np.savez(os.path.join(td,f"feat_osnet_x1_0_{clip_}_x.npz"),frame=np.array([a for a,b in L_]),det=np.array([b for a,b in L_]),emb=g_.randn(len(L_),8).astype(np.float32))
ld=RUN.load_episode_tensors(R+"frozen",td,"osnet_x1_0",R+"frozen/SEED_EPISODE_MANIFEST_V2.json",R+"frozen/EXTRACTION_FRAME_MANIFEST_V1.csv")
ok([len(ld["train"]),len(ld["dev"]),len(ld["test"])]==[1,1,2],"loader: evaluable episodes per split on real structure (1 train, 1 dev, 2 test)")
for sp_ in ld.values():
    for e_ in sp_: ok(e_["cand"].shape[0]==len(e_["meta"])==len(e_["y"]) and e_["seed_A"].shape==(4,8) and e_["seed_B"].shape==(4,8) and set(np.unique(e_["y"]))<={0,1,2},"loader shapes/labels")
# ---- authorization guard fails closed on the real ledger ----
try: AG.require_bakeoff_authorization(R+"frozen"); raise AssertionError("guard did not fail closed")
except SystemExit as e: ok("NOT AUTHORIZED" in str(e),"guard fail-closed message")
# ---- manifests regenerate bit-identically (structural determinism) ----
a1=S.build_all(R); a2=S.build_all(R); ok(json.dumps(a1[2],sort_keys=True,default=str)==json.dumps(a2[2],sort_keys=True,default=str) and a1[0]==a2[0],"real structural manifests regenerate identically")
print("selftest6 ok: B1-B7 synthetic tests pass; mobileclip dim =",mc_dim,"| no experimental features/training/decisions")
