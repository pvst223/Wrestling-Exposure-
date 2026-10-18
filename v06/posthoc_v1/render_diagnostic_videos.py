"""Post-hoc VISUALIZATION of frozen Phase-1 behaviour. Uses frozen features/head/manifests/tracklets; no new inference intended to improve results.
One output frame per frozen candidate frame (every ~3rd source frame, shown at 10 fps); no interpolation; boxes are the frozen tracklet boxes; decisions use the frozen functions with frozen parameters (B0 tau=0.30 margin=0.02; L1 floor=0.80)."""
import sys,os,json,csv,collections,subprocess
import numpy as np,torch,cv2
T="/home/claude/proj/v06_phase1/tools"; sys.path.insert(0,T)
import phase1_run as RUN, phase1_execute as X, heads
FZ="/home/claude/proj/v06_phase1/frozen"; OUT=os.path.dirname(os.path.abspath(__file__)); B="mobileclip_b"
data=X.load_real(FZ,os.path.join(FZ,"features")); v=data[B]
head=heads.LearnedHead(v["d"]); head.load_state_dict(torch.load(os.path.join(FZ,"phase1_results",f"L1_seed0_{B}.pt"))); head.eval()
frz={}
for r in csv.DictReader(open(os.path.join(FZ,"phase1_results","test_decisions.csv"))): frz[(r["method"],r["clip_id"],r["tracklet_id"],int(r["frame"]))]=r["accepted_role"]
VIDS=[("DEV_lesnar_bryan","dev","b2_videoplayback_2"),("TEST_condensed_andrade_mysterio","test","b2_batch2_clip_condensed"),("TEST_andrade_omega","test","b2_videoplayback_5")]
NEG=__import__("phase1_metrics").NEG_CLASSES
def outcome(truth,acc,A,B_):
    tgt=truth in (A,B_)
    if tgt: return "OK" if acc==truth else ("MISS" if acc=="" else "SWAP-FA")
    return "FA" if acc!="" else "rej"
def col(o): return {"OK":(60,200,60),"rej":(160,160,160),"MISS":(0,200,255),"SWAP-FA":(0,0,255),"FA":(0,0,255)}[o]
res={}
for name,split,clip in VIDS:
    ep=[e for e in v[split] if e["clip"]==clip][0]
    rb=RUN.b0_rows(ep,0.3,0.02); rl=RUN.l1_rows(head,ep,0.8)
    e=RUN._tt(ep); e2=dict(e)
    if len(e2["seed_N"])==0: e2.pop("seed_N")
    with torch.no_grad(): P=torch.softmax(head.logits(e2),1).numpy()
    if split=="test":
        for r in rb: assert frz[("B0",clip,r["tracklet_id"],r["frame"])]==r["accepted_role"]
        for r in rl: assert frz[("L1",clip,r["tracklet_id"],r["frame"])]==r["accepted_role"]
    tr={t["tid"]:t for t in json.load(open(os.path.join(FZ,"tracklets",clip+".json")))}
    byf=collections.defaultdict(list)
    for i,(a,b_) in enumerate(zip(rb,rl)):
        t=tr[a["tracklet_id"]]; k=t["frames"].index(a["frame"]); byf[a["frame"]].append(dict(box=t["boxes"][k],truth=a["truth_id"],b0=a["accepted_role"],l1=b_["accepted_role"],p=P[i],tid=a["tracklet_id"]))
    cap=cv2.VideoCapture(os.path.join(FZ,"norm",clip+".mp4")); W,H=1280,720
    raw=os.path.join(OUT,name+"_raw.mp4"); vw=cv2.VideoWriter(raw,cv2.VideoWriter_fourcc(*"mp4v"),10,(W,H)); frames=sorted(byf); n=0; cnt=collections.Counter()
    want=set(frames); fi=0
    while True:
        ok,img=cap.read()
        if not ok: break
        if fi in want:
            img=cv2.resize(img,(W,H)); s=W/640.0
            for c in byf[fi]:
                x0,y0,x1,y1=[int(z*s) for z in c["box"]]; ob=outcome(c["truth"],c["b0"],ep["A"],ep["B"]); ol=outcome(c["truth"],c["l1"],ep["A"],ep["B"]); cnt["B0_"+ob]+=1; cnt["L1_"+ol]+=1
                bad=ob in("FA","SWAP-FA") or ol in("FA","SWAP-FA"); cv2.rectangle(img,(x0,y0),(x1,y1),(0,0,255) if bad else (200,200,200),3 if bad else 1)
                p=c["p"]; lines=[(f"truth: {c['truth']}",(255,255,255)),(f"B0 {c['b0'] or 'ABSTAIN/NT'} [{ob}]",col(ob)),(f"L1 {c['l1'] or 'ABSTAIN/NT'} [{ol}] max(pA,pB)={max(p[0],p[1]):.2f} pNT={p[2]:.2f}",col(ol))]
                yy=max(y0-4,48+len(lines)*16)
                for j,(tx,cc) in enumerate(reversed(lines)):
                    (tw,th),_=cv2.getTextSize(tx,cv2.FONT_HERSHEY_SIMPLEX,0.42,1); yb=yy-j*16; cv2.rectangle(img,(x0,yb-th-3),(x0+tw+4,yb+3),(0,0,0),-1); cv2.putText(img,tx,(x0+2,yb),cv2.FONT_HERSHEY_SIMPLEX,0.42,cc,1,cv2.LINE_AA)
            cv2.rectangle(img,(0,0),(W,40),(0,0,0),-1)
            cv2.putText(img,f"POST-HOC VISUALIZATION of FROZEN Phase-1 behaviour | {split.upper()} {clip} | targets A={ep['A']} B={ep['B']} | frame {fi}",(6,15),cv2.FONT_HERSHEY_SIMPLEX,0.45,(255,255,255),1,cv2.LINE_AA)
            cv2.putText(img,"frozen B0 tau=0.30 margin=0.02 | frozen L1 floor=0.80 | OK=correct accept, MISS=target not accepted, SWAP-FA=accepted as wrong wrestler, FA=non-target accepted, rej=non-target rejected",(6,33),cv2.FONT_HERSHEY_SIMPLEX,0.4,(200,255,255),1,cv2.LINE_AA)
            vw.write(img); n+=1
        fi+=1
    vw.release(); cap.release()
    fin=os.path.join(OUT,name+".mp4"); subprocess.run(["ffmpeg","-y","-loglevel","error","-i",raw,"-c:v","libx264","-pix_fmt","yuv420p","-crf","26",fin],check=True); os.remove(raw)
    res[name]=dict(path=fin,sha256=X.sha(fin),bytes=os.path.getsize(fin),output_frames=n,fps_out=10,outcome_counts=dict(cnt))
json.dump(res,open(os.path.join(OUT,"VIDEO_HASHES.json"),"w"),indent=1); print(json.dumps(res,indent=1))
