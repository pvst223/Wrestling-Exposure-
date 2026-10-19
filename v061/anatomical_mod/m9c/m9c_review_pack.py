#!/usr/bin/env python3
"""Build the blind M9C review images. Reads ONLY: a blind sheet (review_id, clip, tracklet, frame, box, draw_landmarks), frozen pose dets, source video. Never reads a key, ROWS pickles or metrics.
Same layout as the M9/M9B pack. Items with a draw_landmarks list (released frames) show ONLY those landmarks and the bones whose endpoints are both listed (neutral solid style); other items show the full skeleton exactly as in M9."""
import csv, json, os, pickle, sys
import cv2, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); V = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [os.path.join(V, "anatomical", "impl"), os.path.join(V, "anatomical_mod", "impl")]
import render_anat, partial_render, ownership_stage
CYAN = (255, 255, 0)
def iou(a, b):
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]); i = max(0, x2 - x1) * max(0, y2 - y1); u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i
    return i / u if u > 0 else 0
def render_item(fr, d, box, draw_landmarks, review_id):
    j = max(range(len(d["conf"])), key=lambda k: iou(box, d["box"][k])); assert iou(box, d["box"][j]) > 0.9, (review_id, iou(box, d["box"][j]))
    im = fr.copy()
    for k in range(len(d["conf"])):
        if k != j: x1, y1, x2, y2 = [int(v) for v in d["box"][k]]; cv2.rectangle(im, (x1, y1), (x2, y2), (130, 130, 130), 1)
    rec = dict(box=[float(v) for v in d["box"][j]], kp=d["kp"][j].tolist(), kpc=d["kpc"][j].tolist())
    if draw_landmarks is None: render_anat._skel(im, rec, CYAN, "solid")
    else:
        own = ownership_stage._mods()[0]; s = set(int(i) for i in draw_landmarks); rec.update(released_landmarks=sorted(s), released_bones=[list(b) for b in own.BONES if b[0] in s and b[1] in s], record_class="RELEASED_PARTIAL_ANATOMY_A")
        partial_render.draw_partial(im, rec, style="neutral")
    x1, y1, x2, y2 = [int(v) for v in d["box"][j]]; cv2.rectangle(im, (x1, y1), (x2, y2), CYAN, 1)
    H, W = im.shape[:2]; m = int(0.2 * max(x2 - x1, y2 - y1)); cx1, cy1, cx2, cy2 = max(0, x1 - m), max(0, y1 - m), min(W, x2 + m), min(H, y2 + m); crop = im[cy1:cy2, cx1:cx2]
    s = H / crop.shape[0]; crop = cv2.resize(crop, (max(1, int(crop.shape[1] * s)), H), interpolation=cv2.INTER_CUBIC)
    canvas = np.zeros((H, W + crop.shape[1] + 4, 3), np.uint8); canvas[:, :W] = im; canvas[:, W + 4:] = crop
    cv2.putText(canvas, review_id, (6, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA); return canvas
def main(sheet, frozen, out):
    os.makedirs(out, exist_ok=True); rows = list(csv.DictReader(open(sheet, newline=""))); byclip = {}
    for r in rows: byclip.setdefault(r["clip"], []).append(r)
    for clip, rs in byclip.items():
        dets = pickle.load(open(os.path.join(frozen, "dets", f"dets_{clip}.pkl"), "rb")); need = {}
        for r in rs: need.setdefault(int(r["frame"]), []).append(r)
        cap = cv2.VideoCapture(os.path.join(frozen, "norm", f"{clip}.mp4")); i = 0
        while need:
            ok, fr = cap.read()
            if not ok: break
            if i in need:
                for r in need[i]:
                    box = [float(x) for x in json.loads(r["box"])]; dl = json.loads(r["draw_landmarks"]) if r.get("draw_landmarks") else None
                    cv2.imwrite(os.path.join(out, f"{r['review_id']}.png"), render_item(fr, dets[i], box, dl, r["review_id"]))
                del need[i]
            i += 1
    print(len(os.listdir(out)), "images")
if __name__ == "__main__": main(*sys.argv[1:4])
