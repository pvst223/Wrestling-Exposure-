#!/usr/bin/env python3
"""S6 assembly (aggregation only; no scoring). Reads private stage outputs, writes the immutable result JSON + report into the repo (aggregate counts and hashes only; no footage, frames, or per-frame content)."""
import collections, hashlib, json, os, pickle, sys
HERE = os.path.dirname(os.path.abspath(__file__)); P = "/home/claude/proj/v061_anat_private/"
CL = ["b1_orton_rollins_wm31", "b2_batch2_clip_condensed", "b2_videoplayback_2", "b2_videoplayback_5"]
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
J = lambda n: json.load(open(P + n)); S0 = J("S0_PREFLIGHT.json"); S4 = J("S4_METRICS.json"); S5 = J("S5_RENDER.json"); M = S4["metrics"]
rows = {c: pickle.load(open(P + f"ROWS_{c}.pkl", "rb"))["rows"] for c in CL}
meas = [r for c in CL for r in rows[c] if r["pose_status"] == "MEASURED"]
own = collections.Counter(r["ownership_state"] for r in meas); cls = collections.Counter(r["record_class"] for r in meas); ident = collections.Counter(r["identity_state_passthrough"] for r in meas)
reasons = collections.Counter(x for r in meas for x in r["own_reasons"]); joint = collections.Counter((r["identity_state_passthrough"], r["ownership_state_passthrough"]) for r in meas)
guard = collections.Counter((r["ownership_state_passthrough"]) for r in meas if r["merge_guard_would_trigger"])
m2 = [x for x in M["M2"] if x["shot"] not in ("ALL",)]; flagged = [x for x in m2 if x["diagnostic_flag_ge_20pct"]]
res = dict(label="V0.6.1 ANATOMICAL INTEGRATION EXECUTION V1 - DEVELOPMENT ONLY - NOT VALIDATION - IDENTITY UNVALIDATED (MODIFY)", authorization_ledger_id="OGR18", registration_ledger_id="REG1", clips=CL,
           hashes=dict(anat_manifest_sha256=S0["anat_manifest_sha256"], runner_sha256=S0["runner_sha256"], authorization_record_sha256=S0["auth_sha256"], assemble_result_sha256=sha(__file__), pose_weights=S0["pose_w"], seg_weights=S0["seg_w"],
                       oof_private_sha256=S0["oof_private_sha256"], oof_blinded_sha256=S0["oof_blinded_sha256"], per_clip_inputs=S0["per_clip"], seg_caches={c: J(f"S1_{c}.json")["seg_cache_sha256"] for c in CL},
                       m9_sheet_sha256=S4["m9_sheet_sha256"], m9_key_sha256=S4["m9_key_sha256"], rows_pickles={c: sha(P + f"ROWS_{c}.pkl") for c in CL}, renders=S5),
           s1=dict(option="W", seconds={c: J(f"S1_{c}.json")["seconds"] for c in CL}, n_seg_frames={c: J(f"S1_{c}.json")["n_seg_frames"] for c in CL}, missing={c: J(f"S1_{c}.json")["missing"] for c in CL}),
           per_clip=S4["per_clip"], metrics=M, descriptive_post_registration=dict(note="Tabulations computed by assemble_result.py from the registered stage outputs; descriptive, not pre-registered metrics.",
           measured_rows=len(meas), ownership_state_counts=dict(own), record_class_counts=dict(cls), identity_state_counts=dict(ident), ownership_reason_counts=dict(reasons.most_common()),
           identity_x_ownership={f"{a}|{b}": n for (a, b), n in sorted(joint.items())}, merge_guard_flagged_by_ownership_state=dict(guard), m2_shots_total=len(m2), m2_shots_flagged_ge_20pct=len(flagged)),
           defects=[], outcome_class_assigned=False, forbidden_outputs_present=False, holdout2_accessed=False, gemini_transmitted=False)
out = os.path.join(HERE, "ANATOMICAL_RESULT_V1.json")
if os.path.exists(out): raise SystemExit("write-once")
json.dump(res, open(out, "w"), indent=1, sort_keys=True, default=str)
d = res["descriptive_post_registration"]; M2A = [x for x in M["M2"] if x["clip"] == "ALL"][0]
L = ["# V0.6.1 Anatomical Integration Execution V1 - Report (DEVELOPMENT ONLY; NOT VALIDATION)", "",
 "Identity layer: MODIFY, **not validated**, not exposure-ready. Ownership/pose use unchanged V0.5 code (unvalidated). R3 PARKED; R4 UNMET; ANNOTATION-PROVISIONAL. Correct anatomical ownership is not evidence of correct wrestler identity. No outcome class; no accuracy/validation/exposure claim.", "",
 f"Executed S0-S6 once on the four approved clips (OGR18/REG1). Segmentation: Option W (stride-3 pose frames; {sum(res['s1']['n_seg_frames'].values())} frames, none missing). Merge guard diagnostic-only.", "",
 "## Headline descriptive counts (measured pose rows)", f"- Measured rows: {d['measured_rows']}. Ownership: {d['ownership_state_counts']}.", f"- Record classes: {d['record_class_counts']}.",
 f"- M2: {M2A['withheld']}/{M2A['accept_measured']} identity-ACCEPT measured frames withheld by ownership = {M2A['frac']:.3f} (95% CI {M2A['ci95'][0]:.3f}-{M2A['ci95'][1]:.3f}); diagnostic flag (>=20%) on {d['m2_shots_flagged_ge_20pct']} of {d['m2_shots_total']} clip/shot units (diagnostic only; not pass/fail).",
 f"- M3 disagreements: {M['M3']}.", f"- M4: {M['M4']['n_flips']} A<->B label flips within tracklet runs; {len(M['M4']['same_label_on_two_detections'])} frames where the same label sits on two detections.",
 f"- M5 temporal: {M['M5']}.", f"- M6 landmark coverage: {M['M6']['with_min_landmarks']}/{M['M6']['measured']}.", f"- M8 carried share (visualization only): {M['M8']['carried_share']:.3f}.", f"- M9: sheet of {M['M9']['n_sheet']} frames prepared (>=30 assigned + >=30 withheld; shortfall {M['M9']['shortfall']}); **verdicts not yet collected**.", "",
 "## Ownership reasons (descriptive)", f"{d['ownership_reason_counts']}", "",
 "## M7 camera-cut cross-check (reported, not reconciled)", *[f"- {c}: agree {v['agree']}, frozen-only {len(v['frozen_only'])}, classifier-only {len(v['classifier_only'])}" for c, v in M["M7"].items()],
 "For batch2 and videoplayback_2 the V0.2 classifier labels the frozen shot starts PHOTOMETRIC_REGISTERED (same registered scene) rather than CUT; frozen shot indices were used for resets (as in the identity layer).", "",
 "## Merge guard (diagnostic only)", f"Rows flagged would-trigger by ownership state: {d['merge_guard_flagged_by_ownership_state']}. Correspondence with real mixed-body cases is NOT assessed.", "",
 "## Limits", "Stride-3 pose grid with visualization-only carry; instance masks unvalidated (V0.5 caveats); appearance vetoes disabled; ownership withholding is high, i.e. the ownership layer is conservative and most identity-ACCEPT frames are not emitted as anatomical assignments; no ground truth for skeleton correctness exists yet (M9 pending, single reviewer, ANNOTATION-PROVISIONAL).", "No defects occurred during execution."]
open(os.path.join(HERE, "ANATOMICAL_REPORT_V1.md"), "w").write("\n".join(L) + "\n"); print("ok")
