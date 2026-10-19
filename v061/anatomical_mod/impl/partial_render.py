"""Rendering of PARTIAL anatomy: dashed bones in a distinct colour, a 'PARTIAL' tag, only released landmarks drawn. ASSIGNED rendering (render_anat) is not touched."""
import numpy as np, cv2
PARTIAL_BGR = (0, 140, 255)
def draw_partial(img, rec, dash=6, style="partial"):
    """style="partial": dashed + tag (deliverable video). style="neutral": solid cyan, no tag, released landmarks only (blind review composite)."""
    from partial_release import mask_unreleased
    kp = mask_unreleased(rec)
    if style == "neutral":
        for a, b in rec["released_bones"]: cv2.line(img, tuple(map(int, kp[a])), tuple(map(int, kp[b])), (255, 255, 0), 2)
        return img
    for a, b in rec["released_bones"]:
        p, q = np.array(kp[a], float), np.array(kp[b], float); n = max(2, int(np.hypot(*(q - p)) // dash))
        for k in range(0, n, 2):
            s, e = p + (q - p) * k / n, p + (q - p) * min(k + 1, n) / n; cv2.line(img, tuple(map(int, s)), tuple(map(int, e)), PARTIAL_BGR, 2)
    for i in rec["released_landmarks"]: cv2.circle(img, tuple(map(int, kp[i])), 3, PARTIAL_BGR, -1)
    x1, y1 = rec["box"][0], rec["box"][1]; cv2.putText(img, "PARTIAL", (int(x1), int(max(12, y1 - 4))), cv2.FONT_HERSHEY_SIMPLEX, 0.45, PARTIAL_BGR, 1)
    return img
