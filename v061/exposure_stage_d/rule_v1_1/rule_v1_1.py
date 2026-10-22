"""Stage-D Rule V1.1: deterministic shot-level scene/time rule (single authorized revision of Rule V1: F2 veto and T3 removed).
Inputs: frozen shot frame ranges and frozen stride-3 person boxes (box, conf, frame shape) ONLY. No learned component, no fitting. Reads no reference annotation."""
import json,os
HERE=os.path.dirname(os.path.abspath(__file__))
def load_cfg(path=None):
    with open(path or os.path.join(HERE,"rule_v1_1_config.json")) as fh: return json.load(fh)
def shot_features(fs,fe,dets,cfg):
    g=cfg["input_gate_frozen"]; n_ge2=0; k=0
    for f in range(fs,fe):
        if f%g["frame_stride"]!=0 or f not in dets: continue
        box,conf,shape=dets[f]; k+=1; sh=float(shape[0]); m=0
        for b,c in zip(box,conf):
            if float(c)>=g["conf_min"] and float(b[3]-b[1])*g["reference_height_px"]/sh>=g["box_height_min_px_at_360p"]: m+=1
        if m>=2: n_ge2+=1
    if k==0: return None
    return {"n_sampled":k,"F1_frac_ge2":n_ge2/k}
def decide(feat,cfg,replay_indicator=0):
    t=cfg["thresholds"]
    if feat is None: return "UNKNOWN","NO_FEATURES"
    if replay_indicator==1: return "REPLAY_SUSPECT","R"
    if feat["F1_frac_ge2"]<t["T1"]: return "NOT_LIVE","F1<T1"
    if feat["F1_frac_ge2"]>=t["T2"]: return "LIVE","F1>=T2"
    return "UNKNOWN","BAND"
def classify_shots(shots,dets_by_source,cfg=None):
    cfg=cfg or load_cfg(); out=[]
    for sid,src,fs,fe in shots:
        feat=shot_features(fs,fe,dets_by_source[src],cfg); lab,why=decide(feat,cfg)
        out.append({"shot_id":sid,"source_id":src,"frame_start":fs,"frame_end":fe,"features":feat,"rule_class":lab,"why":why})
    return out
