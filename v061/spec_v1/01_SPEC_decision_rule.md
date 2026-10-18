# 01 V0.6.1 decision-rule specification (DRAFT)

## Motivation (from frozen POSTHOC_DIAGNOSTIC_V1; descriptive, 1 DEV and 2 TEST episodes, confounded shifts)
1. Target-vs-non-target separation transferred (TEST L1 AUROC 0.974, CI 0.951-0.989).
2. The DEV-selected floor 0.80 on max(pA,pB) did not transfer (0 of 2195 TEST target candidates cleared it).
3. A-vs-B discrimination was weak on TEST (L1 AUROC 0.716, CI 0.606-0.842; 0.448 on Andrade/Omega where B0 was also near chance), and perfect on the single TRAIN episode.
4. Hypothesised mechanism (a hypothesis, not a finding): one softmax over {A, B, NON-TARGET} couples "is this a target at all" to "which target"; A/B ambiguity lowers max(pA,pB) for genuine targets. A one-episode, two-identity training set probably left the A/B axis pair-specific.

## What changes (decision rule) and what is added (training data)
Given the frozen L1 head output p = (pA, pB, pN) for a candidate, with pA + pB + pN = 1:
- Stage 1, target gate: g = pA + pB (= 1 - pN). If g < tau_g: the candidate is NOT accepted (non-target / reject).
- Stage 2, assignment, only if Stage 1 passes: q = pA / (pA + pB) (conditional target probability; pA + pB > 0 is guaranteed by Stage 1 for tau_g > 0). Accept as A if q >= 0.5 + delta; accept as B if q <= 0.5 - delta; otherwise ABSTAIN (ambiguous A/B). delta in [0, 0.5).
- Output per candidate: one of {ACCEPT_A, ACCEPT_B, REJECT_NONTARGET, ABSTAIN_AMBIGUOUS}. For unit metrics both REJECT and ABSTAIN count as "not accepted" (same as Phase 1). The two reasons are reported separately for diagnosis only.
- Fail-closed: any numerical failure (NaN/inf probability, pA + pB below 1e-12) yields not accepted.
- Score values are heuristic evidence, not probabilities. Names "target probability" in code and reports must carry that disclaimer.

Parameters tau_g and delta are the only new tunable quantities, chosen on development data only (see 03).

Pre-specified grids, matched search budget (49 points each; ranges fixed before any new data and not fitted to any score):
- L1: tau_g in {0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9} x delta in {0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30}.
- B0 comparator: tau in {0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9} x margin in {0.00, 0.02, 0.05, 0.10, 0.15, 0.20, 0.25}. (Open decision O1: Phase-1 B0 grid had 20 points; matching L1's budget avoids giving the new rule a larger search. The extension is motivated in part by the diagnostic that B0's tau=0.30 was non-selective; this is disclosed.)

## Kept frozen (unchanged, by reference to V0.6)
MobileCLIP-B backbone and preprocessing (frozen preprocessing hashes); L1 architecture (128-d linear projection, learned non-target logit, learned scale); episodic prototype scoring and the 3-class softmax; training recipe (Adam, lr 0.01, 30 epochs, seed 0 primary, full-batch per episode, deterministic ordering, no auxiliary losses, no ensembling); unit definition (clip, shot, identity/class); unit-level FTA with exact Clopper-Pearson intervals; coverage definition (unweighted mean of per-unit accepted fraction); matched-coverage rule c* in {0.5, 0.4, 0.3, 0.2, 0.1}; paired exact one-sided sign test; fail-closed fusion with anatomical ownership; B0 as the non-learned comparator; seed-episode eligibility rules for EVALUATION (4 target seeds, >= 2 shots, <= 2/shot, >= 60 frames apart, median-height rule, referee/third-party seeds); the rule that no frozen V0.6 artifact is edited.

## What the training change is (not a rule change)
Training uses a more diverse TRAIN set (see 02). The loss, architecture and hyperparameters do not change. Consequence: a decision-rule-only effect cannot be separated from a training-data effect in the primary comparison. Two descriptive ablations on Holdout #2, run only after the primary result is frozen, address this (03 section 6).

## Determinism and seeds
All random choices (episode resampling for training, bootstrap) use a seed derived as `int(sha256(spec_freeze_hash)[:8],16) % 2**31`, where spec_freeze_hash is the hash of the frozen V0.6.1 specification recorded in the ledger. It is fixed before any new-data result exists and cannot be chosen after seeing outcomes.

## Anatomical ownership
Fusion unchanged: V0.6.1 output may only confirm or withhold; it may never override anatomical ownership, and any disagreement or abstention stays fail-closed.
