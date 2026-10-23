# EXPOSURE V2 CV — ADVERSARIAL CONSTRUCT AUDIT (design only; nothing implemented)

Status: design for independent review. ANNOTATION_PROVISIONAL; R4 unmet; labeller non-independent. No code run, no footage processed, no human labels, no new data, Holdout #2 sealed, Gemini untouched.
LANDING V1.1 (design sha256 c82971641c0a5c618604455e454d982716670966059958a807e6e86c7f8599a0; tool, metric code, tests, owner package, ledger ANA36) is **PARKED before Pass 1 and left unchanged**. Its three unresolved source identities are not addressed here.

## 0. Result in one paragraph
**Principled STOP for the CV exposure branch on edited broadcast footage.** No candidate survives strongly enough to justify implementation. The reasons are structural, not tuning problems: (i) broadcast footage contains no CMJ outcome, so *no* broadcast experiment can ever test whether a CV variable is a valid exposure — only whether it can be measured; (ii) the part of each match that is visible is chosen by a director, so any per-wrestler integral is missing-not-at-random by an unknown mechanism; (iii) the only wrestler-specific link is Identity, which is unvalidated (52 A↔B label flips within tracklet runs in the integration run), and ownership withholds 64.6 % of identity-accepted measured frames; (iv) every physically meaningful quantity (distance, speed, COM, force, pose-intensity) is forbidden from edited footage; (v) the discrete-event constructs that *are* biologically sensible (landings) need human ground truth, which the parked branch already showed is a large separate burden. A CV variable would also have to beat D + sRPE (+ wearable) in a prospective study whose realistic sample size cannot detect a modest increment (≈105 independent wrestler-matches for ΔR² = 0.05, see §7). **Identity/Anatomy are not killed**: their only defensible future role is attributing human- or wearable-defined events on fixed-camera footage, and that waits for prospective data.

## 1. Evidence used (all already in the repo; nothing recomputed)
- Anatomical Integration V1 report (frozen): of 2179 identity-ACCEPT measured frames, 1408 (0.646, CI 0.626–0.666) are withheld by ownership; 52 A↔B label flips inside tracklet runs; 15 frames with the same label on two detections; stride-3 pose grid with visualization-only carry (carried share 0.152). No ground truth for skeleton correctness exists.
- M9B blind diagnostic (single non-independent reviewer, descriptive): of 54 judgeable withheld-ownership frames, 45 (83.3 %) usable, 9 (16.7 %) contaminated — shows ownership is conservative, not that it is accurate.
- Stage-D CHECK: STOP; scene/time classifier closed (P1 48.04 %, all-LIVE comparator 52.15 %): live-time added essentially nothing beyond "assume the match window is live", i.e. beyond D.
- Route postmortem: D is the strongest defensible comparator; sRPE and wearables are the first wrestler-specific measures.

## 2. A. The biological construct that must be represented
The study pairs **acute CMJ deviation** (pre→post change in jump performance, a lower-extremity stretch-shortening-cycle/neuromuscular-fatigue marker) with **exposure**. An exposure variable is useful only if it:
1. is **wrestler-specific** (the CMJ change is per athlete); a shared variable (match length) cannot explain differences between the two wrestlers of one match;
2. reflects **lower-extremity loading or its fatigue drivers** — repeated eccentric/impact loading (landings, jumps, drops), locomotion/sprint-type work, sustained weight-bearing effort — plus overall internal strain (cardiovascular, perceived effort) that co-determines neuromuscular fatigue;
3. is on a **common, monotone scale** across athletes and matches (a unit of the variable means a comparable load for A, B and across events);
4. is **estimable for the whole exposure window**, not only for the parts someone chose to show;
5. is **interpretable a priori** (direction of effect pre-stated) and **adds information** beyond D and sRPE.

