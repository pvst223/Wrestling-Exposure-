"""V0.5 stage: per-person instance segmentation (YOLOv8m-seg, COCO 'person') on every frame, cached.
Masks stored at 320x180, bit-packed. General-purpose COCO model; NOT wrestling-trained."""
import sys, os, pickle, time, cv2, numpy as np
from ultralytics import YOLO
VIDEO, OUT, WEIGHTS = sys.argv[1], sys.argv[2], sys.argv[3]
IMGSZ, CONF = 960, 0.10
MW, MH = 320, 180
res = pickle.load(open(OUT, "rb")) if os.path.exists(OUT) else []
model = YOLO(WEIGHTS); cap = cv2.VideoCapture(VIDEO); i = 0; t0 = time.time()
while True:
    ok, frame = cap.read()
    if not ok: break
    if i < len(res): i += 1; continue
    r = model.predict(frame, imgsz=IMGSZ, conf=CONF, classes=[0], verbose=False, device="cpu")[0]
    if r.masks is not None and len(r.boxes):
        m = r.masks.data.numpy()
        ms = np.stack([cv2.resize((x > 0.5).astype(np.uint8), (MW, MH), interpolation=cv2.INTER_NEAREST) for x in m])
        d = dict(box=r.boxes.xyxy.numpy().astype(np.float32), conf=r.boxes.conf.numpy().astype(np.float32), mask=np.packbits(ms, axis=-1), shape=(MH, MW))
    else:
        d = dict(box=np.zeros((0, 4), np.float32), conf=np.zeros(0, np.float32), mask=np.zeros((0, MH, MW // 8), np.uint8), shape=(MH, MW))
    res.append(d); i += 1
    if i % 50 == 0:
        pickle.dump(res, open(OUT + ".tmp", "wb")); os.replace(OUT + ".tmp", OUT)
        print(i, round(time.time() - t0), "s", flush=True)
pickle.dump(res, open(OUT, "wb")); print("DONE", len(res), flush=True)
