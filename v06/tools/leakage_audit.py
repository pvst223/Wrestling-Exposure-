"""Split-manifest leakage audit. manifest CSV columns: clip_id,tracklet_id,wrestler_id,match_id,promotion_id,split,person_class. Fails (exit 1) if any wrestler/match/clip key occurs in >1 split,
or if excluded keys (EXCLUDED_KEYS json: {"wrestler_id":[..],"match_id":[..],"clip_id":[..]}) occur anywhere. Prints manifest sha256."""
import csv,sys,json,hashlib,collections
def audit(manifest,excluded=None):
    rows=list(csv.DictReader(open(manifest))); bad=[]
    for key in ("clip_id","match_id","wrestler_id"):
        s=collections.defaultdict(set)
        for r in rows:
            if r[key] and r["person_class"]=="WRESTLER" or key!="wrestler_id": s[r[key]].add(r["split"])
        bad+=[(key,k,sorted(v)) for k,v in s.items() if k and len(v)>1]
    if excluded:
        for key,vals in excluded.items(): bad+=[("EXCLUDED_"+key,r[key],r["split"]) for r in rows if r.get(key) in vals]
    return bad,hashlib.sha256(open(manifest,"rb").read()).hexdigest()
if __name__=="__main__":
    ex=json.load(open(sys.argv[2])) if len(sys.argv)>2 else None; bad,h=audit(sys.argv[1],ex); print("manifest_sha256",h); print("VIOLATIONS" if bad else "OK",bad); sys.exit(1 if bad else 0)
