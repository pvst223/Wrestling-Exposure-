# ANATOMICAL MODIFICATION DESIGN V1 — AMENDMENT 1 (reviewer correction)

Registered as a separate addendum; `ANATOMICAL_MODIFICATION_DESIGN_V1.md` (ledger AMD1) is not edited. Where they differ, this amendment controls. Nothing else in the design changes.

**Reviewer ruling:** Q1, Q2, Q3 approved; Q4 approved and required (readiness/self-test next). One prospective criterion corrected.

## Corrected KEEP/MODIFY/KILL denominators (replaces the integer cutoffs in design sec. 6)
- **KEEP requires** (all of): **≥50 judgeable released frames** (was ≥60); contamination among judgeable released frames **≤5.0% as a proportion**, with the exact 95% Clopper-Pearson CI reported (no integer contamination cutoff is created or adjusted after the judgeable denominator is observed); recovered coverage ≥5.0 percentage points of the 2179 identity-ACCEPT measured frames; no clip with ≥3 contaminated released frames; hard-veto control contamination point estimate ≥2× the released-stratum point estimate; ASSIGNED control unchanged by construction.
- **MODIFY** if: contamination ≤5.0% but coverage <5.0 points; or contamination >5.0% and <10.0% (wording cleanup of "4–5/60", which no longer applies as an integer rule); or ≥3 contaminated released frames in any one clip; or NOT_JUDGEABLE >25% of released frames.
- **KILL** if: contamination ≥10.0% as a proportion (wording cleanup of "≥6/60"); or per-landmark unreliability across ≥2 distinct shots (OWN_ONLY landmark attributed to the wrong body); or recomputation not reproducible.
- All other design content (Tier A, UNCERTAIN-only, OWN_ONLY landmark release, bones need both endpoints, `RELEASED_PARTIAL_ANATOMY_A/B` as a class that never merges into ASSIGNED, burned-frame and ±30-frame exclusions, control strata, deterministic sampling, joint coverage/contamination evaluation) is unchanged.

**Open point raised by readiness (not decided here):** see `anatomical_mod/READINESS_README.md`, section "M9C feasibility conflict". The ±30-frame exclusion and ≥30-frame spacing leave too few eligible frames to reach ≥50 judgeable. No criterion was changed; the reviewer must rule.
