"""Generates golden parity fixtures from the FROZEN code (read-only import). Run once in the full repository environment (needs torch for the V0.6 unit code):
python v061/tests/fixtures/make_parity_fixtures.py   -> writes parity_golden.json. Inputs and frozen outputs are stored so tests need neither torch nor the frozen sources."""
import sys, os, json, hashlib, importlib.util
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, REPO); sys.path.insert(0, os.path.join(REPO, "v06", "tools"))
from v061.impl import decision_rule as R
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
ex = os.path.join(REPO, "v061", "exploratory_v1", "exploratory_check_v061.py")
spec = importlib.util.spec_from_file_location("expl", ex); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
rng = np.random.default_rng(7); P = np.concatenate([rng.dirichlet([.5, .5, .5], 2000), rng.dirichlet([3, 3, 1], 2000)])
names = {"A": 0, "B": 1, "REJECT": 2, "ABSTAIN": 3}
rule = {f"{tg}|{dl}": [names[m.two_stage_label(a, b, c, tg, dl)] for a, b, c in P] for tg, dl in R.GRID_L1}
import phase1_run as RUN
rng = np.random.default_rng(3); truths = ["a", "b", "REFEREE", "SPECTATOR", "RINGSIDE_STAFF", "Other Guy"]; rows = []
for i in range(300):
    rows.append(dict(shot=int(rng.integers(0, 4)), truth=truths[rng.integers(0, 6)], accepted=["", "a", "b"][rng.integers(0, 3)]))
old = [dict(clip_id="c", shot=r["shot"], truth_id=r["truth"], accepted_role=r["accepted"]) for r in rows]
metrics = RUN.table_metrics(RUN.unit_table([(dict(A="a", B="b"), old)]))
out = dict(provenance=dict(frozen_exploratory_check_v061_sha256=sha(ex), frozen_phase1_run_sha256=sha(os.path.join(REPO, "v06", "tools", "phase1_run.py")), note="golden outputs of FROZEN code on stored inputs; generated read-only"),
           rule=dict(P=P.tolist(), codes=rule), units=dict(rows=rows, targets=["a", "b"], expected_table_metrics=metrics))
json.dump(out, open(os.path.join(HERE, "parity_golden.json"), "w"), sort_keys=True); print("written; frozen hashes", out["provenance"])
