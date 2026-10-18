"""Centralised V0.3 configuration loader. Tracks which keys are read so check_config_usage.py can prove there are no dead constants."""
import json, os
_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config_v03.json")
class Cfg(dict):
    def __init__(self, d, path=""):
        super().__init__(); self._path = path; self._read = set()
        for k, v in d.items():
            if k.startswith("_"): continue
            self[k] = Cfg(v, path + k + ".") if isinstance(v, dict) else v
    def __getattr__(self, k):
        if k.startswith("_"): raise AttributeError(k)
        self._read.add(k); return self[k]
def load(): return Cfg(json.load(open(_PATH)))
def all_keys(c=None):
    c = c or load(); out = []
    for k, v in c.items():
        out += all_keys(v) if isinstance(v, dict) else [c._path + k]
    return out
