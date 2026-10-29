# Prospective Study 1 — Stage 4 Pilot Design Freeze Decisions Round (U1–U23), V1

Status: DECISIONS DOCUMENT ONLY. DESIGN/RESEARCH ONLY. ANNOTATION_PROVISIONAL. 2026-10-29. Not V3. Not Pilot Protocol V1. Nothing is frozen, executed or collected. V2 (`STUDY1_STAGE4_RELIABILITY_METHODOLOGY_PILOT_DESIGN_V2.md`) is unchanged and remains the audited architecture (audit result: APPROVED WITH MINOR MODIFICATIONS). Gate FV-1 remains OPEN and UNANSWERED. Evidence tags: **[VER]** directly read in this project; **[SEC]** secondary summary or abstract only; **[NV]** not verified / not retrieved; **[DER]** derived here by arithmetic or simulation; **[OWN]** fact only the project owner can supply.

Decision types: S = scientific, T = statistical, O = operational, E = ethical, G = governance.

---

## A. Executive decision summary

| Status | Count | Items |
|---|---|---|
| RESOLVE | 12 | U2, U4, U6, U7, U8, U9, U10, U11, U14, U18, U20, U22 |
| DEFER | 7 | U3, U12, U13, U15, U16, U17, U19 |
| REVIEW | 4 | U1, U5, U21, U23 |
| NOT APPLICABLE | 0 | — |

Four items need independent review or an owner-supplied fact before Pilot Protocol V1 can be **frozen**: U1 (SESOI), U5 (inter-trial rest value), U21 (declared feasible Study 1 size range), U23 (acceptability of the P2-absent safeguards). None of them blocks **drafting** the protocol, because the protocol's audit is where they are reviewed. Three further preconditions to **execution** (not drafting) are facts or approvals that do not yet exist: an ethics determination (U9), a confirmed device class (U8), and recruitment (U2/U3).

---

## B. U1–U23 decision ledger

