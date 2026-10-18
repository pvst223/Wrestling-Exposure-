"""Phase 1 deterministic metric computation, v2 (aligned with PREREGISTRATION_DRAFT_V2). No training code. Report writers must quote metrics.json only.
INDEPENDENT UNIT = (clip_id, shot, truth_id), where truth_id is a named wrestler id or one of REFEREE / STAFF / SPECTATOR / OTHER_WRESTLER_UNNAMED.
Tracklets, frames and detections inside one unit are NEVER independent observations: they only (a) collapse into the unit outcome and (b) appear as descriptive counts.
Input rows (one per evaluated detection): clip_id, shot, tracklet_id, frame, truth_id, accepted_role ('' = not accepted: reject or abstain; else the wrestler id the system accepted the detection as), and optionally best_role + score for risk-coverage curves.
Definitions (identical to the preregistration):
 * false accept of a detection: accepted_role != '' and accepted_role != truth_id (for non-wrestler truth any acceptance is false). A/B swap = a wrestler detection accepted as a different wrestler.
 * unit-level FTA (primary, conservative): over negative units, the fraction with AT LEAST ONE false-accepted detection. Negative units: wrestler units (as swap/other-named-wrestler negatives), referee, staff, spectator, unnamed-other-wrestler units. Exact Clopper-Pearson CI over units; strata with n_units < MIN_N are flagged descriptive-only.
 * coverage (primary): for each wrestler (target) unit, fraction of ITS detections accepted as its own identity; unweighted mean over target units. Pooled detection coverage is not computed as a primary quantity. CI: seeded percentile bootstrap over units (NOT exact; labelled), plus exact CP on the secondary binary 'target units with >=1 correct accept'.
 * frame-level FTA is secondary/descriptive and never given a CI.
"""
import csv,json,sys,hashlib,collections,random
from scipy.stats import beta,binom
MIN_N=15; NEG_CLASSES=("REFEREE","STAFF","SPECTATOR","OTHER_WRESTLER_UNNAMED")
def cp(k,n,a=0.05):
    if n==0: return (None,None)
    lo=0.0 if k==0 else beta.ppf(a/2,k,n-k+1); hi=1.0 if k==n else beta.ppf(1-a/2,k+1,n-k); return (float(lo),float(hi))
def _norm_truth(t): return "STAFF" if t=="RINGSIDE_STAFF" else t
def units_of(rows):
    """Collapse detections to independent units. Returns OrderedDict key=(clip,shot,truth_id) -> dict(n_det,n_correct,n_false,tracklets,frames,max_false_flag...)."""
    U=collections.OrderedDict()
    for r in rows:
        truth=_norm_truth(r["truth_id"]); k=(r["clip_id"],str(r["shot"]),truth); acc=(r.get("accepted_role") or "")
        u=U.setdefault(k,dict(truth=truth,wrestler=truth not in NEG_CLASSES,n_det=0,n_correct=0,n_false=0,tracklets=set(),frames=set()))
        u["n_det"]+=1; u["tracklets"].add(r["tracklet_id"]); u["frames"].add((r["tracklet_id"],r["frame"]))
        if acc!="":
            if u["wrestler"] and acc==truth: u["n_correct"]+=1
            else: u["n_false"]+=1
    return U
def stratum(u): return "OTHER_NAMED_WRESTLER" if u["wrestler"] else u["truth"]
def boot_ci(vals,seed=20261020,B=10000,a=0.05):
    if not vals: return (None,None)
    rng=random.Random(seed); n=len(vals); m=sorted(sum(vals[rng.randrange(n)] for _ in range(n))/n for _ in range(B)); return (m[int(B*a/2)],m[int(B*(1-a/2))-1])
