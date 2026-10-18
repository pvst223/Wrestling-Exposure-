"""Clip ingestion + provenance record. Usage: ingest_clip.py CLIP.mp4 --meta META_ROW.json --out_dir DIR
Writes DIR/<clip_id>/provenance.json (sha256, ffprobe properties, metadata, rights status, retention policy). Does NOT copy or publish footage; does NOT run models.
Required meta keys: clip_id, source_description, source_url_or_origin, access_date, promotion_id, match_id, event_name, wrestler_A, wrestler_B, is_replay, rights_status (default UNRESOLVED), notes."""
import sys,json,hashlib,subprocess,os,argparse,datetime
REQ=["clip_id","source_description","source_url_or_origin","access_date","promotion_id","match_id","event_name","wrestler_A","wrestler_B","is_replay"]
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()
def probe(p):
    o=subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-count_frames","-show_entries","stream=width,height,r_frame_rate,nb_read_frames,codec_name:format=duration","-of","json",p],capture_output=True,text=True).stdout
    j=json.loads(o); s=j["streams"][0]; return dict(width=s["width"],height=s["height"],fps=s["r_frame_rate"],frames=int(s["nb_read_frames"]),codec=s["codec_name"],duration_s=float(j["format"]["duration"]))
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("clip"); ap.add_argument("--meta",required=True); ap.add_argument("--out_dir",required=True); a=ap.parse_args()
    m=json.load(open(a.meta)); miss=[k for k in REQ if k not in m or m[k] in ("",None)]
    if miss: print("MISSING METADATA:",miss); sys.exit(1)
    m.setdefault("rights_status","UNRESOLVED"); pr=probe(a.clip); warn=[]
    if pr["height"]<720: warn.append("height<720")
    if not (45<=pr["duration_s"]<=150): warn.append("duration outside 45-150 s guidance")
    rec=dict(meta=m,file_sha256=sha(a.clip),file_name=os.path.basename(a.clip),probe=pr,ingested_utc=datetime.datetime.utcnow().isoformat()+"Z",
        retention_policy="footage kept in private workspace only; no redistribution; non-target (spectator/staff) imagery: retain features/derived data only where possible, delete crops after feature extraction unless needed for audit",
        warnings=warn)
    d=os.path.join(a.out_dir,m["clip_id"]); os.makedirs(d,exist_ok=True); json.dump(rec,open(os.path.join(d,"provenance.json"),"w"),indent=1); print("ok",m["clip_id"],rec["file_sha256"][:12],pr,warn)
if __name__=="__main__": main()
