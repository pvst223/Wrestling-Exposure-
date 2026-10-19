"""PROPOSED wrapper (new, NOT executed) that applies the UNCHANGED V0.5 segmentation settings of reused_v05/src/seg_extract.py (IMGSZ=960, CONF=0.10, classes=[0], cpu, masks 320x180 nearest, bit-packed)
only to the pose-evaluation frames (stride-3 frames present in the frozen pose detections). Output is keyed by SOURCE FRAME INDEX (dict), unlike the original's per-frame list.
Option F (reviewer choice): run the original script unchanged on every frame and index the list. This wrapper exists only to cut CPU time ~3x; the mask-packing function below is test-pinned to the original's expression."""
import numpy as np
IMGSZ, CONF, MW, MH = 960, 0.10, 320, 180
def pack(boxes_xyxy, conf, masks_data):
    """Identical to the inline block in seg_extract.py. masks_data: (n,h,w) float array (ultralytics r.masks.data.numpy())."""
    import cv2
    if masks_data is not None and len(boxes_xyxy):
        ms = np.stack([cv2.resize((x > 0.5).astype(np.uint8), (MW, MH), interpolation=cv2.INTER_NEAREST) for x in masks_data])
        return dict(box=np.asarray(boxes_xyxy).astype(np.float32), conf=np.asarray(conf).astype(np.float32), mask=np.packbits(ms, axis=-1), shape=(MH, MW))
    return dict(box=np.zeros((0, 4), np.float32), conf=np.zeros(0, np.float32), mask=np.zeros((0, MH, MW // 8), np.uint8), shape=(MH, MW))
def extract(video, frames, weights):
    import cv2
    from ultralytics import YOLO
    want = set(int(f) for f in frames); model = YOLO(weights); cap = cv2.VideoCapture(video); i = 0; out = {}
    while True:
        ok, frame = cap.read()
        if not ok: break
        if i in want:
            r = model.predict(frame, imgsz=IMGSZ, conf=CONF, classes=[0], verbose=False, device="cpu")[0]
            out[i] = pack(r.boxes.xyxy.numpy(), r.boxes.conf.numpy(), r.masks.data.numpy() if r.masks is not None else None) if len(r.boxes) else pack(np.zeros((0, 4)), np.zeros(0), None)
        i += 1
    return out
