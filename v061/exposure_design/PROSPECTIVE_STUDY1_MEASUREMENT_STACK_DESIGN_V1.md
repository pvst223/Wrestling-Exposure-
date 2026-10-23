# PROSPECTIVE STUDY 1 — MEASUREMENT-STACK DESIGN / KILL AUDIT (design only)

Status: design for independent review. Nothing implemented, no data acquired, no devices selected or purchased, no CV, no LANDING coding, no broadcast footage, no Holdout #2, no Gemini, no new Identity/Anatomy validation, no MP4. ANNOTATION_PROVISIONAL for all earlier development work; none of it is used here.

## 0. Rulings frozen from the Exposure V2 review (errata to EXPOSURE_V2_CV_CONSTRUCT_AUDIT_V1.md, sha256 4cf023567a2cc46b1f22410fd1bc86f3c66d0eb9e6bc42dfaf2082166c29dae4, which stays unchanged because it is ledger-hashed)
1. Principled STOP for CV-derived exposure from edited broadcast footage is APPROVED. No further broadcast Exposure V2 experiment is proposed.
2. LANDING V1.1 remains PARKED before Pass 1: its outstanding source identities are not resolved, the tool is not modified, no human coding begins.
3. Identity + Anatomy remain FROZEN and UNVALIDATED.
4. Corrected wording (supersedes "only future role" in the V2 audit): **"No current exposure role survives on edited broadcast footage. Event attribution is the only currently identified defensible future role; additional roles may be reconsidered under fixed/calibrated prospective acquisition if scientifically justified."**
5. The V2 power figures (≈105 / ≈173 / ≈46 wrestler-matches) are rough planning/feasibility figures only, not sample-size requirements or statistical claims. No power calculation is frozen here (see §9).

## 1. The measurement question
Primary question: does professional-wrestling workload cause measurable deterioration in lower-extremity neuromuscular function, with **countermovement jump (CMJ) relative to each wrestler's own baseline** as the current primary neuromuscular candidate?
Two definitional choices the reviewer must fix (§10): (a) "workload" for Study 1 = **acute exposure of a single match** (primary) versus cumulative multi-day load (exploratory covariate); (b) "cause" = a **within-person exposure–response association with a control contrast**, not a randomised causal effect (matches cannot be assigned).

Selection rule applied to every component: it enters the **primary** stack only if (i) the primary question cannot be answered without it and (ii) it adds information no cheaper component supplies. Otherwise it is enhanced, exploratory, parked or killed.

## 2. Component audit (13 required fields each)

### A. Match duration D
1. Construct: time under match exposure. Definition: **D = seconds from match start (first bell, or first physical contact if no bell) to match end (decision/bell)**, from a timing log kept by a named timekeeper with a monotonic clock, cross-checked against the fixed-camera timestamp when video exists. Secondary, logged not analysed in primary: entrance start→bell and post-decision activity. Legal-in-ring time for tag formats is logged per wrestler.
2. Shared between opponents in a singles match (wrestler-specific only through tag/legal-time logging). 3. Relevance: volume of work and time under metabolic/mechanical load; plausible driver of neuromuscular fatigue. 4. Unique information: none beyond itself — it is the baseline; sRPE contains it arithmetically.
5. Reliability: near-exact if the log is kept (seconds). 6–8. Burden: trivial; one person, a stopwatch/clock record, no participant burden, no equipment. 9. Confounders: matches are choreographed and often timed to broadcast/slot constraints, so variance may be small; intensity and role are invisible. 10. Sync: a shared clock with the CMJ timestamps and any video/sensor.
11. Validation: log-versus-video cross-check on all matches where video exists; inter-timer agreement on a subset. 12. **Necessary for the primary question** (mandatory baseline comparator). 13. **KEEP (mandatory).** Misses: intensity, impacts, role, off-match load, who did the work.

