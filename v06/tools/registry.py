"""Append-only experiment/look ledger. Each record: timestamp, kind (dev_eval|sealed_test|holdout|training|feature_extraction), config_hash, split_manifest_hash, code_hash, seed, outputs_sha256, note.
Refuses a second sealed_test/holdout record for the same split_manifest_hash (single-use)."""
import json,sys,time,os
def log(ledger,rec):
    rows=[json.loads(l) for l in open(ledger)] if os.path.exists(ledger) else []
    if rec["kind"] in ("sealed_test","holdout") and any(r["kind"]==rec["kind"] and r["split_manifest_hash"]==rec["split_manifest_hash"] for r in rows): raise SystemExit("SINGLE-USE VIOLATION: "+rec["kind"]+" already opened for this split manifest")
    rec=dict(rec,ts=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())); open(ledger,"a").write(json.dumps(rec)+"\n"); return rec
