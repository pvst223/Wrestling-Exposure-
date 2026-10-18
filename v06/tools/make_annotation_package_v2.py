"""V2 of the annotation package builder (adds the reference-image relaxation approved by the independent reviewer; V1 builder/package kept unchanged for the audit trail). Reference rule: tier 1 = shots outside the reserve (as in V1, identical picks); tier 2 (only if a target has < 4 references) = tracklets from reserve shots whose unit is NOT a reserved unit; tier 3 (only if still < 4) = a tracklet of a reserved unit that has >= 2 tracklets. Tier 2/3 references are tight neutral crops (no context, 320 px letterbox, grey 114) and the exact tracklet used is REMOVED from the items, so no item shows or matches the reference. Model episode-seed rules are untouched.
Build the BLIND independent second-annotation package (deterministic; seeds 20261022 (ids/order) and 20261021 (reference seeds)).
Annotator-facing output (frozen/annotation_package/): instructions, annotation_sheet.csv (item_id, clip_code, image, label, notes), item images (3 frames per tracklet with the detector box), reference seeds per clip (Target A / Target B). Opaque ids and clip codes; shuffled order.
Items = ALL tracklets of every (clip, shot) that contains a reserved unit, so the package does not reveal which units were reserved or any first-pass class.
Contains NO first-pass labels for items and NO model/identity outputs (only detector boxes). Reference images are the only developer-derived content: they define which person is Target A / Target B inside each clip; chosen by seeded rule from first-pass target tracklets in shots NOT in the reserve (disclosed).
Internal key (frozen/annotation_key/, never shared with the annotator): item_id->tracklet id, clip code->clip, Target A/B->wrestler id."""
import json,csv,glob,random,os,cv2,numpy as np,hashlib,collections,statistics
R="frozen"; OUT=f"{R}/annotation_package_v2"; KEY=f"{R}/annotation_key_v2"
os.makedirs(OUT+"/items",exist_ok=True); os.makedirs(OUT+"/reference",exist_ok=True); os.makedirs(KEY,exist_ok=True)
res=json.load(open(f"{R}/SECOND_ANNOTATION_RESERVE_V1.json")); rshots={(r["clip"],r["shot"]) for r in res}
T=[]; 
for p in sorted(glob.glob(f"{R}/tracklets/*.json")): T+=json.load(open(p))
manifest={r["clip_id"]:r for r in csv.DictReader(open(f"{R}/manifest_clips.csv"))}
lab={r["tid"]:r for r in csv.DictReader(open(f"{R}/labels/ALL_firstpass.csv"))}
allitems=[t for t in T if (t["clip"],t["shot"]) in rshots]; clips=sorted({t["clip"] for t in allitems}); runits={(r["clip"],r["shot"],r["key"]) for r in res}
def unit_of(t):
    l=lab[t["tid"]]; return (t["clip"],t["shot"],l["wrestler_id"] if l["person_class"]=="WRESTLER" else ("STAFF" if l["person_class"]=="RINGSIDE_STAFF" else l["person_class"]))
unit_n=collections.Counter(unit_of(t) for t in allitems)
rng=random.Random(20261022); cc=clips[:]; rng.shuffle(cc); code={c:f"CLIP-{i+1}" for i,c in enumerate(cc)}
caps={}
def frame(clip,f):
    c=caps.get(clip) or caps.setdefault(clip,cv2.VideoCapture(f"{R}/norm/{clip}.mp4")); c.set(1,f); ok,im=c.read(); return im if ok else None
def tile(clip,f,box,w=400):
    im=frame(clip,f)
    if im is None: return np.zeros((int(w*0.5625),w,3),np.uint8)
    sc=w/im.shape[1]; im=cv2.resize(im,(w,int(im.shape[0]*sc))); b=[int(x*sc) for x in box]; cv2.rectangle(im,(b[0],b[1]),(b[2],b[3]),(0,255,0),2); return im
def render(t,path):
    n=len(t["frames"]); idx=[0,n//2,n-1] if n>2 else list(range(n)); tiles=[tile(t["clip"],t["frames"][i],t["boxes"][i]) for i in idx]; H=max(x.shape[0] for x in tiles)
    row=np.concatenate([np.pad(x,((0,H-x.shape[0]),(0,0),(0,0))) for x in tiles],1); cv2.putText(row,iid[t["tid"]],(3,14),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),1,cv2.LINE_AA); cv2.imwrite(path,row,[cv2.IMWRITE_JPEG_QUALITY,78])
