# Rule V1 — prospective feature/threshold declaration (written BEFORE any BUILD feature value or BUILD performance number was computed)
Features (2 of max 3), from frozen stride-3 person boxes only (gate: conf>=0.3 and box height>=50 px at 360p; both frozen):
 F1 frac_ge2 = fraction of the shot's sampled frames with >=2 gated person boxes.
    Rationale: wide/medium ring camera shows >=2 bodies (two wrestlers, often a referee); close-ups of faces, crowd, desk or graphics show 0-1.
 F2 h_max_med = median over sampled frames of (tallest gated box height / frame height).
    Rationale: a subject filling most of the frame height signals tight framing in which action is not observable.
Replay indicator R: inert (R=0 always) in V1 -- zero BUILD REPLAY examples exist, so any replay cue would be an untestable invented threshold. Zero thresholds spent. Disclosed as the principal construction concern.
Thresholds (3 of max 5), fixed a priori from rationale, round values, not read from BUILD:
 T1 = 0.20  (below: two-person action essentially never in view -> NOT_LIVE)
 T2 = 0.50  (majority rule: >= half the sampled frames show two bodies -> LIVE eligible)
 T3 = 0.80  (tallest body > 80% of frame height = tight framing -> not eligible for LIVE -> UNKNOWN)
Hierarchy: no sampled frames -> UNKNOWN; F1<T1 -> NOT_LIVE; F1>=T2 and F2<=T3 -> LIVE; else UNKNOWN (fail-closed, never silently LIVE).
Classifier UNKNOWN counts as not-LIVE in P1 (design). Reference UNKNOWN rows are excluded from numerator and denominator.
