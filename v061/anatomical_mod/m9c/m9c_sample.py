#!/usr/bin/env python3
"""M9C deterministic sampler (frozen at registration; run ONLY after reviewer execution authorization).
Strata: RELEASED (60 unique frames), CONTROL_ASSIGNED (30), CONTROL_HARDVETO (30). Exclusions: every M9/M9B reviewed frame itself, and every frame within +-15 source frames of one (same clip).
Within-clip spacing ladder >=30 -> >=15 -> >=0, relaxed only as far as needed to reach the target. Writes blind sheet + hidden key + owner sheet/key + sampling log. Never writes or views images."""
import collections, csv, hashlib, json, os, random, sys
CLIPS = ["b1_orton_rollins_wm31", "b2_batch2_clip_condensed", "b2_videoplayback_2", "b2_videoplayback_5"]
SEED = int("45bd7c69", 16) % 2 ** 31           # prefix of the frozen M9B verdict hash (ledger M9B1)
RADIUS = 15; GAPS = (30, 15, 0); TARGETS = {"RELEASED": 60, "CONTROL_ASSIGNED": 30, "CONTROL_HARDVETO": 30}; OWNER_N = {"RELEASED": 30, "CONTROL_ASSIGNED": 10, "CONTROL_HARDVETO": 10}
def is_excluded(reviewed, clip, frame, radius=RADIUS): return any(abs(frame - g) <= radius for g in reviewed.get(clip, ()))
def dedupe(rows, rng):
    by = collections.defaultdict(list)
    for r in sorted(rows, key=lambda r: (r["clip"], r["frame"], str(r["tracklet"]))): by[(r["clip"], r["frame"])].append(r)
    return [rng.choice(v) for k, v in sorted(by.items())]
def pick(cands, n, rng, gaps=GAPS):
    """cands: unique-frame rows (clip, frame, shot, ...). -> (chosen rows each tagged gap_level, stats). Clip balance: next pick goes to the clip with the fewest picks so far that still has an admissible candidate;
    shots visited round-robin in seeded order. Stricter spacing is exhausted before any relaxation."""
    byshot = {c: collections.defaultdict(list) for c in CLIPS}
    for r in cands: byshot[r["clip"]][r["shot"]].append(r)
    order = {}
    for c in CLIPS: o = sorted(byshot[c], key=str); rng.shuffle(o); order[c] = o
    ptr = {c: 0 for c in CLIPS}; chosen = []; cnt = {c: 0 for c in CLIPS}
    for gap in gaps:
        progress = True
        while len(chosen) < n and progress:
            progress = False
            for c in sorted(CLIPS, key=lambda c: (cnt[c], CLIPS.index(c))):
                if len(chosen) >= n: break
                o = order[c]
                for k in range(len(o)):
                    s = o[(ptr[c] + k) % len(o)]; fr = [x["frame"] for x in chosen if x["clip"] == c]
                    ok = [r for r in byshot[c][s] if r["frame"] not in fr and all(abs(r["frame"] - f) >= gap for f in fr)]
                    if ok:
                        r = dict(rng.choice(ok), gap_level=gap); chosen.append(r); cnt[c] += 1; ptr[c] = (ptr[c] + k + 1) % len(o); progress = True; break
    stats = dict(n=len(chosen), target=n, per_clip=dict(cnt), picked_at_gap=dict(collections.Counter(r["gap_level"] for r in chosen)), shots=len({(r["clip"], r["shot"]) for r in chosen}), clip_imbalance=max(cnt.values()) - min(cnt.values()) if cnt else 0)
    nn = []
    for c in CLIPS:
        fr = sorted(x["frame"] for x in chosen if x["clip"] == c); nn += [b - a for a, b in zip(fr, fr[1:])]
    stats["adjacent_gap_min"] = min(nn) if nn else None; stats["adjacent_gap_hist"] = dict(collections.Counter(">=30" if g >= 30 else (">=15" if g >= 15 else "<15") for g in nn))
    return chosen, stats
def alloc_proportional(rows, n, rng):
    """Owner subset: n rows from `rows`, proportional by clip (largest remainder, ties by clip order), seeded within clip."""
    by = {c: [r for r in rows if r["clip"] == c] for c in CLIPS}; tot = len(rows); q = {c: n * len(by[c]) / tot for c in CLIPS}; base = {c: int(q[c]) for c in CLIPS}
    for c in sorted(CLIPS, key=lambda c: (-(q[c] - base[c]), CLIPS.index(c)))[: n - sum(base.values())]: base[c] += 1
    out = []
    for c in CLIPS: out += rng.sample(sorted(by[c], key=lambda r: r["frame"]), min(base[c], len(by[c])))
    return out
def build(pops, reviewed, seed=SEED):
    """pops: {stratum: [rows with clip, frame, shot, tracklet, box, ...]} -> dict(chosen, items, owner_items, log). Pure function."""
    rng = random.Random(seed); used = set(); chosen = {}; log = dict(seed=seed, radius=RADIUS, gaps=GAPS, strata={})
    for st in ("RELEASED", "CONTROL_ASSIGNED", "CONTROL_HARDVETO"):
        pool = [r for r in pops[st] if not is_excluded(reviewed, r["clip"], r["frame"]) and (r["clip"], r["frame"]) not in used]
        uniq = dedupe(pool, rng); ch, stats = pick(uniq, TARGETS[st], rng); chosen[st] = ch; used |= {(r["clip"], r["frame"]) for r in ch}
        stats["eligible_unique_frames_after_exclusion"] = len(uniq); log["strata"][st] = stats
    items = [dict(r, stratum=st) for st in chosen for r in chosen[st]]; order = list(range(len(items))); rng.shuffle(order); items = [dict(items[i], review_id=f"M{k:03d}") for k, i in enumerate(order)]
    sub = []
    for st in ("RELEASED", "CONTROL_ASSIGNED", "CONTROL_HARDVETO"):
        sub += alloc_proportional([i for i in items if i["stratum"] == st], OWNER_N[st], rng)
    o = list(range(len(sub))); rng.shuffle(o); owner_items = [dict(sub[i], owner_id=f"O{k:03d}") for k, i in enumerate(o)]
    log["n_items"] = len(items); log["n_owner_items"] = len(owner_items); log["owner_released_n"] = sum(1 for i in owner_items if i["stratum"] == "RELEASED")
    return dict(items=items, owner_items=owner_items, log=log)
