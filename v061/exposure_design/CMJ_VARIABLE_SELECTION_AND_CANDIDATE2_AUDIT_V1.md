# PROSPECTIVE STUDY 1 — CMJ VARIABLE SELECTION + "DO WE NEED ANOTHER NEUROMUSCULAR TEST?" AUDIT (design/research only)

Status: design and literature review for independent review. Nothing implemented, no equipment selected, no data acquired, no CV, no LANDING, no Holdout #2, no Gemini, no change to Identity/Anatomy or any frozen/parked branch, no MP4. No power calculation, smallest worthwhile change or responder threshold is frozen here.

## 0. Rulings frozen from the Study 1 stack review (errata to PROSPECTIVE_STUDY1_MEASUREMENT_STACK_DESIGN_V1.md, sha256 2158381ae63246832fa8ce0bdca011d099300cc1d316f62793db5e61ec46c785, which stays unchanged because it is ledger-hashed)
1. Primary stack APPROVED: D + RPE (separate from D) + CMJ series + short covariate log. sRPE-AU = RPE × D is a derived/secondary descriptor only.
2. RPE APPROVED WITH MODIFICATION: CR-10 whole-match rating, always **after** the immediate post-match CMJ, target about 30 min after the match, **not frozen as exactly 30 min**; a pre-specified acceptable collection window is to be finalised later; exact elapsed time recorded for every rating.
3. HR and IMU: ENHANCED/CONDITIONAL only. Study 1 must be able to run without either. Feasibility and added-information gates are pre-specified before any pilot. No device selection, no pilot now.
4. Fixed-camera video: passive record where consent/permissions allow; recording does not imply CV analysis; CV deferred.
5. CMJ timing: conceptual sequence (rested reference → match-day pre → immediate post → recovery) APPROVED. **≤10 min is NOT frozen.** Replaced by: "Immediate post-match CMJ = as soon as safely/logistically feasible; exact elapsed time recorded. Final target/acceptable window will be determined from the dedicated CMJ methodology audit." Nothing exposure-related may delay the immediate post-match CMJ.
6. Terminology: "workload/exposure" primarily means **acute single-match exposure**; cumulative multi-day load is secondary/exploratory; Study 1 does not assume causality. Operational wording: *"Does professional-wrestling match exposure associate with measurable acute deterioration in lower-extremity neuromuscular function, and does the magnitude of change vary with match duration and perceived exertion?"*
7. CV future role (replaces the earlier event-attribution wording): *"No current exposure role survives on edited broadcast footage. Under prospective fixed-camera acquisition, Identity/Anatomy may be reconsidered only for a specifically justified measurement or attribution task not already solved more directly by wearer-linked sensors or simpler methods."* An IMU belongs to its wearer, so CV identity/event attribution is unnecessary for instrumented events.

## 1. Evidence base and its limits (read first)
Citations in §11 are tagged by how far I could check them in this session: **[V]** bibliographic record and abstract-level content read; **[L]** title/listing seen, content not read; **[M]** recalled, not verified. Evidence classes used in the text: **EST** = established generally in exercise-science methodology; **EXT** = extrapolated from other sports/populations; **ASM** = assumption specific to professional wrestling, unvalidated.
**No direct evidence on CMJ, force-plate variables or any neuromuscular test in professional wrestling was found** (searches returned freestyle/Greco-Roman wrestling, a systematic review of repeated combat-sport matches, and professional-wrestler mortality/cardiac studies; none measures neuromuscular function in professional wrestlers). This was a targeted, not exhaustive, search. Everything in this document about wrestlers is therefore ASM unless stated.

