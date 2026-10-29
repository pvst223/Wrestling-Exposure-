# Prospective Study 1 — Stage 4: Reliability / Methodology Pilot — Design Proposal (V2)

Status: DESIGN PROPOSAL ONLY, returned for a second independent audit. NOT frozen, NOT executed. DESIGN/RESEARCH ONLY. ANNOTATION_PROVISIONAL. 2026-10-29. Supersedes `STUDY1_STAGE4_RELIABILITY_METHODOLOGY_PILOT_DESIGN_V1.md` (unchanged, kept as audit trail). V2 is a narrow methodological correction pass in response to the audit result "NOT APPROVED — narrow methodological correction required". The architecture is preserved. No data collected, no code written for the project, no equipment selected or recommended, no ethics submission made. The evidence freeze (ANA50) is not reopened; every frozen decision in checkpoint V5 is unchanged; Gate FV-1 is preserved and unanswered. The pilot does NOT test the wrestling hypothesis.

Label key: **[F]** frozen decision · **[P]** design proposal · **[E]** pilot-derived quantity · **[U]** unresolved decision · **[VER]** verified in this session against a retrieved source (level stated in §K) · **[NV]** not verified; no decision rests on it · **[CALC]** arithmetic or simulation check run in this session on assumed models, not on data (throwaway check, not project code, not committed).

## Correction ledger (audit item → exact V2 change → status)

| # | Audit item | Exact V2 change | Status | Remaining unresolved | Verified literature used |
|---|---|---|---|---|---|
| 1 | TE/SEM/residual SD treated as interchangeable | §B defines the primary-score estimand and model M1; TE, within-subject SD, √MSE-SEM and σ_e are one quantity reported once; lists exactly when other "SEM"/CV/MDC forms are NOT equivalent; MDC is a derived transform, not independent information | Resolved in design | None beyond model-adequacy diagnostics (D2) | Hopkins 2000; Weir 2005 |
| 2 | ICC model | §B4 states what the ICC estimates (session-score variance share), single-measure refers to one session score, agreement vs consistency chosen from the inference, computed on post-plateau sessions; secondary only | Resolved in design | ICC(A,k) not reported; definitions of McGraw–Wong forms to be re-checked against source (U18) | Shrout & Fleiss 1979; Weir 2005; McGraw & Wong 1996 (bibliographic only) |
| 3 | Reference-session formula | §C3 states assumptions A1–A4, diagnostics, and the replacement approach (leave-one-session-out prediction error with person-level bootstrap) if they fail; simulation shows where the multiplier fails | Resolved in design | Diagnostics have low power at k≈4–5 (acknowledged) | [CALC] only |
| 4 | n = 15, k = 4 precision | §C4 re-derives df and CIs under M1, shows the CI is exact under stated assumptions and approximate otherwise, compares practical alternatives including post-plateau k, flags a discrepancy with Hopkins 2000 Table II, notes Hopkins' ≥50 participants guidance | n/k remain a working candidate | Final n and k (U2); Table II discrepancy (U22) | Hopkins 2000 |
| 5 | U1 / SESOI | §C5 defines SESOI for within-person CMJ, separates importance from detectability and from measurement error, lists candidate approaches, labels the 0.2×SD convention as a contextual benchmark only; no value adopted | U1 left unresolved | U1, U20, U21 | Hopkins 2004; Anvari & Lakens 2021; Cormack 2008 |
| 6 | Inter-trial rest | Mini-experiment removed from P1. Rest becomes a single fixed protocol choice, identical at every session and time point, to be fixed from verified literature plus practical limits. Verified literature was not found, so the value stays unresolved. A fully specified AB/BA crossover is kept only as a conditional fallback | Mini-experiment eliminated; value unresolved | U5 | none |
| 7 | ICC pass/fail role | D1 (absolute error vs justified SESOI) is the primary gate; ICC is context plus a justified review trigger, with no veto | Resolved in design | Trigger value (U14) | Hopkins 2000; Weir 2005 |
| 8 | One-modification-cycle | Restated as a project governance rule that triggers mandatory independent review, not a statistical or biological law | Resolved | None | none |
| 9 | 72 h trigger / U19 | §F2 separates logistics information from outcome-dependent information, names what may trigger 72 h, labels any outcome-dependent rule as adaptive design belonging to the Study 1 protocol before data, and fails closed | Resolved in design; trigger itself unresolved | U19 | none |
| 10 | P2 conditionality | P2 is conditional on access, ethics, feasibility and informativeness; §A2 lists what uncertainty remains without P2 and what blocks freeze versus what can be carried into Study 1 with safeguards | Resolved in design | U3, U23 | none |
| 11 | Literature verification | §K lists what was verified, to what level, and what was not; unverifiable claims are removed or left unresolved | Partly resolved | U18 (remaining) | see §K |
| 12 | Data dictionary / confounders | Dictionary preserved; nutrition/hydration/caffeine and menstrual-cycle fields removed from the collected set (acknowledged only); sleep optional; rest-condition field removed | Resolved | None | none |
| 13 | Gate FV-1 | §G copied from V1 without change | Preserved, unanswered | Gate remains open | none |

## 0. Project map

Stage 3 evidence freeze (CLOSED, ANA50) → **Stage 4 reliability/methodology pilot (this design)** → **Gate FV-1: exposure / video decision gate (§G; preserved, unanswered)** → Study 1 protocol freeze → prospective Study 1. The CV / LANDING / Identity / Anatomy branch is PARKED, not abandoned.

