"""AUDIT TOOL (not part of the measurement pipeline): contact sheet of annotated-video frames."""
import sys, cv2, numpy as np, pandas as pd
out=sys.argv[1]; frames=[int(x) for x in sys.argv[2:]]
cap=cv2.VideoCapture("out/annotated.mp4"); tiles=[]
for f in frames:
    cap.set(cv2.CAP_PROP_POS_FRAMES,f); ok,im=cap.read(); im=cv2.resize(im,(520,292)); cv2.rectangle(im,(0,280),(60,292),(0,0,0),-1)
    cv2.putText(im,f"#{f}",(2,290),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,255,255),1); tiles.append(im)
while len(tiles)%3: tiles.append(np.zeros_like(tiles[0]))
cv2.imwrite(out,np.vstack([np.hstack(tiles[i:i+3]) for i in range(0,len(tiles),3)]))
