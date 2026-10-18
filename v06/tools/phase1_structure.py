"""Structural (label/model-free of performance) materialisation for Phase 1 closure. PHASE1_IMPLEMENTATION_CLOSURE_V1.
Builds, deterministically, from frozen artefacts ONLY (detections, tracklets, first-pass labels, splits):
  (1) EXTRACTION_FRAME_MANIFEST_V1.csv : for every clip, the sorted frame keys present in the frozen detection dict (B3) and the retained-tracklet detections (frame, det_index) to be embedded.
  (2) SEED_EPISODE_MANIFEST_V1.json    : deterministic seed selection (seed 20261018) and unordered pairwise episodes (B4), plus the exhaustive TRAIN episode list (B5).
It computes no features, trains nothing, makes no decisions and calculates no performance. Pure functions are used by selftest6.py with synthetic fixtures.
Closure decisions (recorded in PHASE1_IMPLEMENTATION_CLOSURE_V1.md): see that record; every choice below is non-performance-based.
"""
import csv,json,pickle,glob,os,random,statistics,itertools,hashlib,sys
import numpy as np
EPISODE_SEED=20261018; N_TARGET_SEEDS=4; N_REF_SEEDS=2; MIN_GAP_FRAMES=60   # 2 s at the frozen 30 fps
MIN_SIDE=24
NEG_MAP={"REFEREE":"REFEREE","RINGSIDE_STAFF":"STAFF","SPECTATOR":"SPECTATOR","OTHER_WRESTLER_UNNAMED":"OTHER_WRESTLER_UNNAMED"}
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()
def det_index_of(dets,frame,box):
    """Index j of the detection in dets[frame] whose box equals the tracklet box (tracklets store float(box)); must be unique."""
    d=dets[frame]; b=np.asarray(box,float); hits=[j for j in range(len(d["conf"])) if np.allclose(np.asarray(d["box"][j],float),b,atol=1e-4,rtol=0)]
    if len(hits)!=1: raise SystemExit(f"AMBIGUOUS/ABSENT det match frame {frame} box {box} hits {hits}")
    return hits[0]
def crop_ok(box,shape):
    x1,y1,x2,y2=[int(round(v)) for v in box]; H,W=shape[0],shape[1]; x1=max(0,x1);y1=max(0,y1);x2=min(W,x2);y2=min(H,y2)
    return (x2-x1)>=MIN_SIDE and (y2-y1)>=MIN_SIDE
def extraction_rows(clip,dets,tracklets,frame_limit=None):
    """B3/B1: iterate ascending over ACTUAL frame keys; only retained-tracklet detections; no synthesis."""
    keys=sorted(dets.keys());
    if frame_limit is not None: keys=[k for k in keys if k<frame_limit]
    allowed=set(keys); by_frame={}
    for t in tracklets:
        for f,b in zip(t["frames"],t["boxes"]):
            if f not in allowed: continue
            by_frame.setdefault(f,[]).append((det_index_of(dets,f,b),t["tid"],b))
    rows=[]
    for f in keys:
        for j,tid,b in sorted(by_frame.get(f,[])):
            rows.append(dict(clip=clip,frame=f,det=j,tid=tid,box_h=round(b[3]-b[1],3),crop_ok=int(crop_ok(b,dets[f]["shape"]))))
    return keys,rows
# ---------------- seeds / episodes ----------------
def _gap_ok(frame,chosen): return all(abs(frame-c["frame"])>=MIN_GAP_FRAMES for c in chosen)
def select_target_seeds_v1_superseded(clip,identity,cands,seed=EPISODE_SEED):
    """cands: list of dict(frame,det,tid,shot,box_h) = eligible detections of this target in this clip (multi-person tracklets already excluded). Rule: box_h >= median of eligible heights; 4 detections from 4 distinct shots, pairwise >= 60 frames apart; seeded greedy over shuffled shots, one seeded choice per shot."""
    if not cands: return dict(status="NO_ELIGIBLE",median_h=None,n_eligible=0,seeds=[])
    med=statistics.median(c["box_h"] for c in cands); q=sorted([c for c in cands if c["box_h"]>=med],key=lambda c:(c["frame"],c["det"]))
    rng=random.Random(f"{seed}|{clip}|{identity}|target"); shots=sorted({c["shot"] for c in q}); rng.shuffle(shots); chosen=[]
    for s in shots:
        pool=[c for c in q if c["shot"]==s]; pool=pool[:]; rng.shuffle(pool)
        pick=next((c for c in pool if _gap_ok(c["frame"],chosen)),None)
        if pick is not None: chosen.append(pick)
        if len(chosen)==N_TARGET_SEEDS: break
    return dict(status="OK" if len(chosen)==N_TARGET_SEEDS else "INSUFFICIENT_SEEDS",median_h=float(med),n_eligible=len(cands),n_qualifying=len(q),seeds=sorted(chosen,key=lambda c:(c["frame"],c["det"])))
