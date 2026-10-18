"""Orchestrator support (deterministic, no scientific judgment).
  verify_inputs(spec)  : spec = {"name": expected_sha256,...} with paths; halts (SystemExit) on any mismatch.
  run_manifest(...)    : records input hashes, code hash, python/library versions, hardware, OS -> run_manifest.json
  run_stage(name,cmd,out_dir,validator): runs one stage, records wall time + peak memory, validates output (validator returns list of problems) before next stage; never retries with changed settings.
  freeze_dir(dir)      : writes output_hashes.json (sha256 of every file) and makes files read-only (immutable artifacts).
  verify_frozen(dir)   : re-hash and compare against output_hashes.json.
The guard may not change thresholds, models, seeds, code or discard frames: it has no parameters for that."""
import hashlib,json,os,sys,time,platform,subprocess,resource,stat,importlib.metadata as im
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()
def verify_inputs(spec):
    bad=[(k,p,e,sha(p) if os.path.exists(p) else "MISSING") for k,(p,e) in spec.items() if not os.path.exists(p) or sha(p)!=e]
    if bad: raise SystemExit("INPUT HASH MISMATCH, HALT: "+json.dumps(bad))
    return True
def code_hash(files): return {f:sha(f) for f in sorted(files)}
def run_manifest(path,inputs,code_files,libs=("numpy","torch","scipy","ultralytics","opencv-python")):
    v={}
    for l in libs:
        try: v[l]=im.version(l)
        except Exception: v[l]="not installed"
    m=dict(inputs={k:dict(path=p,sha256=sha(p)) for k,p in inputs.items()},code=code_hash(code_files),python=sys.version,libs=v,os=platform.platform(),machine=platform.machine(),cpu_count=os.cpu_count(),started_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()))
    json.dump(m,open(path,"w"),indent=1); return m
def run_stage(name,cmd,log_path,validator=None):
    t=time.time(); r=subprocess.run(cmd,capture_output=True,text=True); dt=time.time()-t
    rec=dict(stage=name,cmd=cmd,returncode=r.returncode,wall_s=round(dt,2),max_rss_mb=round(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss/1024,1),stdout_tail=r.stdout[-500:],stderr_tail=r.stderr[-500:])
    open(log_path,"a").write(json.dumps(rec)+"\n")
    if r.returncode!=0: raise SystemExit(f"STAGE {name} FAILED (technical failure; not retried with changed settings)")
    if validator:
        p=validator()
        if p: raise SystemExit(f"STAGE {name} OUTPUT INVALID, HALT: {p}")
    return rec
def freeze_dir(d):
    out={}
    for root,_,fs in os.walk(d):
        for f in fs:
            if f=="output_hashes.json": continue
            p=os.path.join(root,f); out[os.path.relpath(p,d)]=sha(p)
    json.dump(out,open(os.path.join(d,"output_hashes.json"),"w"),indent=1)
    for root,_,fs in os.walk(d):
        for f in fs: os.chmod(os.path.join(root,f),stat.S_IRUSR|stat.S_IRGRP|stat.S_IROTH)
    return out
def verify_frozen(d):
    exp=json.load(open(os.path.join(d,"output_hashes.json"))); bad=[k for k,h in exp.items() if not os.path.exists(os.path.join(d,k)) or sha(os.path.join(d,k))!=h]
    return bad
