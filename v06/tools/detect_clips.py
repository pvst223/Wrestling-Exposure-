"""Vision-module run for unit measurement (NO identity model). Pose detection (pinned YOLOv8m-pose) at fixed stride on normalized clips; resumable per clip; stops at metadata exclusion frame.
Usage: detect_clips.py NORM_DIR OUT_DIR WEIGHTS CLIP_ID [CLIP_ID...]"""
import sys,os,pickle,time,cv2,numpy as np
from ultralytics import YOLO
NORM,OUT,W=sys.argv[1:4]; clips=sys.argv[4:]; STRIDE=3; LIMIT={"b2_videoplayback_2":1934}
os.makedirs(OUT,exist_ok=True); model=YOLO(W)
for c in clips:
    out=os.path.join(OUT,f"dets_{c}.pkl"); res=pickle.load(open(out,"rb")) if os.path.exists(out) else {}
    cap=cv2.VideoCapture(os.path.join(NORM,c+".mp4")); n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); lim=min(n,LIMIT.get(c,n)); t0=time.time(); i=0
    while i<lim:
        ok,im=cap.read()
        if not ok: break
        if i%STRIDE==0 and i not in res:
            r=model.predict(im,imgsz=960,conf=0.10,verbose=False,device="cpu")[0]
            res[i]=dict(box=r.boxes.xyxy.numpy().astype(np.float32),conf=r.boxes.conf.numpy().astype(np.float32),kp=r.keypoints.xy.numpy().astype(np.float32),kpc=r.keypoints.conf.numpy().astype(np.float32),shape=im.shape[:2]) if len(r.boxes) else dict(box=np.zeros((0,4),np.float32),conf=np.zeros(0,np.float32),kp=np.zeros((0,17,2),np.float32),kpc=np.zeros((0,17),np.float32),shape=im.shape[:2])
            if len(res)%50==0: pickle.dump(res,open(out+".tmp","wb")); os.replace(out+".tmp",out); print(c,i,lim,round(time.time()-t0),"s",flush=True)
        i+=1
    pickle.dump(dict(res) ,open(out,"wb")); print("DONE",c,len(res),"processed frames",flush=True)
