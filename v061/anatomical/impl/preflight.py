"""Preflight/hash checks. Real-data execution additionally requires AUTHORIZATION_RECORD.json (absent at this stage by design)."""
import hashlib, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); ANAT = os.path.dirname(HERE); REPO = os.path.abspath(os.path.join(ANAT, "..", ".."))
LOCKED_IMPL_MANIFEST_SHA256 = "eb99beb359ee28dca883d7976ede4385f8dafb2e739d729f89a3358cd3ea073d"
POSE_SHA256 = "dbe539ea268db2534390942cfdf206e521f376f19e5415967a57f6a2ddfa3c90"
SEG_SHA256 = "51fa7e5ef385efa6d5b1d8e31b73399be6ed5d7ca71bda4bd4b2794bb445c4f4"
CLIPS = ("b1_orton_rollins_wm31", "b2_batch2_clip_condensed", "b2_videoplayback_2", "b2_videoplayback_5")
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
class Blocked(Exception): pass
def check_reused():
    j = json.load(open(os.path.join(ANAT, "REUSED_V05_HASHES.json"))); bad = [p for p, h in j["files"].items() if sha(os.path.join(ANAT, p)) != h]
    if bad: raise Blocked(f"reused V0.5 files changed: {bad}")
    return True
def check_locked_impl():
    import subprocess, sys
    out = subprocess.run([sys.executable, os.path.join(REPO, "v061", "tooling", "impl_manifest.py")], capture_output=True, text=True, cwd=REPO)
    if out.returncode != 0 or sha(os.path.join(REPO, "v061", "impl", "IMPLEMENTATION_MANIFEST.txt")) != LOCKED_IMPL_MANIFEST_SHA256: raise Blocked("locked implementation manifest mismatch")
    return True
def check_models(pose_path, seg_path):
    if sha(pose_path) != POSE_SHA256: raise Blocked("pose weights hash mismatch")
    if sha(seg_path) != SEG_SHA256: raise Blocked("seg weights hash mismatch")
    return True
def check_clips(clips):
    if tuple(sorted(clips)) != tuple(sorted(CLIPS)): raise Blocked("clip set must be exactly the four approved OOF clips")
    return True
def check_authorization(path, ledger_path):
    if not os.path.exists(path): raise Blocked("AUTHORIZATION_RECORD.json absent: real-data execution not authorized")
    a = json.load(open(path)); led = [json.loads(l) for l in open(ledger_path)]
    if not any(e.get("id") == a.get("ledger_id") for e in led): raise Blocked("authorization not registered in ledger")
    return a
def check_exactly_once(result_path):
    if os.path.exists(result_path): raise Blocked("result file exists: exactly-once rule")
    return True