## 2. Part A — The target neuromuscular construct
**Definition for Study 1.** Acute lower-extremity neuromuscular deterioration = a reduction, relative to the athlete's own rested state and beyond ordinary day-to-day variation, in the ability of the lower-extremity musculature to produce **explosive output in a slow stretch–shortening-cycle (SSC) task under maximal voluntary intent**, measured at defined times after a match. Fatigue is defined as an exercise-induced reduction in the ability of muscle to produce force or power (Enoka & Duchateau [V]).
| Dimension | What CMJ gives | What CMJ cannot give |
|---|---|---|
| Maximal performance | indirect (jump output depends on strength) | maximal force capacity (isometric strength) |
| Explosive/ballistic | **yes** (take-off velocity from net impulse) | rate of force development in isolation |
| SSC function | **slow SSC** (countermovement and ground contact well above 250 ms) | fast SSC / reactive stiffness (drop jump, hops) |
| Force production | force-time data **only on a force plate** | force from flight-time or video systems |
| Rate/time characteristics | contraction/movement time **only with time-resolved data** | — |
| Fatigue vs potentiation | net result only | cannot separate them; both change within minutes of exertion (PAP/PAPE literature [L]) and the match context (prolonged intermittent exertion) differs from the conditioning-contraction paradigms in that literature (ASM) |
| Central vs peripheral | **cannot** be inferred; voluntary performance reflects both, plus motivation and strategy | needs stimulation/twitch-interpolation methods (impractical in the field) |
What CMJ **can establish**: a functional decline (or not) in voluntary lower-extremity SSC output at a given time; recovery trajectory with repeated tests; strategy changes if time-resolved data exist. What it **cannot establish**: mechanism, tissue damage, injury risk, unilateral deficits, upper-body/trunk function, or that a decline was caused by the match rather than time of day, warm state or effort.
Sensitivity evidence for acute decline in CMJ is **EXT** (team sports: Claudino meta-analysis [V]; Gathercole [V]; Johnston [V]; post-match review Doeven [V]). Grappling combat sports show upper- and lower-limb performance declines across repeated matches (systematic review [V], low-quality evidence, no professional wrestling).