### B. Session RPE (sRPE)
1. Construct: perceived internal load of the whole bout. Protocol: after the match, wrestler rates **"How hard was the whole match?" on the CR-10 scale**, using a standard anchored card, privately (not in front of the opponent or staff), at **~30 min after match end** (the Foster-style delay that reduces recency bias toward the final seconds), always **after** the immediate post-match CMJ. Optional exploratory second item: legs-specific and breathlessness-specific RPE ("differential RPE"). Calculation: **retain D and RPE as separate predictors in the primary model**; compute sRPE-AU = RPE × D (min) only as a derived descriptor and an exploratory interaction term.
2. Wrestler-specific. 3. Relevance: integrates cardiovascular, muscular and psychological strain; plausible correlate of neuromuscular fatigue. 4. Unique information: the **only wrestler-specific internal-load measure with essentially zero equipment**; it differs from D by capturing intensity, role and effort.
5. Reliability: reasonable in other sports; **not validated in professional wrestling**; subject to self-report bias. 6–8. Burden: seconds per match; one card/form. 9. Confounders: performance conventions (selling/acting), social desirability, motivation, mood, pain (bumps) versus leg fatigue, hydration, heat, and shared subjective state with CMJ effort — RPE and CMJ can both move with how the athlete "feels", so their association is not fully independent evidence.
10. Sync: timestamp of rating relative to match end. 11. Validation: within-person test–retest is impossible per match; instead report (a) distribution and ceiling/floor, (b) correlation with D, (c) concordance with HR when HR exists. 12. **Necessary for the primary stack** (cheapest wrestler-specific internal-load measure). 13. **KEEP.**
**D alone vs RPE alone vs D×RPE:** D alone is shared and blind to intensity; RPE alone ignores volume; the product forces an untested multiplicative form and is collinear with D. Recommendation: **keep D and RPE separately in the primary model; report sRPE-AU as secondary.**

### C. Heart rate (HR)
1. Construct: cardiovascular strain. Candidate variables: mean and peak HR, time above fractions of individual maximum, a summated zone/TRIMP-type load, pre-match resting/arousal HR, post-match HR recovery.
2. Wrestler-specific. 3. Relevance to acute CMJ: **indirect** (central/metabolic strain; neuromuscular fatigue of the legs is only partly cardiovascular). 4. Unique information beyond D + sRPE: an **objective** internal-load readout not subject to self-report bias; partly overlapping with sRPE; may reveal sRPE bias.
5. Reliability: chest-strap ECG-type sensing is generally more robust than wrist optical sensing under motion; wrestling-specific artefacts are likely (dislodgement in grappling, sweat, impacts, costume, compression, optical motion artefact). 6–8. Burden: moderate setup per match, one more item to fit before and remove after; participant discomfort and willingness; the promotion's and production's permission; costume/kayfabe; data-quality loss rate unknown.
9. Confounders: intermittent effort and isometric holds (HR lags work), adrenaline/crowd arousal, heat and costume, caffeine/stimulants, hydration, pre-match anxiety, impacts.
10. Sync: shared clock to bell/end. 11. Validation: signal-quality criteria and a pilot dropout rate; no new physiological validation claim. 12. **Not necessary for the primary question; enhanced.** 13. **MODIFY → ENHANCED (conditional on pilot feasibility; not required for the study to run).**

### D. Inertial measurement unit (IMU)
1. What it would contribute (specific, not "load"): wearer-attached **acceleration (and angular-rate) time series** that support (i) **high-acceleration impact events** per wearer — peak resultant acceleration and count above pre-specified thresholds at the sensor site; (ii) **flight/landing events** and landing impact peaks when worn at the shank (tibial-acceleration-type signals are used as surrogates of lower-limb impact in other settings); (iii) **step/locomotion counts** at the shank; (iv) a pre-specified **accumulated accelerometer load** (summed vector change) — this last one has no validated meaning in wrestling and is exploratory only.
Placement: **upper-back/trunk** (captures falls and whole-body impact; attenuates landing), **bilateral shank** (closest to lower-extremity loading; most exposed to grappling contact and displacement risk). Technical constraints, conceptual: sampling rate and range must not clip impact transients; mounting must stay put and be safe in contact.
2. Wrestler-specific by construction (the wearer). 3. Relevance: the closest practical measure of **external lower-limb impact/locomotion** exposure; trunk bumps are indirect for CMJ. 4. Unique information: yes — impact counts/peaks and landings are invisible to D, sRPE and HR.
5. Reliability: sensor signal is repeatable; **event meaning is not validated** (acceleration at a site ≠ tissue load; bump vs landing vs grappling contact can be confused). 6–8. Burden: high — fitting, safety, secure attachment, data handling, algorithms and thresholds fixed before data. 9. Confounders: mounting/placement, soft-tissue artefact, grappling contact, clipping, surface (ring deflection), opponent impacts recorded on the wearer.
10. Sync: shared clock, a start/stop trigger and a post-match reference jump (CMJ with sensors worn) as a natural timing and amplitude anchor. 11. Validation: bench/placement checks; event-class validity versus video on a **sampled** subset (fixed-camera video is the verification source); thresholds fixed in advance.
12. Not necessary for the primary question; **mechanistic enhancement**. 13. **MODIFY → ENHANCED (conditional on pilot feasibility and safety).**
**Does an IMU make CV landing/event measurement redundant?** For counting impacts and landings on instrumented wrestlers: **yes** — and because an IMU belongs to its wearer, it also makes **event attribution** unnecessary for those events. CV/identity attribution therefore remains relevant only for events that have no wearer-attached sensor. This does not change the frozen CV status; it narrows where any future CV role could matter.