| # | Item | Status | Type | Decision / reason | Evidence basis | Pilot Protocol V1 consequence |
|---|---|---|---|---|---|---|
| U1 | SESOI | **REVIEW** | S | Numeric value cannot honestly be set now. Governance sub-rules ARE resolved (§C1). | No verified anchor or comparable-context magnitude retrieved; Hopkins 2004 0.2×SD is contextual only [VER, V2] | D1 written with Δ as a named input; Δ locked by independent review before any pilot data are analysed (preferably before collection); freeze blocked until then |
| U2 | Final pilot n / k | **RESOLVE** | T, O | P1: n = 15 target, k = 5 sessions (S1 familiarisation + S2–S5), see §D5 | Precision table [DER, V2 §C4]; Hopkins ≥ 50 guidance [VER, V2] | Carry as pilot size with accepted imprecision; no power claim |
| U3 | Wrestler access (P2) | **DEFER** | O | Access is an owner fact and depends on ethics and venue | none | Draft P2 as a conditional module; conditions as in V2 §A2 |
| U4 | Warm-up | **RESOLVE** | O | Single written warm-up, identical every session, fixed before first participant | Standardisation principle; no literature relied on | Script drafted in Protocol V1; not tuned to data |
| U5 | Inter-trial rest value | **REVIEW** | S, O | No verified literature value; crossover fallback REMOVED; no automatic rest experiment | Searches this round returned no retrievable primary source [NV] | Protocol V1 carries the single-fixed-rest rule and an explicit open slot; freeze blocked |
| U6 | P3 positive control | **RESOLVE** | S, O | P3 stays OFF | Complexity-must-earn-place; safety burden of a stressor | P3 absent; limitation sentence carried |
| U7 | Jump-height calculation | **RESOLVE** | S, T | Rule by device class (§D2) | Linthorne 2001 [VER, V2]; Ruf 2024 [VER] | Method named per class, fixed before first participant |
| U8 | Equipment class | **RESOLVE** | O | Two capability classes, no brand (§D3); availability is an owner fact | Same as U7 | Classes and eligibility text carried; device model entered by owner |
| U9 | Ethics pathway / consent / stop rules | **RESOLVE** (requirements only) | E, G | Required content and sequencing resolved (§D4). The board determination itself is not a design decision and does not yet exist | none needed | Mandatory sections carried; "no human data before documented ethics determination" |
| U10 | Plateau wording | **RESOLVE** | T | S1 excluded from σ_e by default; drift in S2–S5 estimated and reported with CIs; interpretive tolerance inherits U1 | V2 §C2, Weir 2005 [VER, V2] | Wording in §E |
| U11 | Diminishing-return proportion | **RESOLVE** | T | Pre-set proportion WITHDRAWN; reference count chosen by D1 itself | Derived (§C4) | k_ref = smallest count meeting D1, bounded by testable and practical |
| U12 | Wrestler baseline drift | **DEFER** | S | Cannot be known before wrestler data | none | Study 1 protocol must define reference window and drift handling |
| U13 | TTO onset parameters | **DEFER** | T | Conditional secondary; parameters fixed once a force-time device is confirmed | none retrieved | TTO module conditional; absent for flight-time class |
| U14 | ICC review-trigger value | **RESOLVE** | T | Descriptive flag at ICC < 0.5 (between-person SD < σ_e); no pass/fail | Algebra (§E) | Flag sentence only |
| U15 | Invalid / incomplete-block cut-offs | **DEFER** | O | No basis for a number; report descriptively | none | D4 reported, judged after data, fail-closed if undeterminable |
| U16 | Completion / attendance cut-offs | **DEFER** | O | Same | none | D7/D8 as above; safety events remain non-negotiable |
| U17 | Same-day pre-match CMJ | **DEFER** | S | Study 1 design question, not a pilot question | none | Not in pilot |
| U18 | ICC form / notation | **RESOLVE** | T | Shrout–Fleiss ICC(3,1), single measure, formula written out (§F) | Shrout & Fleiss 1979 full text [VER] | Formula in protocol; secondary context only |
| U19 | 72 h trigger | **DEFER** | S | Belongs to Study 1; pilot has no match exposure | none | No 72 h visit in pilot; fail-closed |
| U20 | Inference level for D1 | **RESOLVE** | S, T | Group-level within-person primary; individual MDC descriptive only (§C2) | Study 1 question; claims boundary | D1 wording in §C5 |
| U21 | Feasible Study 1 size | **REVIEW** | O | Logic resolved; the number is an owner-declared access fact needing reviewer acceptance (§C3) | Illustrative arithmetic [DER] | N range slot in D1; nothing computed or frozen |
| U22 | Hopkins Table II discrepancy | **RESOLVE** | T | Protocol uses its own computed chi-square factors; Table II not cited for numbers | Computed [DER] | Sentence in §E |
| U23 | P2-absent safeguards | **REVIEW** | G | The reviewer must accept or reject the V2 §A2 safeguards | none | Safeguards stated; acceptance requested at Protocol V1 audit |

---

## C. Detailed resolution of U1 / U20 / U21 and the exact D1 logic

### C1. U1 — SESOI: REVIEW

**Why it cannot be resolved now.** The SESOI is a statement of importance: the smallest within-person drop in the primary session score that would matter. Nothing verified in this project supplies that. The practitioner and anchor options in V2 §C5 need people or evidence that are not available here. Match-fatigue meta-analyses were located (Claudino et al. 2017, *J Sci Med Sport* 20(4):397–402 [SEC abstract only]; Silva et al. 2018, *Sports Med* 48(3):539–583 [SEC abstract only, no CMJ figures in what was retrieved]) but were not read in full, concern other sports, and would be plausibility benchmarks at most.

**What IS resolved (rules carried into Protocol V1):**
1. The SESOI is set by importance reasoning, never from the observed TE or any pilot data, and never as a multiple of σ̂_e.
2. It is locked, with written rationale, by independent review before any pilot data are analysed (preferably before collection).
3. It is expressed in cm and as % of the athlete's own reference mean.
4. Distribution-based conventions (Hopkins 2004: 0.2 × between-athlete SD [VER, V2]) are contextual benchmarks only, because the between-athlete SD would come from the pilot sample and the convention was proposed for team-sport performance, not wrestling.
5. A resource-based value (V2 §C5 option d, "smallest effect the study could detect") may not serve as the D1 SESOI: it makes D1 pass by construction.
6. The pilot may output a SESOI-agnostic detectability table (§C4) only after Δ is locked, so the table cannot steer Δ.