## 3. Part B — CMJ variable audit
Fields: 1 construct; 2 interpretation; 3 acute-fatigue sensitivity (evidence class); 4 reliability; 5 equipment dependence; 6 technique/strategy sensitivity; 7 redundancy; 8 within-athlete interpretability; 9 role; 10 minimum equipment.
| Variable | Construct / interpretation | Fatigue sensitivity; reliability | Equipment; strategy sensitivity | Redundancy; role |
|---|---|---|---|---|
| **Jump height** | take-off velocity squared / 2g; overall explosive output. Impulse-momentum on a force plate vs flight-time differ in method; both measure take-off-to-apex height, and impulse-momentum is judged most appropriate for that quantity (Xu 2023 [V]) | EXT: declines after fatiguing exercise (Gathercole: flight time changed beyond CV in most individuals [V]); **mean of trials more sensitive than best** (Claudino [V]; Alba-Jiménez [V]). Jump-height ICC≈0.82–0.88, CV≈3.8–4.8 % in team-sport samples (Alba-Jiménez [V]); performance variables CV 4.2–11.1 % in a mixed active sample (Anicic [V]) | force plate, contact mat/optical or validated video app. Flight-time systems are sensitive to landing technique (landing must be standardised). Strategy changes can preserve height | core outcome. **PRIMARY** |
| Flight time | basis of flight-time jump height | EXT as above | simple systems | identical information to jump height on flight-time systems. Not separate. **KILL as separate variable** |
| Contraction / movement time (onset to take-off); time to take-off | duration of the countermovement + propulsion; strategy | EXT: time-related variables changed at 72 h in Gathercole [V] (rising times) | needs time-resolved force or video/IMU; strategy-sensitive (that is the point) | partially independent of height (a slower jump can keep height). **SECONDARY** (force plate/time-resolved only) |
| RSI-mod or flight-time:contraction-time ratio | jump height ÷ contraction time | EXT: "alternative" CMJ variables of this type were proposed because typical variables can miss fatigue (Gathercole [V]) | needs time-resolved data | a ratio of two recorded variables; adds no measurement but adds a comparison. **DERIVED/EXPLORATORY** (computed from the two above, not tested as a separate primary) |
| Peak force; relative peak force | peak vertical force (÷ body weight) | fatigue sensitivity not established in what I read (Claudino abstract reports force sensitivity for supercompensation, not fatigue) [V]; force-at-zero-velocity changed in Gathercole [V] | force plate only; technique-sensitive | partly redundant with power/impulse. **EXPLORATORY** |
| Peak power; relative peak power | peak product of force and velocity (÷ body mass) | EXT: mean power and peak velocity changed beyond CV in Gathercole [V]; computed power depends on method | force plate only; calculation-dependent | strongly related to jump height. **EXPLORATORY** (mean concentric power is the preferred form if included) |
| Mean force / mean power (concentric) | average output during propulsion | EXT: mean power sensitive (Gathercole [V]) | force plate | overlaps with height; keep only as exploratory strategy descriptor |
| Net concentric impulse | determines take-off velocity | EXT; not shown as fatigue-specific | force plate | mathematically linked to height. **KILL as separate variable** |
| Eccentric (braking) phase variables (braking RFD, duration, braking impulse) | countermovement control/eccentric loading | not established for post-match fatigue in what I read; braking-phase variables had poor-to-moderate reliability in a related familiarisation study (different jump variant) [V] | force plate; high strategy-sensitivity | **EXPLORATORY**; relevant to eccentric damage hypotheses but unproven |
| Countermovement depth | displacement during the countermovement | strategy marker; reliability and fatigue response not established here | force plate (displacement from double integration) or video | **EXPLORATORY covariate** |
| Force-time "strategy" components | shape of the force-time curve | Anicic: reliable metrics group into performance, eccentric, concentric and jump-strategy components [V]; a few reliable metrics per component describe CMJ; many of 45 metrics had CV >10 % | force plate | motivates keeping a small number of secondary variables, not many |
**Warning (no fishing):** Anicic found that only 24 of 45 computed metrics met CV ≤10 %, and kinetic/kinematic metrics span CV 1.6–93 % [V]. A long list of force-plate variables will contain unreliable ones and many false positives. Secondary and exploratory variables below are limited, pre-specified and separately reported.

### Recommended minimal pre-specified CMJ variable set
- **PRIMARY (1):** jump height, **mean of the pre-specified number of trials per session**, expressed as within-athlete change from that athlete's reference. Method: impulse-momentum if a force plate is used; flight-time on simple systems (same device and method across all sessions of an athlete; never mixed).
- **SECONDARY (up to 2, only when time-resolved data exist):** (i) contraction/movement time (strategy); (ii) mean concentric power or relative peak power (one, chosen before the pilot).
- **EXPLORATORY (reported, not tested for the claim):** countermovement depth, braking-phase descriptors, RSI-mod, peak force.
- **KILL as separate variables:** flight time (equals height on flight-time systems), net concentric impulse (linked to height).

### Force plate vs simpler system
| | Simple jump-height system | Force plate |
|---|---|---|
| Gives | jump height (flight time) | jump height (impulse-momentum), contraction time, power, force-time shape, depth |
| Needs | contact mat/optical/video app with landing standardisation | plate, calibration, software, body weight at each session |
| Burden | low, very portable | moderate–high setup, cost; portable plates exist |
| Detects | decline in height | decline in height **plus** strategy shifts that preserve height |
| Risk | landing-technique artefacts; no timing | more variables, more false positives |
**Ruling.** Jump height alone answers the primary yes/no question (is there a decline beyond ordinary variation); the extra force-plate information addresses *how* performance changes, which matters for mechanism but not for whether the study can answer its primary question. The extra information is **valuable but not required**: a force plate is PREFERRED if permissions, logistics and a pilot reliability check allow, and a validated simple system is ACCEPTABLE for the primary. Choice of device is not made here. Whatever the system, the same device and the same height method must be used for all sessions of an athlete, and its own test–retest reliability in this protocol must be measured before analysis thresholds are set. A smartphone-app validity study exists (Balsalobre-Fernández 2015 [L]) but its results were not verified in this session.

