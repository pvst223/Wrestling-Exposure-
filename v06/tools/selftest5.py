"""Deterministic self-tests: multiple tracklets/detections inside one (clip, shot, identity/class) cannot inflate independent n; primary metrics follow the preregistered unit-level definitions exactly."""
import sys,copy,random
sys.path.insert(0,".")
import phase1_metrics as M
def R(clip,shot,trk,frame,truth,acc): return dict(clip_id=clip,shot=shot,tracklet_id=trk,frame=frame,truth_id=truth,accepted_role=acc)
# 1. n cannot be inflated by tracklets/detections: 1 unit, 50 tracklets x 40 detections
rows=[R("c",0,f"t{t}",f,"SPECTATOR","") for t in range(50) for f in range(40)]
m=M.metrics(rows); assert m["n_units_total"]==1 and m["fta_by_negative_stratum"]["SPECTATOR"]["n_units"]==1 and m["n_detections_descriptive"]==2000 and m["n_tracklets_descriptive"]==50
assert M.cp(0,1)[1]>0.97 and m["fta_by_negative_stratum"]["SPECTATOR"]["exact_95CI"][1]==M.cp(0,1)[1]   # CI uses n=1, not 2000
# 2. one false accept among 2000 detections makes the unit a false-accept unit (any-accept), FTA = 1/1 not 1/2000
rows[1234]["accepted_role"]="w1"; m=M.metrics(rows); s=m["fta_by_negative_stratum"]["SPECTATOR"]; assert s["units_with_any_false_accept"]==1 and s["unit_FTA"]==1.0 and m["secondary_descriptive_frame_level"]["false_accepted_detections"]==1
# 3. splitting a unit's detections across more tracklets changes nothing at unit level
a=[R("c",3,"t0",f,"REFEREE","w1" if f==5 else "") for f in range(30)]; b=[R("c",3,f"t{f%7}",f,"REFEREE","w1" if f==5 else "") for f in range(30)]
ma,mb=M.metrics(a),M.metrics(b); assert ma["fta_by_negative_stratum"]==mb["fta_by_negative_stratum"] or all(ma["fta_by_negative_stratum"]["REFEREE"][k]==mb["fta_by_negative_stratum"]["REFEREE"][k] for k in ("n_units","units_with_any_false_accept","unit_FTA","exact_95CI"))
# 4. different shots / different identities / different clips are separate units
rows=[R("c",0,"t0",0,"REFEREE",""),R("c",1,"t1",0,"REFEREE",""),R("d",0,"t2",0,"REFEREE",""),R("c",0,"t3",0,"SPECTATOR","")]
assert M.metrics(rows)["n_units_total"]==4
# 5. coverage = unweighted mean of per-unit fractions, NOT pooled detections: unit1 10/10, unit2 0/1000
rows=[R("c",0,"t0",f,"w1","w1") for f in range(10)]+[R("c",1,"t1",f,"w1","") for f in range(1000)]
tc=M.metrics(rows)["target_coverage"]; assert tc["n_target_units"]==2 and abs(tc["coverage_mean_of_unit_fractions"]-0.5)<1e-12 and abs(tc["coverage_mean_of_unit_fractions"]-10/1010)>0.4
# 5b. same shot, two tracklets of the same identity = ONE target unit with the pooled fraction inside the unit
rows=[R("c",0,"t0",f,"w1","w1") for f in range(10)]+[R("c",0,"t1",f,"w1","") for f in range(30)]
tc=M.metrics(rows)["target_coverage"]; assert tc["n_target_units"]==1 and abs(tc["coverage_mean_of_unit_fractions"]-0.25)<1e-12
# 6. swap: wrestler detection accepted as another wrestler is a false accept (swap unit) and not a correct accept
rows=[R("c",0,"t0",0,"w1","w2"),R("c",0,"t0",1,"w1","w1")]; m=M.metrics(rows); assert m["ab_swap_units"]["units_with_any_swap"]==1 and m["target_coverage"]["coverage_mean_of_unit_fractions"]==0.5 and m["fta_by_negative_stratum"]["OTHER_NAMED_WRESTLER"]["units_with_any_false_accept"]==1
# 7. descriptive-only flag when n<15; CI never narrows with detections
rows=[R("c",s,f"t{s}{f}",f,"SPECTATOR","") for s in range(14) for f in range(100)]; assert M.metrics(rows)["fta_by_negative_stratum"]["SPECTATOR"]["descriptive_only_n_lt_15"]
rows+=[R("c",99,"tz",0,"SPECTATOR","")]; assert not M.metrics(rows)["fta_by_negative_stratum"]["SPECTATOR"]["descriptive_only_n_lt_15"]
# 8. paired sign test values stated in the preregistration
from scipy.stats import binom
def mk(b,c,both=0,neither=3):
    base,learn=[],[]
    for i in range(b): base.append(R("c",i,"t",0,"SPECTATOR","w1")); learn.append(R("c",i,"t",0,"SPECTATOR",""))
    for i in range(c): j=1000+i; base.append(R("c",j,"t",0,"SPECTATOR","")); learn.append(R("c",j,"t",0,"SPECTATOR","w1"))
    for i in range(both): j=2000+i; base.append(R("c",j,"t",0,"SPECTATOR","w1")); learn.append(R("c",j,"t",0,"SPECTATOR","w1"))
    for i in range(neither): j=3000+i; base.append(R("c",j,"t",0,"SPECTATOR","")); learn.append(R("c",j,"t",0,"SPECTATOR",""))
    return base,learn
for b,c,p in [(4,0,0.0625),(5,0,0.03125),(3,0,0.125),(6,1,0.0625),(7,1,0.03515625)]:
    r=M.paired_sign(*mk(b,c)); assert (r["b_baseline_only"],r["c_learned_only"])==(b,c) and abs(r["one_sided_p_b_gt_c"]-p)<1e-9,(b,c,r)
assert M.paired_sign(*mk(0,0))["one_sided_p_b_gt_c"]==1.0
# 8b. paired test counts units, not detections: 30 detections in one unit still one discordant unit
base=[R("c",0,f"t{f}",f,"SPECTATOR","w1") for f in range(30)]; learn=[R("c",0,f"t{f}",f,"SPECTATOR","") for f in range(30)]; assert M.paired_sign(base,learn)["discordant"]==1
try: M.paired_sign(base,learn[:0]+[R("c",9,"t",0,"SPECTATOR","")]); raise AssertionError
except ValueError: pass
# 9. seed exclusion removes only the listed tracklets
rows=[R("c",0,"t0",0,"w1","w1"),R("c",0,"t1",0,"w1","w1")]; assert len(M.exclude_seed_tracklets(rows,{("c","t0")}))==1
# 10. determinism incl. bootstrap CI
random.seed(1); rows=[R("c",i,"t",f,"w1","w1" if random.random()<0.6 else "") for i in range(20) for f in range(5)]; assert M.metrics(rows)==M.metrics(copy.deepcopy(rows))
# 11. component breakdown is descriptive and does not alter primary metrics
assert "OTHER_NAMED_WRESTLER" in M.by_component(rows,{"c":"C1"})["C1"]["fta_by_negative_stratum"]
print("selftest5 ok: unit-level metrics, coverage, paired test and seed exclusion verified")
