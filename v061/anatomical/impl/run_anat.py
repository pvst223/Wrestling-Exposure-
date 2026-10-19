"""Execution driver (NOT RUN on real data in this phase). Refuses to start without a reviewer authorization record registered in the ledger.
Registered sequence: see EXECUTION_SEQUENCE.md. Segmentation extraction (unchanged seg_extract.py/model/settings, pose-evaluation frames only) is stage S1 and is the first real-data step."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import preflight as pf
def main(auth_path, ledger_path, pose_w, seg_w, result_path, clips=pf.CLIPS):
    pf.check_reused(); pf.check_locked_impl(); pf.check_clips(clips); pf.check_authorization(auth_path, ledger_path); pf.check_models(pose_w, seg_w); pf.check_exactly_once(result_path)
    raise NotImplementedError("stage runners S1-S6 are wired only after execution authorization (planning/implementation phase)")
if __name__ == "__main__":
    a = os.path.join(os.path.dirname(HERE), "AUTHORIZATION_RECORD.json")
    main(a, os.path.join(pf.REPO, "v06", "frozen", "AUDIT_LEDGER.jsonl"), "", "", "")