## 4. Part C — CMJ protocol recommendations
Each item gives the recommendation, rationale, and evidence class; none is frozen beyond what is stated.
| Element | Recommendation | Rationale / evidence |
|---|---|---|
| Familiarisation | ≥1 dedicated session before reference sessions; inspect learning across consecutive trial pairs | Hopkins: check learning effects by pairs of consecutive trials [V]; learning effects in a different jump variant [V]. Number to be set in the pilot (ASM) |
| Rested reference sessions | ≥2 after familiarisation, on separate rested days, same time-of-day window as match-day pre | provide each athlete's typical value and day-to-day variability. Time-of-day effects on neuromuscular performance have been meta-analysed in team-sport athletes [L], magnitude not verified, so time-of-day is standardised and recorded (EXT/ASM) |
| Trials per session | 3 trials, identical at every time point | Hopkins: ≥3 trials for reliability estimation [V]; averaged jumps more sensitive than best (Claudino [V]; Alba-Jiménez [V]) |
| Rest between trials | fixed identical interval (a short interval of the order of tens of seconds to a minute, to be fixed in the pilot) | no verified evidence base for wrestlers; consistency across time points is the requirement (ASM) |
| Arm position | hands on hips | removes arm-swing contribution so the outcome reflects the lower extremity; design choice, not tested in wrestlers (ASM) |
| Footwear and surface | fixed footwear condition per athlete; firm flat surface (not ring canvas) | standardisation requirement (EST) |
| Warm-up | standardised brief warm-up for reference and match-day pre tests; **no added warm-up post-match** (the match is the exertion) | muscle temperature and activation state differ between pre and post and are a confounder; logging warm state and elapsed time handles this (ASM) |
| Countermovement depth | self-selected, recorded when measurable | constrained depth changes strategy and may be unnatural when fatigued; depth recorded as covariate/strategy variable (ASM) |
| Trial summary | mean of trials primary; best-trial as sensitivity analysis | Claudino [V]; Alba-Jiménez [V] |
| Match-day pre timing | after the standardised warm-up, at a pre-specified window before the match; exact elapsed time to bell recorded | keeps pre state comparable to reference sessions (ASM) |
| Immediate post | as soon as safely and logistically feasible; exact elapsed time since match end recorded; safe-start criteria and stop rules pre-specified (e.g., suspected head injury, acute injury, dizziness) | physiology changes within minutes (fatigue development/ dissipation, possible potentiation), so elapsed time is a core covariate; the acceptable window is to be set from the pilot's time-course data (EXT/ASM) |
| 24 h and 48 h recovery points | keep both | post-match review: CMJ largest decrease typically 12–24 h, most studies recovered by 48 h, some later; basketball longer (Doeven [V], team ball sports, EXT). Add 72 h only if the pilot shows non-recovery at 48 h |
| ~30–45 min post point | **PARK (exploratory only)** | adds a second near-term point that could help separate acute net change from transient effects, but doubles burden, adds repeated maximal jumps, and collides with cool-down and the RPE window. No evidence that it adds information that the immediate post plus 24 h cannot provide |
| Fatigue vs potentiation | analyse the immediate post as **acute net change**, not "fatigue"; record elapsed time, warm state and RPE; rely on 24/48 h for fatigue-dominated recovery | cannot be separated with a single test (Part A) |
| Elapsed-time recording | timestamps for match end, each trial, RPE, sensor removal; shared clock | required by the ruling |
| Day-to-day variability | measured in the same athletes, device and protocol, with typical error (CV %) and confidence limits | Hopkins [V]; needed before any thresholds (Part G) |