**What would resolve it.** An independent reviewer decision on approach (practitioner or medical consensus, comparable-context benchmarks read in full, or a combination) with a written rationale and the value. No panel or experiment is launched here.

**Can Pilot Protocol V1 be written and frozen while U1 is open?** Written: yes, with Δ as a named input. Frozen: **no**, because D1 cannot be evaluated without it.

### C2. U20 — inference level: RESOLVE

**Decision.** D1 uses **group-level within-person inference**. Individual-level classification is not required and individual MDC is not a gate.

**Rationale.** Study 1's question is whether match exposure associates with acute within-person change in the CMJ session score across wrestlers. Every claim the project permits is a group-level estimate of change, or its association with D + RPE, relative to each wrestler's own reference. Labelling an individual wrestler as having "truly deteriorated" would need a validated individual-level meaning of change, and the claims boundary rules out fatigue, injury-risk and physical-metric claims. Individual-level MDC (1.96·√2·TE, derived [DER, V2]) is stricter than the group question needs. Reporting it as descriptive context is allowed; letting it pass or fail the pilot is not.

**Limits stated in the protocol.** The SD of observed individual changes includes σ_e·√(1+1/k_ref) plus any real response heterogeneity, so it must not be read as pure noise. If a later Study 1 design wants individual-level statements (for example the proportion exceeding an individual threshold), that needs its own review.

Type: S, T. Evidence: project question and claims boundary; Weir 2005 and Hopkins 2000 on TE and MDC definitions [VER, V2].

**Exact wording for Protocol V1:** "D1 is evaluated at the group level for within-person change. Individual-level MDC is reported descriptively and is not a pass/fail criterion. No individual-level classification of 'change' is made or implied."

### C3. U21 — feasible Study 1 n: REVIEW (logic resolved, number not)

**What is resolved.** D1 needs a Study 1 size only as an input. D1 is evaluated against a range [N_min, N_max] declared before pilot data are analysed.

**Why the number cannot be resolved now.** It is an access fact (how many wrestlers can realistically be recruited, tested before and after matches, and followed at 24 h and 48 h). Only the owner can supply it, and the reviewer must judge whether it is credible. No Study 1 sample-size calculation is done or frozen here.

**What would resolve it.** An owner-declared range with the basis stated (for example a named promotion or roster size), accepted by the reviewer at the Protocol V1 audit.

**Can Protocol V1 be written and frozen with U21 open?** Written: yes, with N_min and N_max as slots. Frozen: no.

### C4. Illustrative detectability arithmetic (illustrative, NOT frozen, NOT a Study 1 sample size)

Per-wrestler acute change is the post value minus the mean of k_ref reference sessions. Under M1 with V2 assumptions A1–A4, its SD is σ_Δ = σ_e·√(1+1/k_ref). For a one-sample test of mean change equal to Δ with SD σ_Δ, the z-approximation is N ≈ 7.85·R², with R = σ_Δ/Δ (two-sided α = 0.05, power 0.80 [DER]). The exact t-based sizes below were computed with the noncentral t. Real response heterogeneity only increases the required N, so these are lower bounds.

Reference-session multiplier √(1+1/k_ref): k_ref = 1: 1.414; 2: 1.225; 3: 1.155; 4: 1.118; 5: 1.095. Going from 3 to 4 references changes σ_Δ by 3.2% and required N by about 6%, which shows the diminishing return directly and is why U11 needs no separate proportion.

Illustration, k_ref = 3 (multiplier 1.155):

