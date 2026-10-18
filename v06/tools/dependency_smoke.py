"""Dependency artifact verification: hash + exact (strict) load + deterministic shape smoke test ONLY. Uses a seeded synthetic tensor, never footage, labels or any dataset; computes no train/dev/test performance and no comparative embeddings.
usage: dependency_smoke.py dinov2|osnet WEIGHTS CODE_DIR OUT.json [--pinned-sha256 HEX]
 dinov2: official facebookresearch/dinov2 code (commit recorded), model dinov2_vits14 (ViT-S/14, NO registers), checkpoint must be the official dinov2_vits14_pretrain.pth; strict state-dict load; 224x224 input; expected 384-d.
 osnet : official KaiyangZhou/deep-person-reid torchreid/models/osnet.py loaded by file path, osnet_x1_0; checkpoint must be a ReID-trained checkpoint (guard: classifier output dim 1000 => ImageNet-only init => REJECT); strict load after stripping 'module.'; 256x128 input; expected 512-d.
Exit code 0 only if every check passes."""
import sys,os,json,hashlib,importlib.util,subprocess,platform
import torch
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()
def commit(d):
    try: return subprocess.check_output(["git","-C",d,"rev-parse","HEAD"],text=True).strip()
    except Exception: return None
def run(which,weights,code_dir,pinned=None):
    rec={"which":which,"weights_file":os.path.basename(weights),"weights_size_bytes":os.path.getsize(weights),"weights_sha256":sha(weights),"code_dir":code_dir,"code_commit":commit(code_dir),"torch":torch.__version__,"python":platform.python_version(),"checks":{},"smoke_only_no_performance_computed":True}
    if pinned: rec["checks"]["sha256_matches_pinned"]=(rec["weights_sha256"]==pinned.lower())
    g=torch.Generator().manual_seed(0)
    sd=torch.load(weights,map_location="cpu",weights_only=True)
    sd=sd.get("state_dict",sd) if isinstance(sd,dict) else sd
    sd={(k[7:] if k.startswith("module.") else k):v for k,v in sd.items()}
    if which=="dinov2":
        sys.path.insert(0,code_dir)
        from dinov2.hub.backbones import dinov2_vits14
        m=dinov2_vits14(pretrained=False)
        r=m.load_state_dict(sd,strict=True); rec["checks"]["strict_load_ok"]=True   # raises on any mismatch
        rec["checks"]["no_register_tokens"]=(getattr(m,"num_register_tokens",0)==0 and not any("register" in k for k in sd))
        rec["checks"]["arch_vit_small_patch14"]=(m.embed_dim==384 and m.patch_embed.patch_size in (14,(14,14)) and len(m.blocks)==12 and m.blocks[0].attn.num_heads==6)
        x=torch.randn(1,3,224,224,generator=g); m.eval()
        with torch.no_grad(): a=m(x); b=m(x)
        rec["input_spec"]={"size":[224,224],"mean":[0.485,0.456,0.406],"std":[0.229,0.224,0.225],"note":"model forward returns the CLS embedding after the final norm (backbone feature, no head)"}
        rec["output_shape"]=list(a.shape); rec["embedding_dim"]=int(a.shape[-1]); rec["checks"]["deterministic_two_runs"]=bool(torch.equal(a,b)); rec["checks"]["dim_384"]=rec["embedding_dim"]==384
    else:
        spec=importlib.util.spec_from_file_location("osnet_official",os.path.join(code_dir,"torchreid","models","osnet.py")); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        ncls=int(sd["classifier.weight"].shape[0]) if "classifier.weight" in sd else None; rec["classifier_out_dim"]=ncls
        rec["checks"]["not_imagenet_only_init"]=(ncls is not None and ncls!=1000)
        m=mod.osnet_x1_0(num_classes=ncls or 1000,pretrained=False); m.load_state_dict(sd,strict=True); rec["checks"]["strict_load_ok"]=True
        x=torch.randn(1,3,256,128,generator=g); m.eval()
        with torch.no_grad(): a=m(x); b=m(x)
        rec["input_spec"]={"size":[256,128],"mean":[0.485,0.456,0.406],"std":[0.229,0.224,0.225],"note":"eval-mode forward returns the 512-d feature (before the classifier)"}
        rec["output_shape"]=list(a.shape); rec["embedding_dim"]=int(a.shape[-1]); rec["checks"]["deterministic_two_runs"]=bool(torch.equal(a,b)); rec["checks"]["dim_512"]=rec["embedding_dim"]==512
    rec["all_checks_passed"]=all(rec["checks"].values()); return rec
if __name__=="__main__":
    a=sys.argv[1:]; pinned=a[a.index("--pinned-sha256")+1] if "--pinned-sha256" in a else None
    try: rec=run(a[0],a[1],a[2],pinned)
    except Exception as e: rec={"which":a[0],"all_checks_passed":False,"error":repr(e)[:500]}
    json.dump(rec,open(a[3],"w"),indent=1); print(json.dumps(rec,indent=1)); sys.exit(0 if rec.get("all_checks_passed") else 1)
