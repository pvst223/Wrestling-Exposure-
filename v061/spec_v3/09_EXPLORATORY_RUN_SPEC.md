# 09 Authorised exploratory run: `V0.6.1 DEVELOPMENT / HYPOTHESIS CHECK ONLY` (revision 3; authorised by PL5 for exactly one execution)

Purpose: a single check of whether the decision rule alone (no new training data, no new head) changes behaviour on existing exposed data. It cannot support any claim, cannot be iterated, and cannot be optimized against old TEST. No KEEP/KILL/MODIFY/INCONCLUSIVE class is assigned.

## Fixed design
- Head: the frozen V0.6 L1 seed-0 MobileCLIP-B state dict (`L1_seed0_mobileclip_b.pt`, hash recorded in the ledger). No retraining, no new head.
- Rule: the V0.6.1 two-stage rule (01). L1 grid (20 points): tau_g {0.5,0.6,0.7,0.8,0.9} x delta {0.05,0.10,0.20,0.30}. B0: original frozen grid tau {0.30,0.40,0.50,0.60,0.70} x margin {0.00,0.02,0.05,0.10}.
- Selection data: old DEV only (Lesnar/Bryan), V0.6 unit tables. Matched coverage c* = largest of {0.5,0.4,0.3,0.2,0.1} reached by at least one grid point of BOTH methods on old DEV (the per-fold requirement reduces to the single DEV episode). Per method: among points with DEV coverage >= c*, lowest DEV unit-FTA; ties highest coverage; ties lexicographically smallest parameters (L1: tau_g then delta; B0: tau then margin). If no c* exists for both, the run ends with "no feasible operating point".
- Evaluation: once on old TEST (two episodes) with the V0.6 unit tables and metrics: unit FTA with exact Clopper-Pearson intervals, coverage, paired exact one-sided sign test (b, c, p), per-stratum false-accept units, gate AUROC (g = pA + pB, target vs non-target) and A-vs-B AUROC (q), with unit-clustered bootstrap CIs (2000 resamples; seed `int(sha256(spec_freeze_hash)[:8],16) % 2**31`, where spec_freeze_hash is the sha256 of the pre-exploratory MANIFEST recorded in ledger PL6). Also reported: the L1 decision decomposition (accept / reject non-target / ambiguous abstain) and, for reference, the frozen V0.6 result.
- In-sample DEV numbers at the selected points are reported for context.
- Labelling: every output file and table carries `V0.6.1 DEVELOPMENT / HYPOTHESIS CHECK ONLY`; results are descriptive; nothing is called validation.

## Controls
- The script and its hash are recorded in the ledger before execution; it is first tested only on synthetic data.
- Executed exactly once. A crash or defect: record it, fix only a genuine specification/implementation defect (an error relative to this document), re-execute, and record both; no performance-driven change is permitted.
- No video, no person-level tables committed; aggregate JSON and hashes only.
- After the result: the reviewer rules on the freeze candidate. The single amendment round (01 section 7) may correct only genuine specification/implementation defects.