## A. Revised pilot architecture

### A1. Questions the pilot must answer (methodology only)
- **Q1** Within-session: how does the error of the session score depend on the number of trials averaged (1…5), so the frozen "3" is checked, not reopened?
- **Q2** Between-session: what is the absolute day-to-day within-person error σ_e of the primary session score, and relative reliability as context?
- **Q3** Learning: from which session does the systematic session effect stop?
- **Q4** How many reference sessions does the later protocol need?
- **Q5** How large is natural day-to-day variation (the noise band against which later acute changes are read)?
- **Q6** Practicality: invalid-trial rate, time per block, adverse events, dropout.
- **Q7** Feasibility only: can the block be delivered as soon as safely/logistically feasible after a match-like context, and can 24 h and 48 h visits be delivered?
- **Q8** If force-time-capable: reliability and non-redundancy of TTO; whether impulse merits promotion; otherwise the zero-secondary pathway stays.
- **Q9** Given a justified SESOI, can it be seen above the noise band? (needs U1)

### A2. Modules
| Module | Purpose | Participants | Default / condition |
|---|---|---|---|
| **P1 Reliability core** | Q1–Q6, Q8, Q9 | Healthy, trained, injury-free adults able to perform a CMJ | ON |
| **P2 Wrestler-context module** | Check transfer of σ_e and practicality to wrestlers; logistics rehearsal for Q7 | Wrestlers, if recruitable; no match-exposure outcome analysis | **CONDITIONAL** on (i) wrestler access, (ii) ethics approval, (iii) venue/athlete feasibility, (iv) whether it would materially change the transfer or logistics conclusion. Not universally necessary |
| **P3 Positive-control sensitivity check** | Does the protocol see a change after a known standardised stressor beyond the noise band, at the immediate-post window and at 24/48 h? | Healthy adults | **OFF** unless the auditor switches it on (U6) |

**If P2 cannot be performed** the following uncertainty remains: whether σ_e measured in healthy adults applies to wrestlers (body mass, motivation, pain, schedule, baseline drift); whether immediate-post delivery at a venue is safe and achievable; acceptability; follow-up attendance. These do NOT all block freeze equally:
- *Can be carried into Study 1 with safeguards (reviewer must accept, U23):* wrestler-specific σ_e is estimated from Study 1's own reference sessions, which are exposure-free and analysed without reference to post-match outcomes; follow-up attendance is monitored descriptively.
- *Blocks freeze unless an independent reviewer accepts a stated safety plan:* immediate-post deliverability and safety, because it cannot be learned without trying. The alternative safeguard is a pre-specified run-in in Study 1 with predefined stopping rules; whether that is acceptable is a reviewer decision.

### A3. Participants and sessions (working candidate [P]; final size [U2])
**P1 working candidate:** n = 15, k = 4 baseline sessions S1–S4, 48–96 h apart within ≤ 2 weeks, same time of day ± 1 h. S1 includes familiarisation. The precision of the error that Study 1 will actually use depends on the number of POST-PLATEAU sessions, not the total (see §C4). If S1 is excluded as pre-plateau, k = 4 leaves 3 stable sessions and cannot empirically test a 3-session reference mean (§C3), so k = 5 is carried as the practical alternative. **n and k are not frozen.**
**P2 (if performed):** all recruitable wrestlers, up to about 10, ≥ 3 non-match baseline sessions where possible, plus the logistics rehearsal below. If fewer than about 5 wrestlers participate it is reported descriptively only.
**Safety/ethics:** ethics review and informed consent are prerequisites to any human data; screening and stop rules apply, especially for immediate-post testing (U9). Pseudonymous IDs only; no video needed for this pilot (§G).

### A4. Within-session CMJ procedure
Frozen [F]: CMJ alone; hands on hips; self-selected countermovement depth recorded when possible; same device and calculation method within athlete; clock time and warm-up recorded/standardised; footwear/surface standardised on practical grounds; primary = mean jump height of 3 prespecified trials (defined here as the **first 3 valid trials**); best trial = sensitivity descriptor only.

