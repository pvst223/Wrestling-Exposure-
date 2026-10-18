"""Camera-cut detection (3 stages). Frame index is 0-based; cut index k = first frame of the new shot.
 1. candidate: HSV-hist Bhattacharyya >= 0.22 AND downscaled mean-abs-diff >= 25; candidates within 4 frames are one event.
 2. geometric verification: ORB + RANSAC homography across the event. If background still registers
    (inliers >= INLIER_MAX) it is a photometric event (flash/dissolve, same scene) and NOT a cut.
 3. cut frame = pair with fewest inliers inside the cluster."""
import cv2, numpy as np, json, sys
BD_THR, MD_THR, INLIER_MAX = 0.22, 25.0, 60
def features(video):
    cap=cv2.VideoCapture(video); H=[]; G=[]; GRAY=[]
    while True:
        ok,f=cap.read()
        if not ok: break
        s=cv2.resize(f,(160,90),interpolation=cv2.INTER_AREA)
        h=cv2.calcHist([cv2.cvtColor(s,cv2.COLOR_BGR2HSV)],[0,1],None,[16,8],[0,180,0,256]); cv2.normalize(h,h,1,0,cv2.NORM_L1)
        H.append(h); G.append(cv2.cvtColor(s,cv2.COLOR_BGR2GRAY).astype(np.float32)); GRAY.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY))
    return H,G,GRAY
def inliers(orb,bf,a,b):
    ka,da=orb.detectAndCompute(a,None); kb,db=orb.detectAndCompute(b,None)
    if da is None or db is None or len(ka)<10 or len(kb)<10: return 0
    m=bf.knnMatch(da,db,k=2); g=[x[0] for x in m if len(x)==2 and x[0].distance<0.75*x[1].distance]
    if len(g)<8: return 0
    _,mask=cv2.findHomography(np.float32([ka[x.queryIdx].pt for x in g]),np.float32([kb[x.trainIdx].pt for x in g]),cv2.RANSAC,4.0)
    return int(mask.sum()) if mask is not None else 0
def detect(video):
    H,G,GRAY=features(video); n=len(H); bd=np.zeros(n); md=np.zeros(n)
    for i in range(1,n):
        bd[i]=cv2.compareHist(H[i-1],H[i],cv2.HISTCMP_BHATTACHARYYA); md[i]=np.mean(np.abs(G[i]-G[i-1]))
    cand=[i for i in range(1,n) if bd[i]>=BD_THR and md[i]>=MD_THR]; cl=[]
    for i in cand:
        if cl and i-cl[-1][-1]<=4: cl[-1].append(i)
        else: cl.append([i])
    orb=cv2.ORB_create(1500); bf=cv2.BFMatcher(cv2.NORM_HAMMING); cuts=[]; photo=[]
    for c in cl:
        n_in=inliers(orb,bf,GRAY[c[0]-1],GRAY[c[-1]])
        if n_in>=INLIER_MAX: photo.append(dict(frame=c[0],inliers=n_in)); continue
        best=min(c,key=lambda k:(inliers(orb,bf,GRAY[k-1],GRAY[k]),-bd[k]))
        cuts.append(dict(frame=int(best),inliers=n_in,bd=float(bd[best]),md=float(md[best])))
    return cuts,photo
if __name__=="__main__":
    cuts,photo=detect(sys.argv[1]); json.dump(dict(cuts=cuts,photometric_events=photo),open(sys.argv[2],"w"),indent=1)
    print("CUTS",[c['frame'] for c in cuts]); print("PHOTOMETRIC",[p['frame'] for p in photo])
