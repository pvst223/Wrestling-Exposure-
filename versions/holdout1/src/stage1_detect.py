"""Stage 1: multi-person 2D pose (YOLOv8m-pose, COCO-17) on every frame, cached to disk. Resumable."""
import sys, os, pickle, time, cv2, numpy as np
from ultralytics import YOLO
VIDEO, OUT, WEIGHTS = sys.argv[1], sys.argv[2], sys.argv[3]
IMGSZ, CONF = 960, 0.10
dets = pickle.load(open(OUT, "rb")) if os.path.exists(OUT) else []
model = YOLO(WEIGHTS); cap = cv2.VideoCapture(VIDEO); i = 0; t0 = time.time()
while True:
    ok, frame = cap.read()
    if not ok: break
    if i < len(dets): i += 1; continue
    r = model.predict(frame, imgsz=IMGSZ, conf=CONF, verbose=False, device="cpu")[0]
    if len(r.boxes):
        d = dict(box=r.boxes.xyxy.numpy().astype(np.float32), conf=r.boxes.conf.numpy().astype(np.float32),
                 kp=r.keypoints.xy.numpy().astype(np.float32), kpc=r.keypoints.conf.numpy().astype(np.float32))
    else:
        d = dict(box=np.zeros((0,4),np.float32), conf=np.zeros(0,np.float32), kp=np.zeros((0,17,2),np.float32), kpc=np.zeros((0,17),np.float32))
    dets.append(d); i += 1
    if i % 50 == 0:
        pickle.dump(dets, open(OUT + ".tmp", "wb")); os.replace(OUT + ".tmp", OUT)
        print(i, round(time.time()-t0), "s", flush=True)
pickle.dump(dets, open(OUT, "wb")); print("DONE", len(dets), flush=True)
