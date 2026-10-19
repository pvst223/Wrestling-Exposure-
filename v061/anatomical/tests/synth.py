"""Synthetic fixtures (no real footage)."""
import numpy as np
TPL = np.array([(0, -75), (-4, -80), (4, -80), (-8, -78), (8, -78), (-20, -55), (20, -55), (-28, -25), (28, -25), (-30, 5), (30, 5), (-12, -5), (12, -5), (-12, 35), (12, 35), (-12, 75), (12, 75)], float)
def skel(cx, cy=100, kc=0.9):
    kp = TPL + np.array([cx, cy]); return kp, np.full(17, kc)
def det_frame(people):
    """people: list of (cx, cy). -> pose det dict with n people."""
    kps, kcs, boxes = [], [], []
    for cx, cy in people:
        kp, kc = skel(cx, cy); kps.append(kp); kcs.append(kc); boxes.append([kp[:, 0].min() - 5, kp[:, 1].min() - 5, kp[:, 0].max() + 5, kp[:, 1].max() + 5])
    return dict(box=np.array(boxes, float).reshape(-1, 4), conf=np.full(len(people), 0.9), kp=np.array(kps).reshape(-1, 17, 2), kpc=np.array(kcs).reshape(-1, 17), shape=(200, 200))
def seg_frame(rects, H=200, W=200):
    """rects: list of (x1,y1,x2,y2) person masks."""
    ms = []
    for x1, y1, x2, y2 in rects:
        m = np.zeros((H, W), bool); m[y1:y2, x1:x2] = True; ms.append(m)
    arr = np.stack(ms) if ms else np.zeros((0, H, W), bool)
    return dict(shape=(H, W), conf=np.full(len(ms), 0.9), box=np.zeros((len(ms), 4)), mask=np.packbits(arr, axis=-1))
def person_rect(cx, cy=100, hw=30): return (int(cx - hw), int(cy - 85), int(cx + hw), int(cy + 85))
def tracklet(tid, clip, shot, dets, det_index, frames):
    return dict(tid=tid, clip=clip, shot=shot, frames=list(frames), boxes=[dets[f]["box"][det_index].tolist() for f in frames])
def decisions(tid, frames, code, g=0.9, q=0.9, extra=True):
    return [dict(tracklet=tid, frame=f, decision=code, g=g, q=q, **(dict(truth="SECRET", b0_decision="A", reason="OK") if extra else {})) for f in frames]
