# R4: owner proposal to use an AI annotator (Gemini) — disclosed deviation, NOT approved

Recorded 2026-10-18 at the owner's request. spec_v4 (manifest `efb2a797c358cdcad73bc933ccc5a80d95979610179240daf6229b4ba86c88af`) is unchanged.

**Owner statement:** a human second annotator was not possible; the owner proposes using Gemini (an AI model) as the second annotator for Holdout #2.

**Facts to carry forward**
- Spec 02 section 2.6 requires an independent, blinded HUMAN second annotator and states: "The AI second annotator used in V0.6 (deviation X1) is not acceptable here." The reviewer's R4 ruling repeats this ("genuinely independent blinded human").
- Gemini is not a human. Using it does NOT satisfy R4, and no human independence attestation can truthfully be signed for it.
- This proposal does not amend the spec and is not authorized. Only the reviewer can rule on it; any change would need a recorded amendment/deviation before Holdout #2 exposure.
- R4 status: OPEN / UNSATISFIED. Acquisition remains blocked on it.

**If the reviewer permits an AI second annotator, the following should be decided and recorded first (not decided here)**
- It is labelled an AI annotator (deviation, like X1), never "human", and any reliability result is reported as AI-vs-first-annotator agreement, not human inter-rater agreement.
- Outcome cap: the prior X1 treatment (annotation-provisional cap) should presumably apply; the reviewer must say.
- Blinding: sees no model/B0 output or first-pass labels; same prompt and frames for every unit; prompt, model name/version and settings recorded and hashed before use.
- Privacy: sending Holdout #2 frames to a third-party service may conflict with "footage remains private", minimised retention of non-target imagery, and the unresolved rights status (R3); the provider's terms and data retention must be checked first.
- A dated attestation by the owner describing the AI annotator accurately (model, version, date, no prior exposure), instead of the human attestation.