# reference seeds (tier 1 as V1): per clip, 4 A + 4 B first-pass target tracklets, single-person, distinct shots, shots not in the reserve, box height >= clip median of target tracklets
rr=random.Random(20261021); rr2=random.Random(20261023); keyseeds={}; keytier={}; gal={}; removed=set(); iid={}
for c in clips:
    A,B=manifest[c]["wrestler_id_A"],manifest[c]["wrestler_id_B"]; gal[c]={"A":A,"B":B}; code_c=code[c]
    for role,wid in (("A",A),("B",B)):
        cand=[t for t in T if t["clip"]==c and (c,t["shot"]) not in rshots and lab[t["tid"]]["person_class"]=="WRESTLER" and lab[t["tid"]]["wrestler_id"]==wid and lab[t["tid"]]["multi_person_flag"]=="0"]
        if not cand: keyseeds[(c,role)]=[]; continue
        hs=[ (b[3]-b[1]) for t in cand for b in t["boxes"]]; med=statistics.median(hs)
        cand=[t for t in cand if statistics.median([b[3]-b[1] for b in t["boxes"]])>=med] or cand
        byshot=collections.defaultdict(list)
        for t in cand: byshot[t["shot"]].append(t)
        sh=sorted(byshot); rr.shuffle(sh); pick=[rr.choice(byshot[s]) for s in sh[:4]]; tiers=[1]*len(pick)
        used={t["shot"] for t in pick}
        for tier in (2,3):
            if len(pick)>=4: break
            pool=[t for t in T if t["clip"]==c and (c,t["shot"]) in rshots and t["shot"] not in used and lab[t["tid"]]["person_class"]=="WRESTLER" and lab[t["tid"]]["wrestler_id"]==wid and lab[t["tid"]]["multi_person_flag"]=="0" and ((unit_of(t) not in runits) if tier==2 else (unit_n[unit_of(t)]>=2))]
            if not pool: continue
            hh=[(b[3]-b[1]) for t in pool for b in t["boxes"]]; m0=statistics.median(hh); pool=[t for t in pool if statistics.median([b[3]-b[1] for b in t["boxes"]])>=m0] or pool
            bs=collections.defaultdict(list)
            for t in pool: bs[t["shot"]].append(t)
            ss=sorted(bs); rr2.shuffle(ss)
            for s_ in ss[:4-len(pick)]: tt=rr2.choice(bs[s_]); pick.append(tt); tiers.append(tier); used.add(s_)
        keyseeds[(c,role)]=[t["tid"] for t in pick]; keytier[f"{c}|{role}"]=tiers
        for k,(t,tier) in enumerate(zip(pick,tiers)):
            m=len(t["frames"])//2
            if tier==1: im=tile(c,t["frames"][m],t["boxes"][m],w=480)
            else:
                removed.add(t["tid"]); fr=frame(c,t["frames"][m]); x1,y1,x2,y2=[int(v) for v in t["boxes"][m]]; x1=max(0,x1);y1=max(0,y1);cr=fr[y1:y2,x1:x2]; h_,w_=cr.shape[:2]; sq=max(h_,w_); pad=np.zeros((sq,sq,3),np.uint8)+114; pad[(sq-h_)//2:(sq-h_)//2+h_,(sq-w_)//2:(sq-w_)//2+w_]=cr; im=cv2.resize(pad,(320,320))
            cv2.imwrite(f"{OUT}/reference/{code_c}_Target{role}_{k+1}.jpg",im,[cv2.IMWRITE_JPEG_QUALITY,80])
items=[t for t in allitems if t['tid'] not in removed]; order=items[:]; rng.shuffle(order); iid.update({t['tid']:f'I{i+1:04d}' for i,t in enumerate(order)})
rows=[]
for t in order:
    p=f"items/{iid[t['tid']]}.jpg"; render(t,f"{OUT}/{p}"); rows.append([iid[t["tid"]],code[t["clip"]],p,"",""])
with open(f"{OUT}/annotation_sheet.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["item_id","clip_code","image","label","notes"]); w.writerows(rows)
open(f"{OUT}/INSTRUCTIONS.md","w").write("""# Independent annotation instructions (blind)
Label every item in annotation_sheet.csv (column `label`). Each item image shows one tracklet: 3 frames (start, middle, end) with a green box around the person to label (the box is a detector output, not a label).
Allowed labels: TARGET_A, TARGET_B, REFEREE, STAFF, SPECTATOR, UNLABELABLE.
- TARGET_A / TARGET_B: the person is the wrestler shown in the reference images `reference/<clip_code>_TargetA_*.jpg` / `..._TargetB_*.jpg` for that clip_code. Targets are defined only by those reference images, within that clip. Do not use outside knowledge of who the wrestlers are, do not compare across clips.
- REFEREE: the match referee (striped shirt). STAFF: ringside staff, camera operators, photographers, security, ring crew, managers/valets or other non-spectator non-wrestling people at ringside. SPECTATOR: audience members.
- UNLABELABLE: you cannot decide (occlusion, too small, motion blur, box on several people with no clear majority, a wrestler who is neither Target A nor Target B, ambiguous identity). When in doubt use UNLABELABLE; do not guess.
- Box with several people: label the person occupying most of the box; if none dominates, UNLABELABLE.
Rules: label items in any order; do not ask the developer or consult any model; do not look at other annotators' labels. Optional `notes` for ambiguous cases. Return the completed CSV unchanged otherwise (do not edit item_id, clip_code, image).
Privacy: the images show spectators and staff. Use only for this annotation; do not copy, share or retain; delete after returning the CSV.
""")
json.dump({"item_to_tracklet":{v:k for k,v in iid.items()},"clip_code":{v:k for k,v in code.items()},"gallery":gal,"reference_seed_tracklets":{f"{k[0]}|{k[1]}":v for k,v in keyseeds.items()},"seeds":{"order_ids":20261022,"reference":20261021,"reference_tier2_3":20261023},"reference_tiers":keytier,"reference_tracklets_removed_from_items":sorted(removed)},open(f"{KEY}/annotation_key.json","w"),indent=1)
json.dump(gal,open(f"{KEY}/gallery.json","w"),indent=1)
print(len(rows),"items",len(clips),"clips; reference seeds",{f"{code[k[0]]}{k[1]}":len(v) for k,v in keyseeds.items()})
