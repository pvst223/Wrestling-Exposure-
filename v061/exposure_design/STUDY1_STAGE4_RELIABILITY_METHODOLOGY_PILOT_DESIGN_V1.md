# Prospective Study 1 — Stage 4: Reliability / Methodology Pilot — Design Proposal (V1)

Status: DESIGN PROPOSAL ONLY, for independent audit. NOT frozen, NOT executed. DESIGN/RESEARCH ONLY. ANNOTATION_PROVISIONAL. 2026-10-25. No data collected, no code, no equipment selected or recommended, no ethics submission made. The evidence freeze (ANA50) is closed and is not reopened. Every frozen decision (checkpoint V5) is unchanged. The pilot does NOT test the wrestling hypothesis.

Label key used throughout: **[F]** frozen decision · **[P]** design proposal (this document) · **[E]** pilot-derived quantity (set from pilot data, not now) · **[U]** unresolved decision needing evidence or a decision before freeze · **[L]** needs literature support (citations here are recalled from memory, NOT verified in this session; verify before any freeze) · **[V]** claim requiring validation, none made.

---

## 0. Project map (so nothing is silently dropped)

Stage 3 evidence freeze (CLOSED, ANA50) → **Stage 4 reliability/methodology pilot (this design)** → **Gate FV-1: exposure / video decision gate (§G; preserved, unanswered)** → Study 1 protocol freeze → prospective Study 1. The CV / LANDING / Identity / Anatomy branch is PARKED, not abandoned; Gate FV-1 is where its future is decided.

## A. Proposed pilot architecture

### A1. What the pilot must answer (questions Q1–Q9)
Before Study 1 can start, the pilot must show whether the frozen CMJ approach is reliable and practical enough. It answers measurement questions only:
- **Q1** Within-session: is the mean of 3 valid trials stable, and how many trials are really needed? (Frozen at 3; pilot checks, does not reopen unless FAIL.)
- **Q2** Between-session: what are relative reliability and absolute measurement error (typical error) of the primary outcome, mean jump height of 3 trials, on separate non-exposure days?
- **Q3** Learning/familiarisation: how many sessions until scores stop drifting systematically? (feeds the reference-session number [E])
- **Q4** How many reference (baseline) sessions are enough for the later wrestler protocol? [E]
- **Q5** Day-to-day natural variation: how large is ordinary noise, so a later acute change is not mistaken for it?
- **Q6** Practicality: invalid-trial rate, time per test, tester burden, set-up consistency, adverse events, dropout.
- **Q7** Feasibility (methodology only): can the CMJ block be delivered at the venue as soon as safely/logistically feasible after a match-like context, and what elapsed times are actually achievable? Can 24 h and 48 h follow-ups be delivered within workable windows?
- **Q8** If force-time-capable equipment is available: is time to take-off (TTO) reliable and non-redundant enough to be the single conditional secondary? Does impulse merit promotion? If not available: confirm the zero-secondary pathway is intact.
- **Q9** Is the smallest change we would care about large enough relative to measurement noise to be detectable? (requires a decision, see U1)

### A2. Two modules plus one optional module (complexity must earn its place)
| Module | Purpose | Participants | Default |
|---|---|---|---|
| **P1 Reliability core** | Q1–Q6, Q8 | Healthy, trained, injury-free adults who can perform CMJ; not necessarily wrestlers | ON |
| **P2 Wrestler-context confirmation** | Check that P1 error and practicality transfer; Q5, Q6 in the target population; Q7 logistics rehearsal | Whatever wrestlers can be recruited; **no match-exposure outcome analysis** | ON if access and ethics allow; else acknowledged limitation |
| **P3 Positive-control sensitivity check (optional)** | Does the protocol detect a change after a known, standardised stressor larger than its own error, at the immediate-post window and at 24/48 h? Informs Q7/Q8 and the 72 h question | Healthy adults only | **OFF unless auditor decides** (U6) |

