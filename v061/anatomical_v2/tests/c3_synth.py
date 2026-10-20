"""Synthetic fixtures for C3 tests (no real footage). Two or more people, per-frame images with solid clothing colours, masks, and V1 rows produced by the FROZEN V1 pipeline."""
import os, sys
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); V2 = os.path.dirname(HERE)
sys.path[:0] = [os.path.join(V2, "impl"), os.path.join(V2, "..", "anatomical", "impl"), os.path.join(V2, "..", "anatomical", "tests")]
import pipeline, ownership_stage, synth
import c3_scene; APP = c3_scene.APP
TPL = synth.TPL * np.array([0.7, 1.0])
RED, BLUE, GREEN = (0, 0, 200), (200, 0, 0), (0, 200, 0)
def skel(cx, cy=100, flip=False, kc=0.9):
    t = TPL.copy()
    if flip: t[:, 0] = -t[:, 0]
    return t + np.array([cx, cy]), np.full(17, kc)
def build(timeline, colors, tr_ids, masks="distinct", W=200, H=200, cfg=None, same_cut=(), kc=0.9, mask_hw=24, pix=None, born=None, shots=None):
    """timeline: list over pose frames t of list of (cx, flip, color_idx_or_None) per person (order = person index, may include extra untracked persons at the end).
    colors: list of BGR. tr_ids: tracklet id per person (None = untracked). masks: 'distinct' (one rect per person) | 'merged' (one rect covering all) | 'none'.
    pix: optional {t: [person colour override indices]} for pixel swaps. Returns dict(rows, dets, seg, frame_q, tracklets, frames)."""
    dets, seg, qs, frames = {}, {}, {}, []
    A = ownership_stage.load_cfg().appearance
    for t, people in enumerate(timeline):
        f = 3 * t; frames.append(f); kps, kcs, boxes = [], [], []
        for cx, flip, ci in people:
            kp, kcc = skel(cx, flip=flip, kc=kc); kps.append(kp); kcs.append(kcc); boxes.append([kp[:, 0].min() - 5, kp[:, 1].min() - 5, kp[:, 0].max() + 5, kp[:, 1].max() + 5])
        dets[f] = dict(box=np.array(boxes, float).reshape(-1, 4), conf=np.full(len(people), 0.9), kp=np.array(kps).reshape(-1, 17, 2), kpc=np.array(kcs).reshape(-1, 17), shape=(H, W))
        img = np.full((H, W, 3), 128, np.uint8)
        for cx, flip, ci in people:
            if ci is not None: cv2.rectangle(img, (int(cx - mask_hw), 15), (int(cx + mask_hw), 185), colors[ci], -1)
        qs[f] = APP.quantize(img, A)
        rects = [(int(cx - mask_hw), 15, int(cx + mask_hw), 185) for cx, _, _ in people]
        if masks == "distinct": seg[f] = synth.seg_frame(rects, H, W)
        elif masks == "merged": seg[f] = synth.seg_frame([(min(r[0] for r in rects), 15, max(r[2] for r in rects), 185)], H, W)
    trs, dec = [], []
    for i, tid in enumerate(tr_ids):
        if tid is None: continue
        fr = [3 * t for t, p in enumerate(timeline) if len(p) > i and p[i] is not None and t >= (born or {}).get(tid, 0)]
        trs.append(dict(tid=tid, clip="c", shot=(shots or {}).get(tid, 0), frames=fr, boxes=[dets[f]["box"][i].tolist() for f in fr]))
        dec += [dict(tracklet=tid, frame=f, decision=("ACCEPT_A" if i % 2 == 0 else "ACCEPT_B"), g=0.9, q=(0.9 if i % 2 == 0 else 0.1)) for f in fr]
    rows, src = pipeline.run_clip(trs, dets, dec, seg, list(same_cut), W, H)
    return dict(rows=rows, src=src, dets=dets, seg=seg, frame_q=(lambda f: qs.get(f)), tracklets=trs, frames=frames, W=W, H=H, cuts=list(same_cut))
def scene_of(b, with_pixels=True):
    from c3_scene import Scene
    return Scene(b["rows"], b["dets"], b["seg"], b["W"], b["H"], frame_q=b["frame_q"] if with_pixels else None)
def standard(sep_flips=(False, True, False, True, False, True), n_contact=4, n_post=2, a_color=0, b_color=1, masks="distinct", cx_contact=(60, 111), cx_sep=(40, 160)):
    """separated approach (alternating Facing so anchors exist), touching contact, separated exit."""
    tl = []
    for fl in sep_flips: tl.append([(cx_sep[0], fl, a_color), (cx_sep[1], fl, b_color)])
    for _ in range(n_contact): tl.append([(cx_contact[0], False, a_color), (cx_contact[1], False, b_color)])
    for _ in range(n_post): tl.append([(cx_sep[0], False, a_color), (cx_sep[1], False, b_color)])
    return tl
