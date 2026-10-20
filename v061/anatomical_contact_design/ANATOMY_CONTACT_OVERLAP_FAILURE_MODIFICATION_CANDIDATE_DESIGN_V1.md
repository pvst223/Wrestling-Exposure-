# ANATOMY CONTACT/OVERLAP FAILURE — MODIFICATION CANDIDATE DESIGN V1

**Design and diagnosis only. Nothing implemented, run or tuned.** Label for everything below: development-only, ANNOTATION-PROVISIONAL, single non-independent primary reviewer (Claude), owner second review on a 50-item subset. Not validation. Rights UNRESOLVED.

Standing: the M9C KILL of `RELEASED_PARTIAL_ANATOMY` is final and is not reopened, reinterpreted or tuned. Frozen Anatomy V1 (manifest f5936ce8…) is unchanged; any candidate below would be a **separate, new version** (provisionally "Anatomy V2 contact modification") and must be frozen before any fresh evaluation. Burned M9/M9B/M9C frames serve development diagnosis only and can never be confirmatory evidence. No Holdout #2, no Gemini, no exposure, no final MP4.

**Objective:** reduce wrong-body landmark ownership during multi-person contact while failing closed when attribution is unsupported. Coverage is explicitly not the objective. Corollary: a modification that "wins" by withholding every contact frame is a retreat, not a fix (see C0 in section 3).

## 1. Failure taxonomy (contaminated contact/overlap cases)

Evidence base: 12 contaminated RELEASED frames with the prospective localized wrong-body call (YES 7 frames in 5 distinct shots; UNDETERMINED 4; NO 1), the owner's free-text notes on his 50 items, and the 7 contaminated ASSIGNED controls and 10 contaminated hard-veto controls. The wrong-body protocol was run only on the released frames; causes for the assigned and hard-veto contaminated frames are inferred from the verdict notes, not individually determined. Taxonomy is a visual reading of 2D drawn frames and is itself provisional.

