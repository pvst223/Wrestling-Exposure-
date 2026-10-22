import os,sys,unittest,re
import numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); RV=os.path.join(HERE,"..","rule_v1_1"); sys.path.insert(0,RV)
import rule_v1_1 as R
def mk(fr,shape=(360,640)):
    return {f:(np.array([[0,0,10,h] for h,_ in bl],np.float32).reshape(-1,4),np.array([c for _,c in bl],np.float32),shape) for f,bl in fr.items()}
class T(unittest.TestCase):
    cfg=R.load_cfg()
    def cls(self,d): return R.classify_shots([("s","x",0,30)],{"x":d},self.cfg)[0]
    def test_live_even_if_tight(self): self.assertEqual(self.cls(mk({f:[(330,.9),(320,.8)] for f in range(0,30,3)}))["rule_class"],"LIVE")
    def test_not_live(self): self.assertEqual(self.cls(mk({f:[(150,.9)] for f in range(0,30,3)}))["rule_class"],"NOT_LIVE")
    def test_band(self): self.assertEqual(self.cls(mk({f:([(150,.9),(140,.8)] if f<9 else [(150,.9)]) for f in range(0,30,3)}))["rule_class"],"UNKNOWN")
    def test_gate(self): self.assertEqual(self.cls(mk({f:[(150,.9),(40,.9),(150,.2)] for f in range(0,30,3)}))["rule_class"],"NOT_LIVE")
    def test_missing_fails_closed(self): r=self.cls({}); self.assertEqual((r["rule_class"],r["why"]),("UNKNOWN","NO_FEATURES"))
    def test_replay_never_live(self): self.assertEqual(R.decide({"F1_frac_ge2":1.0},self.cfg,1)[0],"REPLAY_SUSPECT")
    def test_budget(self): self.assertEqual((len(self.cfg["features"]),len(self.cfg["thresholds"])),(1,2))
    def test_forbidden_tokens(self):
        bad=re.compile(r"identity|skeleton|keypoint|\bkp\b|anatom|owner|mask|merge_guard|carried|\bcom\b|speed|accel|distance|workload|label|check_set|manifest_check",re.I)
        for fn in ("rule_v1_1.py","rule_v1_1_config.json"):
            with open(os.path.join(RV,fn)) as fh: self.assertIsNone(bad.search(fh.read()),fn)
if __name__=="__main__": unittest.main()