## 3. Structural gates (a candidate must clear all that apply)
| Gate | Statement | Consequence |
|---|---|---|
| G1 No outcome | Broadcast dev footage has no CMJ. | Exposure *validity* is untestable on broadcast; only measurement properties are. |
| G2 Informative missingness | Cuts, replays, crowd/commentary shots, camera following one wrestler decide who is seen. | Any per-wrestler sum/rate is biased by an unknown, director-driven mechanism. |
| G3 Identity | IDENTITY_UNVALIDATED; label flips observed; correct ownership ≠ correct wrestler. | Wrestler-specificity of any CV variable is unproven. |
| G4 Ownership/occlusion | 64.6 % of identity-ACCEPT measured frames withheld; contact/overlap limitation. | Usable per-wrestler time-series are sparse exactly during grappling/impact. |
| G5 Physics ban | No COM, distance, speed, acceleration, force or pose-intensity from edited footage. | Intensity-type variables are out. |
| G6 Truth burden | Event-type constructs need human or sensor ground truth to measure error. | Cost must be justified by a claim no simpler measure supports. |

## 4. B. Candidate audit
Common fields for every candidate are stated once, then per-candidate.

### C1 Per-wrestler on-screen / tracked time (presence)
- Rationale: crude "time under load" per athlete. Observable: seconds with ACCEPT identity. Wrestler-specific: nominally. Needs: identity only.
- Assumptions: presence ∝ activity. **Fails G2 outright** — presence measures camera direction. Cuts/zoom/occlusion: fully exposed. Fixed camera: would equal D (both always in frame).
- Adds beyond D/sRPE: none (broadcast: director noise; fixed: duplicates D). Validation burden: prohibitive for no gain. Pairable with CMJ: no. **Verdict: KILL.**

### C2 Per-wrestler fraction of observed time upright vs on the mat (dimensionless posture-state occupancy)
- Rationale: weight-bearing time vs time off the lower limbs differs by role (who sells vs who dominates). Observable: torso inclination relative to image-vertical bucketed {upright, bent, horizontal}, fraction of observed time.
- Wrestler-specific: yes if identity right. Needs: identity ACCEPT + owned torso keypoints. Assumptions: image-vertical ≈ gravity (camera level), torso keypoints correctly owned during contact, observed time representative (**G2 fails**: fraction is computed on director-selected time).
- Cuts/zoom: fraction is scale-free but cuts bias denominator; perspective/camera roll bias inclination; occlusion/contact is where the state changes (G4); identity errors flip the sign of a between-wrestler difference.
- Fixed/calibrated: improves (no cuts, known camera) but still a role proxy, not a load measure; direction of effect on CMJ is ambiguous (mat time is low LE load but high trunk/fatigue strain). Adds beyond D/sRPE: a role correlate that sRPE largely captures. Validation: pose/posture ground truth + identity validation. Pairable: weak. **Verdict: PARK (fixed-camera regime only; needs a stated directional hypothesis first).**

### C3 Discrete bump/fall events (trunk-to-mat) per wrestler
- Rationale: collision-sport impact exposure. Observable: rapid transition upright→horizontal with floor contact. Mechanism to **lower limbs is indirect** (already judged in V1.1 design; BUMP dropped). Needs events + attribution (recipient). Occlusion/contact: exactly the failure zone. Truth burden: human events. **Verdict: KILL for the CMJ-lower-extremity pairing** (may return as a trunk/systemic variable only with its own construct; not proposed).

### C4 Discrete landing events (feet-first landing after flight) per wrestler
- Rationale: the most LE-relevant discrete event (eccentric work of knee/ankle extensors, SSC-like). Observable: first foot contact after visible airborne phase. Wrestler-specific: yes via attribution. Needs: event detector + identity/ownership for attribution only.
- Assumptions: events recognisable; landings comparable in load (they are not — drop height unknown); counts are monotone-ish with load only. Broadcast: edited/replayed events, partial observability, scale and perspective unknown; G2 again (a count of *visible* landings is not a count of landings). Fixed camera: observable; detection still needs human/IMU ground truth.
- Adds beyond D/sRPE: **possibly**, but a wearable IMU measures impacts directly and without identity/occlusion problems. **Verdict: PARK (human-coded version already parked as V1.1; CV-automated version only if IMUs are infeasible and only on fixed-camera footage).**

