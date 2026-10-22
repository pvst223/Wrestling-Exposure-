"""Stage-D Rule V1: deterministic shot-level scene/time rule. Inputs: frozen shot frame ranges and frozen stride-3 person boxes (box, conf, frame shape) ONLY.
No learned component, no fitting. Usage as a module: classify_shots(shots, dets, cfg). Reads no reference annotation."""
import json,os,statistics
HERE=os.path.dirname(os.path.abspath(__file__))
def load_cfg(path=None):
    return json.load(open(path or os.path.join(HERE,"rule_v1_config.json")))
def shot_features(fs,fe,dets,cfg):
    g=cfg["input_gate_frozen"]; n_ge2=0; hs=[]; k=0
    for f in range(fs,fe):
        if f%g["frame_stride"]!=0 or f not in dets: continue
        box,conf,shape=dets[f]; k+=1; sh=float(shape[0]); heights=[]
        for b,c in zip(box,conf):
            h=float(b[3]-b[1])
            if float(c)>=g["conf_min"] and h*g["reference_height_px"]/sh>=g["box_height_min_px_at_360p"]: heights.append(h/sh)
        if len(heights)>=2: n_ge2+=1
        hs.append(max(heights) if heights else 0.0)
    if k==0: return None
    return {"n_sampled":k,"F1_frac_ge2":n_ge2/k,"F2_h_max_med":float(statistics.median(hs))}
def decide(feat,cfg,replay_indicator=0):
    t=cfg["thresholds"]
    if feat is None: return "UNKNOWN","NO_FEATURES"
    if replay_indicator==1: return "REPLAY_SUSPECT","R"
    if feat["F1_frac_ge2"]<t["T1"]: return "NOT_LIVE","F1<T1"
    if feat["F1_frac_ge2"]>=t["T2"] and feat["F2_h_max_med"]<=t["T3"]: return "LIVE","F1>=T2&F2<=T3"
    return "UNKNOWN","BAND"
def classify_shots(shots,dets_by_source,cfg=None):
    cfg=cfg or load_cfg(); out=[]
    for sid,src,fs,fe in shots:
        feat=shot_features(fs,fe,dets_by_source[src],cfg); lab,why=decide(feat,cfg)
        out.append({"shot_id":sid,"source_id":src,"frame_start":fs,"frame_end":fe,"features":feat,"rule_class":lab,"why":why})
    return out