Reasoning: P1 is the cheapest way to get the error estimate with adequate precision; P2 is necessary because error in non-wrestlers may not transfer (body mass, motivation, pain, schedule), but it need not be large because it only has to confirm, not estimate, the error. P3 is the only way to learn anything about immediate-post and 24/48 h behaviour without touching the wrestling hypothesis; it is optional because the CMJ's sensitivity to fatigue is already documented elsewhere [L] and the pilot's primary job is error.

### A3. Participant and session structure (design proposal [P], sizes [U])
**P1.** Proposed **n = 15** adults, **k = 4** baseline sessions (S1–S4). Rationale for these numbers is estimation precision, not hypothesis power: with n = 15 and k = 4 the typical-error estimate has (n−1)(k−1) = 42 degrees of freedom; its 95% CI is about 0.82× to 1.27× the estimate. For comparison: n = 12, k = 3 gives df 22, CI 0.77×–1.42×; n = 20, k = 4 gives df 57, CI 0.85×–1.22×. These are computed from the chi-square distribution and are the basis for choosing a middle option; the final n and k are a decision [U2] that trades precision against recruitment burden. Interval between sessions: 48–96 h, same weekday pattern where possible, within ≤ 2 weeks; same time of day ± 1 h [P].
**P2.** Proposed: all available wrestlers up to ~10, ≥ 3 baseline sessions on non-match days if possible, plus the logistics rehearsal in §A6. Treated as descriptive confirmation. If fewer than ~5 wrestlers are available, P2 is reported as a feasibility description only and the P1 error is carried forward with the explicit limitation that transfer to wrestlers is unconfirmed [U3].
**Safety/ethics:** human data collection requires ethics (IRB) review and informed consent beforehand; an injury/readiness screen and stop rules are required, especially for any immediate-post testing. Whether and how institutional review is obtained is an unresolved prerequisite [U9]. No participant-identifying data beyond pseudonymous IDs; no video required for this pilot (see G).

### A4. Within-session CMJ procedure (consistent with the frozen decisions)
Frozen [F]: CMJ alone; hands on hips; self-selected countermovement depth recorded when possible; same device and calculation method within athlete; clock time and warm-up recorded/standardised; footwear/surface standardised on practical grounds; primary outcome = mean jump height of 3 prespecified trials; best trial = sensitivity descriptor only.

Proposed sequence [P]:
1. Arrival, record time of day, readiness/soreness, prior-48 h activity, body mass, any pain/injury; stop rule if pain.
2. **Standardised warm-up**, identical in content and duration every session, written as a script; content/duration [U4] chosen for practicality in a wrestling venue, and not tuned to the data.
3. **Familiarisation** at S1 (and briefly at every session start): a few submaximal then maximal practice jumps with the same instruction script. Rationale: CMJ is a learned skill; familiarisation reduces the learning drift that would otherwise inflate apparent error. Whether S1 data are excluded from the error estimate is decided by Q3 (see C3) [E].
4. **Recorded block:** 5 maximal-effort CMJ attempts, same script. **The primary outcome is the mean of the first 3 valid trials.** Trials 4–5 are pilot-only data used to ask whether 3 trials are enough and whether a trial-order trend exists; they never enter the primary outcome. (Extra trials are cheap here and impossible to recover later; if immediate-post time pressure in P2 rehearsal shows 5 is impractical, only 3 are recorded there.)
5. **Inter-trial rest** is pilot-derived [E]. Two candidate levels are compared, a short rest that is the shortest practical in an immediate-post setting and a longer comfortable rest, assigned in counterbalanced order across S2–S4 and the other sessions at the standard level; the candidate values and the decision rule need literature support [L][U5]. Principle: choose the shortest rest that does not change the mean or inflate error, because immediate post-match time is the scarce resource.
6. **Invalid trials:** pre-defined operational criteria, recorded as a flag plus reason at the time: hands leave hips, visible knee flexion/tuck in flight, landing off the measuring surface or non-simultaneous foot landing (device-dependent), step or hop before take-off, obvious countermovement-free (static) start, device or software error, tester-judged non-maximal attempt (rare; reason recorded). Invalid trials are discarded and replaced by an additional attempt, up to 2 replacements per block; if the block still has fewer than 3 valid trials the block is recorded as incomplete (this is a feasibility outcome). All attempts and flags are retained. Offline re-checking of validity is allowed only where raw force-time or video exists, and uses the same written criteria, decided blind to the jump-height value.
7. **Set-up consistency:** same device, same surface, same footwear standard (practical basis), same position marking, same tester or tester recorded, scripted instructions, same calculation method fixed before the first participant. The jump-height calculation method (e.g., flight-time versus impulse-momentum on a force plate) is chosen **before** data collection from device capability and literature, not from whichever gives the best ICC, because method differences are known to be non-trivial [L][U7].
8. **Countermovement depth** recorded where the device provides it (force-time capable) or by a stated simple method; if not recordable it is marked not recorded, which is acceptable [F].

