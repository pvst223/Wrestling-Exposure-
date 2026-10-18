"""V0.4 appearance embedding extraction. METHOD: MobileCLIP-B image encoder (Apple, ViT-B/16, 224x224, 512-d, contrastive image-text pretraining on
DataCompDR-1B). IT IS A GENERAL-PURPOSE IMAGE EMBEDDING, NOT A PERSON RE-IDENTIFICATION MODEL (no person-ReID weights could be obtained here).
Weights: image-tower of Ultralytics' TorchScript export 'mobileclip_blt.ts' (sha256 in docs), loaded into the vendored Apple architecture (strict key match).
Crops are cut from the candidate's own pose keypoints (no segmentation): BOX = detection box; UPPER = bbox of confident head/shoulder/hip keypoints
(needs both shoulders and >= 4 of 5 points); LOWER = bbox of confident hip..ankle keypoints (needs >= 3 of 6 including a knee). Letterboxed to 224x224 (grey pad 114).
The embedding is L2-normalised; similarity is cosine similarity -- an UNCALIBRATED heuristic similarity, not a probability. Output is cached (one-off CPU cost)."""
import sys, os, json, pickle, time, argparse
import numpy as np, cv2, torch
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "third_party"))
CT = {"box": 0, "upper": 1, "lower": 2, "mbox": 3}   # mbox = V0.5 masked box (written by embed_masked.py)
KP_CONF_CROP = 0.3; MIN_SIDE = 24; PAD = 0.15
def load_encoder(ts_path):
    from mobileclip.image_encoder import MCi
    m = MCi("vit_b16", projection_dim=512); ts = torch.jit.load(ts_path, map_location="cpu")
    r = m.load_state_dict(ts.image_encoder.state_dict(), strict=True); return m.eval()
def part_box(kp, kc, kind):
    if kind == "upper":
        ok = [i for i in (0, 1, 2, 3, 4, 5, 6, 11, 12) if kc[i] >= KP_CONF_CROP]; core = [i for i in (0, 5, 6, 11, 12) if kc[i] >= KP_CONF_CROP]
        if not (kc[5] >= KP_CONF_CROP and kc[6] >= KP_CONF_CROP and len(core) >= 4): return None
        pts = kp[[i for i in ok]]
    else:
        ok = [i for i in (11, 12, 13, 14, 15, 16) if kc[i] >= KP_CONF_CROP]
        if len(ok) < 3 or not any(i in ok for i in (13, 14)): return None
        pts = kp[ok]
    x1, y1 = pts.min(0); x2, y2 = pts.max(0); w, h = x2 - x1, y2 - y1
    return [x1 - PAD * w, y1 - PAD * h, x2 + PAD * w, y2 + PAD * h]
def crop224(im, box):
    x1, y1, x2, y2 = [int(round(v)) for v in box]; x1 = max(0, x1); y1 = max(0, y1); x2 = min(im.shape[1], x2); y2 = min(im.shape[0], y2)
    if x2 - x1 < MIN_SIDE or y2 - y1 < MIN_SIDE: return None
    c = im[y1:y2, x1:x2]; h, w = c.shape[:2]; s = max(h, w); pad = np.zeros((s, s, 3), np.uint8) + 114
    pad[(s - h) // 2:(s - h) // 2 + h, (s - w) // 2:(s - w) // 2 + w] = c
    return cv2.cvtColor(cv2.resize(pad, (224, 224), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
def crops_for(im, kp, kc, box):
    out = {"box": crop224(im, box)}
    for k in ("upper", "lower"):
        b = part_box(kp, kc, k); out[k] = None if b is None else crop224(im, b)
    return out
@torch.no_grad()
def embed_batch(enc, arrs):
    x = torch.from_numpy(np.stack(arrs)).permute(0, 3, 1, 2).float() / 255.0; e = enc(x).float(); e = e / e.norm(dim=1, keepdim=True).clamp_min(1e-12); return e.numpy()
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--video"); ap.add_argument("--dets"); ap.add_argument("--seeds"); ap.add_argument("--weights"); ap.add_argument("--out"); ap.add_argument("--cfg", default=os.path.join(os.path.dirname(HERE), "config", "config_v05.json")); ap.add_argument("--max_frames", type=int, default=None); a = ap.parse_args()
    cfg = json.load(open(a.cfg)); P = cfg["pose"]; torch.set_num_threads(2); torch.manual_seed(0)
    dets = pickle.load(open(a.dets, "rb")); sd = json.load(open(a.seeds)); enc = load_encoder(a.weights); cap = cv2.VideoCapture(a.video)
    N = len(dets) if a.max_frames is None else a.max_frames; seedset = {(s["frame"], s["det"]) for s in sd["seeds"]}
    keys = []; embs = []; pend = []; BS = 8; t0 = time.time()
    def flush():
        nonlocal pend
        if not pend: return
        e = embed_batch(enc, [p[1] for p in pend])
        for (k, _), v in zip(pend, e): keys.append(k); embs.append(v)
        pend = []
    for t in range(N):
        ok, im = cap.read()
        if not ok: break
        d = dets[t]
        for j in range(len(d["conf"])):
            b = d["box"][j]; gated = d["conf"][j] >= P["DET_CONF_GATE"] and (b[3] - b[1]) >= P["MIN_BOX_H"]
            if not (gated or (t, j) in seedset): continue
            for k, c in crops_for(im, d["kp"][j], d["kpc"][j], b).items():
                if c is not None:
                    pend.append(((t, j, CT[k]), c))
                    if len(pend) >= BS: flush()
        if t % 100 == 0: print(t, len(keys), round(time.time() - t0), "s", flush=True)
    flush(); K = np.array(keys, np.int32)
    np.savez_compressed(a.out, frame=K[:, 0], det=K[:, 1], ctype=K[:, 2], emb=np.array(embs, np.float32)); print("done", len(keys), round(time.time() - t0), "s", flush=True)
if __name__ == "__main__": main()