def load_pops(priv, frozen, repo):
    """I/O wrapper: reads frozen ROWS/SEG/dets (private), applies the readiness machinery; no image/video access."""
    import pickle
    sys.path[:0] = [os.path.join(repo, "v061", "anatomical", "impl"), os.path.join(repo, "v061", "anatomical_mod", "impl")]
    import ownership_stage, partial_release as PR
    own = ownership_stage._mods()[0]; cfg = ownership_stage.load_cfg(); pops = {"RELEASED": [], "CONTROL_ASSIGNED": [], "CONTROL_HARDVETO": []}
    for c in CLIPS:
        dets = pickle.load(open(os.path.join(frozen, "dets", f"dets_{c}.pkl"), "rb")); seg = pickle.load(open(os.path.join(priv, f"SEG_{c}.pkl"), "rb")); D = pickle.load(open(os.path.join(priv, f"ROWS_{c}.pkl"), "rb")); fsc = {}
        for r in D["rows"]:
            if r.get("pose_status") != "MEASURED" or r.get("det") is None: continue
            base = dict(clip=c, frame=int(r["frame"]), shot=r["shot"], tracklet=r["tracklet"], box=[float(x) for x in r["box"]], identity=r["identity_state_passthrough"], own_state=r["ownership_state_passthrough"], reasons=list(r["own_reasons"]),
                        record_class=r["record_class"], merge_guard=bool(r["merge_guard_would_trigger"]), draw_landmarks=None)
            if r["record_class"] in ("ASSIGNED_A", "ASSIGNED_B"): pops["CONTROL_ASSIGNED"].append(base); continue
            if r.get("identity_state_passthrough") not in ("ACCEPT_A", "ACCEPT_B") or r["record_class"] not in PR_WITHHELD: continue
            if PR.eligible(r) and r.get("own_summary") is not None:
                f = int(r["frame"])
                if f not in fsc: fsc[f] = own.FrameSeg(seg[f], D["W"], D["H"], cfg.seg.SEG_CONF_MIN) if f in seg else None
                cls = PR.landmark_classes(r["det"], dets[f], fsc[f], cfg)[0]; o = PR.apply_release(r, cls)
                if o["record_class"].startswith("RELEASED_PARTIAL"): pops["RELEASED"].append(dict(base, draw_landmarks=o["released_landmarks"], record_class=o["record_class"]))
            elif r["own_reasons"] and not all(x in PR.TIER_A for x in r["own_reasons"]): pops["CONTROL_HARDVETO"].append(base)
    return pops
PR_WITHHELD = ("WITHHELD_MIXED_BODY", "WITHHELD_OWNERSHIP_UNCERTAIN")
def main(priv, frozen, repo, out):
    reviewed = collections.defaultdict(set)
    for nm in ("M9_HIDDEN_KEY.csv", "M9B_HIDDEN_KEY.csv"):
        for r in csv.DictReader(open(os.path.join(priv, nm), newline="")): reviewed[r["clip"]].add(int(r["frame"]))
    assert sum(len(v) for v in reviewed.values()) == 120
    res = build(load_pops(priv, frozen, repo), reviewed)
    def w(nm, rows, cols):
        with open(os.path.join(out, nm), "w", newline="") as f:
            wr = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); wr.writeheader(); [wr.writerow(r) for r in rows]
    sheet = lambda items, k: [dict(review_id=i[k], clip=i["clip"], tracklet=i["tracklet"], frame=i["frame"], box=json.dumps(i["box"]), draw_landmarks=json.dumps(i["draw_landmarks"]) if i["draw_landmarks"] is not None else "") for i in items]
    w("M9C_SHEET_BLIND.csv", sheet(res["items"], "review_id"), ["review_id", "clip", "tracklet", "frame", "box", "draw_landmarks"])
    w("M9C_OWNER_SHEET_BLIND.csv", sheet(res["owner_items"], "owner_id"), ["review_id", "clip", "tracklet", "frame", "box", "draw_landmarks"])
    key = [dict(i, reasons=json.dumps(i["reasons"]), draw_landmarks=json.dumps(i["draw_landmarks"]) if i["draw_landmarks"] is not None else "", owner_id=next((o["owner_id"] for o in res["owner_items"] if o["review_id"] == i["review_id"]), "")) for i in res["items"]]
    w("M9C_HIDDEN_KEY.csv", key, ["review_id", "owner_id", "stratum", "clip", "tracklet", "frame", "shot", "identity", "own_state", "reasons", "record_class", "merge_guard", "draw_landmarks", "gap_level"])
    w("M9C_OWNER_KEY.csv", [dict(owner_id=o["owner_id"], review_id=o["review_id"], stratum=o["stratum"]) for o in res["owner_items"]], ["owner_id", "review_id", "stratum"])
    json.dump(res["log"], open(os.path.join(out, "M9C_SAMPLING_LOG.json"), "w"), indent=1, sort_keys=True, default=str); print(json.dumps(res["log"], indent=1, sort_keys=True, default=str)[:1500])
if __name__ == "__main__": main(*sys.argv[1:5])
