"""Runs frozen Rule V1.1 on the CHECK shots from frozen detections (boxes only). Writes a PRIVATE predictions CSV and prints its sha256 + row count only.
Reads no reference annotation. Usage: predict_check.py --priv DIR --dets PKL --out PRED.csv"""
import argparse,csv,pickle,hashlib,os,sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","rule_v1_1"))
import rule_v1_1
def main():
    ap=argparse.ArgumentParser(); [ap.add_argument("--"+k,required=True) for k in ("priv","dets","out")]; a=ap.parse_args()
    man=list(csv.DictReader(open(os.path.join(a.priv,"inputs/manifest_check.csv")))); assert len(man)==92 and all(r["set"]=="check" for r in man)
    ids={r["shot_id"]:r for r in man}
    fr={r["shot_id"]:(int(r["frame_start"]),int(r["frame_end"])) for r in csv.DictReader(open(os.path.join(a.priv,"inputs/shot_frames_private.csv"))) if r["shot_id"] in ids}
    assert len(fr)==92
    raw=pickle.load(open(a.dets,"rb")); dets={f:(d["box"],d["conf"],d["shape"]) for f,d in raw.items()}
    cfg=rule_v1_1.load_cfg(); res=rule_v1_1.classify_shots([(sid,ids[sid]["source_id"],*fr[sid]) for sid in ids],{"rr_balor_full":dets},cfg)
    with open(a.out,"w",newline="") as f:
        w=csv.writer(f); w.writerow(["shot_id","rule_class","why","n_sampled","F1_frac_ge2"])
        for r in res:
            ft=r["features"] or {}; w.writerow([r["shot_id"],r["rule_class"],r["why"],ft.get("n_sampled",""),repr(ft["F1_frac_ge2"]) if ft else ""])
    print(hashlib.sha256(open(a.out,"rb").read()).hexdigest(),len(res))
if __name__=="__main__": main()