### A5. Equipment (no selection or recommendation)
The design is written for two capability classes without choosing a product: (1) force-time-capable (force plate or equivalent) and (2) flight-time-only. Class (1) enables TTO/impulse evaluation (§C7); class (2) uses the valid zero-secondary pathway [F]. Which class is accessible is [U8]; nothing here depends on a brand.

### A6. Methodology-only feasibility rehearsals (P2, and P3 if switched on)
- **Immediate-post logistics rehearsal:** at a wrestling training session or match-like occasion, with consent and safety clearance, rehearse the *procedure*: get the athlete from end-of-activity to the CMJ area, deliver the scripted block, and log timestamps (activity end, arrival, warm-up if any, first valid trial). Outputs are timing distributions, completion, invalid rate, safety events and participant acceptability. No pre/post CMJ comparison is analysed or reported in P2.
- **24 h and 48 h follow-up rehearsal:** attempt scheduled follow-up visits after the rehearsal occasion; outputs are attendance, window deviation and burden only.
- **What stays methodology-only:** timing, completion, validity, safety, acceptability, device operation, tester burden, error on non-match baseline days.
- **What would be premature hypothesis testing (not done):** comparing CMJ before versus after a match or training load in wrestlers; reporting direction or size of acute change; relating change to match duration, RPE or any exposure; estimating recovery time course in wrestlers; presenting effect sizes or p-values for exposure–response. If such data are collected incidentally they are sealed until the Study 1 protocol is frozen [P].

## B. Scientific rationale (component by component)

- **Reliability in non-wrestlers first (P1):** error estimation needs repeated measures on stable, non-exposed days; recruiting healthy adults is faster and removes match-schedule contamination. Its weakness, transfer to wrestlers, is why P2 exists and why the limitation is carried forward if P2 is small.
- **Four baseline sessions:** needed to separate learning drift from ordinary day-to-day variation (needs ≥ 3) and to give acceptable precision (df above). Fewer sessions give a wide error interval; more add burden for little precision gain.
- **5 recorded trials but mean of 3 primary:** keeps the frozen primary intact while measuring whether more trials help. This is the cheapest check of Q1.
- **Time of day, warm-up, footwear, surface, depth:** the frozen controls; each is a known source of session-to-session variation [L] and cheap to standardise or record.
- **Counterbalanced two-level rest comparison:** immediate-post testing will be time-limited; the pilot should learn how short the rest can be before it costs validity, rather than assume.
- **No hypothesis analysis in wrestlers:** keeps the pilot's purpose clean and avoids using Study 1 data twice.
- **Positive control optional:** sensitivity matters, but is already documented in the literature [L], so it must earn its place (U6).
- **Efficiency principle applied:** healthy-adult core before wrestler sample; no video; no extra metrics; optional modules default off; no new equipment classes; flight-time-only pathway preserved.

## C. Reliability / error-analysis plan (statistics fixed in advance [P]; threshold values in §D)

**C1. Distinguish relative from absolute.** Relative reliability = how well the test ranks individuals; it depends on between-person spread and can be low in a homogeneous sample despite a small error. Absolute error = size of ordinary noise in the original units; this is what governs whether a within-person change in Study 1 can be seen. Because Study 1 is a within-person design, **absolute error is the primary reliability criterion; ICC is reported but is secondary.**