### E. Fixed-camera video
1. Construct: none — a **record**, not a measurement. 2. n/a. 3. Relevance: indirect; supplies (i) **audit trail** for D and match context, (ii) **verification** of sensor events (what produced a peak), (iii) **synchronised context** for exploratory work, (iv) **future-proofing**: unedited fixed-view footage cannot be re-acquired. 4. Unique information: nothing the primary question needs; value is verification and optionality.
5–8. Reliability of recording: high if fixed and unattended; burden: low–moderate (mounting, power, storage, retention). Conceptual minimum: one or two **fixed, non-zooming, non-panning** cameras covering the whole ring and apron from opposite corners, constant frame rate with an embedded or visible time reference shared with the timing log; no operator, no edit, no graphics.
9. Confounders: occlusion by ropes/crowd/opponent, lighting; none matter for a record. 10. Sync: shared time source or a visible sync event. 11. Validation: none required to record; any later analysis needs its own reviewed construct. 12. Not necessary; **recommended passive add-on**. 13. **KEEP as record-only.** Participant data governance: consent for recording, rights/permissions with the promotion, secure storage, retention and withdrawal rules (to be specified before acquisition). **"Record footage" ≠ "use CV as a primary measurement"; CV analysis stays deferred.**

### F. CMJ (integration only; the full neuromuscular-test audit stays a separate decision)
- Construct: acute lower-extremity stretch–shortening-cycle neuromuscular performance relative to the athlete's own state; deterioration reflects fatigue (central and peripheral). Early post-exercise testing can also show potentiation, so a single immediate point cannot by itself separate fatigue from potentiation; the recovery points help.
- Primary variable(s), to be fixed in the CMJ audit: jump height and a stretch–shortening-cycle-related measure from the same device; within-person **percent change versus the athlete's own baseline**.
- Timing: **reference baseline** on a rested, non-match day at the same time of day (provides the athlete's typical value and day-to-day variability, i.e. the yardstick for "measurable"); **match-day pre-match baseline** at a fixed interval before the match after standardised preparation; **immediate post-match CMJ as soon as feasible, target ≤10 min after match end, before cooling/showering/interviews**; **24 h and 48 h** recovery points; an optional ~30–45 min second post point (exploratory).
- Standardisation: same device and surface, same instructions and arm condition, same number of trials and rest, same time-of-day windows, recorded warm-up, footwear and prior-48 h activity, hydration/caffeine, and time since match end as a covariate.

### Summary table
| Component | Wrestler-specific | Unique information | Burden | Role | Verdict |
|---|---|---|---|---|---|
| D | shared (tag: per wrestler) | baseline volume | trivial | PRIMARY, mandatory | KEEP |
| sRPE (RPE + D separately) | yes | intensity/perceived strain | very low | PRIMARY | KEEP |
| HR | yes | objective internal load | moderate | ENHANCED | MODIFY (conditional) |
| IMU | yes | external impact/locomotion | high | ENHANCED | MODIFY (conditional) |
| Fixed video | n/a (record) | verification, audit, optionality | low–moderate | passive add-on | KEEP (record-only) |
| CMJ | yes | outcome | moderate | PRIMARY outcome | integrate |

## 3. Redundancy audit
Qualitative, a priori; no number below is an estimate from data. "Added" means information not obtainable from the preceding stack.
| Stack | Adds relative to previous | Main redundancy / risk | Can answer | Burden | Verdict |
|---|---|---|---|---|---|
| D only | — | shared; blind to intensity | does longer exposure predict larger CMJ change (pooled)? | trivial | too weak alone |
| D + RPE (separate) | wrestler-specific intensity | self-report bias; RPE and CMJ share subjective state | within-person exposure–response for duration and perceived strain | very low | **minimum viable** |
| D + sRPE (product) | nothing new vs D + RPE; fixes functional form | collinear with D; untested multiplicative form | same, with a single-number load | very low | derived descriptor only |
| D + sRPE + HR | objective check of internal load | overlaps sRPE; sensor loss in grappling | whether results hold with objective load; bias in sRPE | moderate | enhanced, optional |
| D + sRPE + IMU | external impact/locomotion | interpretation unvalidated; heavy burden | whether impact/landing exposure explains CMJ change beyond effort/volume | high | enhanced, optional |
| D + sRPE + HR + IMU | both | burden may compromise recruitment and the CMJ timeline | joint internal/external load questions | highest | not default; only after a pilot shows feasibility |
| any stack ± fixed video | verification, audit, optionality | storage/consent/rights | nothing for the primary question; enables event verification and later exploration | low–moderate | add where permitted; never a gate |
Conclusion: **more sensors are not assumed to be better**; the smallest stack that can answer the primary question is D + RPE + CMJ. HR and IMU must each earn inclusion in a pilot by pre-specified feasibility and added-information criteria.

## 4. Recommended MINIMUM VIABLE PRIMARY STACK
D (timing log) + RPE (CR-10, ~30 min after) + CMJ (rested reference baseline, match-day pre, ≤10 min post, 24 h, 48 h) + a short covariate log (prior-48 h matches/training, sleep, travel, match type/stipulation, role, injury status, hydration/caffeine, time since match end at CMJ, ambient conditions).
Questions it answers: (1) is there a within-person decline in CMJ after a match beyond the athlete's own day-to-day variability; (2) does the decline scale with duration and with perceived strain; (3) how fast does it recover. It cannot attribute any decline to impacts, landings or cardiovascular strain.

## 5. Recommended ENHANCED STACK (only if the pilot shows it earns inclusion)
MVP + HR and/or IMU (trunk, and shank if safe) + fixed-camera record. Enhanced questions: whether objective internal load or external impact/landing exposure explains CMJ change beyond D and RPE; whether sRPE is biased relative to HR. Inclusion criteria to be pre-specified: wearer acceptance, safe attachment, data-loss rate, absence of delay to the immediate post-match CMJ, and a stated hypothesis for the added variable.

## 6. Exploratory/optional (must not determine whether the study can run)
Differential RPE (legs/breath); soreness and readiness ratings pre/post; second post-match CMJ (~30–45 min); multi-day cumulative load (sessions × RPE); IMU accumulated-load index; fixed-video-based event verification; any later CV construct (each needs its own reviewed construct and sensor/human validation; event attribution remains the only currently identified defensible role and is redundant where IMUs are worn).

## 7. High-level timeline
| Time | Action | Conflict control |
|---|---|---|
| Days −7 to −2 | consent, medical screen, **rested reference CMJ** (≥1 session, ideally 2 to estimate day-to-day variability) | no match in prior 48 h |
| Match day, ~T−90 to −45 min | readiness/covariate log; **pre-match CMJ**; then fit HR/IMU (if enhanced) | sensors fitted **after** baseline CMJ so they cannot affect it |
| Warm-up | athlete's own warm-up, observed and logged | recorded as covariate |
| Match | timing log (D), fixed video, sensors recording | none affects performance |
| T+0 to ≤10 min | **immediate post-match CMJ first** (sensors may stay on until it is done) | CMJ station reachable at once; storyline/promo/interview duties negotiated beforehand; actual delay recorded; beyond the window = protocol deviation, handled by a pre-specified rule |
| ≤T+15 | sensor removal, hydration | after CMJ |
| ~T+30 | **RPE** (private, anchored), optional differential RPE, soreness | after CMJ; not before |
| T+24 h, T+48 h | recovery CMJ + covariate log (activity, sleep, soreness) | same time-of-day window as baseline |
| Follow-up | record injuries and subsequent matches | defines carry-over exclusions |
Foreseeable timing conflicts: wrestlers needed for post-match segments; multi-match nights; travel; immediate access to a CMJ station backstage; heat/cool-down; sensor removal competing with the CMJ. Rule: **nothing exposure-related may delay or precede the immediate post-match CMJ.**

## 8. Conceptual data structure and statistical questions (no power analysis frozen)
- Unit: wrestler-match observations; **wrestlers contribute repeated matches (clustering by wrestler)**; two or more wrestlers share a match (D shared, so clustering by match too → crossed wrestler and match structure).
- Outcome: **paired pre/post CMJ**, expressed as within-person change relative to own baseline, with pre-match value as covariate; recovery adds repeated time points.
- Primary association: **exposure–response** (D, RPE) with person-level adjustment; random slopes only if the data support them.
- "Measurable" deterioration: change exceeding the athlete's own typical day-to-day variation (from the reference sessions) and a pre-stated smallest worthwhile change.
- Control contrast: the rested-day same-time-of-day sessions provide the no-match comparator; other options (matched rest-day mimic) to be decided.
- Missingness and informative dropout (injury, withdrawal) pre-specified.
**Information required before a legitimate power analysis can be frozen:** day-to-day SD and reliability of the chosen CMJ variable in this population; spread of D across available matches (scripted matches may vary little); spread and reliability of RPE; D–RPE correlation; minimum effect worth detecting; number of wrestlers, matches per wrestler, and the match-sharing pattern; expected missingness and delay rates; the chosen estimand and model; any enhanced-variable increments hypothesised. Without these, any number is a guess.

## 9. Unresolved methodological questions
1. Definition of "workload": single match versus cumulative; effect of non-match training, travel, multiple shows.
2. No randomisation: confounding by match type, role and recent load; how strong a causal wording the data can support.
3. Exposure variance: if most matches are similar in duration and perceived load, dose–response is weak and the study reduces to a pre/post contrast.
4. Fatigue versus potentiation at the immediate post point; trunk bumps and soreness depressing CMJ without lower-limb fatigue.
5. Motivational and subjective coupling between RPE and CMJ effort.
6. Feasibility and permissions: access to athletes, backstage CMJ stations, wearing sensors, recording, rights, consent, medical oversight and stopping rules.
7. Event-level interpretation of IMU data in grappling (self vs opponent impact; soft-tissue artefact).
8. Whether a rested reference baseline per athlete is feasible given touring schedules.
9. Data governance: retention, anonymisation, and who may see footage.

## 10. Items requiring independent reviewer approval
1. Primary stack = D (timing log) + RPE (separate) + CMJ series, with the covariate log; sRPE-AU derived only.
2. RPE protocol: CR-10 at ~30 min, strictly after the immediate post-match CMJ.
3. HR and IMU classified ENHANCED/conditional on a pilot, not primary; HR/IMU feasibility criteria to be written before any pilot.
4. Fixed-camera video as record-only passive add-on, with CV analysis deferred.
5. CMJ timeline in §7 (reference baseline, match-day pre, ≤10 min post, 24 h, 48 h) and the rule that nothing delays the immediate post CMJ; the ≤10 min target as a design parameter.
6. Definition of workload and of "cause" for Study 1 (§1).
7. The observation that IMU wear makes event attribution redundant for instrumented events, and its effect on the wording of CV's currently identified role.
8. Whether the CMJ-variable audit (Candidate #2) should be the next separate decision.

## 11. Confirmations
Design only. No code, device selection, data acquisition, CV development, LANDING coding, broadcast analysis, Holdout #2 access, Gemini use, Identity/Anatomy validation or MP4. Frozen and parked branches (Rule V1/V1.1, Stage-D, Tier-A, C3, Identity/Anatomy, LANDING V1.1) are untouched. No exposure-validity, workload, fatigue, injury, identity, anatomy or physical-metric claim is made.
