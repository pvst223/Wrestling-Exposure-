import os,sys,unittest,json,re
import numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); RV=os.path.join(HERE,"..","rule_v1"); sys.path.insert(0,RV)
import rule_v1
def mk(boxes_per_frame,shape=(360,640)):
    d={}
    for f,bl in boxes_per_frame.items():
        d[f]=(np.array([[0,0,10,h] for h,_ in bl],np.float32).reshape(-1,4),np.array([c for _,c in bl],np.float32),shape)
    return d
class T(unittest.TestCase):
    cfg=rule_v1.load_cfg()
    def cls(self,d,fs=0,fe=30):
        return rule_v1.classify_shots([("s","x",fs,fe)],{"x":d},self.cfg)[0]
    def test_live(self):
        r=self.cls(mk({f:[(150,.9),(140,.8)] for f in range(0,30,3)})); self.assertEqual(r["rule_class"],"LIVE")
    def test_not_live_single_subject(self):
        r=self.cls(mk({f:[(150,.9)] for f in range(0,30,3)})); self.assertEqual(r["rule_class"],"NOT_LIVE")
    def test_tight_framing_is_unknown(self):
        r=self.cls(mk({f:[(320,.9),(300,.8)] for f in range(0,30,3)})); self.assertEqual(r["rule_class"],"UNKNOWN")
    def test_band_is_unknown(self):
        d=mk({f:([(150,.9),(140,.8)] if f<9 else [(150,.9)]) for f in range(0,30,3)}); self.assertEqual(self.cls(d)["rule_class"],"UNKNOWN")
    def test_gate(self):
        r=self.cls(mk({f:[(150,.9),(40,.9),(150,.2)] for f in range(0,30,3)})); self.assertEqual(r["rule_class"],"NOT_LIVE")
    def test_missing_fails_closed(self):
        r=self.cls({}); self.assertEqual((r["rule_class"],r["why"]),("UNKNOWN","NO_FEATURES"))
    def test_thresholds_inclusive_rules(self):
        t=self.cfg["thresholds"]; self.assertEqual(rule_v1.decide({"F1_frac_ge2":t["T2"],"F2_h_max_med":t["T3"]},self.cfg)[0],"LIVE")
        self.assertEqual(rule_v1.decide({"F1_frac_ge2":t["T1"],"F2_h_max_med":0.3},self.cfg)[0],"UNKNOWN")
    def test_replay_indicator_inert_but_never_live(self):
        self.assertEqual(rule_v1.decide({"F1_frac_ge2":1.0,"F2_h_max_med":0.3},self.cfg,replay_indicator=1)[0],"REPLAY_SUSPECT")
    def test_budget(self):
        c=self.cfg; self.assertLessEqual(len(c["features"]),3); self.assertLessEqual(len(c["thresholds"]),5)
    def test_deterministic(self):
        d=mk({f:[(150,.9),(140,.8)] for f in range(0,30,3)}); self.assertEqual(self.cls(d),self.cls(d))
    def test_forbidden_tokens_absent_from_code_and_config(self):
        bad=re.compile(r"identity|skeleton|keypoint|\bkp\b|anatom|owner|mask|merge_guard|carried|\bcom\b|speed|accel|distance|workload|label|check_set|manifest_check",re.I)
        for fn in ("rule_v1.py","rule_v1_config.json"):
            with open(os.path.join(RV,fn)) as fh: txt=fh.read(); self.assertIsNone(bad.search(txt),fn)
if __name__=="__main__": unittest.main()
