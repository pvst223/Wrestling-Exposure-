# Independent annotation protocol (recorded before any annotation is returned)
Governed by the frozen PREREGISTRATION_V3 (SHA-256 3e40f5ec3aea93539daeacdac7cb0bf1b4cfadbd90fb7de245641160c5c4ab78) and audit-ledger clarification C1. This document adds no method change; it records how the annotation is to be run.

## 1. Package
V0.6_Annotation_Package_BLIND_v2.zip, SHA-256 1b4499515c26ee29e65a54fa4c34222b22410b7b4ecdcf5f7084d550c655169a; 298 items; 333 files; final, not to be rebuilt. The A/B key, item-to-tracklet map and the 51-unit reserve list are NOT in the package.

## 2. Annotator eligibility (blindness)
A human who has NOT seen: the developer first-pass labels, any model predictions or outputs, any comparative results, or the Target A/B identity key.
- Annotator role: ______________________ (PENDING, to be filled by the investigator)
- Blindness confirmed by annotator (yes/no): ______ (PENDING)
- Date/time package handed over: ______________ and handoff channel: ______________ (PENDING)
- Date/time CSV returned: ______________ (PENDING)

## 3. Task rules
- Label every item with exactly one of TARGET_A, TARGET_B, REFEREE, STAFF, SPECTATOR, UNLABELABLE in the `label` column of annotation_sheet.csv.
- Targets are defined only by the reference images for that clip_code; no outside knowledge of who the wrestlers are; no cross-clip comparison.
- When in doubt use UNLABELABLE; do not guess. The optional `notes` column may hold comments but never replaces the categorical label.
- Do not edit or reorder item_id, clip_code or image. Do not consult the developer, any model or any other annotator.
- The images show spectators and staff: use only for this task, do not copy or share, delete after returning the CSV.

## 4. Return and custody
- The returned CSV is preserved UNCHANGED. Its SHA-256 is recorded BEFORE any reconciliation.
- Any template violation (changed IDs/order/clip codes/images, a missing or invalid label) causes rejection of that return; it is not repaired by the developer.

## 5. Reconciliation (deterministic, frozen)
Run tools/annotation_agreement.py (SHA-256 in audit ledger entry C1) then tools/adjudicate.py. Mandatory reporting: raw tracklet-level agreement; Cohen's kappa INCLUDING UNLABELABLE (governing gate); kappa EXCLUDING items either annotator marked UNLABELABLE (required secondary diagnostic); unit-level agreement on the 51 reserved units; every disagreement documented (classification left to a human, never auto-resolved).
- Governing gate: kappa including UNLABELABLE >= 0.60. Passing only means the prespecified reliability gate is passed; it is NOT validation of the annotation or labels.
- If kappa including UNLABELABLE < 0.60 the result is PROVISIONAL and the primary outcome cannot exceed MODIFY.
- Disagreements are never used to tune models, thresholds, data or rules.

## 6. Status
Phase 1 remains blocked on this annotation (blocker A). Dependency blocker B is RESOLVED (registry SHA-256 1d53543a65d9e9d1c3212c031a9588f979ebf2cf3e69dbd1c53eb9c1c5609cd8). No features have been extracted from experimental data, nothing trained, no thresholds selected, no comparisons run, test unopened.
