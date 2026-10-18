import sys, pickle, cv2, numpy as np
sys.path.insert(0,"src")
dets=pickle.load(open("out/raw_detections.pkl","rb")); cap=cv2.VideoCapture("input.mp4")
frames=[int(x) for x in sys.argv[2:]]; tiles=[]
for fi in frames:
    cap.set(cv2.CAP_PROP_POS_FRAMES,fi); ok,im=cap.read(); d=dets[fi]
    im=cv2.resize(im,(960,540)); s=1.5
    for j,(b,c,k,kc) in enumerate(zip(d["box"],d["conf"],d["kp"],d["kpc"])):
        if c<0.3: continue
        x1,y1,x2,y2=(b*s).astype(int); cv2.rectangle(im,(x1,y1),(x2,y2),(0,255,0),2)
        cv2.putText(im,f"#{j} {c:.2f}",(x1,max(15,y1-4)),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,255),2)
        for p,q in zip(k,kc):
            if q>0.5: cv2.circle(im,tuple((p*s).astype(int)),3,(255,0,255),-1)
    cv2.putText(im,f"frame {fi}",(8,24),cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,255),2); tiles.append(im)
while len(tiles)%2: tiles.append(np.zeros_like(tiles[0]))
cv2.imwrite(sys.argv[1],np.vstack([np.hstack(tiles[i:i+2]) for i in range(0,len(tiles),2)]))