def metrics(rows):
    U=units_of(rows); out={"definition":"unit=(clip,shot,truth_id); see module docstring","n_detections_descriptive":len(rows),"n_tracklets_descriptive":len({(r["clip_id"],r["tracklet_id"]) for r in rows}),"n_units_total":len(U)}
    strata=collections.defaultdict(list)
    for u in U.values(): strata[stratum(u)].append(u)
    out["fta_by_negative_stratum"]={}
    for s,L in sorted(strata.items()):
        k=sum(1 for u in L if u["n_false"]>0); out["fta_by_negative_stratum"][s]={"n_units":len(L),"units_with_any_false_accept":k,"unit_FTA":k/len(L),"exact_95CI":cp(k,len(L)),"descriptive_only_n_lt_15":len(L)<MIN_N,"detections_descriptive":sum(u["n_det"] for u in L),"detections_false_accepted_descriptive":sum(u["n_false"] for u in L),"tracklets_descriptive":sum(len(u["tracklets"]) for u in L)}
    allu=list(U.values()); k=sum(1 for u in allu if u["n_false"]>0)
    out["fta_all_negative_units"]={"n_units":len(allu),"units_with_any_false_accept":k,"unit_FTA":k/len(allu) if allu else None,"exact_95CI":cp(k,len(allu)),"descriptive_only_n_lt_15":len(allu)<MIN_N}
    sw=[u for u in allu if u["wrestler"]]; ks=sum(1 for u in sw if u["n_false"]>0)
    out["ab_swap_units"]={"n_wrestler_units":len(sw),"units_with_any_swap":ks,"exact_95CI":cp(ks,len(sw))}
    fr=[u["n_correct"]/u["n_det"] for u in sw]; any_ok=sum(1 for u in sw if u["n_correct"]>0)
    out["target_coverage"]={"n_target_units":len(sw),"definition":"unweighted mean over target units of (detections accepted as own identity / detections in unit)","coverage_mean_of_unit_fractions":(sum(fr)/len(fr)) if fr else None,"bootstrap_95CI_over_units_NOT_EXACT":boot_ci(fr),"descriptive_only_n_lt_15":len(sw)<MIN_N,"target_units_with_any_correct_accept":any_ok,"any_accept_exact_95CI":cp(any_ok,len(sw))}
    pw=collections.defaultdict(list)
    for (c,sh,t),u in U.items():
        if u["wrestler"]: pw[t].append(u["n_correct"]/u["n_det"])
    out["per_wrestler_unit_mean_coverage"]={w:{"n_units":len(v),"coverage":sum(v)/len(v)} for w,v in sorted(pw.items())}
    tf=sum(u["n_det"] for u in allu); ff=sum(u["n_false"] for u in allu)
    out["secondary_descriptive_frame_level"]={"note":"detections are not independent; no CI; descriptive only","detections":tf,"false_accepted_detections":ff,"frame_FTA":ff/tf if tf else None}
    if rows and "score" in rows[0] and "best_role" in rows[0]: out["risk_coverage_unit_level"]=risk_coverage(rows)
    return out
def risk_coverage(rows,max_points=60):
    ths=sorted({float(r["score"]) for r in rows},reverse=True); ths=ths[::max(1,len(ths)//max_points)]; res=[]
    for th in ths:
        rr=[dict(r,accepted_role=(r["best_role"] if float(r["score"])>=th else "")) for r in rows]; m=metrics_core(rr); res.append(dict(threshold=th,**m))
    return res
def metrics_core(rows):
    U=units_of(rows); allu=list(U.values()); sw=[u for u in allu if u["wrestler"]]
    k=sum(1 for u in allu if u["n_false"]>0); fr=[u["n_correct"]/u["n_det"] for u in sw]
    return {"unit_FTA":k/len(allu) if allu else None,"units_with_any_false_accept":k,"n_units":len(allu),"coverage_mean_of_unit_fractions":sum(fr)/len(fr) if fr else None}
def unit_false_flags(rows):
    return {k:int(u["n_false"]>0) for k,u in units_of(rows).items()}
def paired_sign(rows_base,rows_learn):
    """Paired exact one-sided sign test on negative units. b = units falsely accepted ONLY by the baseline, c = ONLY by the learned head. p = P(X>=b | n=b+c, p=0.5). Unit sets must be identical (same evaluation units)."""
    fb,fl=unit_false_flags(rows_base),unit_false_flags(rows_learn)
    if set(fb)!=set(fl): raise ValueError("unit sets differ between methods")
    b=sum(1 for k in fb if fb[k] and not fl[k]); c=sum(1 for k in fb if fl[k] and not fb[k]); both=sum(1 for k in fb if fb[k] and fl[k]); n=b+c
    p=1.0 if n==0 else float(binom.sf(b-1,n,0.5)) if b>0 else 1.0
    return {"n_units":len(fb),"b_baseline_only":b,"c_learned_only":c,"both":both,"neither":len(fb)-b-c-both,"discordant":n,"one_sided_p_b_gt_c":p}
def exclude_seed_tracklets(rows,seed_tracklets):
    """Remove tracklets that contain seed detections from evaluation (seed units are removed only for their target; shots remain for other people)."""
    return [r for r in rows if (r["clip_id"],r["tracklet_id"]) not in seed_tracklets]
def by_component(rows,component_of_clip):
    """SECONDARY/DESCRIPTIVE robustness only: metrics per wrestler component. Never feeds the primary KEEP/MODIFY/KILL decision."""
    g=collections.defaultdict(list)
    for r in rows: g[component_of_clip[r["clip_id"]]].append(r)
    return {c:metrics(v) for c,v in sorted(g.items())}
def main(p,o):
    rows=list(csv.DictReader(open(p))); m=metrics(rows); m["input_sha256"]=hashlib.sha256(open(p,"rb").read()).hexdigest(); json.dump(m,open(o,"w"),indent=1); print("wrote",o)
if __name__=="__main__": main(sys.argv[1],sys.argv[2])
