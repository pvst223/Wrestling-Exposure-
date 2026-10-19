#!/usr/bin/env python3
"""M9B deterministic sampler (reads frozen ROWS pickles + the M9 V1 key ONLY to exclude its (clip, frame) items). Writes the blind sheet and the hidden key; prints counts only."""
import collections, csv, json, os, pickle, random, sys
CLIPS = ["b1_orton_rollins_wm31", "b2_batch2_clip_condensed", "b2_videoplayback_2", "b2_videoplayback_5"]; SEED = int("fb302b96", 16) % 2 ** 31
STATES = (("MIXED_BODY_SUSPECTED", 7), ("OWNERSHIP_UNCERTAIN", 8)); GAPS = (30, 15, 0)
def population(priv, exclude):
    pop = []
    for c in CLIPS:
        for r in pickle.load(open(os.path.join(priv, f"ROWS_{c}.pkl"), "rb"))["rows"]:
            if r["pose_status"] == "MEASURED" and r["identity_state_passthrough"] in ("ACCEPT_A", "ACCEPT_B") and r["ownership_state_passthrough"] in dict(STATES) and (c, int(r["frame"])) not in exclude:
                pop.append(r)
    return pop
def sample(pop, seed=SEED):
    rng = random.Random(seed); chosen = []; relax = []; allr = []
    for c in CLIPS:
        sel = []   # frames selected in this clip (both states)
        for state, k in STATES:
            cand = [r for r in pop if r["clip"] == c and r["ownership_state_passthrough"] == state]
            byshot = collections.defaultdict(list)
            for r in sorted(cand, key=lambda r: (r["frame"], r["tracklet"])): byshot[r["shot"]].append(r)
            for gap in GAPS:
                order = sorted(byshot); rng.shuffle(order); got = [x for x in chosen if x["clip"] == c and x["ownership_state_passthrough"] == state]
                progress = True
                while len(got) < k and progress:
                    progress = False
                    for s in order:
                        if len(got) >= k: break
                        ok = [r for r in byshot[s] if all(abs(r["frame"] - f) >= gap and r["frame"] != f for f in sel)]
                        if ok:
                            r = rng.choice(ok); got.append(r); chosen.append(r); sel.append(r["frame"]); progress = True
                if len(got) >= k: break
                relax.append(dict(clip=c, state=state, relaxed_to=GAPS[GAPS.index(gap) + 1] if gap != GAPS[-1] else None))
    assert len({(r["clip"], r["frame"]) for r in chosen}) == len(chosen) == 60, len(chosen)
    order = list(range(60)); rng.shuffle(order); return [chosen[i] for i in order], relax
def main(priv, out):
    ex = {(r["clip"], int(r["frame"])) for r in csv.DictReader(open(os.path.join(priv, "M9_HIDDEN_KEY.csv"), newline=""))}; pop = population(priv, ex); ch, relax = sample(pop)
    sheet = [dict(review_id=f"B{i:03d}", clip=r["clip"], tracklet=r["tracklet"], frame=r["frame"], box=r["box"]) for i, r in enumerate(ch)]
    key = [dict(review_id=f"B{i:03d}", clip=r["clip"], tracklet=r["tracklet"], frame=r["frame"], shot=r["shot"], identity=r["identity_state_passthrough"], ownership_state=r["ownership_state_passthrough"], own_reasons=json.dumps(r["own_reasons"]), merge_guard=r["merge_guard_would_trigger"]) for i, r in enumerate(ch)]
    for nm, d in (("M9B_SHEET_BLIND.csv", sheet), ("M9B_HIDDEN_KEY.csv", key)):
        p = os.path.join(out, nm)
        if os.path.exists(p): raise SystemExit("write-once")
        with open(p, "w", newline="") as f: w = csv.DictWriter(f, fieldnames=list(d[0])); w.writeheader(); w.writerows(d)
    json.dump(dict(population_rows=len(pop), population_cells={f"{c}|{s}": sum(1 for r in pop if r["clip"] == c and r["ownership_state_passthrough"] == s) for c in CLIPS for s, _ in STATES}, relaxations=relax, seed=SEED), open(os.path.join(out, "M9B_SAMPLING_LOG.json"), "w"), indent=1)
    print("population", len(pop), "sampled", len(ch), "relaxations", relax)
if __name__ == "__main__": main(*sys.argv[1:3])
