"""Blind review sampling + commitment (deterministic).
  select_frames(candidates_csv, seed, n_random, strata): candidates_csv has columns clip_id,frame,det_idx and PRE-TRACKER descriptor columns only (e.g. n_people, box_overlap_flag, cut_nearby, small_box).
     Never read tracker status/identity. Picks n_random uniformly at random plus up to n_per_stratum rows for each boolean stratum column, by seed. Writes sample.csv and sample.sha256.
  neutral_colors(n, seed): randomized per-detection colour assignment so overlays carry no system labels.
  commit_labels(labels_csv): writes labels.sha256 (commitment) BEFORE automated results are opened; verify_commit() checks it later."""
import csv,random,hashlib,json,sys
def select_frames(cand_csv,out_csv,seed,n_random,strata=(),n_per_stratum=10):
    rows=list(csv.DictReader(open(cand_csv))); rnd=random.Random(seed); pick={}
    for r in rnd.sample(rows,min(n_random,len(rows))): pick[(r["clip_id"],r["frame"],r["det_idx"])]=(r,"random")
    for s in strata:
        pool=[r for r in rows if str(r.get(s,"0")).lower() in ("1","true","yes")]
        for r in rnd.sample(pool,min(n_per_stratum,len(pool))): pick.setdefault((r["clip_id"],r["frame"],r["det_idx"]),(r,"stratum:"+s))
    keys=sorted(pick); cols=list(rows[0].keys())+["sample_reason"]
    with open(out_csv,"w",newline="") as f:
        w=csv.writer(f); w.writerow(cols)
        for k in keys: w.writerow([pick[k][0][c] for c in rows[0].keys()]+[pick[k][1]])
    h=hashlib.sha256(open(out_csv,"rb").read()).hexdigest(); open(out_csv+".sha256","w").write(h+"\n"); return h,len(keys)
def neutral_colors(n,seed):
    r=random.Random(seed); return [(r.randint(60,255),r.randint(60,255),r.randint(60,255)) for _ in range(n)]
def commit_labels(labels_csv):
    h=hashlib.sha256(open(labels_csv,"rb").read()).hexdigest(); open(labels_csv+".sha256","w").write(h+"\n"); return h
def verify_commit(labels_csv): return open(labels_csv+".sha256").read().strip()==hashlib.sha256(open(labels_csv,"rb").read()).hexdigest()
