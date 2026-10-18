# 02 Data plan (DRAFT; no acquisition authorized)

## 2.1 Current limitation
Under the frozen seed rule only 4 of 6 acquired clips yield an evaluable pair episode: 1 TRAIN (Orton/Rollins), 1 DEV (Lesnar/Bryan), 2 TEST (Andrade/Mysterio, Andrade/Omega). Two clips (HBK/Benjamin, Rock/HHH) fell short of the seed rule (identities with 1-3 qualifying seeds), so L1 trained on 1 episode and 2 identities. Source, resolution and promotion shifts are confounded with split.

## 2.2 Status of existing data
| Data | V0.6.1 status |
|---|---|
| Old V0.6 TEST (Andrade/Mysterio, Andrade/Omega) | Development-exposed (opened, scored, diagnosed, videos rendered). **Permanently ineligible as a confirmatory V0.6.1 test.** May be used only as development data (training or selection) under the rules below. Any number computed on it is exploratory and must be labelled so. |
| Old DEV (Lesnar/Bryan) | Development data. |
| Old TRAIN clips (Orton/Rollins, HBK/Benjamin, Rock/HHH) | Development data. |
| Holdout #2 | Sealed, untouched, not opened by this session; reserved for one-shot prospective evaluation after V0.6.1 is completely frozen. |
| Holdout #1 (failed V0.5 holdout, Jeff Hardy) | Excluded, as before. |
| Cena | Development-only, as before. |

## 2.3 Development protocol on existing data (all development-exposed, so only for building and selecting, never for claims)
- Pool all six clips as the development pool D. Group clips by identity components (Andrade links the two Andrade clips) and use leave-one-component-out cross-fitting: 5 folds {HBK/Benjamin}, {Orton/Rollins}, {Rock/HHH}, {Lesnar/Bryan}, {Andrade/Mysterio + Andrade/Omega}. Never split a component across train and held-out.
- Per fold: train the head on the other folds' training episodes; score the held-out fold's EVALUATION episodes (strict seed rule). Strictly evaluable episodes exist only in 4 of the 5 folds, so cross-fitted selection rests on 4 episodes: thin. This is why new data is required for any real claim.
- Thresholds (tau_g, delta; B0 tau, margin) are selected on the pooled out-of-fold predictions only (03 section 3). The final head for the one-shot run is trained on all development training episodes.

## 2.4 Training-diversity plan
Training-episode construction may use a relaxed seed rule (TRAIN ONLY; evaluation episodes keep the strict rule): at least 2 seed crops per identity from at least 1 shot, so the HBK/Benjamin and Rock/HHH clips can contribute episodes. Rationale: seeds in training only simulate enrolment. Risk: relaxed episodes are easier/noisier than evaluation episodes; disclosed and tested by an ablation that drops them (descriptive).
Episode multiplicity: for each evaluable or relaxed pair, resample the seed draw K = 5 times (fixed seed, section 01) so the head sees several enrolments of the same pair; each draw is a separate full-batch episode. Resamples of the same pair are NOT independent evidence and are never counted as independent units.
Pairing rule: pairs are formed only within a clip (same shot context). Cross-clip synthetic pairs are prohibited because they let the head separate A from B using background, overlay, resolution or promotion cues (shortcut risk).
Hard negatives: referees, staff, spectators and third wrestlers from the same clip as non-target examples, as in V0.6.
No augmentation beyond that is proposed (augmentation would be a new modelling choice needing separate approval).

## 2.5 New data acquisition target (requires reviewer approval, rights and privacy review first)
Targets are minimum sizes needed for a non-vacuous test; they are planning figures, not tuned.
- Additional development clips: at least 6 new clips with at least 12 new named wrestler identities, each clip yielding at least 1 strictly evaluable pair episode (each target identity visible in at least 4 distinct shots, as per the seed rule), spanning at least 3 sources/eras/resolutions and at least 2 promotions. Target: at least 12 evaluable development episodes in total (currently 4).
- Holdout #2: at least 4 clips, at least 8 named identities, at least 150 units with at least 60 target units, at least 40 units expected to be baseline false-accept units. Sizing logic (illustrative, uses the exposed old-TEST B0 false-accept rate of about 0.35 as an assumption; not tuned): the exact one-sided sign test at alpha 0.10 needs roughly 8 or more discordant units favouring the new rule with none against; with 150 units and a B0 rate near 0.35 there would be about 50 baseline-false-accept units, so a realistic improvement can produce enough discordant units.
- Names are user-supplied and authoritative; no appearance-based re-identification; unsupported metadata stays UNRESOLVED.
- Rights: UNRESOLVED stays; no redistribution; supplying footage is not permission to publish or build a persistent spectator/staff dataset; non-target imagery minimised and not retained beyond need.

## 2.6 Holdout #2 preservation
- Sealed: no pixels, frames, features, detections, tracklets, labels or videos from Holdout #2 are read before the V0.6.1 freeze. The existing sealed registry (single-use) is reused; opening writes a ledger entry first.
- Holdout #2 is excluded from every selection step: backbone, grids, thresholds, episode resampling, training, tooling tests, renderer tests.
- Identity overlap with development data: determined once from user-supplied NAMES only (no imagery), by the project owner, and recorded as a count per stratum at freeze time. Primary analysis uses all Holdout #2 units; overlap/non-overlap strata are descriptive only.
- Near-duplicate and same-event audit between Holdout #2 and all development clips uses hash-only comparison (the existing dHash audit logic) run by the custodian; only counts are reported to the reviewer and any flagged overlap is resolved by the reviewer before freeze.
- Annotation: blinded, human second annotator for Holdout #2 (open decision O3); labels committed by hash before any V0.6.1 output exists.
