"""Contact sheets for first-pass tracklet labelling. One tile per tracklet: the full (360p) frame at the tracklet's middle detection with its box drawn and its id; 6x6 tiles per sheet; ordered by clip, shot.
No automated identity, status or score is shown (none exists at this stage)."""
import sys,json,cv2,numpy as np,os
clip=sys.argv[1]; T=json.load(open(f"frozen/tracklets/{clip}.json")); cap=cv2.VideoCapture(f"frozen/norm/{clip}.mp4"); os.makedirs("frozen/sheets",exist_ok=True)
TW,TH=320,180; COLS=6; ROWS=6; tiles=[]
for k,t in enumerate(T):
    m=len(t["frames"])//2; f=t["frames"][m]; cap.set(1,f); ok,im=cap.read()
    if not ok: continue
    b=[int(x) for x in t["boxes"][m]]; sc=min(TW/im.shape[1],TH/im.shape[0]); im=cv2.resize(im,(int(im.shape[1]*sc),int(im.shape[0]*sc))); b=[int(x*sc) for x in b]
    cv2.rectangle(im,(b[0],b[1]),(b[2],b[3]),(0,255,0),2)
    canvas=np.zeros((TH,TW,3),np.uint8); canvas[:im.shape[0],:im.shape[1]]=im
    cv2.rectangle(canvas,(0,0),(150,16),(0,0,0),-1); cv2.putText(canvas,f"#{k} s{t['shot']} n{t['n_det']}",(2,12),cv2.FONT_HERSHEY_SIMPLEX,0.45,(255,255,255),1)
    tiles.append(canvas)
per=COLS*ROWS; n=0
for i in range(0,len(tiles),per):
    chunk=tiles[i:i+per]; sheet=np.zeros((ROWS*TH,COLS*TW,3),np.uint8)
    for j,c in enumerate(chunk): r,cc=divmod(j,COLS); sheet[r*TH:(r+1)*TH,cc*TW:(cc+1)*TW]=c
    cv2.imwrite(f"frozen/sheets/{clip}_sheet{n:02d}.jpg",sheet,[cv2.IMWRITE_JPEG_QUALITY,88]); n+=1
print(clip,len(tiles),"tracklets",n,"sheets")
