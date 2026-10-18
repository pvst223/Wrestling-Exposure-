# Developer notice: please read before touching anything

**Phase 1 of V0.6 is frozen. Do not "improve" V0.6 yet.**

The post-hoc diagnostics for Phase 1 are being run now (`v06/posthoc_v1/`). Any change that affects the scientific model, its features, thresholds, training, or evaluation must go in a **new branch and version (V0.6.1+)**, never over the frozen Phase-1 implementation (`v06/tools/`, `v06/frozen/`). V0.6.1 itself is only a proposal at this point and will not be implemented until the project reviewer authorizes it.

## You may (review stage)
- Architecture and code review
- Reproducibility review
- Software-engineering review and bug identification
- Performance and bottleneck analysis
- Documentation review
- Test-coverage review
- Security and dependency review

Open issues or pull requests that touch only docs, tests that do not alter behaviour, or tooling outside the frozen scientific path.

## You may not
- Silently modify the frozen scientific implementation, or rerun Phase 1 "with improvements".
- Change thresholds, grids, seeds, selection rules, or any frozen manifest or ledger entry.
- Add footage, frames, crops, annotation images, model weights, or person-level data to the repo.
- Make or imply claims of validation, accuracy, generalisation, clinical utility, workload, fatigue or injury prediction.

## If you find a bug that could affect the frozen Phase-1 result
Do **not** patch it and rerun. Record it as an issue (describe the code path, a minimal reproduction on synthetic data, and why it could matter), leave the original state untouched, and tell the project owner. The reviewer decides what happens next.

## Where scientific change proposals go
Write them as a proposal document under `proposals/` (or an issue labelled `v0.6.1-proposal`) stating: the observation motivating it, the failure mechanism hypothesised, what changes, what stays frozen, and the prospective experiment that could falsify it. They are reviewed before any experimental evaluation.

## Before every push (maintainers)
Verify the commit has no secrets or tokens, no model weights, no copyrighted match video, no private source media, and no caches or large generated artifacts. Do not rewrite history or delete tags or branches that make a frozen state recoverable. Frozen states are tagged (see git tags).