| code | mechanism | released-frame examples (note) | where it defeats the frozen ownership layer |
|---|---|---|---|
| T1 | **Merged or absorbing instance mask.** Touching bodies yield one mask (or the top body's mask absorbs the lower one). Landmarks of the other body lie inside the "owner" mask. | M026, M041, M062, M107 (hip or bones land on the underlying wrestler) | `owner_for` picks the mask holding most landmarks; with a merged mask every landmark is OWN_ONLY. Only `unexplained_frac` can notice, and only when the extra body is large. When it does not fire (below 0.25) the frame is ASSIGNED. |
| T2 | **Pose detector crosses bodies.** A single skeleton takes joints from two people (shoulders on the top body, hips on the lower body). | M041 (shoulders on top body, hips on lower body), M107 (bones span three regions) | Upstream of ownership. Ownership only compares landmarks with masks; if the masks are merged (T1) the crossed skeleton looks single-body. Bone-length and torso-symmetry cues catch only gross cases. |
| T3 | **Contested overlap region.** Landmarks sit in the intersection of two masks (clinch, lift, pin edge). | M064, M065 (hip/knee on the other wrestler's trousers or back) | Detected as CONTESTED (reason CONTESTED_LANDMARKS) and withheld by V1; contamination appears only when released by the killed Tier A. In ASSIGNED frames contested_frac stayed at or below 0.1, so a few contested joints pass. |
| T4 | **Third-party body in the scene** (referee, spectator, ringside). | M063 (referee shirt and trousers); owner notes "referee/cyan-box contamination", "spectator tracked" | Partly an identity error (the detection is not a wrestler) and partly overlap; ownership does not know who is a wrestler. |
| T5 | **Not resolvable from one 2D frame.** Pins, piles, entangled clinches. | M033, M035, M100, M118 (UNDETERMINED even for a human reviewer) | No single-frame rule can resolve these; the only correct output is to withhold. This sets a ceiling on any candidate: roughly a third of the contaminated released frames. |
| T6 | **Perspective/bleed** (owner: "tracking bleeds onto Daniel", "some contamination due to angle") | owner items | Soft cases that the owner labelled CONTAMINATED while Claude labelled PARTIAL (kappa 0.36, raw 0.56): part of this class is a reviewer-threshold disagreement, not a distinct mechanism. |

Not in scope: missing head/arm/leg (owner notes "head not tracked", "legs only") is **partial coverage**, not wrong-body ownership; the objective excludes it.

**Descriptive counts on the burned frames** (`CONTACT_DIAGNOSTICS_COUNTS_V1.json`, counts only, no rule derived):

| | contaminated (29: 7 assigned, 12 released, 10 hard-veto) | correct/partial (79) |
|---|---|---|
| another tracked person's box in the same frame | 22 | 64 |
| max other-person box IoU ≥ 0.1 / ≥ 0.3 | 7 / 4 | 20 / 4 |
| an earlier clean frame on the same track (any distance) | 15 | 56 |
| clean frame within 30 source frames | 13 | 50 |
| merge-guard diagnostic flag | 2 | 4 |

Reading: box overlap and the merge guard are poor separators (consistent with the merge guard being diagnostic-only and unsupported; box IoU ≥ 0.1 holds in only 7 of 29 contaminated frames, while 22 of 29 have another tracked person in the frame, as do 64 of 79 non-contaminated frames). A clean anchor on the same track exists for only about half (15/29) of contaminated frames, so any candidate that depends on one would withhold the rest. Limits: rows contain only tracked persons; "contact" is a subjective flag; n is small and clustered.

## 2. Information already in the frozen pipeline that could distinguish target from opponent during overlap

Available now (all deterministic, no training needed to read it):
1. **All pose detections in the frame** (17 keypoints + confidences for every person, including the opponent and the referee).
2. **Instance masks** (YOLOv8m-seg, person, 320×180 bit-packed, stride-3 frames) and per-landmark mask membership including CONTESTED/OTHER_ONLY classes; owner-mask coverage; `unexplained_frac`.
3. **Per-tracklet history**: stride-3 poses of the same tracklet before contact, ownership state per frame, body scale S, box geometry.
4. **Shot boundaries** (cuts reset tracks).
5. **Identity decision** (g, q) from the frozen head: weak, unvalidated appearance evidence at the detection level.
6. **Opponent tracklet** (the other named wrestler's own detections before/after contact), enabling a two-body view rather than a one-body view.
7. **Source video pixels** for deterministic appearance or motion measures (colour of trunks/gear around a landmark; dense optical flow), which the pipeline does not currently use for ownership. Appearance votes exist in the vendored V0.5 code but were disabled in V1 (clarification A2).

Not available: depth, amodal masks, per-part segmentation, any multi-view data, higher-resolution masks than 320×180 for stride-3 frames (mask tolerance is 4 px at that scale).

## 3. Candidate fixes

All three are deterministic logic over frozen general-purpose models (no training on anatomy labels, none tuned on burned verdicts). None re-enables partial release; none loosens a V1 threshold. In every candidate the output is only ever the **current frame's own measured keypoints** or a withholding; nothing is copied, carried or interpolated from another frame.

**C0 (reference floor, not a separation candidate): contact-conditioned withholding.** Withhold ASSIGNED anatomy whenever a geometric overlap context (already computed as `overlap_context` but not used by V1 decisions) is present. Guaranteed to cut contact contamination by construction, but the counts above show box-overlap detects only 7/29 contaminated frames at IoU ≥ 0.1 (the 22/29 "other person present" would remove most of the data), and it discards exactly the contact events of interest. Listed so that every candidate is compared against it (any candidate must beat C0 on yield at equal fail-closed behaviour, or it adds nothing).

### C1 — Clean-anchor body-consistency veto (temporal evidence, no pose carry)
- **Mechanism.** For a target tracklet, take its most recent **clean** measured frame (SINGLE_BODY_SUPPORTED, no overlapping other-person box, within an expiry horizon) as a reference body model: relative joint geometry (limb-length ratios to scale S), and a local appearance descriptor per body region (colour statistics in small patches at the anchor's landmarks, e.g. trunks, skin, gear). During overlap, each current-frame landmark must be **consistent with the anchor's body model** (limb-length ratios; patch colour similar to the same region of the anchor and not more similar to the opponent's or referee's anchor). Landmarks or whole frames that fail are withheld; frames without an eligible anchor are withheld.
- **New assumptions.** Body parts keep appearance over the horizon; the two wrestlers and the referee are separable by local colour (not true for similar gear/lighting; V0.5 already demoted appearance from vouching for ownership to veto-only); limb ratios are stable enough through a foreshortened/rotating body. Anchor tracklet identity does not swap at contact onset.
- **Training.** None. Deterministic; reuses the dormant V0.5 appearance region code; constants fixed a priori from the frozen V0.5 constants or stated rules and frozen before any fresh data.
- **Expected failure modes.** Similar gear; anchor expiry (diagnostic: no clean anchor for 14/29 contaminated frames, so these would be withheld, not fixed); the underlying wrestler hidden for the whole interval; rapid pose change at onset; compounding error if the anchor is chained instead of fixed (the design forbids chaining: reference is always the last clean frame, never a previous verified-in-contact frame).
- **Burden.** Low-moderate CPU; small code; patch statistics at stride-3 frames.
- **Fail-closed.** Yes: no anchor, low descriptor separability between wrestlers, or any landmark failing → withhold (reason code recorded).
- **KILL evidence (prospectively fixed, fresh contact-stratum footage).** Emitted-frame wrong-body rate in contact frames fails the pre-registered bound; or descriptor separability is below its pre-registered floor on most contact frames (nothing emitted); or yield in contact is no better than C0; or wrong-body appears in ≥ N distinct shots.

### C2 — Pose-prompted competitive re-segmentation (mutual exclusion of bodies)
- **Mechanism.** In frames where two or more people overlap (union-box geometry), run a promptable segmentation model (a general-purpose pretrained interactive segmenter such as the SAM family) at higher resolution on a crop of the union region, **once per body**, prompting with that body's own confident keypoints as positives and the other bodies' keypoints as negatives. Compare the resulting masks: enforce mutual exclusivity (a pixel/landmark may belong to at most one body). Accept a landmark as owned by the target only if it lies in the target's prompted mask and not in an opponent's prompted mask, with a minimum margin of mask support; otherwise withhold that landmark and, past a count, the frame.
- **New assumptions.** A promptable segmenter separates touching bodies when given positive/negative points; the **keypoints used as prompts are themselves on the right bodies** (fails under T2). Prompting from the very skeleton being verified is partly circular; negative prompts from the opponent's skeleton partly break the circularity.
- **Training.** None of our own; adds a new pretrained dependency and licence/rights/weights review (a new frozen model component, hashed). The model is not wrestling-trained.
- **Expected failure modes.** T2 (prompts wrong); entangled pins (T5) where even humans cannot separate; segmenter leaking onto similar-coloured body; computational cost; non-determinism across hardware.
- **Burden.** Highest: a heavy model on contact frames, new weights to register, determinism checks.
- **Fail-closed.** Yes by construction (exclusivity + margin), provided margins are stated before any fresh run.
- **KILL evidence.** As C1, plus: the prompted masks of different bodies overlap (non-exclusive) on a pre-registered share of contact frames, or run-to-run/hardware variation changes ownership calls beyond a stated tolerance.

### C3 — Joint two-body hypothesis test with a uniqueness (ambiguity) margin
- **Mechanism.** In a detected overlap interval, treat ownership as an explicit assignment problem: enumerate a small, a-priori hypothesis set for how the detected keypoints of the (up to three) people in the union region may be partitioned among the tracked bodies (identity-preserving, swap, mixed), score each hypothesis by deterministic consistency costs (limb-length ratios vs the clean anchors of **both** wrestlers, mask membership consistency, mutual exclusion, bounded motion since the clean anchors), and accept the target's landmarks **only if one hypothesis wins by a pre-registered margin over the best competing hypothesis**; else withhold.
- **New assumptions.** The hypothesis set contains the truth; the cost terms rank true assignments above false ones in overlap; anchors for both bodies exist (needs the opponent's clean frame as well as the target's).
- **Training.** None (combinatorial scoring with a-priori costs).
- **Expected failure modes.** Needs two anchors (even fewer eligible frames than C1); symmetric/near-symmetric poses make the margin small, so most frames would be withheld; costs are heuristic and share C1's assumptions.
- **Burden.** Moderate (small combinatorics per frame).
- **Fail-closed.** Strongest of the three: the output is "unique explanation or nothing", which also gives an explicit ambiguity reason that can be audited.
- **KILL evidence.** As C1; plus the ambiguity margin never satisfied on a pre-registered share of contact frames (nothing emitted), or accepted frames showing wrong-body despite a margin.

Not offered as candidates (and why): extending carry/interpolation across the overlap (impermissible, see section 4); retuning Tier A/contested/unexplained thresholds (a threshold variant of the killed rule); a learned contact classifier trained on the burned verdicts (training on burned frames as selection evidence; also not to be used for tuning); using the merge guard as a filter (diagnostic-only, poor separator per the counts above).

## 4. Temporal person/pose continuity: permissible use versus impermissible carry

**Impermissible (unchanged):** emitting, drawing or measuring a landmark whose position comes from another frame — carry beyond the existing 3-frame visualization-only carry, interpolation across the overlap, or filling missing joints from the pre-contact skeleton. Carried frames never enter metrics, and that stays.

**Potentially permissible (hypothesis, to be tested, not assumed):** using an earlier clean frame **as evidence for a decision about the current frame's own measured keypoints**: it supplies a reference (limb ratios, local appearance, plausible motion) against which the current detection is accepted or rejected. Position is never copied; the only outputs are the current measured keypoints or a withholding. This is C1/C3. It is genuinely different from carry because it can only remove output, never create it.

Cautions drawn from the frozen record:
- The V1 temporal check already exists but is local: it compares with the previous measured frame within 3 source frames (clarification A4), with torso-centred displacement. Ownership drift that occurs gradually, or begins inside a long pin (anchor older than 3 frames), passes. Chaining verifications through contact compounds error, so the reference must be the last **clean** frame, with an expiry horizon fixed before any fresh run.
- The tracker itself can swap or merge bodies through contact (greedy IoU ≥ 0.3 tracklets), so tracklet continuity across overlap is an assumption to test, not a premise. The anchor must come from before onset and the tracklet's identity continuity across onset should be treated as unverified.
- The diagnostic counts show a clean same-track anchor for only 15/29 contaminated frames; continuity evidence is simply absent for the rest (withheld by design).

## 5. Strengthening instance-level segmentation / target-mask association without anatomy labels

Possible without any use of anatomical correctness labels:
1. **Resolution**: current masks are 320×180 nearest-neighbour with 4 px tolerance in that space; re-running the same frozen segmenter on a union-region crop at higher resolution is a deterministic input change (no label use).
2. **Mutual-exclusion competition** between prompted/instance masks (C2), or between instance masks and the opponent's skeleton (already partially present as `OPPONENT_LANDMARKS_IN_MASK`).
3. **Mask-pose agreement diagnostics that need no verdicts** (for example the fraction of the owner mask explained by the target skeleton plus the opponent skeleton), used only as reporting, never tuned against verdicts.
4. **Parameter-free or a-priori parameters**: every constant is stated, justified by geometry or a vendor default, hashed and frozen in the candidate's freeze entry before any fresh footage is drawn; no constant is selected by looking at burned verdicts or at fresh verdicts.

Limits: the same general COCO segmenter merges touching bodies (T1) with no amodal ordering; prompted segmentation fails if the prompts are wrong (T2); neither resolves T5.

## 6. Does the existing architecture contain enough information?

My assessment (judgment, not evidence):
- **Partially.** For moderate overlap with a clean pre-contact anchor and distinguishable gear/motion (T3 and some T1/T4), C1 or C3 plausibly removes some wrong-body ownership at the cost of withholding more frames; whether that cost leaves a useful contact yield is exactly what a fresh test would measure.
- **Not for entangled pins, piles and deep clinches** (T5, about a third of the contaminated released frames) or whenever the pose detector itself splits a body across two people (T2) and the masks are merged (T1). A single-view 2D pose detector with a general instance segmenter and no amodal/occlusion reasoning has no signal there, so the only correct behaviour is to withhold.
- Reliable ownership **through** contact would most plausibly need a materially different component: a multi-person tracker with explicit occlusion handling and re-identification across overlap, or video instance segmentation with memory (amodal, per-body), or depth/multi-view input. That is outside the current architecture and not proposed here.
- Realistic outcome of the candidates above: not "solved", but a **smaller, characterised, fail-closed contact region**. A KEEP bar like the separated-body evaluation's (exact upper bound ≤ 5% on a few hundred judgeable emitted frames) would require essentially zero wrong-body calls among emitted contact frames; that is attainable only by high withholding. The yield in contact frames must therefore be reported alongside contamination and compared to C0.

## 7. Notes for a later evaluation design (not started)

- Fresh contact-stratum footage, with contact defined **prospectively by geometry/mask overlap** (not by a human flag), a pre-registered per-landmark wrong-body protocol (localized, not whole-frame PARTIAL/CONTAMINATED, given kappa 0.36 on the frame-level verdict), an independent human primary reviewer (same blocker as R4), a blinded owner second, and Holdout #2 sealed.
- Candidate frozen and hashed before the footage is drawn; one evaluation; burned frames excluded from confirmation.
- Report: contamination of emitted contact frames, yield versus C0, withholding reasons, per-shot clustering.
- Open question for the reviewer: whether this evaluation and the SEPARATED-BODY V1 evaluation of frozen Anatomy V1 may share one acquisition of fresh footage (they would need separate sampling frames and a rule that a clip is used by only one confirmatory evaluation), or must be separate.

## 8. Rulings requested
1. Is the taxonomy (T1–T6) accepted as the working description of the failure, with T5 as a hard ceiling?
2. Which of C1, C2, C3 (if any) may proceed to a **detailed design** with pre-registered constants and KILL criteria (still no implementation)? Is C0 accepted as the mandatory comparator? My own ordering for feasibility and fail-closed strength is C3 ≥ C1 > C2, but this is judgment and is not based on how any candidate would score on the burned frames.
3. Is C2's new pretrained dependency acceptable in principle (a new frozen model component, with registration and rights review)?
4. May the descriptive counts file be recorded as development diagnosis (done, hashed), with no further use of the burned verdicts to choose between candidates?
5. Sequencing: should the R3 final-readiness work (approved in the previous ruling; paused at the owner's redirect) resume now, or wait until this design is ruled on?

STOP for reviewer ruling.
