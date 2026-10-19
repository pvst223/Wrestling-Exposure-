#!/usr/bin/env python3
"""Build the blind two-step review images. Reads ONLY: blind sheet (item_id, clip, frame, box), frozen dets, source video. Never reads the hidden key, rows, ownership states, identity or metrics.
step1/<id>.png : unannotated frame + crop with ONLY the assigned detection box outlined (no skeleton, no other boxes). step2/<id>.png : same layout with the frozen ASSIGNED skeleton as the frozen renderer draws it, plus small landmark index labels."""
import csv, json, os, pickle, sys
import cv2, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "impl")); sys.path.insert(0, os.path.join(HERE, "..", "anatomical", "impl"))
import render_anat
from drawn import drawn_landmarks
CYAN = (255, 255, 0)
def iou(a, b):
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]); i = max(0, x2 - x1) * max(0, y2 - y1); u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i
    return i / u if u > 0 else 0
def _compose(im, box, label):
    x1, y1, x2, y2 = [int(v) for v in box]; cv2.rectangle(im, (x1, y1), (x2, y2), CYAN, 1); H, W = im.shape[:2]; m = int(0.2 * max(x2 - x1, y2 - y1)); cx1, cy1, cx2, cy2 = max(0, x1 - m), max(0, y1 - m), min(W, x2 + m), min(H, y2 + m)
    crop = im[cy1:cy2, cx1:cx2]; s = H / crop.shape[0]; crop = cv2.resize(crop, (max(1, int(crop.shape[1] * s)), H), interpolation=cv2.INTER_CUBIC)
    canvas = np.zeros((H, W + crop.shape[1] + 4, 3), np.uint8); canvas[:, :W] = im; canvas[:, W + 4:] = crop; cv2.putText(canvas, label, (6, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA); return canvas
def render_step1(fr, box, item_id): return _compose(fr.copy(), box, item_id + " step1")
def render_step2(fr, d, box, item_id):
    j = max(range(len(d["conf"])), key=lambda k: iou(box, d["box"][k])); assert iou(box, d["box"][j]) > 0.9, (item_id, iou(box, d["box"][j]))
    im = fr.copy(); rec = dict(box=[float(v) for v in d["box"][j]], kp=d["kp"][j].tolist(), kpc=d["kpc"][j].tolist()); render_anat._skel(im, rec, CYAN, "solid")
    for i in drawn_landmarks(rec["box"], rec["kp"], rec["kpc"]):
        x, y = [int(v) for v in rec["kp"][i]]; cv2.circle(im, (x, y), 2, (0, 0, 255), -1); cv2.putText(im, str(i), (x + 3, y - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1, cv2.LINE_AA)
    return _compose(im, rec["box"], item_id + " step2")
def main(sheet, dets_dir, video_dir, out):
    os.makedirs(os.path.join(out, "step1"), exist_ok=True); os.makedirs(os.path.join(out, "step2"), exist_ok=True); rows = list(csv.DictReader(open(sheet, newline=""))); byclip = {}
    for r in rows: byclip.setdefault(r["clip"], []).append(r)
    for clip, rs in byclip.items():
        dets = pickle.load(open(os.path.join(dets_dir, f"dets_{clip}.pkl"), "rb")); need = {}
        for r in rs: need.setdefault(int(r["frame"]), []).append(r)
        cap = cv2.VideoCapture(os.path.join(video_dir, f"{clip}.mp4")); i = 0
        while need:
            ok, fr = cap.read()
            if not ok: break
            if i in need:
                for r in need[i]:
                    box = [float(x) for x in json.loads(r["box"])]
                    cv2.imwrite(os.path.join(out, "step1", f"{r['item_id']}.png"), render_step1(fr, box, r["item_id"])); cv2.imwrite(os.path.join(out, "step2", f"{r['item_id']}.png"), render_step2(fr, dets[i], box, r["item_id"]))
                del need[i]
            i += 1
    print(len(os.listdir(os.path.join(out, "step1"))), "items")
if __name__ == "__main__": main(*sys.argv[1:5])
