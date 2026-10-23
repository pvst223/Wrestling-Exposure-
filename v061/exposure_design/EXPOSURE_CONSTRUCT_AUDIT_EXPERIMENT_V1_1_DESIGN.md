# EXPOSURE-CONSTRUCT OBSERVABILITY/RELIABILITY AUDIT — EXPERIMENT V1.1 (design only)
Status: prospective design for independent review, written in response to "REVIEWER MODIFICATION BEFORE IMPLEMENTATION". **Nothing implemented. No coding, no annotation, no tool, no MP4, no fresh data, no frozen system touched.** ANNOTATION_PROVISIONAL; R4 unmet; labeller non-independent (owner); rights UNRESOLVED. This design supersedes section 7 of the route-design proposal (ANA34); the rest of that document is unchanged.

## 0. Summary of changes from the previous proposal
1. **BUMP is DROPPED; LANDING is the only event class** (disposition C). Reasons in section 2.
2. **Low event count is separated from measurement failure** (section 9): fewer than 20 recognised events = `INCONCLUSIVE_PREVALENCE`, never KILL.
3. **All denominators, matching and formulas are frozen here** (sections 5–8). KILL now requires statistical evidence of failure, not only a low point estimate.
4. Thresholds are **kept as previously stated** (reviewer-set utility choices, not optimized on any footage). One criterion is **added for reviewer approval** (performer agreement, section 8); it may be deleted without affecting the rest.

## 1. Construct review — LANDING
**Definition (operational).** One LANDING = the first ground-supported contact of a wrestler's own **feet** on the ring canvas, ring apron, arena floor or equivalent solid supporting surface, ending a **visible airborne phase** (both feet clearly off any surface at the same time, or a jump/drop from an elevated position such as the second/top rope, turnbuckle, apron or table) during live match action. Event time = the first foot-contact instant, coded to 0.1 s.
**Plausible lower-extremity mechanism.** A feet-first landing from flight imposes an impact transient and rapid eccentric work of the knee extensors, plantar flexors and hip extensors to absorb ground reaction force — the same family of loading as drop-landing/plyometric work, which in the sport-science literature is associated with acute neuromuscular fatigue and reduced jump performance (citations to be verified and added to the coding protocol, not asserted here). The ring surface is sprung, which attenuates but does not remove the load. This is a plausibility argument for testing observability, **not** evidence that landings cause CMJ deterioration.
**Why a COUNT is a reasonable first representation.** Landings are discrete events with a clear onset; counts of jumps/landings are a standard first unit in load monitoring; a count needs no calibration, intensity grading or unvalidated CV, and is wrestler-specific by attribution.
**What the count does NOT measure.** Drop height, landing technique, single- vs double-leg, ground reaction force, surface compliance, running/deceleration load, bumps and falls, overall effort, internal load, fatigue, injury risk. Every landing counts equally.
**Recognised without CV/anatomy/identity outputs.** By a human watching the footage; the coder sees no classifier output, shot-level feature or Stage-D result.
**Inclusion criteria (all required).** (I1) the performer is one of the competing wrestlers (not referee, crowd, staff); (I2) a visible airborne phase or elevated take-off precedes the contact; (I3) the first contact is by the feet; (I4) it occurs in live match action, not in a replay or non-match material.
**Exclusion criteria (any).** Walking/running gait steps; stepping or climbing down without flight (including ring steps); hops where both feet do not clearly leave the surface together; landing first on knees, hips, back, chest or hands (these are bumps/falls, out of scope); feet landing on an opponent's body; landing on the ropes/turnbuckle after a jump up (non-ground-supported surface); events seen only in replay (the replay is evidence, not a second event); entrance/celebration outside live match action.
**Ambiguous examples and default rulings.** (a) Springboard flip landing on feet — include. (b) Leapfrog over an opponent landing on feet — include. (c) Being thrown/whipped and landing on feet — include (forced flight counts). (d) Low two-foot hop to avoid a kick — include only if both feet are clearly off the surface together; otherwise exclude. (e) Top-rope dive landing on the opponent's body — exclude. (f) Dismount from the apron to the floor by jumping — include. (g) Landing on feet then immediately collapsing — count the landing once. (h) Dropkick/hip-toss ending on the back — exclude. **Default rule: when in doubt between jump and stride, or between feet-first and other contact, exclude.**

## 2. Construct review — BUMP, disposition: **DROP (option C)**
A body-to-mat bump loads mainly the trunk, shoulder girdle and hips; its pathway to the knee-extensor/plantar-flexor function measured by CMJ is indirect (systemic fatigue, contusion, soreness) and not specific to the lower extremity. Narrowing it to a lower-extremity mechanism would amount to inventing a taxonomy of falls without evidence, and a "recipient" attribution for bumps is attractive because it is easy, which is exactly the Stage-D mistake. BUMP may re-enter only through a separate construct review that supplies a lower-extremity mechanism. I also considered running/deceleration bouts as a second class and **did not retain it**: it needs its own construct work (what is a bout, how is intensity separated from walking) and would add taxonomy before one class is shown observable. **Final classes: 1 (LANDING).** Honest risk of this choice: landings may be rare in the allowed material (section 9 handles this).

