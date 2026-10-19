"""Path configuration: all external locations come from environment variables; no absolute paths in code."""
import os
def _p(name, default=None):
    v = os.environ.get(name, default)
    return os.path.abspath(v) if v else None
def frozen_dir(): return _p("V061_FROZEN_DIR")
def feature_dir(): return _p("V061_FEATURE_DIR")
def weights_dir(): return _p("V061_WEIGHTS_DIR")
def private_data_dir(): return _p("V061_PRIVATE_DATA_DIR")
def require(name):
    v = _p(name)
    if not v: raise SystemExit(f"environment variable {name} is required for this entry point")
    return v