**C2. Statistics to report for the primary outcome (session score = mean of 3 valid trials):**
1. Two-way (participants × sessions) repeated-measures ANOVA components, used only to extract variance components: between-person, session (systematic), residual. [L] (Weir 2005; Hopkins 2000, as recalled)
2. **Typical error (TE)** = residual SD, in cm, with 95% CI (chi-square). SEM = within-person SD; reported once with the name defined so TE and SEM are not shown as different things.
3. **Coefficient of variation (CV%) of TE from log-transformed data**, only to check heteroscedasticity (whether error scales with jump height). If error is proportional, CV% is the expressed error; if not, TE in cm is.
4. **ICC(A,1) with 95% CI** (absolute agreement, single session score), plus ICC(C,1) as a check on whether systematic session effects drive disagreement; report the CI, never the point value alone [L] (Shrout & Fleiss 1979; Koo & Li 2016, as recalled).
5. **Systematic bias between sessions** (mean difference S1→S4, learning trend) with CI; a plot of every participant's score by session.
6. **MDC95 (minimum detectable change, individual level)** = 1.96 × √2 × SEM, reported as the individual-level noise band; group-level detectability is handled in Study 1, not here.
7. Within-session: ICC and TE across trials 1–3 and 1–5 in each session, and trial-order trend (does jump height change with trial number).
8. Best-trial descriptor: TE of best-of-3 versus mean-of-3, descriptive only [F: best trial = sensitivity descriptor].

**Not included (they would add convention, not information):** Pearson r as a reliability measure; Cronbach's alpha; significance tests of "no difference between sessions" as evidence of reliability; limits of agreement as an additional layer on top of TE unless heteroscedasticity or a clear bias makes the plot informative; multiple reliability coefficients per outcome.

**C3. Familiarisation and learning (Q3).** Estimate the systematic S-to-S trend. The learning plateau is defined as the first session after which the mean change between consecutive sessions is within the noise band and the trend CI includes zero; threshold wording [U10]. Error estimates are then computed with and without pre-plateau sessions; the version excluding them is reported as the error expected in Study 1 after familiarisation.

**C4. Number of reference sessions (Q4).** Analytical, not arbitrary: if the baseline for a person is the mean of k reference sessions and the later post value is a single session, the SD of the difference is TE × √(1 + 1/k) (assuming stable true state). The multiplier is 1.414, 1.225, 1.155, 1.118, 1.095, 1.080 for k = 1…6. The pilot chooses the smallest k for which (a) the learning drift is over by session k's start, and (b) adding a further session reduces the multiplier by less than a pre-set proportion [U11], while remaining practical for wrestlers' schedules. The pilot also reports whether the baseline mean of k sessions is itself stable (within-person SD across the last k). Wrestlers' true baseline may drift with training load and season; this cannot be resolved by a short pilot and is acknowledged [U12].

**C5. Natural day-to-day variation (Q5).** From the non-exposed baseline sessions after the plateau: within-person SD (TE), its CI, whether it varies by person (heterogeneity of error), by time of day, or with recorded soreness/readiness/sleep (descriptive only). P2 repeats this in wrestlers on non-match days. The output is a **noise band** for the primary outcome which Study 1 changes will be read against. Nothing here estimates an exposure effect.

**C6. Sensitivity to rest and trial number.** Compare session scores under the two rest levels (mean difference with CI, and TE) and score using 3 versus 5 trials (difference and TE). Interpreted against the noise band, not by p-values.

**C7. Force-time-capable branch (Q8) — TTO and impulse.** Only if force-time-capable. TTO definition (onset detection from the force trace, quiet-standing duration, bodyweight stability criterion) is fixed before data and applied by a single fixed algorithm; the threshold value is [U13]. Evaluate TTO with the same statistics (TE, CV%, ICC with CI). **TTO earns the single conditional-secondary slot only if** it meets reliability criteria set in §D, its onset detection is stable on every valid trial (no manual adjustment), and it carries information not already in jump height (within-person correlation with jump height across sessions is not near-perfect, and its error is small relative to its own between-person spread). **Impulse** is assessed the same way; it can replace TTO only if it clearly exceeds TTO on both reliability and non-redundancy, because at most one secondary is permitted [F]. If neither qualifies, or the equipment is flight-time-only, **zero secondary is the valid result** [F]. No promotion occurs on the basis of conventional popularity.

