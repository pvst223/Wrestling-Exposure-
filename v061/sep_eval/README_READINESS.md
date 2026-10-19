# SEPARATED-BODY EVALUATION V1 — READINESS PACKAGE (candidate; nothing executed on fresh data)
Run from the package root (clean unzip), Python 3 with numpy, scipy, opencv-python:
1. `python v061/sep_eval/verify_package.py` — every vendored dependency (frozen Anatomy V1, plan, locked implementation, tests) is byte-identical to its recorded sha256; anatomical manifest f5936ce8… and locked manifest eb99beb3… match.
2. `cd v061/sep_eval/tests && python -m unittest test_sep_eval` — 27 synthetic tests (eligibility boundaries and no-forbidden-input check, exact event-count table, decision rules, D6 binding, Claude cannot decide, sampler determinism/constraints/burned-clip rejection/shortfall reporting, blind-file leak checks, two-step image render, end-to-end synthetic join).
3. Frozen Anatomy V1 tests still pass: `cd v061/anatomical/tests` (see v061/anatomical/README_REVIEWER.md).
Real-data scripts (private data, not in this package): `feasibility_count.py` (counts only), `sep_sample.py`, `sep_review_pack.py`, `sep_join.py`. The burned-clip indicative feasibility result is `SEP_FEASIBILITY_BURNED_INDICATIVE_V1.json` (counts only; cannot support KEEP).