| σ_e / Δ | R | N (z-approx) | N (exact t) |
|---|---|---|---|
| 0.5 | 0.58 | 2.6 | 5 |
| 1.0 | 1.15 | 10.5 | 13 |
| 1.5 | 1.73 | 23.5 | 26 |
| 2.0 | 2.31 | 41.9 | 44 |
| 3.0 | 3.46 | 94.2 | 97 |

The table shows how the pilot's noise estimate relative to a locked Δ translates into a Study 1 size. It does not say what Δ or N should be.

### C5. Exact D1 logic (replaces the D1 row of V2 §D)

**Inputs fixed before any pilot data are analysed:**
- Δ (U1), locked by independent review.
- [N_min, N_max] (U21), declared by the owner and accepted by the reviewer.
- Candidate reference counts k_ref ∈ {1, …, k_ref,max}, where k_ref,max is the largest count that the pilot can test out of sample (stable sessions minus 1; with the §D5 design, 3).
- α = 0.05 and power 0.80 as the illustrative planning convention, not a Study 1 commitment.

**Quantities:** σ̂_e^U = upper limit of the two-sided 95% CI for σ_e on post-plateau sessions (chi-square, V2 §C4). σ_Δ^U = σ̂_e^U·√(1+1/k_ref), or the leave-one-session-out prediction-error RMSE where the A1–A4 diagnostics fail. N_req(k_ref) = N from the t-based formula with R = σ_Δ^U/Δ.

**Verdict:**
- **PASS** if some k_ref ≤ k_ref,max gives N_req ≤ N_min.
- **MODIFY** if N_req is above N_min but not above N_max for the best k_ref (Study 1 would need the larger declared size); or if a permitted procedural change not touching the primary outcome (reviewed rest value, script, tester training, device class, set-up) is expected to reduce σ_e. A MODIFY is reported with what changed and is followed by a re-estimate, not by an automatic repeat of the pilot.
- **FAIL** if N_req > N_max for every k_ref ≤ k_ref,max.

**What MODIFY may NOT include.** "More trials" is removed as a D1 pathway. The primary is the mean of the first 3 valid trials; trials 4–5 remain diagnostic only. Any proposal to change the 3-trial primary needs a separate independent review and is not a D1 outcome.

**Fail-closed.** If σ̂_e^U cannot be computed (insufficient post-plateau sessions or failed diagnostics), D1 is not PASS.

**Exact wording for Protocol V1:** "D1 compares the upper 95% confidence limit of the day-to-day within-person error, scaled by the reference-session multiplier, with the independently locked SESOI at the owner-declared range of feasible Study 1 sizes. D1 is evaluated at the group level. It is a measurement-feasibility judgement, not a hypothesis test, a power claim for Study 1, or evidence about wrestlers. Increasing the number of trials is not a D1 modification; the primary outcome remains the mean of the first three valid trials."

---

## D. U5 / U7 / U8 / U9 / U3 / U23 / U2

### D1. U5 — inter-trial rest: REVIEW

**Attempt made.** A literature search this round returned only indirect hits (rest intervals in depth-jump and squat contexts, a poster abstract, and database records) and no retrievable primary source reporting the effect of rest length between repeated CMJ trials on jump height or reliability [NV]. PubMed, PMC, Wiley and JSTOR were not reachable from this environment. A rest value fixed from practical constraints alone (for example "what is convenient") would be a number dressed as evidence.

**Decision.** U5 stays unresolved and is **returned for independent review**. The AB/BA crossover fallback is **removed**. No rest experiment is designed or launched.

**What is resolved.** The structural rule stays: one fixed rest value, identical at every session and time point, so rest cannot create a pre/post bias even if the best rest is unknown.

**What would resolve it.** Either (a) the reviewer supplies or verifies primary sources for a defensible rest value, or (b) the reviewer decides, openly labelled as a practical decision and not as literature-derived, that a stated rest value is acceptable and states the reason.

**Can Protocol V1 be written and frozen with U5 open?** Written: yes, with an explicit open slot. Frozen: no.

**Exact wording for Protocol V1:** "Inter-trial rest is a single fixed duration, identical at every trial, session and time point. The duration is [OPEN — returned for independent review; no value has been set from verified literature]. The pilot does not compare rest durations."

