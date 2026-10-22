import os,sys,csv,json,subprocess,tempfile,hashlib,unittest
HERE=os.path.dirname(os.path.abspath(__file__)); EV=os.path.join(HERE,"..","check_eval","evaluate_check.py")
def run(rows,marks_ok=True):
    d=tempfile.mkdtemp(); man=os.path.join(d,"m.csv"); lab=os.path.join(d,"l.csv"); pr=os.path.join(d,"p.csv"); mk=os.path.join(d,"k.csv"); out=os.path.join(d,"o.json")
    t=0.0; mr=[]
    for i,(ref,rule,dur) in enumerate(rows): mr.append((f"s{i}",t,t+dur)); t+=dur
    with open(man,"w",newline="") as f:
        w=csv.writer(f); w.writerow(["shot_id","source_id","set","t_start_s","t_end_s"]); [w.writerow([a,"x","check",b,c]) for a,b,c in mr]
    with open(lab,"w",newline="") as f:
        w=csv.writer(f); w.writerow(["shot_id","label","unknown_reason","flags"]); [w.writerow([mr[i][0],r[0],"PIP_AMBIGUOUS" if r[0]=="UNKNOWN" else "",""]) for i,r in enumerate(rows)]
    with open(pr,"w",newline="") as f:
        w=csv.writer(f); w.writerow(["shot_id","rule_class","why"]); [w.writerow([mr[i][0],r[1],"x"]) for i,r in enumerate(rows)]
    open(mk,"w").write("source_id,start_s,end_s,evidence_note,flags\nx,,,n,NO_D\n")
    sh=hashlib.sha256(open(man,"rb").read()).hexdigest()
    subprocess.run([sys.executable,EV,"--labels",lab,"--marks",mk,"--pred",pr,"--manifest",man,"--manifest_sha256",sh,"--out",out],check=True,capture_output=True)
    return json.load(open(out))
class T(unittest.TestCase):
    def test_exactly_10pct_not_inconclusive(self):
        r=run([("LIVE_ACTION","LIVE",9),("UNKNOWN","LIVE",1)]); self.assertNotEqual(r["decision"] if "decision" in r else "","REFERENCE_INCONCLUSIVE"); self.assertIn("P1",r)
    def test_over_10pct_inconclusive_no_classifier(self):
        r=run([("LIVE_ACTION","LIVE",8),("UNKNOWN","LIVE",2)]); self.assertEqual(r["decision"],"REFERENCE_INCONCLUSIVE"); self.assertNotIn("P1",r); self.assertNotIn("classifier",r)
    def test_p1_and_baseline(self):
        r=run([("LIVE_ACTION","LIVE",6),("LIVE_ACTION","UNKNOWN",2),("CLOSE_UP","LIVE",1),("CLOSE_UP","NOT_LIVE",1)]); self.assertAlmostEqual(r["P1"]["fraction"],0.3); self.assertAlmostEqual(r["all_LIVE_comparator"]["fraction"],0.2)
    def test_p3_not_evaluable_without_replay(self):
        r=run([("LIVE_ACTION","LIVE",10)]); self.assertEqual(r["P3"]["status"],"NOT_EVALUABLE"); self.assertEqual(r["decision"],"NO_STOP_TRIGGER_P3_NOT_EVALUABLE")
    def test_stop_on_p1(self):
        r=run([("LIVE_ACTION","UNKNOWN",5),("LIVE_ACTION","LIVE",5)]); self.assertEqual(r["decision"],"STOP")
    def test_p3_leak_and_continue(self):
        r=run([("LIVE_ACTION","LIVE",9),("REPLAY","NOT_LIVE",1)]); self.assertEqual(r["P3"]["numerator_s"],0.0); self.assertEqual(r["decision"],"CONTINUE")
        r=run([("LIVE_ACTION","LIVE",5),("REPLAY","LIVE",5)]); self.assertEqual(r["decision"],"STOP")
if __name__=="__main__": unittest.main()
