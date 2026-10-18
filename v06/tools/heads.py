"""Phase 1 identity heads on cached frozen features. Two methods, identical inputs/episodes/metrics:
 (1) NonLearnedBaseline: prototype cosine + margin + explicit non-target gallery, thresholds chosen on dev under a stated FTA target (set by preregistration, not here).
 (2) LearnedHead: ONE linear projection trained with the minimum episodic A/B/NON-TARGET objective (prototype cosine logits with a learned non-target logit = learned scalar threshold). No ensemble, no extra losses.
An episode = (seed features for A, seed features for B, optional referee/neither seeds, candidate features with labels in {A,B,NONTARGET}). Outputs per candidate: score_A, score_B, score_nontarget and decision in {A,B,NONTARGET,ABSTAIN}.
Training is written but is NOT run on real data until the preregistration is frozen; tests use synthetic features only."""
import numpy as np,torch,torch.nn as nn,torch.nn.functional as F
def _n(x): return x/np.maximum(np.linalg.norm(x,axis=-1,keepdims=True),1e-12)
class NonLearnedBaseline:
    def __init__(self,tau=0.5,margin=0.05): self.tau=tau; self.margin=margin
    def scores(self,ep):
        pa=_n(_n(ep["seed_A"]).mean(0)); pb=_n(_n(ep["seed_B"]).mean(0)); X=_n(ep["cand"])
        neg=[_n(ep[k]) for k in ("seed_N","online_N") if k in ep and len(ep[k])]; N=np.concatenate(neg) if neg else None
        sa=X@pa; sb=X@pb; sn=(X@N.T).max(1) if N is not None else np.full(len(X),-1.0); return sa,sb,sn
    def decide(self,ep):
        sa,sb,sn=self.scores(ep); out=[]
        for a,b,n in zip(sa,sb,sn):
            best,lab=(a,"A") if a>=b else (b,"B"); other=max(min(a,b),n)
            out.append(lab if (best>=self.tau and best-other>=self.margin) else ("NONTARGET" if n>=best else "ABSTAIN"))
        return out,(sa,sb,sn)
class LearnedHead(nn.Module):
    def __init__(self,d_in,d_out=128,seed=0):
        super().__init__(); torch.manual_seed(seed); self.proj=nn.Linear(d_in,d_out,bias=False); self.nt=nn.Parameter(torch.tensor(0.3)); self.scale=nn.Parameter(torch.tensor(10.0))
    def emb(self,x): return F.normalize(self.proj(x),dim=-1)
    def logits(self,ep):
        pa=F.normalize(self.emb(ep["seed_A"]).mean(0),dim=0); pb=F.normalize(self.emb(ep["seed_B"]).mean(0),dim=0); X=self.emb(ep["cand"])
        negs=[self.emb(ep[k]) for k in ("seed_N","online_N") if k in ep and len(ep[k])]
        sn=(X@torch.cat(negs).T).max(1).values if negs else torch.zeros(len(X))-1
        nt=torch.maximum(sn,self.nt.expand(len(X)))     # explicit NON-TARGET logit: strongest non-target similarity or learned floor
        return self.scale*torch.stack([X@pa,X@pb,nt],1)
def train(head,episodes,epochs=30,lr=1e-2,seed=0):
    """episodes: list of dict with torch tensors + 'y' (0=A,1=B,2=NONTARGET). Deterministic given seed. Returns loss history."""
    torch.manual_seed(seed); opt=torch.optim.Adam(head.parameters(),lr=lr); hist=[]
    for e in range(epochs):
        tot=0.0
        for ep in episodes:
            opt.zero_grad(); loss=F.cross_entropy(head.logits(ep),ep["y"]); loss.backward(); opt.step(); tot+=loss.item()
        hist.append(tot/len(episodes))
    return hist
def decide(head,ep,tau=0.5,margin=0.0):
    with torch.no_grad(): p=F.softmax(head.logits(ep),1)   # softmax output is an uncalibrated heuristic evidence score, not a probability
    out=[]
    for r in p.numpy():
        k=int(r.argmax()); s=np.sort(r)[::-1]; out.append(("A","B","NONTARGET")[k] if (r[k]>=tau and s[0]-s[1]>=margin) else "ABSTAIN")
    return out,p.numpy()