1. Arrival; record time of day, soreness/readiness (frozen covariates), prior-48 h activity, body mass, pain/injury; stop rule on pain.
2. Standardised written warm-up, identical every session (content and duration U4; fixed before data; not tuned to data).
3. Familiarisation at S1 and briefly at each session start: submaximal then maximal practice jumps with the same script. Whether S1 data enter the error estimate is decided by the plateau analysis (§C2).
4. Recorded block: 5 maximal CMJ attempts. **Primary = mean of the first 3 valid trials.** Trials 4–5 are diagnostic only and never enter the primary.
5. **Inter-trial rest: one fixed value, identical at every session and at every time point (baseline and immediate-post alike)**, fixed before data from verified literature plus practical limits (U5). Rationale: if rest differed between baseline and post testing, rest would become a systematic bias in the pre/post comparison; a single common value removes that problem, and trial-order trend at that rest is still observed in trials 1–5. The V1 two-level comparison is removed. *Conditional fallback (only if the auditor decides the rest value cannot be set from verified literature):* an AB/BA crossover in the two post-plateau sessions, randomising participants to sequence in equal blocks, rest as the only intended difference, with the rest effect estimated as half the difference between sequence-specific session differences (which cancels any period effect), a pre-stated equivalence margin tied to U1, and no use of the result to select whichever rest gives the smallest error.
6. Invalid trials: operational criteria (hands leave hips; visible knee flexion or tuck in flight; landing off the measuring surface or non-simultaneous landing, device-dependent; step or hop before take-off; no still start; device/software error; tester-judged non-maximal attempt with reason). Invalid trials are discarded and replaced, up to 2 replacements per block; fewer than 3 valid trials = incomplete block (a feasibility outcome). All attempts and flags retained. Offline re-checks use the same written criteria, blind to the jump value, only where raw force-time or video exists.
7. Set-up consistency: same device, surface, footwear standard, position marking, scripted instructions, tester recorded, calculation method fixed before the first participant (U7). Verified facts relevant to U7: flight-time and impulse-momentum jump heights differ and the flight-time method usually gives the larger value, about 0.5–2 cm with hands on hips in the one paper checked [VER Linthorne 2001]; impulse-momentum depends on correctly identifying the still start and body weight. The method is chosen from device capability and verified literature before data, not from which gives the best reliability.
8. Countermovement depth recorded where the device provides it, otherwise marked not recorded [F].

### A5. Equipment
No selection or recommendation. Two capability classes only: force-time-capable, and flight-time-only (zero-secondary pathway [F]). Which is available is U8.

### A6. Methodology-only rehearsals (P2, and P3 if on)
Immediate-post logistics: with consent and safety clearance, rehearse getting an athlete from end-of-activity to the CMJ area and delivering the scripted block; log timestamps and completion. 24 h/48 h: attempt scheduled follow-up visits; log attendance, window deviation, burden. **Methodology-only:** timing, completion, validity, safety, acceptability, device operation, error on non-match days. **Premature hypothesis testing (not done):** any comparison of CMJ before versus after a match or load in wrestlers; direction or size of acute change; relation to duration, RPE or any exposure; recovery time course in wrestlers; effect sizes or p-values for exposure–response. Incidental data of that kind are sealed until the Study 1 protocol is frozen.

## B. Reliability / error estimand and model

### B1. Measurement unit and estimand
The measurement unit is the **session score** Y_ij = mean jump height (cm) of the first 3 valid trials for person i in session j, under one fixed device, calculation method, rest, warm-up and script. The estimand for absolute error is the **within-person, between-day standard deviation of the session score on exposure-free days after learning has plateaued**, because Study 1 will compare one session score against baseline session scores on other days.

### B2. Model M1 (primary), variance decomposition
Y_ij = μ + a_i + s_j + e_ij, with a_i ~ N(0, σ²_a) (persons), s_j fixed session effects (systematic change, e.g. learning), e_ij ~ N(0, σ²_e) independent. Estimation: with one score per person per session, complete and balanced, σ̂²_e = residual mean square (MSE) of the two-way ANOVA, df = (n−1)(k−1); with missing sessions, REML mixed model.
σ²_e is a **total** day-to-day variance: true day-to-day state variation + trial-to-trial noise averaged over the 3 trials + set-up and tester variation. It is deliberately not "instrument error alone", because what Study 1 must be read against is the full between-day noise.
A nested companion model M2 at trial level, Z_ijt = μ + a_i + s_j + c_ij + τ_t + ε_ijt (c_ij random session state, τ_t fixed trial-order effect, ε_ijt trial noise), splits σ²_e of an m-trial mean into σ²_c + σ²_ε/m (if trial errors are independent given the session). This answers Q1 (what 1, 3 or 5 trials buy) without conflating day and trial variation. Its assumptions are checked, not assumed.