## 3. Coding manual (what the owner records per recognised event)
Fields: `source_id`, `event_time_s` (0.1 s; first foot contact; for PARTIAL/INFERRED events, best estimate), `performer` ∈ {A, B, (C…per source table), UNCLEAR}, `observability` ∈ {FULL, PARTIAL, INFERRED}, `evidence` (short text; mandatory for PARTIAL/INFERRED), `note` (≤200 chars). A/B (and any further wrestlers) are fixed per source in a frozen source table taken from the provenance records before coding. The coder works through each source in continuous time order and sees no information other than the footage (with sound) and, for context, the same ±5 s rule as Protocol V1.1 where a shot boundary needs context.
**Observability, per event (frozen definitions).**
- **FULL:** within one continuous shot (no cut between), the coder sees both (a) the airborne phase or elevated take-off and (b) the first foot-contact moment with the feet/lower legs visible at contact.
- **PARTIAL:** exactly one of (a) and (b) is seen in live footage (e.g., cut away before contact, or contact seen without the take-off, or feet obscured at contact).
- **INFERRED:** neither is seen live, yet the coder can state specific evidence that a landing occurred (replay of the landing, a wrestler seen on the elevated spot then on the floor across a cut with the impact sound, commentary or crowd reaction tied to a visible take-off). Mere suspicion is not enough: no stated evidence → not recorded.
**Performer rule.** A/B/other wrestler if the owner can name the wrestler at the moment of landing from the same shot or the ±5 s context (face, attire, graphics, commentary); otherwise UNCLEAR. This is human identification, not a CV output.

## 4. Allowed development footage; scope exclusions
Allowed: the five Stage-D development sources only — b1_orton_rollins_wm31, b2_batch2_clip_condensed, b2_videoplayback_2 (frames < 1934), b2_videoplayback_5 and the full Reigns–Bálor source (779.133 s) — about 18.7 minutes (1,120 s) in total. Not allowed: any other clip, Holdout #2, Gemini, fresh acquisition. Events in material that the frozen Stage-D reference labels mark REPLAY or NON_MATCH are removed **after** coding by a deterministic filter (not shown to the coder; the Stage-D labels are read-only and unchanged). Stage-D footage has already been viewed by the owner while labelling scenes; that prior familiarity (not event counting) is disclosed as a limitation.

## 5. Recognised event, passes and matching
**Pass 1** = the owner's first complete coding. **Pass 2** = a complete independent re-code **≥ 7 days after Pass 1 is completed**, blind to Pass 1 (the tool never shows Pass 1 events, counts or times). Let E1 and E2 be the sets of recognised events (any observability, after the REPLAY/NON_MATCH filter) in Pass 1 and Pass 2. A **recognised event** is any event that the coder recorded under section 3.
**Matching algorithm (frozen, deterministic).** Within each source, build all pairs (i ∈ E1, j ∈ E2) with |t_i − t_j| ≤ 0.5 s (comparison in integer deciseconds, ≤ 5). Choose the one-to-one matching of **maximum cardinality** that, among maximum matchings, **minimises the sum of |Δt|**; remaining ties are broken by the earliest Pass-1 time, then the earliest Pass-2 time. M = number of matched pairs. Performer and observability are **not** used for matching.
**Class disagreement.** Not applicable (single class). If a class is ever added, a time-matched pair with different classes would count as unmatched in both sets.

## 6. Which events enter which denominator
| Event status | Agreement (A) union | Observable fraction (O) | Performer identifiable (I) | Performer agreement (PA) |
|---|---|---|---|---|
| Matched pair | counted once (M) | each member enters its own pass's set | each FULL member enters its own pass's set | enters only if **both** members have performer ≠ UNCLEAR (observability may differ) |
| Only in Pass 1 | enters union (unmatched) | enters E1 | enters if FULL | no |
| Only in Pass 2 | enters union (unmatched) | enters E2 | enters if FULL | no |
Unmatched events never enter PA.