**C8. Missing data.** All planned/obtained sessions reported; incomplete blocks counted; no imputation for the reliability estimate; a sensitivity analysis excluding participants with any incomplete session.

## D. PASS / MODIFY / FAIL decision framework

The criteria are predefined as **structures**; numeric thresholds are labelled by how they can be justified. I do not invent unjustified numbers.

| # | Criterion | PASS | MODIFY | FAIL | Threshold source |
|---|---|---|---|---|---|
| D1 | **Absolute error vs smallest effect of interest**: TE (and upper CI bound) relative to the smallest change that Study 1 must be able to detect (SESOI) | Upper CI bound of TE is small enough that the noise band does not swallow the SESOI | TE acceptable only with more reference sessions or more trials | TE so large that the SESOI is within ordinary noise even after allowed modifications | SESOI is a **decision [U1]**, not data; benchmark candidates [L]: 0.2 × between-person SD (Hopkins), published post-exercise CMJ decrements |
| D2 | Relative reliability: ICC(A,1) lower 95% bound | Meets reviewer-fixed floor | Below floor but TE criterion D1 passes and between-person spread is demonstrably narrow | Below floor and D1 also fails | Convention (Koo & Li bands) [L]; a floor value [U14] |
| D3 | Learning/systematic drift after familiarisation | No trend beyond noise from the plateau session on | Plateau later than planned, solved by adding familiarisation/reference sessions | Persistent drift after allowed additions | Pilot-derived [E]; wording U10 |
| D4 | Heteroscedasticity | Error roughly constant, or proportional and handled by CV% | Proportional error requiring log analysis plan | Error so heterogeneous that no single noise band applies | Pilot-derived [E] |
| D5 | Invalid-trial and incomplete-block rates | Low enough that most blocks complete in ≤ planned attempts | Rate reducible by script, setup or tester change | Rate remains prohibitive after one modification cycle | Empirical [E]; cut-offs [U15] |
| D6 | Within-session trial number | Mean of 3 is adequate (3 vs 5 within noise) | Evidence 3 is too few, or trial-order trend | n/a (changing the primary count is a reviewer decision, not an automatic modification) | Pilot-derived [E]; any change to frozen "3" requires independent review |
| D7 | Rest comparison | Shortest practical rest gives same mean and no extra error | Intermediate rest required | No practical rest preserves validity | Empirical [E] |
| D8 | Immediate-post logistics (P2) | Venue delivery achievable with logged elapsed times and no safety event | Procedure changed (location, flow, staffing) | Unsafe or infeasible after one modification cycle | Safety = non-negotiable; elapsed-time distribution [E]; completion cut-off [U16] |
| D9 | 24 h / 48 h follow-up feasibility | Attendance and window adherence workable | Window widened or logistics changed | Follow-up not deliverable | Empirical [E]; cut-offs [U16] |
| D10 | Transfer to wrestlers (P2) | Wrestler TE not materially worse than P1 TE | Wrestler error larger: use wrestler-based noise band | Wrestler error disqualifying on D1 | Descriptive when n small; acknowledge [U3] |
| D11 | TTO / impulse (force-time-capable only) | Qualifies per C7 → one secondary selected | Does not qualify → zero secondary (not a failure) | Not applicable | See C7 |
| D12 | Safety | No serious adverse event | Event leads to screen/stop-rule change | Repeated serious events | Non-negotiable |

**Overall:**
- **PASS** = D1–D5, D8–D10 and D12 pass (D6, D7, D11 may resolve to any non-FAIL state): the measurement protocol is a candidate to freeze, subject to independent audit.
- **MODIFY** = no FAIL, but one or more MODIFY: apply only the permitted modifications listed, repeat the minimum necessary sessions **once**, and re-audit. A second MODIFY on the same criterion escalates to independent review rather than repeating.
- **FAIL** = any D1, D5, D8, D12 FAIL or D2+D1 both failing: do not proceed to Study 1 as designed; independent review decides among restructuring (e.g., 24 h/48 h only if immediate-post is infeasible), further evidence, or reconsideration of the measurement. **Failure does not automatically reopen Candidate #2**; any reopening is a separate reviewed decision.