## 5. Part D — What CMJ misses
After a well-instrumented CMJ the following remain unmeasured; only blind spots that bear on lower-extremity neuromuscular function after a wrestling match can justify a second test.
1. **Maximal force capacity and rate of force development** (isometric) — conceptually relevant (strength underlies jumping) but jump height is already sensitive to strength changes; incremental value unproven.
2. **Fast-SSC / reactive function** (short ground contacts) — relevant to landings and rebound-type actions; CMJ is slow SSC.
3. **Unilateral and asymmetric deficits** — bilateral CMJ can mask one-leg deficits; injury-relevant but not what the Study 1 primary asks.
4. **Landing/eccentric tolerance** — CMJ landing is not usually analysed; wrestling involves bumps and landings (ASM).
5. **Central drive (voluntary activation)** — only measurable with stimulation.
6. **Postural control/balance** — plausible after contact exertion but confounded by arousal and possible head impact.
7. **Upper-body and trunk function** — outside the stated lower-extremity question.
8. **Muscle soreness and perceived readiness** — perceptual covariates, not neuromuscular tests (collected in the covariate log).

## 6. Part E — Candidate #2 audit
Candidates considered; IMTP appears only as a comparator.
| Candidate | Unique construct | Overlap with CMJ | Wrestling relevance | Acute-fatigue sensitivity | Reliability | Setup / duration | Burden / safety post-match | Contaminates or delays CMJ? | Incremental value over CMJ | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| **Drop jump (RSI)** | fast-SSC reactivity | partial (same jump family) | landings, rebounds (ASM) | not verified in this session | high in basketball (CV 2.1–3.1 %, ICC .95–.99, Markwick [V]) | box + plate/mat, minutes | impact landing on fatigued legs after a match is a safety concern; needs familiarisation | before CMJ: yes; after CMJ: adds delay | unproven | **PARK** (revisit at a non-immediate time only if a fast-SSC blind spot is shown) |
| Single-leg CMJ / hop | unilateral output and asymmetry | high (same task) | unilateral injuries (ASM) | not verified | not verified | doubles trials | unilateral landings when fatigued | after CMJ: adds delay | unproven | **PARK** |
| Isometric strength (IMTP/isometric squat) — comparator | maximal force, RFD | low | strength underlies performance | not verified here | standardisation described (Comfort [V]); reliability statistics not read | rack/bar/plate; maximal efforts | maximal-effort burden and setup; previously parked for immediate repeated post-match use | contamination risk before CMJ | unproven | **KILL for Study 1 immediate-post use**; may remain a baseline-only characterisation if a separate question arises |
| Balance / postural control | postural control | low | head impacts, stability (ASM) | not verified in this session | not verified | short | low physical load; heavily confounded by arousal, dizziness, possible concussion | minor | unproven | **PARK** (exploratory only with its own hypothesis) |
| Voluntary activation (stimulation) | central vs peripheral | none | mechanism | strong in laboratory settings (EXT) | lab-level | heavy equipment, pain, expertise | impractical backstage | n/a | high mechanistically, impossible in field | **KILL for field Study 1** |
| Sprint / agility test | locomotor performance | partial | match-like demands | not verified | not verified | space and time | injury risk when fatigued, delays | delays CMJ | unproven | **KILL** |
| Perceptual soreness/readiness | not neuromuscular | — | symptoms | — | — | seconds | trivial | none | covariate | **KEEP as covariate** (not a second NM test) |

## 7. Part F — Kill question
**Does Study 1 need a second neuromuscular test? No. Final ruling: CMJ ALONE** for the primary Study 1 design.
A second test survives only if (a) it measures an important construct CMJ does not, (b) that construct matters to the biological question, (c) it is reliable, (d) it is practical in the immediate post-match setting, (e) its incremental information justifies the burden, (f) it does not compromise the immediate CMJ. For every candidate above at least one of these fails or cannot be shown with the evidence available: (a)/(b) are plausible for drop jump, unilateral and isometric tests but (e) is unproven in this population, (d) is doubtful backstage for drop jump, isometric and stimulation tests, and (f) is at risk for anything performed before or immediately after the CMJ.
Conditions under which Candidate #2 may be reconsidered (not planned): the pilot shows a specific CMJ blind spot (e.g., preserved height with an altered strategy), a stated hypothesis for the added construct, evidence of reliability, a safe and non-delaying slot (for example at a later recovery time rather than immediate post).