## 7. Exact metrics (computed per pass where stated; all counts are event counts, durations are not used)
- **A (event agreement)** = M / (|E1| + |E2| − M). Descriptive companions: M/|E1|, M/|E2|.
- **O_k (observable fraction), k = 1,2** = (# FULL events in E_k) / |E_k|. **O = min(O_1, O_2).**
- **I_k (performer identifiable), k = 1,2** = (# FULL events in E_k with performer ≠ UNCLEAR) / (# FULL events in E_k). **I = min(I_1, I_2).**
- **PA (performer agreement)** = (# matched pairs, both performers ≠ UNCLEAR, same performer) / (# matched pairs, both performers ≠ UNCLEAR).
- Descriptive only (no criterion): PARTIAL/INFERRED shares; observability agreement among matched pairs; events per minute of live action by source; D for any source with marked start/end.
Taking the minimum of the two passes avoids the bias of restricting O and I to events both passes happened to find.
**Uncertainty.** For each proportion metric, a Wilson 90% two-sided interval (equivalently 95% one-sided bounds) is reported. A is treated as a proportion with denominator |E1| + |E2| − M.

## 8. Criteria (unchanged numbers; not tuned on any footage; reviewer-set utility choices, not statistically derived)
| Metric | PASS-zone | FAIL-zone (point estimate) | Minimum denominator to be evaluable |
|---|---|---|---|
| O | ≥ 0.70 | < 0.50 | min(|E1|,|E2|) ≥ 20 |
| A | ≥ 0.80 | < 0.65 | union ≥ 20 |
| I | ≥ 0.80 | < 0.60 | FULL events per pass ≥ 10 |
| PA (new, for reviewer approval) | ≥ 0.90 | < 0.75 | matched pairs with both identifiable ≥ 10 |
Coherence check: the criteria are internally consistent for event detection. If both passes recognise n events and match m, A = m/(2n − m); A ≥ 0.80 requires m ≥ 0.889n (about 89% of each pass's events matched) and A < 0.65 corresponds to m < 0.788n. With n ≈ 20 one event moves A by about 4–5 points, which is why KILL needs evidence below. O and I use each pass's own full set, not the matched set, so they are not inflated by agreement. PA is needed because "identifiable" alone says nothing about whether the identification is the same twice.

## 9. Outcome logic (frozen before any count exists)
Let N = |E1|, the number of Pass-1 recognised events after the filter.
1. **N < 20 → `INCONCLUSIVE_PREVALENCE`.** This is a statement about sample adequacy in the allowed material, **not** about the construct. No PASS, MODIFY or KILL is issued; the descriptive counts are reported; the only follow-up is a reviewer ruling on whether more already-held development material may be designated (no fresh acquisition). It never triggers KILL.
2. Otherwise, a metric is **evaluable** if its minimum denominator (section 8) is met. A metric whose denominator is below its minimum is `INCONCLUSIVE_DENOMINATOR` and can neither pass nor contribute to KILL.
3. **KILL** if any evaluable metric has a point estimate in its FAIL-zone **and** its one-sided 95% Wilson **upper** bound is below that metric's PASS bound (the data are statistically incompatible with a passing value). Reserved for evidence that the candidate is not sufficiently observable, reliable or attributable.
4. **PASS** if all four metrics are evaluable and every point estimate is in its PASS-zone and no KILL applies.
5. **MODIFY** if all four metrics are evaluable, no KILL applies, and at least one point estimate is below its PASS bound (including FAIL-zone estimates with insufficient evidence). One refinement round only; a repeat audit would be reported as not independent.
6. **INCONCLUSIVE_DENOMINATOR (partial)** if N ≥ 20 but some metric is not evaluable and no KILL applies: report which; no PASS.
**Low prevalence versus measurement failure.** Rule 1 is the only place prevalence changes the outcome; rules 3–6 depend on measurement quality only. With a single class there is no class-level versus candidate-level split. (If a second class is ever approved, a class with fewer than 10 recognised events would be `INCONCLUSIVE` for that class and would neither pass nor kill the other class; this is stated now so it cannot be decided after counts are known.)
**A PASS means only** that landings are recognisable, observable on edited broadcast, attributable to a wrestler and reproducible by one owner over time. It does not establish biological relevance, incremental value over D, or any workload validity, and it does not authorise CV, fresh data or the CMJ pairing.

## 10. What is forbidden during coding and the audit
Identity outputs, anatomical ownership, pose/skeleton, masks, merge guard, carried rows, COM, physical distance/speed/acceleration, Rule V1/V1.1 and any person-box or other CV output, Anatomy V1, C3/Tier-A, any classifier, Holdout #2, Gemini, fresh acquisition, relabelling or reading shot labels while coding, changing criteria or definitions after coding starts.

## 11. Confirmations
- No candidate events were counted, listed or searched for by me; no footage was reviewed for events in preparing this design. (Disclosures: the owner labelled scenes in these sources for Stage D, not events; I viewed a single frame of a private diagnostic video, showing post-match content, after the Stage-D result was frozen.)
- Identity, anatomical ownership, pose, COM, Rule V1/V1.1 and all CV outputs remain forbidden during human coding.
- Frozen/killed components remain untouched (as listed in route-design section 8).

## 12. Exact owner workflow IF the reviewer approves V1.1 (nothing below happens before approval)
1. Reviewer approves (or modifies) this design; the design file hash is recorded in the ledger.
2. I build the **event-coding tool** (new; hash-chained append-only, no CV, no counts displayed to the coder, Pass-2 blind) with tests, a source table frozen from provenance, and an owner package; separate reviewer audit before use.
3. Owner completes **Pass 1** on the five allowed sources (time-ordered), submits, and the pass is closed and hashed.
4. **Wait ≥ 7 days** (enforced by the tool: Pass 2 opens only after the interval).
5. Owner completes **Pass 2** blind.
6. Both passes are exported; I apply the frozen REPLAY/NON_MATCH filter, the frozen matching algorithm and metric code (written and hashed before Pass 1 begins) and report outcomes per section 9, with counts and intervals.
7. STOP; return the frozen result to the reviewer. No tuning, no second pass without a ruling.
