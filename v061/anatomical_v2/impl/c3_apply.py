"""Anatomy V2 (C3) post-filter on frozen V1 rows. SUBTRACT-ONLY: an ASSIGNED_A/B row is either left exactly as V1 produced it or relabelled WITHHELD_C3.
No row is added, no V1-withheld row is released, no coordinate is written. Carry (visualization-only) is recomputed with the frozen carry function and then suppressed in/adjacent to intervals."""
import os, sys, copy
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "..", "anatomical", "impl"))
import c3_core as K, carry as V1CARRY
from c3_scene import Scene
COORD_FIELDS = ("kp", "kpc", "box")
def apply_c3(scene, v1_rows, cut_frames):
    """-> dict(rows, src, stats). rows: V1 rows with extra fields c3_status, c3_reason, c3_margin (and v1_record_class when withheld)."""
    out = []; stats = dict(n_rows=len(v1_rows), n_assigned_v1=0, pass_through=0, in_interval=0, supported=0, withheld=0, reasons={}, c0_withheld=0, partition=dict(R1=0, R2=0, R3=0, R4c=0, R5=0), margins={})
    for r in v1_rows:
        r2 = dict(r)
        if r["record_class"] not in K.ASSIGNED:
            r2.update(c3_status="NOT_APPLICABLE", c3_reason="", c3_margin=None); out.append(r2); continue
        stats["n_assigned_v1"] += 1
        iv = scene.interval_of(r); c0w = bool(scene.analysis(r)["overlap_a"]); stats["c0_withheld"] += c0w
        if iv is None:
            r2.update(c3_status="PASS_THROUGH", c3_reason="", c3_margin=None); stats["pass_through"] += 1; stats["partition"]["R5"] += 1; out.append(r2); continue
        stats["in_interval"] += 1; res = scene.decide_row(r, iv)
        if res["status"] == "SUPPORTED_UNIQUE":
            r2.update(c3_status="SUPPORTED_UNIQUE", c3_reason="", c3_margin=res["margin"]); stats["supported"] += 1
            stats["margins"][str(res["margin"])] = stats["margins"].get(str(res["margin"]), 0) + 1; stats["partition"]["R2" if c0w else "R4c"] += 1
        else:
            r2.update(v1_record_class=r["record_class"], record_class="WITHHELD_C3", assigned_label=None, landmarks_emitted=False, identity_unvalidated_flag=False,
                      c3_status="WITHHELD_C3", c3_reason=res["reason"], c3_margin=None, c3_landmarks=res.get("landmarks", []))
            stats["withheld"] += 1; stats["reasons"][res["reason"]] = stats["reasons"].get(res["reason"], 0) + 1; stats["partition"]["R1" if c0w else "R3"] += 1
        out.append(r2)
    src = V1CARRY.source_rate(out, cut_frames); src = K.suppress_carry(src, scene.interval_spans())
    verify_invariants(v1_rows, out)
    return dict(rows=out, src=src, stats=stats)
def verify_invariants(v1_rows, v2_rows):
    """Raises AssertionError on any violation: same rows in same order; emitted(V2) subset of ASSIGNED(V1); coordinates identical (same values); non-ASSIGNED V1 rows untouched (no release)."""
    assert len(v1_rows) == len(v2_rows), "row count changed"
    for a, b in zip(v1_rows, v2_rows):
        assert (a["tracklet"], a["frame"], a.get("det")) == (b["tracklet"], b["frame"], b.get("det")), "row identity/order changed"
        for k in COORD_FIELDS:
            if k in a: assert k in b and np.array_equal(np.asarray(a[k]), np.asarray(b[k])), f"coordinate field {k} changed"
        if b["record_class"] in K.ASSIGNED: assert a["record_class"] == b["record_class"] and a["record_class"] in K.ASSIGNED, "row emitted that V1 did not assign"
        if a["record_class"] not in K.ASSIGNED: assert b["record_class"] == a["record_class"] and b.get("landmarks_emitted") == a.get("landmarks_emitted"), "V1-withheld/unassigned row changed (release)"
        if a["record_class"] in K.ASSIGNED and b["record_class"] not in K.ASSIGNED: assert b["record_class"] == "WITHHELD_C3" and not b["landmarks_emitted"], "unexpected relabel"
    return True
