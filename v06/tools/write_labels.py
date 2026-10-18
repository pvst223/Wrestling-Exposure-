import sys,json,csv
clip=sys.argv[1]; ids=sys.argv[2]; spec=sys.argv[3]   # id map "A=brock_lesnar,B=..." ; spec file of "idx code" tokens
idm=dict(x.split("=") for x in ids.split(","))
toks=open(spec).read().split()
T=json.load(open(f"frozen/tracklets/{clip}.json"))
assert len(toks)==len(T),(len(toks),len(T))
out=f"frozen/labels/{clip}_labels_firstpass.csv"
w=csv.writer(open(out,"w",newline="")); w.writerow("tid,person_class,wrestler_id,multi_person_flag,annotator,independent".split(","))
for t,v in zip(T,toks):
    m=int(v.endswith("m")); c=v[0]
    cls,wid={"R":("REFEREE",""),"S":("RINGSIDE_STAFF",""),"P":("SPECTATOR",""),"U":("UNLABELABLE",""),"O":("OTHER_WRESTLER_UNNAMED","")}.get(c,("WRESTLER",idm.get(c,"")))
    assert cls!="WRESTLER" or wid,c
    w.writerow([t["tid"],cls,wid,m,"claude_firstpass",0])