## E. Minimum data dictionary (reliability pilot)

Pseudonymous IDs only; no names, faces, video or footage.

| Field | Type | Notes |
|---|---|---|
| participant_id | string | pseudonym |
| module | P1/P2/P3 | |
| session_id, session_number | int | |
| session_date, local_clock_time | date, time | time of day |
| hours_since_prior_session | number | |
| tester_id, instruction_script_version | string | |
| device_class (force-time / flight-time), device_id, software_version, calculation_method | string | method fixed before data |
| surface, footwear_standard (Y/N), footwear_note | string | |
| body_mass_kg | number | |
| prior_48h_training/competition (type, hard Y/N), sleep_last_night (h), soreness 0–10, readiness 0–10, pain/injury flag | mixed | descriptive covariates |
| warm_up_script_id, warm_up_duration_min, warm_up_completed (Y/N) | | |
| trial_number (1–5), rest_before_trial_s, rest_condition | | |
| valid_flag, invalid_reason | | invalid reasons from the fixed list |
| jump_height_cm | number | by the fixed method |
| countermovement_depth (if recordable) | number/NA | |
| TTO, impulse, raw force-time file reference | number/NA | force-time-capable only |
| block_complete (Y/N), attempts_used | | |
| session_primary_score | number | mean of first 3 valid trials |
| adverse_event (Y/N, description), stop_rule_triggered | | |
| P2 rehearsal only: activity_end_time, time_arrived, time_first_valid_trial, elapsed_end_to_first_trial_s, follow_up_window_actual_h, followed_up (Y/N), reason_missed | | timing/feasibility only |
| notes | text | |

## F. Unresolved decisions requiring evidence or a decision before freeze
- **U1 SESOI**: the smallest change in jump height Study 1 must be able to detect. Cannot come from pilot error alone; needs [L] and a reasoned decision. This is the single most important gate for D1.
- **U2** Final P1 n and k (proposal n = 15, k = 4).
- **U3** Wrestler access, how many, and how P2 is reported if fewer than ~5.
- **U4** Warm-up content/duration, feasible in a wrestling venue, fixed before data.
- **U5** Rest candidate values and decision rule [L].
- **U6** Whether optional P3 positive control is switched on.
- **U7** Jump-height calculation method, fixed from device capability and literature before data [L].
- **U8** Equipment class available (force-time vs flight-time), without choosing a brand.
- **U9** Ethics/IRB pathway, consent, safety and stop rules, medical oversight; prerequisite to any human data.
- **U10** Wording and threshold for the learning plateau.
- **U11** Pre-set proportion defining "diminishing return" for the reference-session number.
- **U12** Whether wrestler baselines drift across weeks/training; may need a longer observation in Study 1 itself.
- **U13** TTO onset-detection parameters.
- **U14** ICC floor value.
- **U15** Invalid-trial/incomplete-block cut-offs.
- **U16** Completion and attendance cut-offs for immediate-post and 24/48 h feasibility.
- **U17** Whether Study 1 uses an additional same-day pre-match CMJ in addition to separate-day reference sessions (affects what the pilot should test; same-day reliability is not covered here).
- **U18** Citation verification: all literature references in this document were recalled, not checked in this session, and must be verified before any freeze.
- **U19** 72 h trigger (below).

**72 h trigger (conditional) and 24 h + 48 h operationalisation [F framework; P proposal].** The pilot cannot determine in wrestlers whether recovery is complete at 48 h without testing the hypothesis. It can (i) test deliverability of 24 h and 48 h visits (D9), (ii) if P3 is on, show in healthy adults after a known stressor whether the protocol can see a deficit at 24 h and 48 h beyond the noise band, and (iii) fix the windows. Proposed trigger for adding 72 h in Study 1: a **pre-specified interim rule** in the Study 1 protocol (not decided here), based on at least one of: literature or P3 evidence of incomplete 48 h recovery, or an interim blind-to-hypothesis feasibility check in Study 1; and practical feasibility. Whether the rule can be pre-specified now is U19; the pilot's role is limited to deliverability and, optionally, protocol sensitivity.

