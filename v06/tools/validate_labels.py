"""Tracklet label schema validator. Labels CSV columns:
clip_id,tracklet_id,frame_start,frame_end,person_class,wrestler_id,gear_episode_id,visibility,viewpoint,body_state,scale_bucket,overlap_flag,n_people_in_box,clothing_change_flag,annotator,label_source,label_version,independent
person_class in WRESTLER|REFEREE|RINGSIDE_STAFF|SPECTATOR|OTHER|UNLABELABLE ; WRESTLER rows need wrestler_id; independent in {0,1} (developer first-pass = 0).
Fails on schema/enum errors, WRESTLER without id, non-WRESTLER with id, frame_end<frame_start, duplicate (clip,tracklet,annotator)."""
import csv,sys,collections
ENUM=dict(person_class={"WRESTLER","REFEREE","RINGSIDE_STAFF","SPECTATOR","OTHER","UNLABELABLE"},visibility={"clear","partial","occluded","blurred"},viewpoint={"front","back","side","above","ground","unknown"},
 body_state={"upright","grounded","aerial","grappled","unknown"},scale_bucket={"small","medium","large"},independent={"0","1"})
COLS="clip_id,tracklet_id,frame_start,frame_end,person_class,wrestler_id,gear_episode_id,visibility,viewpoint,body_state,scale_bucket,overlap_flag,n_people_in_box,clothing_change_flag,annotator,label_source,label_version,independent".split(",")
def validate(p):
    rows=list(csv.DictReader(open(p))); err=[]
    if rows and set(COLS)-set(rows[0]): err.append(("missing_columns",sorted(set(COLS)-set(rows[0]))))
    seen=set()
    for i,r in enumerate(rows,2):
        for k,v in ENUM.items():
            if r.get(k) not in v: err.append((i,k,r.get(k)))
        if r.get("person_class")=="WRESTLER" and not r.get("wrestler_id"): err.append((i,"wrestler_id missing"))
        if r.get("person_class")!="WRESTLER" and r.get("wrestler_id"): err.append((i,"wrestler_id on non-wrestler"))
        try:
            if int(r["frame_end"])<int(r["frame_start"]): err.append((i,"frame_end<frame_start"))
        except Exception: err.append((i,"bad frame numbers"))
        k=(r.get("clip_id"),r.get("tracklet_id"),r.get("annotator"))
        if k in seen: err.append((i,"duplicate",k))
        seen.add(k)
    return err
if __name__=="__main__":
    e=validate(sys.argv[1]); print("OK" if not e else e); sys.exit(1 if e else 0)
