#!/usr/bin/env python3
"""Seeded sampler for the SEPARATED-BODY EVALUATION V1 (frozen before data). Candidates = frozen ASSIGNED_A/B measured rows with eligibility flags (feasibility_count.clip_counts(with_rows=True)).
ELIGIBLE stratum target 150 (>=30 shots, >=4 clips, spacing >=30 source frames in a clip, <=10 per shot, <=40% per clip, proportional by clip). INELIGIBLE contrast stratum target 50, clip-matched, same spacing.
Shortfalls are reported, never hidden or relaxed. Seed = int(sha256(<protocol freeze hash hex>)[:8],16) mod 2^31. Burned clips are rejected outright."""
import argparse, csv, hashlib, json, os, pickle, random, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "impl"))
import feasibility_count as FC
BURNED = {"b1_orton_rollins_wm31", "b2_batch2_clip_condensed", "b2_videoplayback_2", "b2_videoplayback_5"}
T_EL, T_INEL, SPACING, PER_SHOT, CLIP_CAP, MIN_SHOTS_TARGET, MIN_CLIPS_TARGET = 150, 50, 30, 10, 0.40, 30, 4
def seed_from_hash(h): return int(hashlib.sha256(h.encode()).hexdigest()[:8], 16) % 2 ** 31
def _pick_clip(cands, quota, rng, taken_frames):
    """Round-robin over shots (random order) taking one random admissible frame per shot per pass; admissible = >=SPACING from every taken frame in the clip, <=PER_SHOT per shot."""
    byshot = {}
    for c in cands: byshot.setdefault(c["shot"], []).append(c)
    shots = sorted(byshot); rng.shuffle(shots)
    for s in shots: byshot[s].sort(key=lambda c: (c["frame"], c["tracklet"])); rng.shuffle(byshot[s])
    picked = []; cnt = {s: 0 for s in shots}; frames = list(taken_frames); progress = True
    while len(picked) < quota and progress:
        progress = False
        for s in shots:
            if len(picked) >= quota: break
            if cnt[s] >= PER_SHOT: continue
            for i, c in enumerate(byshot[s]):
                if all(abs(c["frame"] - f) >= SPACING for f in frames):
                    picked.append(c); frames.append(c["frame"]); cnt[s] += 1; byshot[s].pop(i); progress = True; break
    return picked
def _alloc(avail, total, cap_frac=CLIP_CAP):
    cap = int(cap_frac * total); alloc = {c: 0 for c in avail}; rem = total; open_ = {c for c, a in avail.items() if a > 0}
    while rem > 0 and open_:
        w = sum(avail[c] for c in open_); share = {c: rem * avail[c] / w for c in open_}; fixed = [c for c in open_ if alloc[c] + share[c] >= min(cap, avail[c])]
        if fixed:
            for c in fixed: rem -= min(cap, avail[c]) - alloc[c]; alloc[c] = min(cap, avail[c]); open_.discard(c)
            continue
        base = {c: int(share[c]) for c in open_}; left = rem - sum(base.values())
        for c in sorted(open_, key=lambda c: (-(share[c] - base[c]), c))[:left]: base[c] += 1
        for c in open_: alloc[c] += base[c]
        rem = 0
    return alloc
