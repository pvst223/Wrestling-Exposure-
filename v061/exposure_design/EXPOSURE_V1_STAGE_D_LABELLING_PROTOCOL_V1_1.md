# EXPOSURE V1 — STAGE D OWNER SHOT-LABELLING PROTOCOL V1.1 (protocol only; no footage labelled, no classifier implemented)

Status: V1.1 for final independent protocol verification. It is V1 plus ONLY the two defect corrections required by the reviewer ruling "STAGE-D PROTOCOL V1: MODIFY" (M1 reference-adequacy rule, M2 replay-edge evidence). All other text is unchanged from V1.

## Changelog V1 → V1.1 (the only changes)
- **M1** — section 4 (final paragraph): added the hard reference-adequacy rule and the `REFERENCE_INCONCLUSIVE` Stage-D outcome; the earlier "weak reference" wording is removed.
- **M2** — section 3 step 2 and the tie-break paragraph; section 11 examples E7 and E16 re-worded to match: a replay branding/wipe/transition at a shot edge is no longer automatically sufficient.
Original status text: draft following the ruling "EXPOSURE V1 DESIGN V2: APPROVE". Development only. Labels are ANNOTATION_PROVISIONAL; R4 (independent human reviewer) is UNMET; the labeller is the project owner and is not independent. Rights UNRESOLVED (footage private, never committed). Nothing here validates exposure, workload, identity or anatomy. Anatomy V1, C3, partial release, identity training, Holdout #2, Gemini and fresh acquisition are untouched.

## 0. Purpose and what a label means
A label states **what a shot is, as a broadcast production element**, to serve as the reference for P1–P4 of the scene/time classifier. It states nothing about wrestler effort, contact, identity or load. A label is the owner's judgement from the picture and sound of that shot, not an inference about hidden match activity.

## 1. Unit of labelling
- Unit = one **shot** as delimited by the frozen shot boundaries (PREPROC_V1: ffmpeg scene > 0.3, events < 0.25 s merged). The owner labels the shot as delimited; the owner does not move boundaries.
- If the owner believes a boundary is wrong (a real cut missed, or a false cut inside one continuous shot), the shot is flagged `BOUNDARY_ISSUE` (still labelled by its dominant content); boundary issues are counted and reported, and do not change boundaries during Stage D.
- Dissolves/wipes/graphic transitions: the shot is whatever the frozen boundary gives; transitions shorter than 1 s do not change a label.

## 2. Categories (mutually exclusive, one per shot)
1. **LIVE_ACTION** — the shot shows the in-match ring action itself in real time: at least one competing wrestler is in the ring (or immediately around it as part of the match) and the camera framing shows enough of the ring/bodies that match action is observable (wide, medium or tracking views of ring action, including action outside the ring that is part of the match, e.g. a brawl at ringside). Live time-stamped speed, live crowd noise and ordinary live camera work are supporting cues, not required.
2. **REPLAY** — the shot is a re-showing of earlier material: slow motion, instant replay, highlight/recap segments, "previously" packages, stylised replay wipes/branding, or a clearly repeated angle of an action already seen. Replay is never match time.
3. **CLOSE_UP** — the shot is live (not replay) but framed so tightly or on a non-action subject that the match action is **not observable**: faces/upper bodies in tight framing, a single wrestler's face between moves, the referee's face, a crowd member, ringside personnel, the announce desk, a handheld/hard-camera detail with no observable action, etc. Actual match time may be passing, but it is not observed.
4. **NON_MATCH** — the shot is not the match: entrances and pre-match introductions, post-match scenes after the finish, backstage segments, commercials/sponsor reads, show graphics/title cards, interview segments, studio shots, and any shot that does not belong to the bell-to-bell match.
5. **UNKNOWN** — the owner cannot assign a category by the rules below (section 3). UNKNOWN is a legitimate label and is never forced to another category.

