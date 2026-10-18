"""Fail-closed authorization guard. Any script that touches experimental pixels/features, trains, selects thresholds or evaluates must call require_bakeoff_authorization() first.
It passes only if AUDIT_LEDGER.jsonl contains an entry with id starting 'AUTH' and kind 'BAKEOFF_AUTHORIZATION' whose ready_manifest_sha256 equals the sha256 of the frozen FINAL_READY_MANIFEST (V2 or later) AND that manifest's status is READY. No parameters can bypass it."""
import json,hashlib,os
def _sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
def require_bakeoff_authorization(frozen_dir):
    L=os.path.join(frozen_dir,"AUDIT_LEDGER.jsonl"); rows=[json.loads(l) for l in open(L)]
    auth=[r for r in rows if str(r.get("id","")).startswith("AUTH") and r.get("kind")=="BAKEOFF_AUTHORIZATION"]
    if not auth: raise SystemExit("NOT AUTHORIZED: no BAKEOFF_AUTHORIZATION entry in the audit ledger. Phase 1 has not been authorised by the reviewer.")
    a=auth[-1]; mp=os.path.join(frozen_dir,a["ready_manifest_file"])
    if not os.path.exists(mp) or _sha(mp)!=a["ready_manifest_sha256"]: raise SystemExit("NOT AUTHORIZED: READY manifest missing or hash mismatch")
    if json.load(open(mp)).get("status")!="READY": raise SystemExit("NOT AUTHORIZED: manifest status is not READY")
    return True