### D2. U7 — jump-height calculation: RESOLVE (S, T)

**Decision.** The method is determined by device class and fixed before the first participant.
- **Class F (force-time-capable):** primary jump height by the **impulse–momentum** method from the vertical ground reaction force. A trial without a valid still start (already an invalid-trial criterion in V2 §A4.6) is invalid and replaced, not recalculated. Flight-time jump height from the same signal may be computed as a **descriptor only**, never as the primary.
- **Class T (flight-time device):** primary jump height by **flight time**.
- The same device and the same method are used for an athlete at every session and time point. Values from different methods or classes are never pooled into one σ_e or compared with each other; σ_e is reported per class.

**Rationale.** The two methods give systematically different values, with flight time usually larger: about 0.5–2 cm with hands on hips in Linthorne 2001 [VER, V2 §A4.7], and 3.2 cm for a mat against a force plate in Ruf 2024 [VER]. A systematic offset cancels within athlete only if the method never changes. The rule avoids double analysis and does not need a method comparison study.

**Exact wording for Protocol V1:** "Jump height is calculated by the impulse–momentum method when a force-time device is used and by the flight-time method when a flight-time device is used. The method is fixed before the first participant, is identical across all sessions and time points for each athlete, and values from different methods are never combined or compared."

### D3. U8 — equipment capability class: RESOLVE (O)

**Decision.** Two capability classes, no brand or product named.
- **Class F:** a device that records vertical ground reaction force over time, permitting a still-weighing phase, take-off detection and impulse–momentum calculation. Eligible for the conditional TTO secondary and for impulse assessment.
- **Class T:** a device that measures flight time (or gives jump height from it) but not force-time. Zero secondary outcomes is the valid result for Class T.
- Force plate preferred, not required (frozen).
- Any device: calibration or zero check recorded each session; sampling rate and software version recorded; same device for an athlete throughout; the device model is entered by the owner and is an owner fact. A minimum sampling rate for Class F is not set here because no verified source was read [NV]; Protocol V1 must state the device's rate and the reviewer may set a minimum.

**Exact wording for Protocol V1:** "Equipment is described by capability class (F: force-time; T: flight-time). The device class is confirmed by the project owner before the protocol is frozen. Calibration, sampling rate and software version are recorded."

### D4. U9 — ethics requirements: RESOLVE (requirements only) (E, G)

**Decision.** Protocol V1 must contain the following, and the sequencing rule is non-negotiable.
1. **Sequencing:** no human data collection, recruitment or testing before a documented determination from the ethics review body responsible for the investigator's institution (approval or a documented exemption).
2. **Consent:** written informed consent covering purpose (a methods pilot, not a wrestling hypothesis test), procedures, maximal-effort jumping, time, risks, voluntariness and withdrawal without penalty, data handling, pseudonymous IDs, and, for P2, that participation has no bearing on employment or standing with any promotion.
3. **Screening:** health and injury screening before each session; pain or injury at arrival is recorded and stops maximal jumping.
4. **Stop rules:** stop on pain, dizziness, instability or participant request; any adverse event is logged; an immediate-post session (P2) is stopped by tester or medical staff discretion.
5. **Medical oversight:** a named responsible clinician or qualified first-aid person is identified for immediate-post testing. The name is an owner fact.
6. **Data protection:** pseudonymous IDs; no video and no footage; no identifiable data in the repository.

**What is not resolved.** Which board applies, whether the pilot is exempt, and whether approval has been obtained. These are governance events outside the design and are not claimed.

**Exact wording for Protocol V1:** "No participant is recruited and no data are collected until the responsible ethics review body has issued a documented determination. Participants give written informed consent. Screening and stop rules apply at every session. A named responsible clinician or qualified first-aid person is present for any immediate-post testing."

### D5. U3 / U23 / U2

**U3 — DEFER.** P2 is conditional on access, ethics, venue feasibility and whether it would change the transfer or logistics conclusion (V2 §A2). Wrestler access cannot be known from the design. Protocol V1 is written with P2 as a conditional module that is switched on only if all four conditions hold. Resolving information: owner-supplied access and an ethics determination.