## 3. Decision hierarchy (apply in order; first match wins)
1. **Is it before the declared match start or after the declared match end?** (section 7) → NON_MATCH. (Entrances, introductions, post-match scenes, commercials outside the match window, graphics.)
2. **Is it a replay?** Replay is established directly (→ REPLAY) by any of: clear slow motion; a clearly repeated, previously observed action; an explicit "REPLAY"/"INSTANT REPLAY"/recap graphic or title that applies to this shot; or other unambiguous replay presentation. A replay branding/wipe/transition at a frozen shot edge establishes REPLAY **only when it materially identifies this shot as replay content** (e.g. the wipe introduces this shot and the shot's own content is the replayed material). A brief transition artifact inherited from an adjacent shot (e.g. the last frames of a wipe bleeding into a shot that is otherwise live) is supporting evidence only and is **not**, by itself, determinative. If replay status remains genuinely ambiguous after applying these rules → UNKNOWN `REPLAY_AMBIGUOUS` (never forced to REPLAY or LIVE_ACTION).
3. **Is match action observable in this shot?** Observable means a reasonably attentive viewer can see at least one competing wrestler and ongoing physical match action (holds, strikes, throws, movement, ring entrances/exits during the match, brawling), irrespective of how much of the ring is visible. Yes → LIVE_ACTION.
4. **Otherwise (live, but action not observable)** → CLOSE_UP if the shot is of match participants, referee, crowd, ringside or announcers while the match is in progress; → NON_MATCH if it is graphics, a commercial or a studio/backstage element inside the match window.
5. **Any step cannot be decided** → UNKNOWN (with a reason code, section 4).

Tie-break rules, fixed in advance: **established** replay evidence (per step 2) beats LIVE evidence (conservative for P3), whereas mere edge-transition artifacts do not establish replay and, if unresolved, give `REPLAY_AMBIGUOUS`; non-observability beats partial observability only when no wrestler's physical action is visible for the majority of the shot's duration.

## 4. Specific situations (pre-declared rulings)
| Situation | Ruling |
|---|---|
| Picture-in-picture (live main picture + replay or graphic inset) | Label by the **dominant full-frame content** (main picture). If both occupy comparable area (inset ≥ ~25% of frame), UNKNOWN reason `PIP_AMBIGUOUS`. A replay inset on a live main picture is LIVE_ACTION; a live inset on a replay main is REPLAY. |
| Cut during ongoing action (the camera angle changes while the same action continues) | Each resulting shot is labelled independently; each is LIVE_ACTION if action is observable in it. A cut to a replay of that action is REPLAY. |
| Close-up with some action visible (e.g. tight framing but a hold/strike clearly in view) | LIVE_ACTION if the action itself is observable for the majority of the shot's duration; otherwise CLOSE_UP. A face-only or reaction shot with a limb or body part incidentally at the edge → CLOSE_UP. Borderline majority (≈ 40–60% observable) → UNKNOWN `CLOSEUP_BORDERLINE`. |
| Crowd / fan reaction | CLOSE_UP (live, action not observable) if the match is in progress; NON_MATCH if outside the match window. |
| Referee-only / referee-and-one-wrestler framing | If a competing wrestler is physically engaged in observable action → LIVE_ACTION; if the shot is the referee's face/count with no observable wrestler action → CLOSE_UP. |
| Ring-announcer/commentator desk | CLOSE_UP inside the match window; NON_MATCH outside. |
| Entrance / introductions / pre-match graphics | NON_MATCH. |
| Post-match celebration/aftermath after the declared end | NON_MATCH. |
| Match graphics overlaid on live action (name bars, scoreboard) | Ignore the overlay; label the underlying picture. |
| Commercial break / possibly removed material (picture jumps, time clearly skipped, no visible break marker) | Shots on either side are labelled as seen. A visible commercial/sponsor/branded break is NON_MATCH. A discontinuity that cannot be classed as a break or ordinary cut → flag the shot following the gap `EDIT_DISCONTINUITY`, label by its content. A suspected gap does **not** change D (section 7). |
| Image degraded/black/frozen/unreadable for the whole shot | UNKNOWN `UNREADABLE`. |
| Mixed shot (distinct content in the first and second half, boundary not detected) | Label by the content covering the majority of duration; flag `BOUNDARY_ISSUE`; if no majority → UNKNOWN `MIXED_SHOT`. |
| Very short shots (< 0.5 s) | Label normally; reported separately in the shot-count table. |

UNKNOWN reason codes (required): `PIP_AMBIGUOUS`, `CLOSEUP_BORDERLINE`, `REPLAY_AMBIGUOUS` (replay cues conflict or are unclear), `UNREADABLE`, `MIXED_SHOT`, `OUT_OF_WINDOW_AMBIGUOUS` (cannot tell whether inside the match window), `OTHER` (free-text reason required).
In the reference, UNKNOWN shots are **excluded from the P1 disagreement numerator and denominator** and counted separately (P1 is computed on reference-decidable duration only). For P2/P3 the reference T_live_ref is computed from LIVE_ACTION only, with UNKNOWN reported as a reference-uncertainty band [T_live_ref, T_live_ref + T_unknown_ref].

**Hard reference-adequacy rule (Stage-D check).** Let U_ref = total duration of shots labelled UNKNOWN in the check set, and T_check = total duration of the check set (the duration being evaluated). If **U_ref > 10% of T_check**, Stage D returns **`REFERENCE_INCONCLUSIVE`**:
- No ordinary CONTINUE or KILL-at-development ruling may be made from that check.
- This is a property of the *reference labels*; it is not classifier abstention and must remain distinct from classifier UNKNOWN and P4 in every report.
- Ambiguous reference labels must not be changed to get below the 10% threshold (any such change is a protocol violation under section 9).
- The cause distribution of reference UNKNOWN reason codes (counts and duration by code) is reported.
- Any response to `REFERENCE_INCONCLUSIVE` (protocol amendment, relabelling, additional material, or other) requires independent reviewer authorization; nothing is amended or relabelled automatically.
The same U_ref fraction is computed and reported for the build set (descriptive; it does not trigger the outcome).

## 5. Context the labeller may use
- The shot itself (picture and sound), at full speed, repeatable any number of times before submitting.
- Up to **5 s of the preceding and 5 s of the following material** as context, used only for: identifying replay branding/transitions, deciding the match window, and recognising a repeated action. Context is not itself labelled.
- The labeller does **not** see or use: any classifier output, shot-level detection features, thresholds, Stage-D results, performance metrics, or labels of other sets while labelling. Pose/identity/anatomy outputs are not shown.
- Labelling of the shot is based on content, not on how the classifier is expected to behave; there is no objective to make the classifier succeed. The labeller records `CONFIDENCE ∈ {HIGH, MEDIUM, LOW}` for each shot (LOW is allowed with a category; UNKNOWN is for undecidable cases).

## 6. Order, sets and sealing
- Sets are those fixed in the Design V2 (build: development clips + match 150–450 s; check: match 450–779 s). The split is fixed before labels exist and is not altered.
- **Build set** is labelled first and delivered to the rule builder (Claude). The rule is constructed under the complexity budget, hashed and frozen (ledger entry) **before** any check-set label is delivered.
- **Check set** is labelled by the owner (the owner may label any time but) the check labels are **sealed**: stored privately and hashed; only their hash goes to the ledger. The rule builder receives them only after the frozen rule's hash is recorded. 
- Shots within a set are presented in **chronological order** (needed for context and window decisions).
- A **reliability subsample**: a random 10% of shots (seed 20261021; stratified is not required), re-presented blind after at least 7 days without access to earlier labels, to estimate self-consistency (reported with Cohen's kappa and raw agreement as descriptive; not a validity claim). Differences in the re-label are NOT corrections and do not change the reference labels.

## 7. Match start / end marking (for D)
- **Start** = the first frame after the bell/start signal (or, if the bell is not audible/visible, the first frame of the first physical contact of the match as the referee signals the start), marked by the owner to 0.1 s. Entrances and pre-match introductions precede it.
- **End** = the finishing sequence's decision frame: the frame of the referee's pin count completing (third count), submission/stop signal, countout/DQ/stoppage signal, or the bell sounding ending the match, marked to 0.1 s. Post-match scenes are after it.
- Both marks are recorded with a text note of the evidence used, and a flag if ambiguous (`START_AMBIGUOUS`/`END_AMBIGUOUS`). D = end − start in broadcast-timeline seconds; if the source is a declared partial segment without marked start/end, D is not computed and the segment is flagged `NO_D` (the segment contributes to P1/P3 only).
- Suspected removed material (commercial breaks cut out) is flagged but does not alter D.
- The match window defined by the start and end marks is the **only** basis for step 1 of the hierarchy.

## 8. Interface and data schema
Tool: a simple private labelling sheet or script (to be audited before use) that plays each shot clip with the 5 s context option and records the label. It must not display classifier output or any computed feature.

Private label table `labels_{set}.csv` (never committed; hashes only):
| field | content |
|---|---|
| `shot_id` | frozen boundary id |
| `source_id` | clip/match id |
| `t_start_s`, `t_end_s` | frozen shot boundary times |
| `label` | LIVE_ACTION / REPLAY / CLOSE_UP / NON_MATCH / UNKNOWN |
| `unknown_reason` | code from section 4 or empty |
| `confidence` | HIGH / MEDIUM / LOW |
| `flags` | semicolon list from {BOUNDARY_ISSUE, EDIT_DISCONTINUITY, PIP_AMBIGUOUS, START_AMBIGUOUS, END_AMBIGUOUS, NO_D, NOTE} |
| `note` | optional free text (≤ 200 characters, no outcome-related text) |
| `labelled_at_utc` | timestamp of final submission |
| `protocol_version` | this document's hash |
Separate files: `match_marks.csv` (source_id, start_s, end_s, evidence note, flags), `reliability_relabel.csv`, `corrections_log.jsonl`.
Public (committable): label counts, durations by category, UNKNOWN reason counts, reliability statistics, and file hashes. No frames, clips or per-shot content.

## 9. Revisiting labels (predeclared)
Labels are **final on submission** except in these cases:
1. **Tool/transcription error** (the intended label was not recorded, e.g. mis-click, wrong shot id): corrected before the rule is frozen (build set) or before the check labels are unsealed (check set), by an append-only entry in `corrections_log.jsonl` (shot id, old label, new label, reason, timestamp). After unsealing, the check labels cannot be changed for any reason; the error is reported as a limitation.
2. **Protocol ambiguity discovered**: no relabelling. The ambiguity is documented as an amendment request, the protocol is amended only with reviewer approval, and shots already labelled keep their label; an amendment applies only to unlabelled shots unless the reviewer rules otherwise.
3. **After the rule is frozen** (build labels delivered), build labels likewise cannot be changed except for case 1 documented as a defect and reviewed.
No label may be changed because of classifier output, disagreement with the classifier, or its metrics. Any change made after rule freeze that cannot be shown to meet case 1 is a protocol violation and is reported.

## 10. Audit trail
- Every file (labels, marks, corrections log, relabel subsample, tool script) is hashed; hashes recorded in the ledger at: protocol approval, build labels complete, rule frozen, check labels sealed, check labels unsealed.
- Corrections are append-only; corrected rows retain the original in the log.
- The labelling date, protocol hash, and count of corrections are reported with every Stage-D result.

## 11. Examples (constructed for instruction; not drawn from the check set, no outcomes)
Written descriptions of constructed shots, to calibrate the boundaries of each category:
- **E1 LIVE_ACTION:** wide shot, two wrestlers grappling mid-ring, referee visible. 
- **E2 LIVE_ACTION:** medium shot following a wrestler running the ropes toward a ringside brawl.
- **E3 LIVE_ACTION (borderline-clear):** tight-ish shot of a hold, both bodies in frame, action continuing for the entire shot.
- **E4 CLOSE_UP:** a wrestler's face between moves, no limbs or opponent visible.
- **E5 CLOSE_UP:** crowd member reacting during the match.
- **E6 CLOSE_UP:** referee's face counting, no wrestler action.
- **E7 REPLAY:** the same slam shown in slow motion with a branded wipe that introduces the shot (slow motion and the wipe both identify it as replay).
- **E8 REPLAY:** a recap packaging of earlier highlights with a graphic title.
- **E9 NON_MATCH:** a wrestler's entrance walk before the declared start.
- **E10 NON_MATCH:** a commercial for a sponsor at a break.
- **E11 NON_MATCH:** post-match celebration after the declared end.
- **E12 UNKNOWN `PIP_AMBIGUOUS`:** a live shot with a replay inset covering about 30% of the frame.
- **E13 UNKNOWN `CLOSEUP_BORDERLINE`:** tight framing that shows a strike for roughly half of the shot's duration.
- **E14 UNKNOWN `UNREADABLE`:** a black or frozen frame.
- **E15 cut during ongoing action:** angle A shows a suplex starting; angle B shows it finishing: both LIVE_ACTION.
- **E16 cut to replay of the action just seen:** REPLAY when slow motion or the clearly repeated angle is evident, even if any branding is brief. A live shot that merely shows the last few frames of a preceding wipe, with no other replay evidence, is not REPLAY; if unresolved, UNKNOWN `REPLAY_AMBIGUOUS`.
Ties and judgement calls follow the hierarchy in section 3.

## 12. Obligations carried to later stages (not part of this protocol's authorisation)
- Before any confirmatory Stage-F result is inspected, the evidentiary rule for a NO_ADDED_VALUE determination (descriptive P5 inputs, the decision criteria, who judges, and the uncertainty reporting) must be prospectively written and reviewed. This protocol does not define it.
- Stage F needs its own labelling protocol amendment (second labeller if available, double-labelled fraction), reviewed before use.

## 13. What is not authorised by this document
No labelling of Stage-D footage; no classifier implementation; no fresh acquisition; no rights actions; no claims of exposure validity, workload, identity or anatomy.

STOP for independent reviewer audit.
