import sys,os,csv,json,tempfile,stat
sys.path.insert(0,".")
import pipeline_guard as PG, blind_sample as BS, adjudicate as AD, report_check as RC, phase1_metrics as M
d=tempfile.mkdtemp()
f=os.path.join(d,"in.txt"); open(f,"w").write("x"); h=PG.sha(f)
assert PG.verify_inputs({"a":(f,h)})
try: PG.verify_inputs({"a":(f,"0"*64)}); raise AssertionError
except SystemExit: pass
PG.run_manifest(os.path.join(d,"m.json"),{"in":f},[__file__])
PG.run_stage("echo",["echo","hi"],os.path.join(d,"log.jsonl"),lambda:[])
try: PG.run_stage("bad",["echo","hi"],os.path.join(d,"log.jsonl"),lambda:["empty"]); raise AssertionError
except SystemExit: pass
o=os.path.join(d,"out"); os.makedirs(o); open(os.path.join(o,"a.txt"),"w").write("a"); PG.freeze_dir(o); assert not PG.verify_frozen(o)
try: open(os.path.join(o,"a.txt"),"w").write("b"); changed=True
except PermissionError: changed=False
if os.geteuid()!=0: assert not changed
else:
    open(os.path.join(o,"a.txt"),"w").write("b"); assert PG.verify_frozen(o)==["a.txt"]  # root can write, but tampering is detected by hash
# blind sampling
c=os.path.join(d,"c.csv"); open(c,"w").write("clip_id,frame,det_idx,overlap\n"+"".join(f"c1,{i},0,{int(i%7==0)}\n" for i in range(100)))
h1,n=BS.select_frames(c,os.path.join(d,"s1.csv"),7,10,("overlap",),5); h2,_=BS.select_frames(c,os.path.join(d,"s2.csv"),7,10,("overlap",),5); assert h1==h2 and n>=10
# adjudication
lab=os.path.join(d,"lab.csv"); open(lab,"w").write("clip_id,tracklet_id,shot,label\nc1,t1,0,TARGET_A\nc1,t2,0,SPECTATOR\nc1,t3,1,TARGET_B\n"); BS.commit_labels(lab)
sy=os.path.join(d,"sy.csv"); open(sy,"w").write("clip_id,tracklet_id,frame,accepted_role,best_role,score\nc1,t1,1,w1,w1,0.9\nc1,t2,2,w1,w1,0.8\nc1,t3,3,,w2,0.1\n")
g=os.path.join(d,"g.json"); json.dump({"c1":{"A":"w1","B":"w2"}},open(g,"w"))
n,dis,unl=AD.run(lab,sy,g,os.path.join(d,"dec.csv"),os.path.join(d,"adj.csv")); assert (n,dis)==(3,1)
mm=M.metrics(list(csv.DictReader(open(os.path.join(d,"dec.csv"))))); assert mm["fta_by_negative_stratum"]["SPECTATOR"]["units_with_any_false_accept"]==1
open(lab,"a").write("c1,t9,2,TARGET_A\n")
try: AD.run(lab,sy,g,os.path.join(d,"dec.csv"),os.path.join(d,"adj.csv")); raise AssertionError
except SystemExit: pass
# report check
met={"a":{"cov":0.5,"n":30}}; txt=RC.render("Coverage {{a.cov}} over {{a.n}} units.",met); assert RC.verify(txt,met)==[]; assert RC.verify("Coverage 0.77 over 30 units.",met)==["0.77"]
print("selftest3 ok")
