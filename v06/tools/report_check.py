"""Report integrity. render(template, metrics_json) fills {{path.to.value}} placeholders (dotted keys, list indices) ONLY from metrics.json: the writer generates prose, no computed numbers.
verify(report_text, metrics_json): extracts every number in the prose and fails if any number does not appear (after rounding to the number's displayed precision, also as a percentage) among metric values, or in an allowed list (years, dates, hashes, section numbers via ALLOW). Prints unmatched numbers."""
import re,json,sys
def flat(o,acc):
    if isinstance(o,dict):
        for v in o.values(): flat(v,acc)
    elif isinstance(o,list):
        for v in o: flat(v,acc)
    elif isinstance(o,(int,float)) and not isinstance(o,bool): acc.append(float(o))
    return acc
def get(o,path):
    for p in path.split("."): o=o[int(p)] if isinstance(o,list) else o[p]
    return o
def render(template,metrics):
    m=json.load(open(metrics)) if isinstance(metrics,str) else metrics
    return re.sub(r"\{\{([^}]+)\}\}",lambda x:str(get(m,x.group(1).strip())),template)
def verify(text,metrics,allow=()):
    m=json.load(open(metrics)) if isinstance(metrics,str) else metrics; vals=flat(m,[]); bad=[]
    text=re.sub(r"[0-9a-f]{12,}","",text)
    for s in re.findall(r"(?<![\w.])-?\d+(?:\.\d+)?%?",text):
        pct=s.endswith("%"); x=float(s.rstrip("%")); dec=len(s.rstrip("%").split(".")[1]) if "." in s else 0
        if str(s.rstrip("%")) in set(map(str,allow)): continue
        cands=[v*(100 if pct else 1) for v in vals]+[v for v in vals]+[v*100 for v in vals]
        if not any(round(c,dec)==round(x,dec) for c in cands): bad.append(s)
    return bad
if __name__=="__main__":
    b=verify(open(sys.argv[1]).read(),sys.argv[2]); print("OK" if not b else ("UNMATCHED NUMBERS: "+str(b))); sys.exit(1 if b else 0)