**U23 — REVIEW.** The reviewer must accept or reject the P2-absent safeguards of V2 §A2: (i) wrestler σ_e estimated from Study 1's own exposure-free reference sessions, analysed without reference to post-match outcomes; (ii) follow-up attendance monitored descriptively; (iii) because immediate-post deliverability and safety cannot be learned without trying, either an accepted stated safety plan or a pre-specified Study 1 run-in with predefined stopping rules. Whether (iii) is acceptable is a governance judgement that cannot be made by the designer. Protocol V1 can be written with the safeguards stated; it cannot be frozen on a P2-absent path until the reviewer accepts them.

**U2 — RESOLVE (T, O): n = 15 target, k = 5 sessions.**
- Sessions: S1 (familiarisation), S2–S5, 48–96 h apart, same time of day ± 1 h, completed within about three weeks. The exact scheduling window is an operational detail for Protocol V1.
- Reason for k = 5 over k = 4: with S1 treated as pre-plateau, k = 4 leaves 3 stable sessions and cannot out-of-sample test a 3-session reference mean (V2 §C3). k = 5 leaves 4 and can test up to k_ref = 3 by leave-one-session-out. Precision: 4 stable sessions at n = 15 gives a 95% factor of 0.82–1.27; 3 stable gives 0.79–1.35 [DER, V2 §C4]. Sessions are low-cost for healthy volunteers, so the extra session earns its place.
- Imprecision is accepted openly: Hopkins 2000 suggests about 50 participants for reasonable precision and notes most published reliability studies are pilots [VER, V2]. D1 uses the upper CI limit, so imprecision makes D1 harder to pass instead of being hidden.
- If fewer than 15 complete, the same analysis is run and the wider CI is carried by the upper-limit rule. No minimum-n threshold is invented.
- This is not a power calculation and not a Study 1 sample size.

**Exact wording for Protocol V1:** "The reliability core targets 15 participants completing 5 sessions (S1 familiarisation, S2–S5). This size is a pilot size with accepted imprecision; it is not a power calculation and is not a Study 1 sample size."

---

## E. Remaining lower-priority decisions

