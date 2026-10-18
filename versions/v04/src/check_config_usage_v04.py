"""V0.4 doc/code consistency aid: (1) every config key must be referenced in source; (2) list numeric literals in behaviour code that are NOT from config."""
import re, sys, os, ast
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import config
here = os.path.dirname(os.path.abspath(__file__)); files = ["track_v04.py", "integrity_v04.py", "integrity_v03.py", "reid_v04.py", "embed_crops.py", "appearance.py", "cuts_events.py"]
src = {f: open(os.path.join(here, f)).read() for f in files}; allsrc = "\n".join(src.values()) + open(os.path.join(here, "evaluate_v04.py")).read()
unused = [k for k in config.all_keys() if not re.search(r"\b" + re.escape(k.split(".")[-1]) + r"\b", allsrc)]
print("UNUSED CONFIG KEYS:", unused)
ALLOW = {0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 7, 17, 255, 0.0, 1.0, 1e-6, 999, 1500}
for f in files:
    lits = sorted({n.value for n in ast.walk(ast.parse(src[f])) if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool) and n.value not in ALLOW})
    print(f, "numeric literals outside allowlist:", lits)