### B3. Names and equivalences
- **One quantity, one name: typical error (TE) ≡ σ_e.** Within-subject SD and the standard error of measurement computed as √MSE are the same quantity under M1 with complete balanced data (Hopkins 2000 treats within-subject SD as the typical error and as the SEM; Weir 2005 favours √MSE) [VER]. For two sessions, TE = SD of differences / √2 [VER Hopkins 2000]. It is reported once, with its CI, in cm. Residual variance is σ̂²_e, the same number squared.
- **NOT equivalent:** (i) SEM computed as SD × √(1 − ICC) depends on the ICC form; with a systematic session effect it differs from √MSE, which is why Weir 2005 recommends √MSE for comparability and pairing with the consistency-type ICC [VER]. Under M1, SD_total·√(1 − ICC_agreement) ≈ √(σ²_s + σ²_e), i.e. it includes the systematic part [derived; see U18]. (ii) CV% is a log-scale quantity; it approximates 100 × TE/mean only when error is proportional and small (Hopkins 2000: accurate below about 5%; otherwise 100(e^err − 1)) [VER]. (iii) Missing or unbalanced data break the mean-square equivalence; use the mixed model. (iv) If error differs between persons, there is no single TE; a pooled value is an average and must be labelled as such.
- **Derived, not independent:** MDC95 = 1.96 × √2 × TE (Weir 2005's "minimal difference") [VER]; for a later session compared with the mean of k reference sessions the corresponding band is 1.96 × TE × √(1 + 1/k) under the assumptions in §C3. These are deterministic transforms of TE and are reported as conveniences, not as extra information.

### B4. What the ICC estimates
For the session score, ICC(A,1) = σ²_a / (σ²_a + σ²_s + σ²_e): the share of total variance in a session score that is stable between-person difference, with systematic session differences counted as disagreement. "Single" refers to one **session score** (itself a mean of 3 trials), not one jump. The inference Study 1 needs is agreement of the same person's absolute score across other days, so an absolute-agreement form with sessions treated as a sample of days is the one consistent with the question; it is computed on post-plateau sessions, where s_j ≈ 0 and consistency and agreement forms coincide. Pre-plateau systematic change is quantified directly through the s_j estimates, not through a second ICC. The average-measure form is a deterministic function of the single-measure one and is not reported unless needed. The ICC depends on between-person spread; Hopkins 2000 notes the retest correlation depends on how heterogeneous the participants are while TE does not [VER]. The ICC is therefore secondary context. Shrout & Fleiss state that the choice of form depends on the model and how results will be used [VER abstract]; the exact mean-square formulas and the McGraw–Wong form definitions must be checked against the source before freeze (U18) because the definition text could not be retrieved here.

## C. Revised statistical analysis plan

### C1. Primary and supporting quantities
Primary: **σ̂_e (TE) with 95% CI** (chi-square CI, §C4). Supporting: systematic session profile ŝ_j with CI and individual trajectories; model diagnostics (§C3); ICC(A,1) with CI (context); trial-count curve from M2; best-of-3 versus mean-of-3 error (descriptive only [F]). Not reported: Pearson r as reliability; Cronbach's alpha; tests of "no session difference" as evidence of reliability; Bland–Altman limits unless heteroscedasticity or bias makes the plot informative; duplicate names for σ_e.

### C2. Learning plateau
Estimate the ŝ_j profile. A session is "post-plateau" when subsequent consecutive session changes are within the noise band and the trend CI includes zero (exact wording U10). σ_e and the ICC reported for Study 1 planning come from post-plateau sessions; the all-sessions version is shown for comparison. Because a non-significant session effect does not prove absence of bias [VER Weir 2005], the profile is judged by magnitude with CIs, not by a p-value.

### C3. Reference-session number
**Formula (retained as a working approximation):** comparing one later session with the mean of k reference sessions, SD of the difference = TE × √(1 + 1/k) (1.414, 1.225, 1.155, 1.118, 1.095, 1.080 for k = 1…6).
**It holds only under:** A1 session errors independent; A2 stable true state after the plateau, with no systematic or person-specific drift; A3 equal error variance across persons and sessions; A4 no serial correlation.
**How the pilot checks them:** A1/A4: correlation between adjacent-session residuals from M1 and a comparison with an AR(1) mixed model, reported with CIs, not tests; A2: ŝ_j profile plus the person-specific slope variance from a random-slope model with CI; A3: residual spread against person mean on the raw and log scale, and a pooled comparison across persons. With about 4–5 sessions per person these diagnostics have low power; absence of evidence of violation is not evidence of assumption validity and is reported that way.
**Replacement if assumptions fail:** a direct **leave-one-session-out prediction-error analysis**: for each person and each post-plateau session, predict the score from the mean of the preceding reference sessions and compute the RMSE of the prediction errors with a person-level cluster bootstrap CI, for each reference count that the data allow. This estimates directly the noise a Study 1 post-minus-baseline difference will carry, without the formula, under whatever dependence and drift exist. Its limit: with k total sessions and s excluded pre-plateau, reference counts only up to k − s − 1 can be examined (k = 4 with S1 excluded: reference counts 1–2 only), which is why k = 5 is carried as the alternative.
**Choice of reference count:** the smallest count for which the learning drift is over, the prediction-error (or formula) improvement from adding another session is smaller than a pre-set proportion (U11), and the count is practical for wrestlers' schedules.
**Illustration of fragility [CALC, assumed models, n = 15, k = 4, true σ_e = 1]:** the chi-square CI covers at about 95% (0.949) when errors are independent, equal-variance and normal; it covered about 0.74 when person-specific error SDs varied (lognormal, CV of SD about 0.4), 0.86 and 0.27 with lag-1 error correlation 0.3 and 0.6 (and σ̂ was biased low, mean 0.90 and 0.73), and 0.77 with person-specific linear drift (σ̂ biased high, 1.12). The simulated SD of (new session − mean of k references) matched the formula under independence (e.g. 1.117 vs 1.118 at k = 4) but was smaller under positive serial correlation (1.09 at k = 4 for lag-1 0.3). The multiplier is therefore not universal.

### C4. Precision under M1 (n = 15, k = 4 verified as a working candidate only)
Under M1 with independent normal errors, complete balanced data, (n−1)(k−1)·σ̂²_e / σ²_e follows a chi-square distribution with (n−1)(k−1) degrees of freedom, giving the **exact** interval σ̂_e × √(df/χ²_{0.975,df}) to σ̂_e × √(df/χ²_{0.025,df}); it is exact only under those assumptions and approximate otherwise (§C3). A simulation of M1 [CALC] confirmed the degrees of freedom and a coverage of 0.949 for the 95% interval at n = 15, k = 4. The earlier V1 table used the same df formula. Factors multiply σ̂_e:

| n | sessions total | stable sessions used | df | 95% CI factor | 90% CI factor |
|---|---|---|---|---|---|
| 10 | 3 | 3 | 18 | 0.76–1.48 | 0.79–1.38 |
| 12 | 3 | 3 | 22 | 0.77–1.42 | 0.81–1.34 |
| 12 | 4 | 4 | 33 | 0.81–1.32 | 0.83–1.26 |
| 15 | 3 | 3 | 28 | 0.79–1.35 | 0.82–1.29 |
| **15** | **4** | **4** | **42** | **0.82–1.27** | **0.85–1.22** |
| 15 | 5 | 5 | 56 | 0.84–1.23 | 0.87–1.19 |
| 20 | 3 | 3 | 38 | 0.82–1.29 | 0.84–1.24 |
| 20 | 4 | 4 | 57 | 0.85–1.22 | 0.87–1.18 |
| 30 | 4 | 4 | 87 | 0.87–1.17 | 0.89–1.14 |
| 50 | 3 | 3 | 98 | 0.88–1.16 | 0.90–1.13 |

**Post-plateau reading:** if S1 is excluded, the usable stable sessions are k − 1, so n = 15 with 4 total sessions behaves like the row n = 15, 3 stable sessions (df 28, 95% factor 0.79–1.35); n = 15 with 5 total behaves like n = 15, 4 stable (df 42, 0.82–1.27). This is a precision statement, not a hypothesis-power calculation, and no Study 1 sample size is derived or frozen. Hopkins 2000 reports that reasonable precision needs roughly 50 participants and at least 3 trials and that most published reliability studies are pilots [VER]; a pilot of 12–20 will be imprecise, which is accepted openly. **Discrepancy:** Hopkins 2000's Table II gives a confidence factor of 1.24 for 15 participants × 4 trials; the computed upper factors are 1.22 (90%) and 1.27 (95%). The level or df convention behind Table II was not established from the retrieved text (U22). Final n and k remain unresolved pending independent review.

### C5. SESOI — what it means here (U1 unresolved)
**Definition for this application:** the smallest within-person change in the primary session score (cm or %), relative to the person's own reference baseline, that would be judged practically or biologically meaningful as an *acute net neuromuscular-performance change* in wrestlers. It is a statement about importance, not about statistics.
**Three things that must not be merged:** (i) **importance** (SESOI: what matters to athletes, coaches, medical staff); (ii) **detectability** (what a design with a given σ_e, number of reference sessions and number of wrestlers can see; depends on n, which is a Study 1 matter); (iii) **measurement error** (σ_e: how large ordinary noise is). The pilot supplies (iii) and informs (ii); it cannot supply (i), and SESOI must not be defined as a multiple of the observed TE, which would make D1 pass by construction.
**Candidate approaches (none adopted):** (a) anchor-based: relate score change to an external judgement of meaningful change, as in the anchor-based SESOI method of Anvari & Lakens 2021 [VER abstract; developed for subjective-experience scales, no validated anchor exists for wrestlers, so this would need its own anchor]; (b) structured practitioner/medical consensus on what jump-height loss would change decisions; (c) magnitudes of acute CMJ change reported in comparable contexts, as plausibility benchmarks only [NV: no such literature was retrieved here]; (d) resource-based justification (smallest effect the study could detect, openly labelled as that, not as importance); (e) distribution-based conventions as **contextual benchmarks only**: Hopkins 2004 proposes one-fifth of the between-athlete SD (standardised 0.20) as a default for team sports where test and performance are not directly linked, and says it is an appropriate default for that reason [VER]; individual-sport rules in that paper do not apply. Cormack et al. 2008 evaluated CMJ variables by whether overall TE was below the smallest worthwhile change [VER abstract]; this is a convention used in CMJ monitoring, not a justification of any particular SESOI.
**Decision required before freeze (U1):** which approach (or combination) defines the SESOI, with written rationale.

### C6. Force-time-capable branch (TTO and impulse)
Only if force-time-capable. TTO onset detection (quiet standing duration, body-weight stability, onset threshold: U13) is fixed before data and applied by one algorithm with no manual adjustment. TTO is evaluated with the same quantities (σ_e in its own units, CI, ICC as context). **TTO earns the single conditional secondary only if** (a) σ_e relative to its own meaningful change is acceptable under a rule set with U1, (b) onset detection is stable on every valid trial, and (c) it carries information beyond jump height (within-person change in TTO is not almost entirely predictable from jump height). **Impulse** is assessed the same way and replaces TTO only if clearly superior on reliability and non-redundancy, because at most one secondary is allowed [F]. Otherwise, or with flight-time-only equipment, zero secondary is the valid result [F].

## D. Revised PASS / MODIFY / FAIL framework

Thresholds are labelled by how they can be justified; none is invented. **D1 is the primary measurement gate.**

| # | Criterion | PASS | MODIFY | FAIL | Source of threshold |
|---|---|---|---|---|---|
| **D1** | **Absolute error relative to the justified SESOI** (noise band N = z·σ̂_e^upper·√(1+1/k_ref) or prediction-error RMSE, compared with SESOI according to the inference level chosen in U20) | Noise-to-SESOI relation meets the rule fixed in the decision round | Meets it only with more reference sessions, more trials, or a changed procedure the design permits | Does not meet it after the permitted modification | SESOI = decision (U1); inference level (U20); feasible Study 1 size (U21); candidate rule forms: σ̂_e ≤ SESOI (TE < SWC convention), group-level minimal detectable change at feasible n ≤ SESOI, individual-level MDC ≤ SESOI |
| D2 | Model adequacy (heteroscedasticity, serial correlation, drift) | Assumptions plausible; formula usable | Departures handled by log analysis, mixed model, or the prediction-error approach | Error so heterogeneous or drifting that no single noise band can be stated even by the prediction-error approach | Empirical [E] |
| D3 | Learning plateau | Plateau reached by a session that leaves ≥ the planned stable sessions | Plateau later: add familiarisation or reference sessions | Persistent drift after allowed additions | Empirical [E]; wording U10 |
| D4 | Invalid-trial and incomplete-block rates | Blocks usually complete within planned attempts | Reducible by script/set-up/tester change | Prohibitive after the permitted modification | Empirical [E]; cut-offs U15 |
| D5 | Trial-count adequacy (M2 curve) | 3 trials adequate | Evidence 3 is not enough (reported to reviewer; frozen "3" not changed by the pilot) | n/a | Empirical [E]; any change to frozen "3" needs independent review |
| D6 | ICC context | Not used as pass/fail | Warning review trigger (below) | Never a FAIL by itself | See below |
| D7 | Immediate-post logistics (P2, if performed) | Delivery achievable, logged, no safety event | Flow/staffing/location changed | Unsafe or infeasible after the permitted modification | Safety non-negotiable; times [E]; cut-off U16 |
| D8 | 24 h / 48 h deliverability | Workable attendance and windows | Windows or logistics changed | Not deliverable | Empirical [E]; cut-off U16 |
| D9 | Transfer to wrestlers | P2 σ̂_e not materially worse than P1, or the P2-absent safeguards (A2) are accepted by the reviewer | Wrestler-based noise band used | Disqualifying relative to D1 | Descriptive if n small; U3, U23 |
| D10 | TTO / impulse (force-time-capable only) | One secondary selected per §C6 | None qualifies → zero secondary (not a failure) | n/a | §C6 |
| D11 | Safety | No serious adverse event | Event changes screening/stop rules | Repeated serious events | Non-negotiable |

**ICC role (D6):** a poor ICC can arise from restricted between-person variability even when absolute error is small, so a generic ICC category must not veto a protocol with adequately small error for a within-person question. A **review trigger** is retained for two reasons: (1) a low ICC together with a narrow between-person SD signals range restriction, so ICC values should not be transferred to wrestlers; (2) a low ICC with a not-narrow between-person SD signals that σ_e is large relative to real differences, which is a prompt to re-examine D1, and matters if Study 1 later uses between-person comparisons or covariates. The trigger value is U14.

**Overall:** **PASS** = D1–D4, D7–D9 (D7–D9 as applicable) and D11 pass, and D5, D6, D10 are non-FAIL; the measurement protocol becomes a freeze candidate, subject to independent audit. **MODIFY** = no FAIL, at least one MODIFY: apply only the permitted modifications, repeat the minimum necessary sessions **once**, and return for independent review. **FAIL** = a FAIL on D1, D2, D4, D7 or D11: do not proceed as designed; independent review decides among restructuring (e.g. 24 h/48 h only), more evidence, or reconsidering the measurement. Failure does not automatically reopen Candidate #2.

**Governance note on "one modification cycle":** this is a **project governance rule** that makes a second failure or MODIFY outcome trigger mandatory independent review before any further redesign. It is not a statistical or biological law and does not mean the measurement is scientifically impossible. After the permitted correction cycle, an unresolved failure requires independent review before any additional redesign.

## E. Minimum data dictionary

Pseudonymous IDs only; no names, faces, video or footage. Changes from V1: rest-condition field removed (single fixed rest); sleep optional; nutrition/hydration/caffeine and menstrual-cycle fields not collected.

| Field | Type | Notes |
|---|---|---|
| participant_id, module (P1/P2/P3), session_id, session_number | string/int | |
| session_date, local_clock_time, hours_since_prior_session | date/time/number | |
| tester_id, instruction_script_version | string | |
| device_class, device_id, software_version, calculation_method | string | method fixed before data |
| surface, footwear_standard (Y/N), footwear_note | string | |
| body_mass_kg | number | |
| soreness 0–10, readiness 0–10 (frozen covariates), prior_48h_activity (type, hard Y/N), pain/injury flag | mixed | descriptive |
| sleep_last_night_h | number, optional | optional only |
| warm_up_script_id, warm_up_duration_min, warm_up_completed | | |
| trial_number (1–5), rest_before_trial_s (actual) | | |
| valid_flag, invalid_reason | | fixed reason list |
| jump_height_cm | number | by the fixed method |
| countermovement_depth | number/NA | if recordable |
| TTO, impulse, raw force-time file reference | number/NA | force-time-capable only |
| block_complete, attempts_used, session_primary_score (mean of first 3 valid) | | |
| adverse_event, stop_rule_triggered | | |
| P2 rehearsal only: activity_end_time, time_arrived, time_first_valid_trial, elapsed_end_to_first_trial_s, follow_up_window_actual_h, followed_up, reason_missed | | timing/feasibility only |
| notes | text | |

## F. Updated unresolved decisions (U1–U23)

**F1. List.**
- **U1** SESOI: unresolved; approaches in §C5; gating decision for D1.
- **U2** Final n and k: working candidate n = 15, k = 4, with k = 5 and larger-n alternatives in §C4; verified only under M1; needs independent review.
- **U3** Wrestler access and how P2 is reported if small.
- **U4** Warm-up content/duration.
- **U5** Single fixed inter-trial rest value: **unresolved**, needs verified literature plus practical constraint; conditional crossover fallback in A4.5.
- **U6** Whether P3 is switched on.
- **U7** Jump-height calculation method (verified facts in A4.7; decision open).
- **U8** Equipment class (no brand).
- **U9** Ethics/IRB pathway, consent, stop rules, medical oversight.
- **U10** Plateau wording and threshold.
- **U11** Pre-set "diminishing return" proportion for the reference count.
- **U12** Wrestler baseline drift over weeks/training.
- **U13** TTO onset parameters.
- **U14** ICC review-trigger value, with the justification in D6.
- **U15** Invalid-trial/incomplete-block cut-offs.
- **U16** Completion/attendance cut-offs for immediate-post and 24/48 h.
- **U17** Whether Study 1 adds a same-day pre-match CMJ.
- **U18** Remaining citation verification: McGraw & Wong 1996 form definitions and Koo & Li 2016 content not retrieved; the SD·√(1−ICC_A) identity stated in B3 is derived, to be confirmed; no V2 decision depends on Koo & Li interpretation bands.
- **U19** 72 h trigger (F2).
- **U20 (new)** Inference level for D1: group-level within-person change only, or individual-level classification. Study 1's stated question is group-level, which would make an individual-level MDC criterion stricter than needed.
- **U21 (new)** Feasible Study 1 number of wrestlers (needed for any group-level detectability rule); no sample size is calculated or frozen here, and σ_e alone gives a lower bound on required n because true response heterogeneity adds variance.
- **U22 (new)** Hopkins 2000 Table II (factor 1.24 for 15×4) versus computed 1.22/1.27.
- **U23 (new)** Whether the P2-absent safeguards (A2) are acceptable to the reviewer.

**F2. 72 h trigger and 24 h + 48 h operationalisation.** 24 h + 48 h is frozen; 72 h is conditional [F]. Information is separated into two kinds:
- **Logistics information (allowed):** whether a 72 h visit is deliverable (attendance, window adherence, burden). This can decide whether 72 h is *possible*; it can never decide whether it is *added*.
- **Outcome-independent evidence that could justify planning 72 h (allowed, none verified yet):** verified literature in comparable populations showing incomplete recovery at 48 h; or P3 data in healthy adults showing, after a known stressor, a deficit still beyond the noise band at 48 h (a different stressor, so supportive only).
- **Outcome-dependent evidence (not feasibility):** adding 72 h because Study 1 CMJ data at 48 h have not returned toward reference would be an **adaptive design rule that inspects outcome data**. It is labelled as such and must be written into the Study 1 protocol/analysis plan before any data are collected, with its statistic, threshold and error-rate consequences stated. It is **not** a pilot decision, and P2 data may not be used for it because P2 does not test the hypothesis.
- **Options for the Study 1 protocol (not chosen here):** O1 fixed 72 h for all if outcome-independent evidence supports it; O2 a pre-specified adaptive rule (as above); O3 no 72 h.
- **Status: U19 unresolved.** Insufficient verified evidence exists now, so the fail-closed default is 24 h + 48 h only until a later reviewed decision.

## G. Future exposure / video decision gate (unchanged from V1)

**Gate FV-1** sits after Stage 4 and before the Study 1 protocol freeze, and persists in the project map until formally closed by independent review.

**Question carried forward:** once the biological-response measurement is shown to be reliable, which exposure variables are scientifically worth measuring in Study 1, and which of those genuinely require validated video/CV coding beyond match duration + RPE?

- **Inputs from Stage 4:** the noise band and SESOI (can an exposure variable's expected contribution be seen above noise at all?), wrestler-context feasibility, what consent and rights allow, and what D + RPE alone appears able to support.
- **Options the gate must choose among (not chosen now):** (a) D + RPE sufficient; (b) add HR and/or IMU if they earn inclusion [F: conditional]; (c) human-coded event counts such as impacts/bumps/landings from fixed-camera passive video, which would first need their own definition and validation; (d) targeted CV/MP4 development of a specific discrete-event construct, with its own validation, human ground truth and rights clearance.
- **Frozen context that remains true:** broadcast CV exposure development stopped; no CV construct earns inclusion; LANDING V1.1 parked before Pass 1; Identity/Anatomy frozen and unvalidated; footage rights unresolved; no new acquisition.
- **During Stage 4:** no coding of any kind. Fixed-camera passive video is not needed for the pilot. If a venue rehearsal happens and consent and rights explicitly allow, a passive record may be kept to keep the option open, but it is not analysed or coded in this stage.
- **Gate closure requires** an independent reviewer's explicit decision recorded in the ledger; silence does not close it.

## H. Exact next action after this V2 is independently audited
1. Independent audit of V2.
2. One consolidated "pilot design freeze decisions" round on U1–U23, starting with U1 (SESOI) and U20/U21, then U5, U7/U8, U9, U3/U23, U2.
3. Only then Pilot Protocol V1 (still no data), audited and frozen with a ledger entry.
4. Only after that: ethics/IRB submission, then execution.
Nothing is executed, collected or purchased before step 3 and ethics clearance. Gate FV-1 stays open.

## I. Confounders and procedural variables
| Variable | Handling |
|---|---|
| Time of day, warm-up, footwear, surface, device, calculation method, rest, script | Control (fixed/standardised) and record, per the frozen decisions and A4 |
| Tester | Script; tester recorded |
| Countermovement depth | Record when possible; self-selected variability acknowledged [F] |
| Prior 48 h activity | Record; request no unusual exertion before baseline sessions |
| Soreness, readiness, pain, injury/illness | Record (frozen covariates); screen/flag |
| Body mass | Record |
| Sleep | Optional single item |
| Nutrition, hydration, caffeine | Acknowledged only; not collected unless verified evidence shows necessity for this question |
| Menstrual-cycle phase | Acknowledged only; not collected by default |
| Motivation | Script; acknowledged |
| Season/training phase, environment | Acknowledged (U12); environment recorded only if cheap |
| Learning | Controlled by familiarisation; estimated by ŝ_j |
No claim is made that these variables are sources of day-to-day variation beyond what the frozen decisions already assume; literature for such claims was not verified and none is relied on.

## J. Claims boundary
No claim that CMJ is validated in entertainment professional wrestling; no injury-risk prediction; no causal workload claim; no exposure-validity, fatigue, identity, anatomy or physical-metric claim. The pilot yields measurement error and feasibility only. Immediate post-match CMJ would represent "acute net neuromuscular-performance change", not automatically fatigue.

## K. Literature verification
**Verified against retrieved sources in this session** (level in brackets):
1. Hopkins WG. Measures of reliability in sports medicine and science. *Sports Med* 2000;30(1):1–15. [Full text from the author's PDF: TE ≡ within-subject SD ≡ SEM; TE = SD_diff/√2; s = S√(1−r); retest correlation depends on participant heterogeneity; log-transformed CV; ≥ 50 participants and ≥ 3 trials guidance; Table II value 1.24 for 15×4.] Volume/pages were given by the retrieval summary from its own knowledge, with the Sports Med year and the DOI 10.2165/00007256-200030010-00001 appearing in search results.
2. Weir JP. Quantifying test-retest reliability using the intraclass correlation coefficient and the SEM. *J Strength Cond Res* 2005;19(1):231–240. [Full text copy: √MSE SEM; ICC choice depends on systematic error; ICC 3,1 vs 2,1; MD = 1.96·√2·SEM; trials effect and bias.]
3. Hopkins WG. How to interpret changes in an athletic performance test. *Sportscience* 2004;8:1–7. [Page: noise vs smallest worthwhile change; team-sport default of 0.20 of between-athlete SD; individual-sport rule; later updates mentioned.]
4. Anvari F, Lakens D. Using anchor-based methods to determine the smallest effect size of interest. *J Exp Soc Psychol* 2021;96:104159. [Abstract/record only; no content on distribution-based benchmarks.]
5. Cormack SJ, Newton RU, McGuigan MR, Doyle TLA. Reliability of measures obtained during single and repeated countermovement jumps. *Int J Sports Physiol Perform* 2008;3(2):131–144. [Abstract/record only; jump-height reliability not reported there.]
6. Linthorne NP. Analysis of standing vertical jumps using a force platform. *Am J Phys* 2001;69(11):1198–1204. [Full text: flight-time vs impulse-momentum; typical 0.5–2 cm overestimate by flight time with hands on hips.]
7. Shrout PE, Fleiss JL. Intraclass correlations: uses in assessing rater reliability. *Psychol Bull* 1979;86(2):420–. [Abstract/record only; author names were not shown in the retrieved record.]

**Bibliographic existence only (content not retrieved):** McGraw KO, Wong SP. Forming inferences about some intraclass correlation coefficients. *Psychol Methods* 1996;1(1):30–46. Koo TK, Li MY. A guideline of selecting and reporting intraclass correlation coefficients for reliability research. *J Chiropr Med* 2016 (DOI 10.1016/j.jcm.2016.02.012; PMID 27330520). No V2 decision relies on the content of either.

**Not verified, not relied on:** inter-trial rest evidence for CMJ testing; effects of time of day or warm-up on CMJ variability; magnitudes of acute CMJ change in comparable populations; a systematic review of jump-height calculation methods that was located by search but could not be read. Wherever these would have been needed the corresponding decision is left unresolved (U5, U7, C5c).

**Project decisions, pilot-derived quantities and verified literature are kept separate** by the labels in the key.

## L. Confirmation of frozen decisions
Unchanged and not modified by V2: CMJ alone; primary = mean jump height of the first 3 valid prespecified trials; trials 4–5 diagnostic only; best trial = sensitivity descriptor only; at most one conditional secondary TTO if force-time-capable, zero acceptable; impulse pilot-assess only; force plate preferred not required; same device and calculation method within athlete; hands on hips; self-selected depth recorded when possible; clock time and warm-up recorded/standardised; footwear/surface standardised on practical grounds; Candidate #2 closed/parked; recovery 24 h + 48 h, 72 h conditional, 30–45 min parked; terminology "acute net neuromuscular-performance change"; exposure D + RPE MVP; HR/IMU conditional; fixed-camera passive video where consent permits; broadcast CV exposure stopped; LANDING parked before Pass 1; Identity/Anatomy frozen and unvalidated; Holdout #2 sealed; Gemini untouched; footage rights unresolved; no claim boundary altered. V2 neither freezes nor executes anything.
