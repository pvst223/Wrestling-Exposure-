"""Build the BLIND independent second-annotation package (deterministic; seeds 20261022 (ids/order) and 20261021 (reference seeds)).
Annotator-facing output (frozen/annotation_package/): instructions, annotation_sheet.csv (item_id, clip_code, image, label, notes), item images (3 frames per tracklet with the detector box), reference seeds per clip (Target A / Target B). Opaque ids and clip codes; shuffled order.
Items = ALL tracklets of every (clip, shot) that contains a reserved unit, so the package does not reveal which units were reserved or any first-pass class.
Contains NO first-pass labels for items and NO model/identity outputs (only detector boxes). Reference seeds are the only developer-derived content: they define which person is Target A / Target B inside each clip; chosen by seeded rule from first-pass target tracklets in shots NOT in the reserve (disclosed).
Internal key (frozen/annotation_key/, never shared with the annotator): item_id->tracklet id, clip code->clip, Target A/B->wrestler id."""
import json,csv,glob,random,os,cv2,numpy as np,hashlib,collections,statistics
R="frozen"; OUT=f"{R}/annotation_package"; KEY=f"{R}/annotation_key"
os.makedirs(OUT+"/items",exist_ok=True); os.makedirs(OUT+"/reference",exist_ok=True); os.makedirs(KEY,exist_ok=True)
res=json.load(open(f"{R}/SECOND_ANNOTATION_RESERVE_V1.json")); rshots={(r["clip"],r["shot"]) for r in res}
T=[]; 
for p in sorted(glob.glob(f"{R}/tracklets/*.json")): T+=json.load(open(p))
manifest={r["clip_id"]:r for r in csv.DictReader(open(f"{R}/manifest_clips.csv"))}
lab={r["tid"]:r for r in csv.DictReader(open(f"{R}/labels/ALL_firstpass.csv"))}
items=[t for t in T if (t["clip"],t["shot"]) in rshots]; clips=sorted({t["clip"] for t in items})
rng=random.Random(20261022); cc=clips[:]; rng.shuffle(cc); code={c:f"CLIP-{i+1}" for i,c in enumerate(cc)}
order=items[:]; rng.shuffle(order); iid={t["tid"]:f"I{i+1:04d}" for i,t in enumerate(order)}
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
rows=[]
for t in order:
    p=f"items/{iid[t['tid']]}.jpg"; render(t,f"{OUT}/{p}"); rows.append([iid[t["tid"]],code[t["clip"]],p,"",""])
with open(f"{OUT}/annotation_sheet.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["item_id","clip_code","image","label","notes"]); w.writerows(rows)
# reference seeds: per clip, 4 A + 4 B first-pass target tracklets, single-person, distinct shots, shots not in the reserve, box height >= clip median of target tracklets
rr=random.Random(20261021); keyseeds={}; gal={}
for c in clips:
    A,B=manifest[c]["wrestler_id_A"],manifest[c]["wrestler_id_B"]; gal[c]={"A":A,"B":B}; code_c=code[c]
    for role,wid in (("A",A),("B",B)):
        cand=[t for t in T if t["clip"]==c and (c,t["shot"]) not in rshots and lab[t["tid"]]["person_class"]=="WRESTLER" and lab[t["tid"]]["wrestler_id"]==wid and lab[t["tid"]]["multi_person_flag"]=="0"]
        if not cand: keyseeds[(c,role)]=[]; continue
        hs=[ (b[3]-b[1]) for t in cand for b in t["boxes"]]; med=statistics.median(hs)
        cand=[t for t in cand if statistics.median([b[3]-b[1] for b in t["boxes"]])>=med] or cand
        byshot=collections.defaultdict(list)
        for t in cand: byshot[t["shot"]].append(t)
        sh=sorted(byshot); rr.shuffle(sh); pick=[rr.choice(byshot[s]) for s in sh[:4]]; keyseeds[(c,role)]=[t["tid"] for t in pick]
        for k,t in enumerate(pick):
            m=len(t["frames"])//2; im=tile(c,t["frames"][m],t["boxes"][m],w=480); cv2.imwrite(f"{OUT}/reference/{code_c}_Target{role}_{k+1}.jpg",im,[cv2.IMWRITE_JPEG_QUALITY,80])
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
json.dump({"item_to_tracklet":{v:k for k,v in iid.items()},"clip_code":{v:k for k,v in code.items()},"gallery":gal,"reference_seed_tracklets":{f"{k[0]}|{k[1]}":v for k,v in keyseeds.items()},"seeds":{"order_ids":20261022,"reference":20261021}},open(f"{KEY}/annotation_key.json","w"),indent=1)
json.dump(gal,open(f"{KEY}/gallery.json","w"),indent=1)
print(len(rows),"items",len(clips),"clips; reference seeds",{f"{code[k[0]]}{k[1]}":len(v) for k,v in keyseeds.items()})