## 8. Part G — Measurable change
- The Study 1 yardstick for "real within-athlete change" is variability observed in the **same athletes, device, protocol and time-of-day** on rested days: typical error (as CV %) with confidence limits (Hopkins [V]). ICC alone is not sufficient because it depends on the heterogeneity of the sample (Hopkins [V]).
- Learning effects must be checked (consecutive-pair comparisons) before reference values are used.
- Standardised thresholds expressed as multiples of the CV (a summary of rugby-league monitoring quotes small/moderate/large multiples of 0.3/0.9/1.6 [V, secondary summary]) and individual-level frameworks (Swinton 2018 [L]) are options; **no smallest worthwhile change or responder threshold is frozen**.
- Match-day variability may exceed rested-day variability (fatigue, travel, heat); the pilot should estimate both.
**Information needed before thresholds and a power calculation can be frozen:** day-to-day TE/CV of the chosen primary variable and the secondary variables in this population and device (with confidence limits); learning-effect pattern; between-athlete SD; match-day noise; pre-to-post change distribution; elapsed-time effect on the immediate post; missingness; and the estimand and model (stack document §8). Hopkins suggests roughly 50 participants and ≥3 trials for reasonable precision of a reliability estimate [V]; a smaller pilot will give wide confidence limits and must say so.

## 9. Part H — Evidence classification summary
| Claim | Class |
|---|---|
| CMJ is sensitive to acute neuromuscular fatigue in team-sport athletes; mean of trials more sensitive than best | EXT [V] |
| Alternative/strategy CMJ variables add sensitivity beyond height | EXT [V] (one study, 11 athletes) |
| CMJ largest decrease 12–24 h and recovered by ~48 h after team ball sports; longer in basketball | EXT [V] |
| Grappling combat sports show lower-limb performance declines across repeated matches | EXT [V] (low quality) |
| Drop-jump RSI is reliable in basketball | EXT [V] |
| Any CMJ variable, time course, reliability or sensitivity **in professional wrestling** | ASM, no direct evidence found |
| Potentiation after a match, and its time course | ASM |
| Hands-on-hips, three-trial mean, self-selected depth as the right protocol for wrestlers | design choices (ASM) |

## 10. Items requiring independent reviewer approval
1. Final ruling: CMJ alone; no second neuromuscular test in Study 1; Candidate #2 stays closed unless the conditions in §7 are met.
2. Pre-specified variable set: PRIMARY jump height (mean of trials); SECONDARY at most two time-resolved variables when a force plate is used; the rest exploratory; flight time and net impulse not analysed separately.
3. Force plate PREFERRED but not required; simple validated system acceptable for the primary; same device and method within athlete.
4. Protocol: familiarisation, ≥2 rested reference sessions at the same time of day, 3 trials, hands on hips, self-selected depth with recording, fixed footwear/surface, standardised warm-up for pre only, immediate post "as soon as safely feasible" with exact elapsed time recorded.
5. 24 h and 48 h recovery points kept; 72 h optional contingent on the pilot; the ~30–45 min post point PARKED as exploratory.
6. The framing of the immediate post as "acute net change" rather than fatigue.
7. Part G: no thresholds frozen; a reliability pilot is required before thresholds and power are set, with the information list in §8.
8. The statement that no professional-wrestling-specific neuromuscular evidence was found, and the reviewer's view on whether a broader systematic search is warranted before the pilot.
9. Whether the next step is a methodology/reliability pilot design (not to be started without approval).