MAX_PER_SHOT=2; MIN_SHOTS=2
def select_target_seeds(clip,identity,cands,seed=EPISODE_SEED):
    """AMENDED rule (SEED_FEASIBILITY_AMENDMENT_V1, uniform for all splits): exactly 4 seeds from >= 2 distinct shots, <= 2 per shot, pairwise >= 60 frames apart, box_h >= clip/target median of eligible detections, seed 20261018. Exhaustive deterministic DFS: UNEVALUABLE only if no valid 4-subset exists."""
    if not cands: return dict(status="NO_ELIGIBLE",median_h=None,n_eligible=0,n_qualifying=0,n_qualifying_shots=0,seeds=[])
    med=statistics.median(c["box_h"] for c in cands); q=sorted([c for c in cands if c["box_h"]>=med],key=lambda c:(c["frame"],c["det"]))
    rng=random.Random(f"{seed}|{clip}|{identity}|target"); shots=sorted({c["shot"] for c in q}); rng.shuffle(shots); per={}
    for s_ in shots:
        pool=[c for c in q if c["shot"]==s_]; rng.shuffle(pool); per[s_]=pool
    order=[]; r=0
    while any(r<len(per[s_]) for s_ in shots):
        order+=[per[s_][r] for s_ in shots if r<len(per[s_])]; r+=1
    best=[None]
    def dfs(start,chosen):
        if len(chosen)==N_TARGET_SEEDS:
            if len({c["shot"] for c in chosen})>=MIN_SHOTS: best[0]=list(chosen); return True
            return False
        for i in range(start,len(order)):
            c=order[i]
            if sum(1 for x in chosen if x["shot"]==c["shot"])>=MAX_PER_SHOT or not _gap_ok(c["frame"],chosen): continue
            chosen.append(c)
            if dfs(i+1,chosen): return True
            chosen.pop()
        return False
    ok=len({c["shot"] for c in q})>=MIN_SHOTS and dfs(0,[])
    chosen=best[0] if ok else []
    return dict(status="OK" if ok else "INSUFFICIENT_SEEDS",median_h=float(med),n_eligible=len(cands),n_qualifying=len(q),n_qualifying_shots=len({c["shot"] for c in q}),seeds=sorted(chosen,key=lambda c:(c["frame"],c["det"])))
def select_referee_seeds(clip,cands,seed=EPISODE_SEED):
    """2 seeds from eligible referee detections; distinct shots preferred, else same shot >= 60 frames apart; fewer if infeasible (recorded)."""
    if not cands: return dict(status="NO_REFEREE",seeds=[],n_eligible=0)
    q=sorted(cands,key=lambda c:(c["frame"],c["det"])); rng=random.Random(f"{seed}|{clip}|referee"); shots=sorted({c["shot"] for c in q}); rng.shuffle(shots); chosen=[]
    for s in shots:
        pool=[c for c in q if c["shot"]==s]; rng.shuffle(pool); pick=next((c for c in pool if _gap_ok(c["frame"],chosen)),None)
        if pick is not None: chosen.append(pick)
        if len(chosen)==N_REF_SEEDS: break
    if len(chosen)<N_REF_SEEDS:
        rest=q[:]; rng.shuffle(rest)
        for c in rest:
            if c not in chosen and _gap_ok(c["frame"],chosen): chosen.append(c)
            if len(chosen)==N_REF_SEEDS: break
    return dict(status="OK" if len(chosen)==N_REF_SEEDS else "FEWER_THAN_2",seeds=sorted(chosen,key=lambda c:(c["frame"],c["det"])),n_eligible=len(cands))
