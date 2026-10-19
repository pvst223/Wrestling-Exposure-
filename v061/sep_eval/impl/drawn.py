"""Which landmarks the FROZEN renderer actually draws for an ASSIGNED skeleton (endpoints of drawn bones). Uses the frozen render_anat constants/rule; changes nothing there."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "anatomical", "impl"))
import render_anat
def drawn_bones(box, kp, kpc):
    kp = np.asarray(kp, float); kc = np.asarray(kpc, float); x1, y1, x2, y2 = box; bd = float(np.hypot(x2 - x1, y2 - y1)); out = []
    for a, b in render_anat.BONES:
        if kc[a] >= render_anat.DISPLAY_KP_CONF and kc[b] >= render_anat.DISPLAY_KP_CONF and np.hypot(*(kp[a] - kp[b])) <= render_anat.MAX_BONE_FRAC * bd: out.append((a, b))
    return out
def drawn_landmarks(box, kp, kpc): return sorted({i for b in drawn_bones(box, kp, kpc) for i in b})