### C5 Articulated limb-motion energy (camera-translation- and scale-normalised keypoint motion relative to torso)
- Rationale: activity level without distances. Observable: sum of limb keypoint speeds in torso-lengths/s about the torso centre.
- Fails G5 in spirit ("pose-derived intensity"); estimator is noise-dominated (pose jitter adds energy; M5 shows joint jumps; carried frames are synthetic); ownership contamination (G4) injects the opponent's motion; perspective changes projected limb length. No stated mechanism linking this scalar to LE load. **Verdict: KILL (broadcast). In a fixed-camera study it would be a candidate only after validation against IMU/HR; not proposed now.**

### C6 Contact/engagement time (grappling vs separation)
- Shared by both wrestlers (**not wrestler-specific**), depends on the known contact/overlap failure, duplicates D for load purposes. **Verdict: KILL.**

### C7 Locomotion events (steps/run bouts)
- Rationale: running/sprint-type load. Observable: foot-strike cadence from ankle vertical oscillation. Needs ground reference, high frame rate, unoccluded feet; stride-3 grid and ownership withholding make this unmeasurable on broadcast; fixed camera could, but IMU/step counters do it directly. **Verdict: PARK (fixed camera; IMU preferred).**

### C8 Event attribution ("who landed/took the bump") for events defined by humans or sensors
- Not an exposure variable by itself: a *use* of Identity/Ownership. Required validation: identity accuracy with abstention on fresh data (not available; Holdout #2 sealed). Only relevant if C4 is ever pursued. **Verdict: PARK (the sole surviving future role of Identity/Anatomy).**

### C9 Normalised vertical excursion (hip height in torso-lengths) as a "jump height" proxy
- Dimensionless in principle, but needs a ground reference and a level, non-zooming camera; camera tilt moves everything; flight vs lean indistinguishable. Equivalent to a physical-height claim (G5). **Verdict: KILL (broadcast); PARK for fixed/calibrated only if C4 is pursued and validated against IMU/force data.**

### Summary
| Cand. | Construct | Wrestler-specific | Broadcast regime | Fixed-camera regime | Verdict |
|---|---|---|---|---|---|
| C1 | on-screen time | nominal | invalid (G2) | = D | KILL |
| C2 | posture occupancy | yes (if identity ok) | invalid (G2,G4) | role proxy, direction unclear | PARK |
| C3 | bumps | yes | fails (G4) | indirect to LE | KILL |
| C4 | landings | yes | visible-only counts (G2) | observable, needs truth | PARK |
| C5 | limb-motion energy | yes | noise + G5 | needs IMU validation | KILL |
| C6 | contact time | no | fails | duplicates D | KILL |
| C7 | locomotion events | yes | unmeasurable | IMU better | PARK |
| C8 | event attribution | enabling only | n/a | needs identity validation | PARK |
| C9 | normalised excursion | yes | G5 | needs calibration | KILL / PARK |

## 5. C. Is there ANY useful information in anatomical trajectories without physical claims?
Candidates were limited to dimensionless or discrete-temporal quantities: posture-state occupancy (C2), counts of discrete events (C3/C4/C7), torso-normalised relative motion (C5/C9). Findings:
1. **Dimensionless ≠ valid.** Scale-free quantities remove zoom but not camera roll/tilt, perspective, cuts or the opponent's landmarks in the mask.
2. **Discrete temporal constructs are the only biologically defensible class** (landings), but their *detection* from trajectories is exactly what needs ground truth; trajectories add no information a human or IMU does not already give for the same event.
3. **Occupancy/fraction constructs inherit the director's selection (G2)** and are role proxies.
4. The only information with a plausible unique role is **which wrestler** an externally defined event belongs to — an attribution, not an exposure.
Conclusion: **no trajectory-derived exposure variable is retained.** This is a finding about edited broadcast footage, not about the pose model.

## 6. D. Regimes
1. **Existing edited broadcast footage — legitimate use:** development of *measurement* components only (not exposure). Nothing is proposed, because no component serves a retained construct. Exposure validity claims, workload/fatigue/injury claims and physical metrics: not available. Match duration D can be taken from an event timing log, not from edited video.
2. **Prospective fixed/calibratable camera(s) — deferred:** C2, C4, C7, C9 (and C8 as their attribution layer) become reconsiderable, each only after (a) a directional hypothesis, (b) validation against sensors (IMU/HR) or human truth, (c) identity validated with abstention on fresh data, (d) incremental value over the simple stack shown (see §7).

## 7. E. Comparison with D + sRPE (+ wearable)
| Property | D + sRPE (+ HR/IMU) | Best surviving CV (C4, fixed camera) |
|---|---|---|
| Wrestler-specific | sRPE, HR, IMU yes; D shared | yes, via validated identity (unvalidated) |
| Load content | sRPE internal load; HR cardiovascular; IMU impacts/locomotion directly | landing counts only |
| Occlusion/cut/identity risk | none (sensors) | all of G2–G4 (reduced by fixed camera, not removed) |
| Validation burden | established elsewhere | identity + event truth + sensor concordance |
| Cost/complexity | low–moderate | high |
| Adds information? | baseline | only where IMUs are not worn |

**Power reality check (approximate, noncentral F, α = 0.05, power 0.8, 3 covariates in the base model):** detecting an increment ΔR² = 0.05 over a model with R² = 0.35 needs ≈105 independent wrestler-matches; ΔR² = 0.03 needs ≈173; ΔR² = 0.10 over R² = 0.45 needs ≈46. A small prospective cohort cannot show that a CV variable adds unique explanatory value; repeated measures help only partly. **Answer to "does CV add enough to justify its complexity?": not under current broadcast constraints, and unlikely in a small prospective study unless wearables are infeasible.**

## 8. F. Decision
**STOP the CV exposure-construct branch on broadcast footage. No Exposure V2 experiment is proposed**, because every available experiment would test measurability of a variable whose validity cannot be tested (G1) and which cannot beat the simple stack; proposing one would be inventing work.

Frozen reconsideration conditions (a record of what would reopen the branch — not an experiment):
- Fixed/calibrated prospective footage exists with D (timing log), sRPE and, if feasible, HR/IMU recorded for the same athletes and matches.
- A named construct (landing counts or posture occupancy) with a pre-stated direction of effect on CMJ deviation.
- Identity validated with abstention on fresh data (separate reviewer-approved protocol; Holdout #2 handling decided then).
- A pre-specified incremental-value test over D + sRPE (+ wearable) with a feasible sample size.
- Minimum human annotation: only events needed to measure detector error for the named construct (e.g., landing times/performers on a sampled subset), specified then.
Diagnostic MP4: none generated. An MP4 on broadcast footage would show only that landmarks can be drawn on a person; it would demonstrate nothing about exposure validity, identity, ownership accuracy or load.

## 9. Decisions requiring independent reviewer approval
1. Approve the principled STOP for CV exposure on broadcast footage (no experiment).
2. Confirm LANDING V1.1 stays parked unchanged and that its unresolved identities need no action.
3. Confirm Identity/Anatomy remain frozen and unvalidated, with attribution of externally defined events on fixed-camera footage as their only future role.
4. Decide whether the project's next effort is the prospective measurement stack design (D timing log, sRPE, HR/IMU, fixed-camera spec) rather than any further broadcast CV — a design task, not proposed without instruction.
5. Confirm the power note (§7) is acceptable as a planning figure, not a statistical claim.

## 10. Confirmations
No code, footage, labels, events or new data used; no frozen/killed component (Rule V1/V1.1, Stage-D, Tier-A, C3, Identity/Anatomy) touched; Holdout #2 sealed; Gemini untouched; no exposure-validity, workload, fatigue, injury, identity, anatomy or physical-metric claim made.