## G. Future exposure / video decision gate (preserved, NOT answered, NO code or coding now)

**Gate FV-1** sits after Stage 4 and before the Study 1 protocol freeze, and persists in the project map until formally closed by independent review.

**Question carried forward:** once the biological-response measurement is shown to be reliable, which exposure variables are scientifically worth measuring in Study 1, and which of those genuinely require validated video/CV coding beyond match duration + RPE?

- **Inputs from Stage 4:** the noise band and SESOI (can an exposure variable's expected contribution be seen above noise at all?), wrestler-context feasibility, what consent and rights allow, and what D + RPE alone appears able to support.
- **Options the gate must choose among (not chosen now):** (a) D + RPE sufficient; (b) add HR and/or IMU if they earn inclusion [F: conditional]; (c) human-coded event counts such as impacts/bumps/landings from fixed-camera passive video, which would first need their own definition and validation; (d) targeted CV/MP4 development of a specific discrete-event construct, with its own validation, human ground truth and rights clearance.
- **Frozen context that remains true:** broadcast CV exposure development stopped; no CV construct earns inclusion; LANDING V1.1 parked before Pass 1; Identity/Anatomy frozen and unvalidated; footage rights unresolved; no new acquisition.
- **During Stage 4:** no coding of any kind. Fixed-camera passive video is not needed for the pilot. If a venue rehearsal happens and consent and rights explicitly allow, a passive record may be kept to keep the option open, but it is not analysed or coded in this stage.
- **Gate closure requires** an independent reviewer's explicit decision recorded in the ledger; silence does not close it.

## H. Exact next action after this design is independently audited
1. Independent audit of this design.
2. One consolidated **"Pilot design freeze decisions" round** resolving U1–U19 (decisions and evidence), starting with U1 (SESOI), U7/U8 (method and equipment class, no brand), U9 (ethics path) and U3 (wrestler access).
3. Only then issue Pilot Protocol V1 (still no data), audited, frozen with a ledger entry.
4. Only after that: ethics/IRB submission, then execution.
Nothing is executed, collected or purchased before step 3 and ethics clearance.

## I. Confounders and procedural variables
| Variable | Control / Record / Acknowledge |
|---|---|
| Time of day | Control (± 1 h), record clock time |
| Warm-up | Control (script), record |
| Footwear, surface, position | Control on practical grounds, record |
| Device, software, calculation method | Control (fixed), record |
| Tester and instruction script | Control (script, same tester where possible), record |
| Countermovement depth | Record (when possible); acknowledge self-selected variability [F] |
| Prior 48 h training/competition | Record; ask for no unusual exertion 48 h before baseline sessions |
| Sleep, soreness, readiness, pain | Record (descriptive); not adjusted in the reliability estimate |
| Nutrition, hydration, caffeine | Acknowledge; record if simple |
| Motivation, tester encouragement | Control by script; acknowledge |
| Body mass | Record |
| Injury/illness | Screen; exclude or flag |
| Season/training phase | Acknowledge (U12) |
| Learning/familiarisation | Control and estimate (C3) |
| Menstrual cycle phase (if relevant to participants) | Acknowledge; record only if consented and simple |
| Environment (temperature, venue) | Record if cheap; acknowledge |

## J. What would allow freezing the measurement protocol vs force modification (Q13)
- **Freeze candidate:** overall PASS (§D) after independent audit, with U1–U19 resolved, and the noise band and chosen reference-session number, rest, warm-up, trial rules and (if force-time-capable) the secondary decision documented.
- **Modify:** specific MODIFY outcomes; one repeat cycle only; re-audit.
- **Reconsider:** FAIL: independent review decides; the pilot's results are not used to alter any other frozen decision.

## K. Claims boundary
No claim that CMJ is validated in entertainment professional wrestling; no injury-risk prediction; no causal workload claim; no exposure-validity, fatigue, identity, anatomy or physical-metric claim; the pilot yields measurement error and feasibility only. Immediate post-match CMJ would represent "acute net neuromuscular-performance change", not automatically fatigue.
