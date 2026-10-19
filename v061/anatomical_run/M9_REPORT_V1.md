# M9 Blind Review - Report V1 (single reviewer = Claude, NON-independent; ANNOTATION-PROVISIONAL; exploratory; NOT validated anatomical accuracy)
Frozen 60-frame sample (30 ASSIGNED + 30 WITHHELD; 7-8 per clip per stratum); verdict definitions and tooling registered (M9R0) before the first verdict; 60 verdicts frozen (M9R1, sha256 fb302b96...) before the hidden key was read; key joined once. No ownership/identity/merge-guard rule was touched.

## Required items
1. **Overall (60):** CORRECT 21 · PARTIAL_BUT_USABLE 31 · CONTAMINATED 6 · NOT_JUDGEABLE 2.
2. **ASSIGNED stratum (30):** CORRECT 19 · PARTIAL_BUT_USABLE 10 · CONTAMINATED 1 · NOT_JUDGEABLE 0.
3. **WITHHELD stratum (30):** CORRECT 2 · PARTIAL_BUT_USABLE 21 · CONTAMINATED 5 · NOT_JUDGEABLE 2.
4. **Withheld by ownership state:** MIXED_BODY_SUSPECTED (9): CORRECT 1, PARTIAL 5, CONTAMINATED 3. OWNERSHIP_UNCERTAIN (21): CORRECT 1, PARTIAL 16, CONTAMINATED 2, NOT_JUDGEABLE 2. Reason x verdict table: `M9_POSTHOC_V1.json` (e.g. OPPONENT_LANDMARKS_IN_MASK 12 withheld items: 11 PARTIAL, 1 CONTAMINATED; LIMB_TOO_LONG:* items: 4 of 9 CONTAMINATED).
5. **CONTAMINATED ASSIGNED frame (1 of 30):** R049, b2_videoplayback_5 frame 1041, ASSIGNED_B, ownership SINGLE_BODY_SUPPORTED (no reasons), merge guard did NOT trigger: two entangled bodies in one box, skeleton segments run across both. (Other contaminated items were all withheld: R001, R014, R042 [MIXED_BODY_SUSPECTED]; R013, R019 [OWNERSHIP_UNCERTAIN].)
6. **Withheld frames judged CORRECT or PARTIAL_BUT_USABLE:** 23/28 judgeable = 82.1% (exact 95% CI 63.1%-93.9%); 2 NOT_JUDGEABLE excluded.
7. **Assigned frames judged CONTAMINATED:** 1/30 = 3.3% (exact 95% CI 0.08%-17.2%).

## Required context for interpreting 6 (post-hoc, not pre-registered)
- The withheld stratum is NOT mostly identity-ACCEPT frames: 18/30 are REJECT_NONTARGET (spectators, referees, others), 3 NO_IDENTITY_EVAL, 3 ABSTAIN, and only **6 are identity-ACCEPT** (all 6 judged usable: 4+1 PARTIAL, 1 CORRECT; 0 contaminated; CI 54%-100%, n=6, essentially uninformative). By reviewer notes, 16/30 withheld and 2/30 assigned items showed a non-wrestler (spectator/referee/woman at ringside).
- Therefore M9 does not measure the 64.6% identity-ACCEPT withholding rate of M2 directly; it says that, in this sample, most WITHHELD skeletons (mostly non-targets) were anatomically plausible fragments and the clearly bad ones (5) were concentrated in MIXED/entangled-body or crowd-overlap cases the layer did flag.
- Leniency caveat: PARTIAL_BUT_USABLE (31/60) covers many sparse fragments (side-on, edge-cropped, torso-only, spectator segments); a stricter bar would shift items toward NOT_JUDGEABLE/CONTAMINATED. The reviewer is also the system's implementer (not independent). Frames cluster within shots; n=30 per stratum.
- Merge guard (diagnostic only): flagged 3 of the 60 sampled items (R044 CORRECT assigned, R056 PARTIAL assigned, R046 NOT_JUDGEABLE withheld); it did not flag the one contaminated assigned frame. Correspondence with real mixed-body cases remains unestablished.

## Not claimed
No validated anatomical accuracy; no exposure readiness; no rule change authorized or made. STOP for reviewer interpretation.
