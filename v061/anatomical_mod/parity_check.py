#!/usr/bin/env python3
"""Recomputation-parity + determinism check against the FROZEN caches (pose dets, tracklets, seg caches, frozen V1 rows). No inference, no video, no verdicts viewed.
Compares per-detection ownership numbers recomputed with the UNCHANGED V0.5 modules against the frozen anatomical rows; hashes the recomputed per-landmark classes (run twice).
Writes only aggregate counts + hashes (no per-frame geometry). Private inputs are read from --priv/--frozen and are never committed."""
import argparse, hashlib, json, os, pickle, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__)); V = os.path.dirname(HERE)
sys.path[:0] = [os.path.join(V, "anatomical", "impl"), os.path.join(HERE, "impl")]
import ownership_stage, partial_release as PR
CLIPS = ["b1_orton_rollins_wm31", "b2_batch2_clip_condensed", "b2_videoplayback_2", "b2_videoplayback_5"]
def once(frozen, priv):
    own = ownership_stage._mods()[0]; cfg = ownership_stage.load_cfg(); res = dict(per_clip={}); h = hashlib.sha256(); tot = collections.Counter(); changed_bad = 0; sample_ids = []
    for c in CLIPS:
        dets = pickle.load(open(os.path.join(frozen, "dets", f"dets_{c}.pkl"), "rb")); seg = pickle.load(open(os.path.join(priv, f"SEG_{c}.pkl"), "rb"))
        D = pickle.load(open(os.path.join(priv, f"ROWS_{c}.pkl"), "rb")); rows, W, H = D["rows"], D["W"], D["H"]; fsc = {}; k = collections.Counter(); ev_new = collections.Counter()
        for r in sorted(rows, key=lambda x: (x["tracklet"], x["frame"])):
            base = r
            if r.get("pose_status") != "MEASURED" or r.get("det") is None: k["not_measured"] += 1; continue
            f = r["frame"]; d = dets[f]
            if r.get("own_summary") is None:
                k["no_own_summary(cross_body_or_no_seg)"] += 1; o = PR.apply_release(r, None); assert o == r; continue
            if f not in fsc:
                sd = seg.get(f); fsc[f] = own.FrameSeg(sd, W, H, cfg.seg.SEG_CONF_MIN) if sd is not None else None
            cls, M, S = PR.landmark_classes(r["det"], d, fsc[f], cfg)
            k["recomputed"] += 1
            if cls is None: k["no_masks"] += 1; continue
            ok = all(M.get(x) == r["own_summary"].get(x) for x in ("owner", "cover", "own_only_frac", "contested_frac", "other_only_frac", "unexplained_frac")) and S == r["S"] and M["n_landmarks"] == r["n_landmarks"]
            k["summary_parity_ok" if ok else "summary_parity_MISMATCH"] += 1
            state, reasons = own.decide(M, cfg.ownership) if M["owner"] is not None or True else (None, None)
            if all(x in ("CONTESTED_LANDMARKS", "TOO_FEW_OWN_ONLY_LANDMARKS", "MASK_NOT_EXPLAINED_BY_SKELETON", "OPPONENT_LANDMARKS_IN_MASK", "BONES_LEAVE_MASK", "SOME_LANDMARK_IN_OTHER_INSTANCE",
                                                      "NO_OWNER_MASK", "FEW_LANDMARKS", "BONE_SPANS_INSTANCES", "LANDMARKS_IN_OTHER_INSTANCE") for x in r["own_reasons"]) and r["ownership_state"] in ("OWNERSHIP_UNCERTAIN", "SINGLE_BODY_SUPPORTED"):
                k["decide_parity_ok" if (state == r["ownership_state"] and list(reasons) == list(r["own_reasons"])) else "decide_parity_MISMATCH"] += 1
            h.update(json.dumps([c, r["tracklet"], f, sorted((int(i), v) for i, v in cls.items())], sort_keys=True).encode())
            o = PR.apply_release(r, cls)
            if o["record_class"] != r["record_class"]:
                if not PR.eligible(r) or not o["record_class"].startswith("RELEASED_PARTIAL_ANATOMY_") or o["released_landmarks"] != sorted(i for i, v in cls.items() if v == "OWN_ONLY"): changed_bad += 1
                ev_new[o["record_class"]] += 1
            elif PR.eligible(r): k["eligible_but_stays_withheld(min_bone_rule)"] += 1
            if o is not r and o["record_class"] == r["record_class"] and o != r: changed_bad += 1
        res["per_clip"][c] = dict(k, released=dict(ev_new)); tot.update(k)
    res.update(totals=dict(tot), recomputed_cls_sha256=h.hexdigest(), unexpected_changes=changed_bad)
    return res
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--frozen", default="/home/claude/proj/v06_phase1/frozen"); ap.add_argument("--priv", default="/home/claude/proj/v061_anat_private"); ap.add_argument("--out", required=True); a = ap.parse_args()
    r1 = once(a.frozen, a.priv); r2 = once(a.frozen, a.priv); r1["second_run_identical"] = (r1 == r2); r1["second_run_cls_sha256"] = r2["recomputed_cls_sha256"]
    r1["label"] = "RECOMPUTATION PARITY / DETERMINISM ONLY. No verdicts viewed. Counts of eligible/released frames are the structural ceiling, not performance."
    json.dump(r1, open(a.out, "w"), indent=1, sort_keys=True); print(json.dumps(r1["totals"], indent=1)); print("identical", r1["second_run_identical"], "unexpected_changes", r1["unexpected_changes"], r1["recomputed_cls_sha256"][:12])
if __name__ == "__main__": main()
