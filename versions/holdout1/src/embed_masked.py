"""V0.5 masked-box embedding: the detection-box crop with every pixel OUTSIDE the candidate's owner person-mask (dilated by MASK_TOL_PX) replaced by grey 114, embedded with the same
MobileCLIP-B image encoder as V0.4 (general-purpose image embedding, NOT person-ReID; cosine similarity is an uncalibrated heuristic, not a probability). Purpose: identity evidence that
excludes the opponent's and the background's pixels when the segmenter separates them. Written to cache as crop type 3 ('mbox'). Candidate set = V0.4's (gated detections + seed detections).
The owner mask is chosen by ownership_v05.owner_for (pose-landmark coverage; decision-free)."""
import sys, os, json, pickle, time, argparse
import numpy as np, cv2, torch
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "third_party"))
import embed_crops as EC, ownership_v05 as OW
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--video"); ap.add_argument("--dets"); ap.add_argument("--seg"); ap.add_argument("--seeds"); ap.add_argument("--weights"); ap.add_argument("--out"); ap.add_argument("--cfg", default=os.path.join(os.path.dirname(HERE), "config", "config_v05.json")); ap.add_argument("--max_frames", type=int, default=None); a = ap.parse_args()
    cfg = json.load(open(a.cfg)); P = cfg["pose"]; C = type("C", (), cfg["ownership"]); SG = cfg["seg"]; torch.set_num_threads(2); torch.manual_seed(0)
    dets = pickle.load(open(a.dets, "rb")); seg = pickle.load(open(a.seg, "rb")); sd = json.load(open(a.seeds)); enc = EC.load_encoder(a.weights); cap = cv2.VideoCapture(a.video)
    W = int(cap.get(3)); H = int(cap.get(4)); N = len(dets) if a.max_frames is None else a.max_frames; seedset = {(s["frame"], s["det"]) for s in sd["seeds"]}
    keys = []; embs = []; pend = []; BS = 8; t0 = time.time(); nomask = 0
    def flush():
        nonlocal pend
        if not pend: return
        e = EC.embed_batch(enc, [p[1] for p in pend])
        for (k, _), v in zip(pend, e): keys.append(k); embs.append(v)
        pend = []
    for t in range(N):
        ok, im = cap.read()
        if not ok: break
        d = dets[t]; fs = OW.FrameSeg(seg[t], W, H, SG["SEG_CONF_MIN"])
        for j in range(len(d["conf"])):
            b = d["box"][j]; gated = d["conf"][j] >= P["DET_CONF_GATE"] and (b[3] - b[1]) >= P["MIN_BOX_H"]
            if not (gated or (t, j) in seedset): continue
            own, cov = OW.owner_for(fs, d["kp"][j], d["kpc"][j], P["KP_CONF"], C)
            if own is None: nomask += 1; continue
            m = OW.owner_mask_fullres(fs, own, C); im2 = im.copy(); im2[~m] = 114; c = EC.crop224(im2, b)
            if c is not None:
                pend.append(((t, j, EC.CT["mbox"]), c))
                if len(pend) >= BS: flush()
        if t % 100 == 0: print(t, len(keys), round(time.time() - t0), "s", flush=True)
    flush(); K = np.array(keys, np.int32)
    np.savez_compressed(a.out, frame=K[:, 0], det=K[:, 1], ctype=K[:, 2], emb=np.array(embs, np.float32)); print("done", len(keys), "no_owner_mask", nomask, round(time.time() - t0), "s", flush=True)
if __name__ == "__main__": main()