## 11. Literature / evidence table
[V] = bibliographic record and abstract-level content read in this session. [L] = title or listing seen only. [M] = recalled, not verified.
| # | Citation | Tag | Used for |
|---|---|---|---|
| 1 | Gathercole R, Sporer B, Stellingwerff T, Sleivert G. Alternative countermovement-jump analysis to quantify acute neuromuscular fatigue. Int J Sports Physiol Perform. 2015;10(1):84–92. doi:10.1123/ijspp.2013-0413; PMID 24912201 (author list from memory; page did not list authors) | V (authors M) | 11 male college team-sport athletes; 22 CMJ variables; most CV <10 %; flight time, mean power, peak velocity, force at zero velocity changed beyond CV at 0 h; time-related variables changed at 72 h; recommends strategy variables |
| 2 | Claudino JG, Cronin J, Mezêncio B, McMaster DT, McGuigan M, Tricoli V, Amadio AC, Serrão JC. The countermovement jump to monitor neuromuscular status: a meta-analysis. J Sci Med Sport. 2017;20(4):397–402. doi:10.1016/j.jsams.2016.08.011 | V | 151 articles/531 effect sizes; average CMJ height more sensitive than highest |
| 3 | Cormack SJ, Newton RU, McGuigan MR, Doyle TLA. Reliability of measures obtained during single and repeated countermovement jumps. Int J Sports Physiol Perform. 2008;3(2):131–144. doi:10.1123/ijspp.3.2.131 | V (metadata only; results not read) | reliability of CMJ measures |
| 4 | McMahon JJ, Suchomel TJ, Lake JP, Comfort P. Understanding the key phases of the countermovement jump force-time curve. Strength Cond J. 2018;40(4):96–106. doi:10.1519/SSC.0000000000000375 | V | six CMJ phases |
| 5 | Anicic Z, et al. Assessment of countermovement jump: what should we report? Life (Basel). 2023;13:190. doi:10.3390/life13010190 | V | 45 metrics, 24 with CV ≤10 %; components; n=79 |
| 6 | Xu J, Turner A, Comfort P, Harry J, McMahon J, Chavda S, Bishop C. A systematic review of the different calculation methods for measuring jump height during the countermovement and drop jump tests. Sports Med. 2023. doi:10.1007/s40279-023-01828-x | V | flight-time vs impulse-momentum |
| 7 | Doeven SH, Brink MS, Kosse SJ, Lemmink KAPM. Postmatch recovery of physical performance and biochemical markers in team ball sports: a systematic review. BMJ Open Sport Exerc Med. 2018;4:e000264. doi:10.1136/bmjsem-2017-000264 | V | CMJ recovery time course (28 studies) |
| 8 | Alba-Jiménez C, Moreno-Doutres D, Peña J. Trends assessing neuromuscular fatigue in team sports: a narrative review. Sports. 2022;10(3):33. doi:10.3390/sports10030033 | V | CMJ most used; averaged jumps more sensitive; reliability values |
| 9 | Johnston RD, Gibson NV, Twist C, Gabbett TJ, MacNay SA, MacFarlane NG. Physiological responses to an intensified period of rugby league competition. J Strength Cond Res. 2013;27(3):643–654. doi:10.1519/JSC.0b013e31825bb469 | V (abstract) | CMJ decline after a match (ES −0.73), 7 players |
| 10 | Markwick WJ, Bird SP, Tufano JJ, Seitz LB, Haff GG. The intraday reliability of the reactive strength index calculated from a drop jump in professional men's basketball. Int J Sports Physiol Perform. 2015;10(4):482–488. doi:10.1123/ijspp.2014-0265 | V | DJ RSI CV 2.1–3.1 % |
| 11 | Comfort P, Dos'Santos T, Beckham GK, Stone MH, Guppy SN, Haff GG. Standardization and methodological considerations for the isometric midthigh pull. Strength Cond J. 2019;41(2):57–79. doi:10.1519/SSC.0000000000000433 | V (abstract) | IMTP standardisation (comparator) |
| 12 | Enoka RM, Duchateau J. Muscle fatigue: what, why and how it influences muscle function. J Physiol. 2008;586(1):11–23. doi:10.1113/jphysiol.2007.139477 | V | definition of fatigue; central/peripheral |
| 13 | Hopkins WG. Measures of reliability in sports medicine and science. Sports Med. 2000;30(1):1–15 | V | typical error, ICC limits, ≥3 trials/≈50 participants, learning effects |
| 14 | Tillin NA, Bishop D. Factors modulating post-activation potentiation and its effect on performance of subsequent explosive activities. Sports Med. 2009;39(2):147–166. doi:10.2165/00007256-200939020-00004; PMID 19203135 | L | PAP concept |
| 15 | Blazevich AJ, Babault N. Post-activation potentiation versus post-activation performance enhancement in humans: historical perspective, underlying mechanisms, and current issues. Front Physiol. 2019;10:1359. doi:10.3389/fphys.2019.01359 | L | PAP/PAPE concept |
| 16 | Balsalobre-Fernández C, Glaister M, Lockey RA. The validity and reliability of an iPhone app for measuring vertical jump performance. J Sports Sci. 2015;33(15):1574–1579. doi:10.1080/02640414.2014.996184 | V (metadata only) | existence of app validity data |
| 17 | Bright TE, Lake J, Handford MJ, Theis N, Mundy P, Hughes JD. The effects of familiarisation on countermovement jumps with accentuated eccentric loading (youth athletes). Eur J Sport Sci. 2025;25(9). doi:10.1002/ejsc.70033 | V (abstract; different jump variant) | learning effects in phase variables |
| 18 | Systematic review: acute performance responses during repeated matches in combat sports. J Sci Med Sport. 2020;23(5):512–518. doi:10.1016/j.jsams.2019.12.004 (authors not verified) | V (abstract; authors M) | grappling sports show upper/lower-limb declines; no professional wrestling |
| 19 | Herman CW, Conlon ASC, Rubenfire M, Burghardt AR, McGregor SJ. The very high premature mortality rate among active professional wrestlers is primarily due to cardiovascular disease. PLoS One. 2014;9(11):e109945. doi:10.1371/journal.pone.0109945 | V | professional-wrestler literature found is mortality/cardiac, not neuromuscular |
| 20 | Swinton PA, et al. A statistical framework to interpret individual response to intervention: paving the way for personalized nutrition and exercise prescription. Front Nutr. 2018;5:41. doi:10.3389/fnut.2018.00041 | L | individual-response framework |
| 21 | Monitoring fatigue and recovery in rugby league players. Int J Sports Physiol Perform. 2013;8(5):467–474 (authors not shown on the page) | V (summary page) | practical monitoring; CV multipliers for meaningful change |
| 22 | Influence of time-of-day on neuromuscular performance in team sport athletes: a systematic review and meta-analysis. Front Sports Act Living. 2024 (doi:10.3389/fspor.2024.1466050 inferred from the URL) | L | time-of-day standardisation |
| 23 | Determination of vertical jump as a measure of neuromuscular readiness and fatigue. Int J Sports Physiol Perform. 2017 (PMID 28902119 from listing) | L | not used for any claim |
| 24 | Weir JP. Quantifying test–retest reliability using the intraclass correlation coefficient and the SEM. J Strength Cond Res. 2005;19(1):231–240 | M | not used for any claim |
References marked L or M do not support any claim in this document beyond their being the natural sources to read before the pilot.

## 12. Confirmations
Design/research only. No equipment, device selection, data acquisition, pilot, CV, LANDING coding, Holdout #2, Gemini, MP4 or change to frozen/parked branches. No validation claim for any measure in professional wrestling. No smallest worthwhile change, responder threshold or power calculation is frozen.
