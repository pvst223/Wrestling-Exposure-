"""Supplementary (added after first inspection; descriptive, NOT an operating point). Reads only posthoc_candidate_scores.csv (derived from frozen scores)."""
import csv,json,os,numpy as np
OUT=os.path.dirname(os.path.abspath(__file__)); R=list(csv.DictReader(open(os.path.join(OUT,"posthoc_candidate_scores.csv"))))
ep_AB={}
for r in R: ep_AB.setdefault(r["episode"],r["episode"].split("|")[1:3])
out={}
for s in ("dev","test"):
    rows=[r for r in R if r["split"]==s]; sw=[]
    for f in (0.3,0.4,0.5,0.6,0.7,0.8):
        c=w=n=nt=nn=0
        for r in rows:
            A,B=ep_AB[r["episode"]]; p=[float(r["pA"]),float(r["pB"]),float(r["pNONTARGET"])]; k=int(np.argmax(p)); acc=k<2 and p[k]>=f; ident=(A,B)[k] if k<2 else ""
            if r["truth"] in (A,B):
                nt+=1; c+=int(acc and ident==r["truth"]); w+=int(acc and ident!=r["truth"])
            else:
                nn+=1; n+=int(acc)
        sw.append(dict(floor=f,target_candidates_accepted_as_correct_wrestler=c/nt,target_candidates_accepted_as_wrong_wrestler=w/nt,nontarget_candidates_accepted=n/nn))
    out[s]=sw
json.dump(out,open(os.path.join(OUT,"posthoc_floor_sweep_identity_supplementary.json"),"w"),indent=1); print(json.dumps(out))