def sample(cands, seed, burned=BURNED, t_el=T_EL, t_inel=T_INEL):
    assert not any(c["clip"] in burned for c in cands), "burned clip in candidate set: not admissible as confirmatory data"
    clips = sorted({c["clip"] for c in cands}); el = {c: [x for x in cands if x["clip"] == c and x["eligible"]] for c in clips}; inel = {c: [x for x in cands if x["clip"] == c and not x["eligible"]] for c in clips}
    avail = {c: len(_pick_clip(el[c], 10 ** 9, random.Random(f"{seed}:{c}:avail"), [])) for c in clips}; alloc = _alloc(avail, t_el); picks_el = {}
    for c in clips: picks_el[c] = _pick_clip(el[c], alloc[c], random.Random(f"{seed}:{c}:EL"), [])
    tot = sum(len(v) for v in picks_el.values()); matched = {c: round(t_inel * len(picks_el[c]) / tot) if tot else 0 for c in clips}
    while sum(matched.values()) > t_inel: matched[max(matched, key=lambda c: (matched[c], c))] -= 1
    picks_in = {}
    for c in clips:
        taken = [x["frame"] for x in picks_el[c]]; picks_in[c] = _pick_clip(inel[c], matched[c], random.Random(f"{seed}:{c}:INEL"), taken)
    out = []
    for c in clips:
        out += [dict(x, stratum="ELIGIBLE_ASSIGNED") for x in picks_el[c]] + [dict(x, stratum="INELIGIBLE_ASSIGNED") for x in picks_in[c]]
    E = [x for x in out if x["stratum"] == "ELIGIBLE_ASSIGNED"]; N = [x for x in out if x["stratum"] == "INELIGIBLE_ASSIGNED"]
    rep = dict(seed=seed, eligible_target=t_el, eligible_picked=len(E), eligible_shortfall=t_el - len(E), contrast_target=t_inel, contrast_picked=len(N), contrast_shortfall=t_inel - len(N),
               eligible_shots=len({(x["clip"], x["shot"]) for x in E}), eligible_clips=len({x["clip"] for x in E}), per_clip_available_eligible=avail, per_clip_alloc=alloc,
               max_clip_share=(max(len(v) for v in picks_el.values()) / len(E) if E else None), max_per_shot=(max(__import__("collections").Counter((x["clip"], x["shot"]) for x in E).values()) if E else 0),
               meets_shot_target=len({(x["clip"], x["shot"]) for x in E}) >= MIN_SHOTS_TARGET, meets_clip_target=len({x["clip"] for x in E}) >= MIN_CLIPS_TARGET)
    rng = random.Random(f"{seed}:shuffle"); order = list(range(len(out))); rng.shuffle(order); items = []
    for n, i in enumerate(order): items.append(dict(out[i], item_id=f"S{n:03d}"))
    items.sort(key=lambda x: x["item_id"]); return items, rep
def write(items, rep, outdir):
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "SEP_SHEET_BLIND.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["item_id", "clip", "frame", "box"])
        for x in items: w.writerow([x["item_id"], x["clip"], x["frame"], json.dumps(x["box"])])
    with open(os.path.join(outdir, "SEP_HIDDEN_KEY.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["item_id", "stratum", "clip", "shot", "tracklet", "frame", "record_class", "assigned_label", "n_drawn", "eligible10", "eligible25"])
        for x in items: w.writerow([x["item_id"], x["stratum"], x["clip"], x["shot"], x["tracklet"], x["frame"], x["record_class"], x["assigned_label"], x["n_drawn"], int(x["eligible10"]), int(x["eligible25"])])
    json.dump(rep, open(os.path.join(outdir, "SEP_SAMPLING_LOG.json"), "w"), indent=1, sort_keys=True)
def load_candidates(dets_dir, rows_dir, clips):
    c = []
    for clip in clips:
        dets = pickle.load(open(os.path.join(dets_dir, f"dets_{clip}.pkl"), "rb")); D = pickle.load(open(os.path.join(rows_dir, f"ROWS_{clip}.pkl"), "rb"))
        _, _, _, keep = FC.clip_counts(dets, D, with_rows=True); c += [dict(x, clip=clip) for x in keep]
    return c
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dets-dir", required=True); ap.add_argument("--rows-dir", required=True); ap.add_argument("--clips", nargs="+", required=True)
    ap.add_argument("--protocol-hash", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
    items, rep = sample(load_candidates(a.dets_dir, a.rows_dir, a.clips), seed_from_hash(a.protocol_hash)); write(items, rep, a.out); print(json.dumps(rep, indent=1, sort_keys=True))
if __name__ == "__main__": main()
