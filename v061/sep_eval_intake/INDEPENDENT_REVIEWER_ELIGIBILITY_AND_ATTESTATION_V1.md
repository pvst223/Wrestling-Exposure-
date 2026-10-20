# INDEPENDENT HUMAN PRIMARY REVIEWER — ELIGIBILITY, INSTRUCTIONS AND BLANK ATTESTATION (V1)
Applies to the SEPARATED-BODY EVALUATION V1. No reviewer is named, proposed or implied here. Execution is blocked until a person meeting every requirement exists; **Claude is never substituted as the independent reviewer.** If none can be obtained: STOP and report the reviewer constraint.

## 1. Minimum eligibility (all required)
1. A human adult who agrees to review blind and unassisted.
2. **Not** the project owner, **not** Claude or any AI system, **not** a contributor to or developer of any code in this repository, **not** a first-pass tracklet labeller, seed auditor, acquisition-manifest author or Holdout #2 custodian for the clips under review.
3. Has **not** seen, and will not see before returning the completed response file: any anatomical review verdict (M9, M9B, M9C or this evaluation), Claude's or the owner's verdicts, the hidden key, item strata, eligibility flags or parameters, ownership/identity/merge-guard state, identity scores, any pipeline output other than the review images, or any evaluation result.
4. Is not directed, coached or compensated contingent on any outcome; has no stake in KEEP, MODIFY or KILL; no financial or authorship interest in the project's results.
5. Can distinguish individual bodies in broadcast wrestling frames (no wrestling knowledge or identification of any person is needed; do not try to identify anyone).
6. Agrees to keep images private: no copying, sharing, screenshots or uploading; delete after returning the file (rights UNRESOLVED; images include non-target people).
7. Completes the attestation (section 4) before receiving any image. The signed attestation and real identity stay private; the ledger records only the date, the role and the attestation's sha256.
Not required: medical or biomechanical expertise.

## 2. Reviewer instructions (what the person will do)
You receive two image folders and one response CSV (`RESPONSE_TEMPLATE.csv`). Each item is a broadcast frame with a cyan box around ONE person (the "assigned person").
**Step 1 (folder `step1/`, complete for ALL items before opening `step2/`):** the frame shows only the box. For each item record
- `box_person`: WRESTLER, REFEREE, SPECTATOR_OTHER, MULTIPLE_PERSONS_IN_BOX, or CANNOT_TELL;
- `separation_audit`: SEPARATED (no other body touches or overlaps the boxed person or sits right next to them), OTHER_BODY_TOUCHING_OVERLAPPING, or CANNOT_TELL.
**Step 2 (folder `step2/`):** the same frame now shows a drawn skeleton (cyan bones) with small numbered landmark labels. The question is **whose body each drawn landmark and bone lies on**, not whether the skeleton looks plausible or accurate.
- `judgeable`: NO if you cannot tell (very few landmarks, unreadable); else YES.
- `landmarks_other_person`: landmark numbers lying on any body other than the boxed person (another wrestler, referee, spectator), separated by `;`.
- `bones_other_person`: bones (pairs like `5-7`) that run onto another person's body, separated by `;`.
- `landmarks_off_body`: landmark numbers lying on no body (background, ropes, floor), separated by `;`.
- A landmark that is on the boxed person but in the wrong place on that person is NOT an error for this question.
Leave a list blank when none apply. Do not leave other columns blank. Do not edit item ids. Notes are optional and never replace the categorical fields. When in doubt use CANNOT_TELL / judgeable = NO; do not guess.
Return the CSV unchanged apart from your entries; its sha256 is recorded before anything else happens. Do not discuss items with anyone, including the project owner, until told the evaluation is closed.

## 3. Independence safeguards (project side)
- The reviewer receives images and the blank template only; no sheet, key, stratum or flag.
- The owner reviews separately and blind; neither file is shown to the other reviewer or to Claude before both files (and Claude's sensitivity file) are frozen and hashed; the hidden key is joined once, after.
- A review that departs from these rules is rejected, not repaired.

## 4. BLANK ATTESTATION (to be completed privately by the prospective reviewer; do not fill in this repository copy)
I, ______________________________ (printed name), attest that:
1. I am not the project owner, not an AI system, and not a developer of or contributor to this project's code; I have not labelled, audited or selected any clip or frame for this evaluation. ☐
2. I have not seen any anatomical review result, verdict, key, stratum, flag or pipeline state described in section 1.3, and I will not seek them. ☐
3. I have no stake in the outcome and my compensation, if any, does not depend on it. ☐
4. I will review alone, from the provided images and instructions only, without assistance from any person, model or tool that sees the images. ☐
5. I will keep the images private and delete them after returning my file. ☐
6. I will disclose immediately any contact with the project owner, developers or other reviewers about the items. ☐
Role / relationship to the project (for the private record): ______________________________
Signature: ______________________   Date/time (with time zone): ______________________
Received by (project): ______________   sha256 of this signed attestation (to be recorded in the ledger): ______________________
