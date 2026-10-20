#!/usr/bin/env python3
"""Confirms the SEP1-registered readiness candidate is byte-unchanged: every file hash recorded in ledger entry SEP1 equals the current file, no file under v061/sep_eval was added/removed, and the Anatomy V1 / locked manifests are unchanged. Run from the repo root."""
import glob, hashlib, json, os, sys
d = "v061/sep_eval/"; sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
sep1 = [json.loads(l) for l in open("v06/frozen/AUDIT_LEDGER.jsonl") if json.loads(l)["id"] == "SEP1"][0]; rec = sep1["files_sha256"]
cur = {os.path.relpath(f, d): sha(f) for f in sorted(glob.glob(d + "**/*", recursive=True)) if os.path.isfile(f) and "__pycache__" not in f}
changed = [k for k in rec if cur.get(k) != rec[k]]; added = sorted(set(cur) - set(rec)); removed = sorted(set(rec) - set(cur))
ok_m = sha("v061/anatomical/ANATOMICAL_IMPLEMENTATION_MANIFEST.txt") == "f5936ce8bee667f15eaa55c2545a15ecf060afa06b1539abd3e824a8351b7dfb" and sha("v061/impl/IMPLEMENTATION_MANIFEST.txt") == "eb99beb359ee28dca883d7976ede4385f8dafb2e739d729f89a3358cd3ea073d"
out = dict(files_registered=len(rec), changed=changed, added=added, removed=removed, anatomy_and_locked_manifests_unchanged=ok_m, protocol_sha256_registered=sep1["protocol_sha256"], protocol_sha256_current=cur["SEPARATED_BODY_EVALUATION_V1_FINAL_PROTOCOL.md"])
print(json.dumps(out, indent=1)); sys.exit(0 if not changed and not added and not removed and ok_m else 1)