- **U4 (RESOLVE, O).** "A single written warm-up is used at every session, identical in content and duration, fixed before the first participant and not adjusted to data. It is low in fatigue load. Warm-up content and clock time are recorded. Any difference in warm-up between baseline and post conditions in a later module is recorded as a known factor, not corrected."
- **U6 (RESOLVE, S, O).** "P3 (positive-control stressor) is OFF." Reason: a standardised stressor adds ethics and safety burden and a second experiment, and the project's methodological questions Q1–Q8 do not need it. **Limitation to carry:** without P3 the pilot does not show that the protocol detects a known true change; it shows only whether the noise is small relative to a locked Δ. A null Study 1 result must be read with that limit. The reviewer may switch P3 on.
- **U10 (RESOLVE, T).** "S1 is excluded from the error estimate by default, irrespective of its data. The session-effect profile for S2–S5 is estimated and reported with confidence intervals and judged by magnitude, not by a p-value. The tolerance for calling the profile flat is the locked SESOI (U1); no separate numeric tolerance is set. An analysis including S1 is reported as a sensitivity analysis." This narrows the V2 data-driven plateau rule to remove analytic flexibility.
- **U11 (RESOLVE, T).** The pre-set diminishing-return proportion is **withdrawn**. "The Study 1 reference-session count is the smallest k_ref for which D1 is met, bounded by the largest count the pilot can test and by what wrestlers' schedules allow." The multiplier table in §C4 gives the diminishing return directly.
- **U14 (RESOLVE, T).** With sessions stable, ICC = σ²_a/(σ²_a + σ²_e). ICC = 0.5 exactly when the between-person SD equals σ_e (algebra [DER]). "The ICC is reported with its CI and the between-person SD. A flag is raised if the point estimate is below 0.5, meaning between-person spread is smaller than day-to-day error. The flag prompts a reading (range restriction, or error large relative to spread) and has no pass/fail consequence." No Koo & Li interpretation bands are used [NV].
- **U22 (RESOLVE, T).** The computed upper factors for n = 15, k = 4 (df = 42) are 1.22 (90%) and 1.27 (95%) [DER]. Hopkins 2000 Table II gives 1.24 [VER, V2]. A 90% factor of 1.24 is reproduced at df = 36 (1.244), but no convention linking df = 36 to 15 × 4 was established, so this is a hypothesis only. "Confidence factors in this protocol are computed from the chi-square distribution under the stated assumptions. Hopkins 2000 Table II is not used as a source of numbers; the discrepancy remains unexplained."
- **U12 (DEFER, S).** Wrestler baseline drift across weeks and training phases cannot be known before wrestler data. Resolving information: Study 1 reference-session data (and P2 non-match baselines if P2 runs). Protocol V1 can be written and frozen without it; Study 1's protocol must define the reference window and drift handling before data.
- **U13 (DEFER, T).** TTO onset parameters (quiet-standing duration, body-weight stability, threshold) depend on a confirmed Class F device and on a verified algorithm convention that was not retrieved. Resolving information: device confirmed (U8) and the reviewer's choice of one documented algorithm, fixed before the first participant, with no manual adjustment. Protocol V1 can be written and frozen with a conditional TTO module that is absent for Class T.
- **U15 (DEFER, O).** Cut-offs for invalid-trial and incomplete-block rates have no verified basis. The rate is reported descriptively; D4 is judged after data by the reviewer with the reasoning disclosed; if it cannot be judged, D4 is not PASS. Protocol V1 can be written and frozen.
- **U16 (DEFER, O).** Same for completion and attendance. Safety events remain non-negotiable at any rate.
- **U17 (DEFER, S).** Whether Study 1 adds a same-day pre-match CMJ is a Study 1 design decision and is not part of the pilot. Resolving information: P2 logistics findings (if P2 runs) and the Study 1 design stage. Protocol V1 can be written and frozen.
- **U19 (DEFER, S).** The pilot has no match exposure, so no 72 h visit is included. Any 72 h trigger is Study 1's, defined before data, and an outcome-dependent trigger is an adaptive design needing its own review. Fail-closed default stands: 24 h + 48 h only.

---

## F. U18 — ICC model and notation (audit condition 1)

### F1. What was directly verified and what was not

**Verified (Shrout & Fleiss 1979, *Psychological Bulletin* 86(2):420–428, full text read [VER]):**
- ICC(2,1) is the two-way random-effects, single-measure coefficient: ICC(2,1) = (BMS − EMS)/(BMS + (k−1)·EMS + k·(JMS − EMS)/n), where BMS = between-targets mean square, JMS = between-judges mean square, EMS = residual mean square, k = judges, n = targets.
- ICC(3,1) is the two-way mixed single-measure coefficient: ICC(3,1) = (BMS − EMS)/(BMS + (k−1)·EMS).
- Random judges are used when they are a sample of a population to which results are to be generalised; fixed judges (mixed model) when the specific judges are the only ones of interest. The two share EMS, so √EMS is the same.

**Not verified:** the McGraw & Wong 1996 form definitions (ICC(A,1), ICC(C,1) notation and labels) [NV]; Koo & Li 2016 content [NV]; the agreement/consistency labels as applied to the Shrout–Fleiss forms (the labels are McGraw & Wong terminology). Secondary pages surfaced by search (IBM SPSS support, UCLA OARC) were not opened or read here and are not relied upon [NV].

### F2. The model issue and its resolution