def pair_episodes(identities):
    """Unordered pairs in lexicographic canonical order; A = lexicographically smaller identity."""
    ids=sorted(identities); return [(a,b) for a,b in itertools.combinations(ids,2)]
def build_clip(clip,split,tracklets,labels,dets_index):
    """tracklets: list of tracklet dicts; labels: tid -> dict(person_class,wrestler_id,multi_person_flag); dets_index: (frame,box)->det via tracklet['dets'] map (dict tid -> list of det idx aligned with frames).
    Returns dict with seeds, episodes."""
    tr={t["tid"]:t for t in tracklets}; lab={t:labels[t] for t in tr if t in labels and labels[t]["person_class"]!="UNLABELABLE"}
    wrest=sorted({l["wrestler_id"] for l in lab.values() if l["person_class"]=="WRESTLER"})
    def dets_of(tids):
        out=[]
        for tid in tids:
            t=tr[tid]
            for f,b,j in zip(t["frames"],t["boxes"],dets_index[tid]): out.append(dict(frame=f,det=j,tid=tid,shot=t["shot"],box_h=float(b[3]-b[1])))
        return out
    target_info={}
    for w in wrest:
        tids=[tid for tid,l in lab.items() if l["person_class"]=="WRESTLER" and l["wrestler_id"]==w and l["multi_person_flag"]=="0"]
        target_info[w]=select_target_seeds(clip,w,dets_of(tids)); sd=target_info[w]["seeds"]; fr=sorted(x["frame"] for x in sd)
        target_info[w]["n_represented_shots"]=len({x["shot"] for x in sd}); target_info[w]["selected_shot_ids"]=[x["shot"] for x in sd]; target_info[w]["selected_tracklet_ids"]=[x["tid"] for x in sd]; target_info[w]["selected_frame_ids"]=[x["frame"] for x in sd]
        target_info[w]["pairwise_separations_frames"]={f"{a}-{b}":abs(a-b) for a,b in itertools.combinations(fr,2)}
    ref_tids=[tid for tid,l in lab.items() if l["person_class"]=="REFEREE" and l["multi_person_flag"]=="0"]
    ref_info=select_referee_seeds(clip,dets_of(ref_tids))
    def seed_tids(info): return {s["tid"] for s in info["seeds"]}
    episodes=[]
    for a,b in pair_episodes(wrest):
        status="OK" if target_info[a]["status"]=="OK" and target_info[b]["status"]=="OK" else "UNEVALUABLE"
        reason=[f"{w}:{target_info[w]['status']}" for w in (a,b) if target_info[w]["status"]!="OK"]
        others=[w for w in wrest if w not in (a,b)]
        nseed=[dict(s,source="REFEREE") for s in ref_info["seeds"]]+[dict(s,source="NAMED_NONTARGET:"+w) for w in others for s in target_info[w]["seeds"]]
        used=seed_tids(target_info[a])|seed_tids(target_info[b])|{s["tid"] for s in nseed}
        cands=[]
        for tid,l in sorted(lab.items()):
            if tid in used: continue
            c=l["person_class"]; truth=l["wrestler_id"] if c=="WRESTLER" else NEG_MAP.get(c)
            if truth is None: continue
            y=0 if truth==a else (1 if truth==b else 2)
            cands.append(dict(tid=tid,shot=tr[tid]["shot"],truth=truth,y=y,n_det=len(tr[tid]["frames"])))
        units_pre=len({(tr[t]['shot'],(lab[t]['wrestler_id'] if lab[t]['person_class']=='WRESTLER' else lab[t]['person_class'])) for t in lab if lab[t]['person_class'] in ('WRESTLER','REFEREE','RINGSIDE_STAFF','SPECTATOR','OTHER_WRESTLER_UNNAMED')})
        units_post=len({(tr[c['tid']]['shot'],c['truth']) for c in cands})
        tgt_pre=len({(tr[t]['shot'],lab[t]['wrestler_id']) for t in lab if lab[t]['person_class']=='WRESTLER' and lab[t]['wrestler_id'] in (a,b)}); tgt_post=len({(tr[c['tid']]['shot'],c['truth']) for c in cands if c['truth'] in (a,b)})
        episodes.append(dict(units_before_seed_removal=units_pre,units_after_seed_removal=units_post,target_units_before_seed_removal=tgt_pre,target_units_after_seed_removal=tgt_post,id=f"{clip}|{a}|{b}",clip=clip,split=split,A=a,B=b,status=status,unevaluable_reason=reason,seed_A=target_info[a]["seeds"],seed_B=target_info[b]["seeds"],seed_N=nseed,online_N=[],excluded_tracklets=sorted(used),n_candidate_tracklets=len(cands),candidate_tracklets=cands))
    return dict(clip=clip,split=split,named_wrestlers=wrest,target_seed_info=target_info,referee_seed_info=ref_info,episodes=episodes)
