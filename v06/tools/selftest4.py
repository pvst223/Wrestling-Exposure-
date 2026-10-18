import sys,os,tempfile,numpy as np,torch
sys.path.insert(0,".")
import heads as H, extract_features as EF
rng=np.random.default_rng(0); D=64
def ep(n_per=20,shift=0.0):
    ca,cb,cn=[rng.normal(size=D) for _ in range(3)]
    mk=lambda c,n:c+rng.normal(scale=0.6,size=(n,D))
    cand=np.concatenate([mk(ca,n_per),mk(cb,n_per),mk(cn,2*n_per)]); y=np.array([0]*n_per+[1]*n_per+[2]*(2*n_per))
    return dict(seed_A=mk(ca,4),seed_B=mk(cb,4),seed_N=mk(cn,2),cand=cand,y=y)
eps=[ep() for _ in range(20)]
b=H.NonLearnedBaseline(tau=0.2,margin=0.02); acc=0
for e in eps[:5]: dec,_=b.decide(e); acc+=np.mean([d=={0:"A",1:"B",2:"NONTARGET"}[y] for d,y in zip(dec,e["y"])])
print("baseline synthetic agreement",round(acc/5,2))
T=lambda e:{k:torch.tensor(v,dtype=torch.float32) if k!="y" else torch.tensor(v) for k,v in e.items()}
h=H.LearnedHead(D); hist=H.train(h,[T(e) for e in eps[:15]],epochs=15); assert hist[-1]<hist[0]
h2=H.LearnedHead(D); hist2=H.train(h2,[T(e) for e in eps[:15]],epochs=15); assert np.allclose(hist,hist2),"training not deterministic"
dec,p=H.decide(h,T(eps[16])); assert len(dec)==80 and np.allclose(p.sum(1),1,atol=1e-5)
# crop recipe + cache key determinism
im=(np.random.rand(360,640,3)*255).astype(np.uint8); c=EF.crop(im,[100,50,200,300]); assert c.shape==(224,224,3) and EF.crop(im,[0,0,10,10]) is None
print("selftest4 ok (synthetic only; no real data, no identity model trained)")
