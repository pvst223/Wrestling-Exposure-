"""Thin P5 driver: frozen extract_features functions (mobileclip_b, frozen crop rule) applied to the fresh clip's retained-tracklet detections (frozen extraction_rows). No new logic.
Usage: p5_features.py --clip C --video NORM.mp4 --dets DETS.pkl --tracklets T.json --weights W --out_dir D [--sanity_dev_clip CLIP --dev_video V --dev_dets P --dev_frozen F --dev_feat_dir D]"""
import os, sys, json, csv, glob, pickle, argparse, hashlib
import numpy as np
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "v06", "tools"))
import torch, extract_features as XF, phase1_structure as PS
def main():
    ap = argparse.ArgumentParser(); [ap.add_argument(f"--{x}") for x in ("clip", "video", "dets", "tracklets", "weights", "out_dir", "sanity_n")]
    ap.add_argument("--sanity", nargs=5, default=None, help="dev_clip dev_video dev_dets dev_frozen_dir dev_feat_dir")
    a = ap.parse_args(); torch.set_num_threads(os.cpu_count() or 2); torch.manual_seed(0); m = XF.load_backbone("mobileclip_b", a.weights)
    if a.sanity:
        dc, dv, dd, df, dfd = a.sanity; rows = XF.manifest_rows(os.path.join(df, "EXTRACTION_FRAME_MANIFEST_V1.csv"))[dc]; dets = pickle.load(open(dd, "rb"))
        n = int(a.sanity_n or 40); first_frames = sorted({r[0] for r in rows})[:12]; sub = [r for r in rows if r[0] in set(first_frames)][:n]
        K, E = XF.extract_clip(dv, dets, sub, m, "mobileclip_b"); z = np.load(glob.glob(os.path.join(dfd, f"feat_mobileclip_b_{dc}_*.npz"))[0]); idx = {(int(f), int(d)): i for i, (f, d) in enumerate(zip(z["frame"], z["det"]))}
        same = all(np.array_equal(E[i], z["emb"][idx[(int(f), int(d))]]) for i, (f, d) in enumerate(K)); print("SANITY dev re-embed bitwise equal:", same, "n", len(K)); json.dump(dict(sanity_bitwise_equal=bool(same), n=len(K)), open(os.path.join(a.out_dir, "FEATURE_SANITY.json"), "w"))
        if not same: sys.exit(2)
        return
    T = json.load(open(a.tracklets)); dets = pickle.load(open(a.dets, "rb")); keys, rows = PS.extraction_rows(a.clip, dets, T)
    man = os.path.join(a.out_dir, f"EXTRACTION_MANIFEST_{a.clip}.csv"); os.makedirs(a.out_dir, exist_ok=True)
    w = csv.DictWriter(open(man, "w", newline=""), fieldnames=["clip", "frame", "det", "tid", "box_h", "crop_ok"]); w.writeheader(); w.writerows(rows)
    r2 = [(int(r["frame"]), int(r["det"]), r["tid"], int(r["crop_ok"])) for r in rows]; r2.sort(key=lambda x: (x[0], x[1]))
    K, E = XF.extract_clip(a.video, dets, r2, m, "mobileclip_b"); out = os.path.join(a.out_dir, f"feat_mobileclip_b_{a.clip}.npz")
    np.savez_compressed(out, frame=K[:, 0], det=K[:, 1], emb=E, meta=json.dumps(dict(video_sha=XF.sha(a.video), backbone="mobileclip_b", weights_sha=XF.sha(a.weights), manifest_sha=XF.sha(man), crop=XF.CROP)))
    print("wrote", out, len(K), "crops of", len(rows), "rows")
if __name__ == "__main__": main()