def load_all(R):
    sp={r["clip_id"]:r["split"] for r in csv.DictReader(open(R+"frozen/splits_v1.csv"))}
    labels={r["tid"]:r for r in csv.DictReader(open(R+"frozen/labels/ALL_firstpass.csv"))}
    return sp,labels
def build_all(R):
    sp,labels=load_all(R); EX=[]; frames_meta={}; clips={}
    for clip in sorted(sp):
        dets=pickle.load(open(R+f"frozen/dets/dets_{clip}.pkl","rb")); T=json.load(open(R+f"frozen/tracklets/{clip}.json"))
        lim=1934 if clip=="b2_videoplayback_2" else None
        keys,rows=extraction_rows(clip,dets,T,lim); EX+=rows
        frames_meta[clip]=dict(n_frame_keys=len(keys),first=keys[0],last=keys[-1],frame_keys_sha256=hashlib.sha256(json.dumps(keys).encode()).hexdigest(),dets_pkl_sha256=sha(R+f"frozen/dets/dets_{clip}.pkl"))
        # det index per tracklet aligned with frames
        di={t["tid"]:[det_index_of(dets,f,b) for f,b in zip(t["frames"],t["boxes"])] for t in T}
        clips[clip]=build_clip(clip,sp[clip],T,labels,di)
    return EX,frames_meta,clips,sp
def write_outputs(R):
    EX,fm,clips,sp=build_all(R)
    p=R+"frozen/EXTRACTION_FRAME_MANIFEST_V1.csv"
    if not os.path.exists(p):
        with open(p,"w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=["clip","frame","det","tid","box_h","crop_ok"]); w.writeheader(); w.writerows(EX)
    train_eps=[e["id"] for c in sorted(clips) for e in clips[c]["episodes"] if e["split"]=="train" and e["status"]=="OK"]
    seed_manifest=dict(manifest="SEED_EPISODE_MANIFEST_V2",amendment="frozen/SEED_FEASIBILITY_AMENDMENT_V1.md",episode_seed=EPISODE_SEED,n_target_seeds=N_TARGET_SEEDS,min_distinct_shots=MIN_SHOTS,max_seeds_per_shot=MAX_PER_SHOT,n_referee_seeds=N_REF_SEEDS,min_gap_frames=MIN_GAP_FRAMES,
      rules=dict(A_B_orientation="lexicographic canonical identity order, A smaller",pairs="all unordered 2-combinations of named wrestlers labelled in the clip",online_N="empty",
                 seed_eligibility="WRESTLER/REFEREE tracklets with multi_person_flag==0; target seeds: box_h >= clip/target median of eligible detections; exactly 4 seeds from >=2 distinct shots, <=2 per shot, pairwise >=60 frames; exhaustive deterministic DFS over a seeded round-robin order",
                 evaluation_exclusion="all tracklets containing any seed used by the episode (A,B and N seeds) are excluded from that episode's candidates",
                 truth_source="developer first-pass labels (non-independent); UNLABELABLE tracklets excluded"),
      extraction_frame_manifest=dict(file="frozen/EXTRACTION_FRAME_MANIFEST_V1.csv",sha256=sha(p),n_rows=len(EX),per_clip=fm),
      train_episode_ids_exhaustive=train_eps,clips=clips)
    q=R+"frozen/SEED_EPISODE_MANIFEST_V2.json"; json.dump(seed_manifest,open(q,"w"),indent=1,sort_keys=True,default=lambda o:int(o) if isinstance(o,np.integer) else float(o))
    return p,q
if __name__=="__main__":
    R=sys.argv[1] if len(sys.argv)>1 else "/home/claude/proj/v06_phase1/"
    p,q=write_outputs(R); print(p,sha(p)); print(q,sha(q))
