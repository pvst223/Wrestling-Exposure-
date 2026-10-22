"""ONE diagnostic CHECK overlay video (private, local only; NEVER commit its output). Diagnostic only; must not be used to tune Rule V1.1.
Overlay: frozen shot id, owner reference category, Rule V1.1 class, F1, rule reason, disagreement marker, reference-UNKNOWN status. No identity/anatomy/ownership/COM/distance/workload overlay.
Usage: diagnostic_mp4.py --norm match_check_norm.mp4 --first_frame 13546 --frames shot_frames_private.csv --labels labels_check.csv --pred check_predictions_private.csv --out OUT.mp4"""
import argparse,csv,cv2,subprocess,os
def main():
    ap=argparse.ArgumentParser(); [ap.add_argument("--"+k,required=True) for k in ("norm","frames","labels","pred","out")]; ap.add_argument("--first_frame",type=int,required=True); a=ap.parse_args()
    lab={r["shot_id"]:r for r in csv.DictReader(open(a.labels))}; pred={r["shot_id"]:r for r in csv.DictReader(open(a.pred))}
    fr=sorted((int(r["frame_start"]),int(r["frame_end"]),r["shot_id"]) for r in csv.DictReader(open(a.frames)) if r["shot_id"] in lab)
    cap=cv2.VideoCapture(a.norm); w=int(cap.get(3)); h=int(cap.get(4)); tmp=a.out+".tmp.mp4"
    vw=cv2.VideoWriter(tmp,cv2.VideoWriter_fourcc(*"mp4v"),30,(w,h)); i=0; F=cv2.FONT_HERSHEY_SIMPLEX
    for fs,fe,sid in fr:
        L=lab[sid]["label"]; P=pred[sid]; rc=P["rule_class"]; unk=L=="UNKNOWN"
        dis=(not unk) and ((rc=="LIVE")!=(L=="LIVE_ACTION"))
        f1=("%.2f"%float(P["F1_frac_ge2"])) if P["F1_frac_ge2"] else "n/a"
        col=(0,0,255) if dis else ((0,200,255) if unk else (0,200,0))
        for f in range(fs,fe):
            idx=f-a.first_frame
            if idx<0: continue
            cap.set(cv2.CAP_PROP_POS_FRAMES,idx); ok,im=cap.read()
            if not ok: break
            cv2.rectangle(im,(0,0),(w,58),(0,0,0),-1)
            cv2.putText(im,f"{sid}  REF: {L}"+(" ("+lab[sid]["unknown_reason"]+")" if unk else ""),(6,16),F,0.45,(255,255,255),1)
            cv2.putText(im,f"RULE V1.1: {rc}   F1={f1}   why={P['why']}",(6,34),F,0.45,(255,255,255),1)
            cv2.putText(im,"REF-UNKNOWN (excluded)" if unk else ("DISAGREE" if dis else "agree"),(6,52),F,0.5,col,2)
            cv2.rectangle(im,(0,0),(w-1,h-1),col,3)
            vw.write(im)
    vw.release()
    subprocess.run(["ffmpeg","-y","-v","error","-i",tmp,"-c:v","libx264","-pix_fmt","yuv420p","-crf","23","-an",a.out],check=True); os.remove(tmp)
if __name__=="__main__": main()
