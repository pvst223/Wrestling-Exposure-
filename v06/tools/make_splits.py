"""Deterministic wrestler-disjoint split assignment from clip metadata (CSV: clip_id,promotion_id,match_id,wrestler_A,wrestler_B,...). Uses only metadata, never results.
Clips sharing any wrestler are linked (union-find) and always land in the same split. Components are assigned greedily (seeded order) to train/dev/test to hit target wrestler fractions.
Excluded keys (EXCLUDED json) are refused. Output: splits.csv (clip_id, split, component) + report of wrestlers/promotions per split. Freeze+hash before any experiment."""
import csv,sys,json,random,hashlib,collections
def run(meta_csv,seed=20261017,frac=(0.5,0.25,0.25),excluded=None):
    rows=list(csv.DictReader(open(meta_csv))); ex=excluded or {}
    for r in rows:
        for w in (r["wrestler_A"],r["wrestler_B"]):
            if w in ex.get("wrestler_id",[]) : raise SystemExit(f"EXCLUDED wrestler {w} in {r['clip_id']}")
        if r["match_id"] in ex.get("match_id",[]) or r["clip_id"] in ex.get("clip_id",[]): raise SystemExit(f"EXCLUDED match/clip {r['clip_id']}")
    par={}
    def f(x):
        par.setdefault(x,x)
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for r in rows:
        a,b=f("W:"+r["wrestler_A"]),f("W:"+r["wrestler_B"]); par[a]=b; f("C:"+r["clip_id"]); par[f("C:"+r["clip_id"])]=f("W:"+r["wrestler_A"])
    comp=collections.defaultdict(list)
    for r in rows: comp[f("C:"+r["clip_id"])].append(r)
    keys=sorted(comp); random.Random(seed).shuffle(keys); W=sorted({r[k] for r in rows for k in ("wrestler_A","wrestler_B")}); tgt=[len(W)*x for x in frac]; got=[0,0,0]; out={}
    for k in keys:
        ws={r[x] for r in comp[k] for x in ("wrestler_A","wrestler_B")}; need=[tgt[i]-got[i] for i in range(3)]; i=max(range(3),key=lambda j:need[j]); got[i]+=len(ws)
        for r in comp[k]: out[r["clip_id"]]=("train","dev","test")[i]
    rep={s:dict(clips=sorted(c for c,v in out.items() if v==s),wrestlers=sorted({r[x] for r in rows if out[r["clip_id"]]==s for x in ("wrestler_A","wrestler_B")}),promotions=sorted({r["promotion_id"] for r in rows if out[r["clip_id"]]==s})) for s in ("train","dev","test")}
    return out,rep
if __name__=="__main__":
    ex=json.load(open(sys.argv[3])) if len(sys.argv)>3 else None; out,rep=run(sys.argv[1],excluded=ex)
    with open(sys.argv[2],"w") as f: f.write("clip_id,split\n"+"".join(f"{c},{s}\n" for c,s in sorted(out.items())))
    print(json.dumps(rep,indent=1)); print("splits_sha256",hashlib.sha256(open(sys.argv[2],"rb").read()).hexdigest())
    for w in ("train","dev","test"):
        if not rep[w]["wrestlers"]: print("WARNING: empty",w)
