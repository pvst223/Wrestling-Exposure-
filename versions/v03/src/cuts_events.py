"""V0.2 camera-event classifier. Same candidate stage as V0.1 (histogram + pixel difference) so recall of *events* is unchanged;
the NEW part is the classification of each event, based on a stated principle: a camera cut starts a NEW, STABLE shot that does not
return to the old scene, whereas a flash / exposure transient is unstable immediately after the event and the old scene returns.
  1. registered background (ORB+RANSAC inliers >= INLIER_MAX)           -> PHOTOMETRIC (same scene)         [as V0.1]
  2. post-event instability: max Bhattacharyya(H[f], H[f+1..POST]) > POST_STABILITY_MAX_BD -> TRANSIENT (not a cut)   [new]
  3. scene return: min Bhattacharyya(H[f-1], H[f+1..RETURN]) <= SCENE_RETURN_MIN_BD       -> SAME_SCENE (not a cut)    [new]
  otherwise CUT.  All thresholds are in config_v02.json and were chosen a priori, but see the report: with 24+4 labelled events the
  result is IN-SAMPLE and says nothing about other clips."""
import cv2, numpy as np, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
def _features(video, C):
    cap = cv2.VideoCapture(video); H = []; G = []; GRAY = []
    while True:
        ok, f = cap.read()
        if not ok: break
        s = cv2.resize(f, (C.THUMB_W, C.THUMB_H), interpolation=cv2.INTER_AREA)
        h = cv2.calcHist([cv2.cvtColor(s, cv2.COLOR_BGR2HSV)], [0, 1], None, [C.HIST_BINS_H, C.HIST_BINS_S], [0, 180, 0, 256]); cv2.normalize(h, h, 1, 0, cv2.NORM_L1)
        H.append(h); G.append(cv2.cvtColor(s, cv2.COLOR_BGR2GRAY).astype(np.float32)); GRAY.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY))
    return H, G, GRAY
def _inliers(orb, bf, a, b, C):
    ka, da = orb.detectAndCompute(a, None); kb, db = orb.detectAndCompute(b, None)
    if da is None or db is None or len(ka) < 10 or len(kb) < 10: return 0
    m = bf.knnMatch(da, db, k=2); g = [x[0] for x in m if len(x) == 2 and x[0].distance < C.ORB_RATIO * x[1].distance]
    if len(g) < 8: return 0
    _, mask = cv2.findHomography(np.float32([ka[x.queryIdx].pt for x in g]), np.float32([kb[x.trainIdx].pt for x in g]), cv2.RANSAC, C.RANSAC_PX)
    return int(mask.sum()) if mask is not None else 0
def detect(video, cfg=None):
    C = (cfg or config.load()).cuts; H, G, GRAY = _features(video, C); n = len(H); bd = np.zeros(n); md = np.zeros(n)
    for i in range(1, n):
        bd[i] = cv2.compareHist(H[i-1], H[i], cv2.HISTCMP_BHATTACHARYYA); md[i] = np.mean(np.abs(G[i] - G[i-1]))
    cand = [i for i in range(1, n) if bd[i] >= C.BD_THR and md[i] >= C.MD_THR]; cl = []
    for i in cand:
        if cl and i - cl[-1][-1] <= C.CLUSTER_FRAMES: cl[-1].append(i)
        else: cl.append([i])
    orb = cv2.ORB_create(C.ORB_FEATURES); bf = cv2.BFMatcher(cv2.NORM_HAMMING); events = []
    for c in cl:
        n_in = _inliers(orb, bf, GRAY[c[0]-1], GRAY[c[-1]], C)
        best = c[0] if n_in >= C.INLIER_MAX else min(c, key=lambda k: (_inliers(orb, bf, GRAY[k-1], GRAY[k], C), -bd[k]))
        f = int(best)
        post = [cv2.compareHist(H[f], H[min(f+m, n-1)], cv2.HISTCMP_BHATTACHARYYA) for m in range(1, C.POST_FRAMES + 1)]
        ret = [cv2.compareHist(H[f-1], H[min(f+m, n-1)], cv2.HISTCMP_BHATTACHARYYA) for m in range(1, C.RETURN_FRAMES + 1)]
        ps, sr = float(max(post)), float(min(ret))
        if n_in >= C.INLIER_MAX: cls = "PHOTOMETRIC_REGISTERED"
        elif ps > C.POST_STABILITY_MAX_BD: cls = "TRANSIENT_UNSTABLE_AFTER"
        elif sr <= C.SCENE_RETURN_MIN_BD: cls = "SAME_SCENE_RETURNS"
        else: cls = "CUT"
        events.append(dict(frame=f, cls=cls, cluster_inliers=int(n_in), bd=float(bd[f]), md=float(md[f]), post_stability_max_bd=round(ps, 3), scene_return_min_bd=round(sr, 3)))
    return events
if __name__ == "__main__":
    ev = detect(sys.argv[1]); json.dump(dict(events=ev, cuts=[e for e in ev if e["cls"] == "CUT"], transient_frames=[e["frame"] for e in ev if e["cls"] != "CUT"]), open(sys.argv[2], "w"), indent=1)
    print("CUTS", [e["frame"] for e in ev if e["cls"] == "CUT"]); print("NOT CUTS", [(e["frame"], e["cls"]) for e in ev if e["cls"] != "CUT"])