V2 stated that sessions are treated as a sample of days with an absolute-agreement form, while model M1 treats the session profile s_j as estimated, systematic session effects. The two statements conflict. The conflict resolves as follows.
- A "session" j is an **ordered occasion** shared by all participants, not a calendar day. Different participants test on different calendar days, so a day-specific random shock belongs in the residual e_ij, not in a session effect common to everybody. What the session term captures is **systematic order or practice change**, which is estimated and reported, not a random draw from a population of sessions.
- Therefore the model-consistent coefficient is the **fixed-occasion** one: **ICC(3,1), two-way mixed, single measure**, computed on post-plateau session scores. The "generalise to other days" target is carried by σ_e (= √EMS), which is identical under both forms.
- Residual session effects (s_j ≠ 0) are quantified through the s_j profile and its CIs, not through a second ICC. Where s_j ≈ 0 ICC(2,1) and ICC(3,1) coincide numerically, so the choice matters only if a systematic offset remains, and then it is shown by the profile.
- "Single measure" refers to one **session score** (the mean of the first 3 valid trials), not one jump. The average-measure form is not reported.

**Replacement for V2 §B4:** "The ICC reported is Shrout–Fleiss ICC(3,1) (two-way mixed, single measure), ICC = (BMS − EMS)/(BMS + (k−1)·EMS), computed on post-plateau session scores, where BMS is the between-participants mean square, EMS the residual mean square and k the number of post-plateau sessions. The formula is stated in full so that no notation from another source is needed. TE is the square root of EMS. The ICC is secondary context and a descriptive flag (U14); it cannot fail the protocol."

**Also corrected:** V2 §B3 states the SD_total·√(1 − ICC_agreement) ≈ √(σ²_s + σ²_e) identity as derived and to be confirmed. It is not needed by any decision and is withdrawn from the protocol; SEM is reported as √EMS only.

**Remaining dependency:** none of the resolved decisions depends on McGraw & Wong, Koo & Li or interpretation bands.

---

## G. Confirmation that the three audit conditions were implemented

1. **ICC.** Done in §F. The fixed/random conflict is resolved (fixed-occasion model, ICC(3,1)); the exact form and formula are verified against Shrout & Fleiss full text; verified and unverified material are separated; ICC remains secondary context and a descriptive flag, with no power to fail the protocol (§E U14).
2. **Inter-trial rest.** Done in §D1. An attempt to resolve U5 from literature returned no verified source; the AB/BA crossover is removed as a pre-authorised fallback; U5 is returned for independent review; no rest experiment is invented or launched.
3. **D1 and more trials.** Done in §C5. "More trials" is removed from D1's MODIFY pathway; the primary stays the mean of the first 3 valid trials; trials 4–5 stay diagnostic only; any change to the 3-trial primary requires separate independent review.

---

## H. Decisions safe to carry into Pilot Protocol V1

U2 (n = 15, k = 5; pilot size, not power), U4, U6 (P3 off, with limitation), U7, U8 (class rule), U9 (requirements and sequencing), U10, U11, U14, U18, U20, U22, the D1 structure of §C5 with Δ and the N range as inputs, the single-fixed-rest rule of §D1 (value open), and the DEFER items' stated handling (U3, U12, U13, U15, U16, U17, U19). All frozen decisions in the task statement carry unchanged.

---

## I. Items that block freezing versus items that may legitimately remain pilot-derived

**Block FREEZING of Pilot Protocol V1 (not drafting):**
- **U1** SESOI value and rationale, locked by independent review.
- **U5** Inter-trial rest value (or the reviewer's explicit practical decision).
- **U21** Owner-declared feasible Study 1 range, accepted by the reviewer.
- **U23** Reviewer acceptance of the P2-absent safeguards.

**Block EXECUTION (preconditions that do not yet exist, independent of the design):** a documented ethics determination (U9), a confirmed device class and model (U8), and recruitment (U2/U3).

**May legitimately remain pilot-derived or Study 1-derived:** U3 (access), U12 (drift), U13 (TTO parameters, if a Class F device), U15 and U16 (feasibility cut-offs, judged descriptively), U17 (same-day pre-match CMJ), U19 (72 h trigger).

---

## J. Final recommendation

**READY TO DRAFT PILOT PROTOCOL V1**

(Drafting only. Freezing is blocked by U1, U5, U21 and U23 as listed in §I. Nothing has been frozen, executed or collected, no equipment recommended, and Gate FV-1 remains OPEN and UNANSWERED.)
