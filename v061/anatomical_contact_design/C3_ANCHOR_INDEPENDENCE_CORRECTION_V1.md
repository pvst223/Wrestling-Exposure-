# C3 ANCHOR-INDEPENDENCE CORRECTION V1 (design only; supersedes the `MIN_GAP = 60` anchor-spacing rule in ANATOMY_V2_C3 DETAILED DESIGN V1 sections 2 and 4)

Nothing implemented or run. No M9/M9B/M9C correctness outcome, verdict, owner note or contact diagnostic was inspected or used for this correction. Development-only, rights UNRESOLVED. No Holdout #2, no Gemini, no exposure, no final MP4. R3 stays on HOLD.

Acknowledged: the 60-frame spacing was inherited from the identity strict-seed subsystem, where it serves a different purpose (keeping identity seeds from being near-duplicates). Reuse of that number is withdrawn as a justification for C3.

## 1. What the second view is for (the information requirement)

In the frozen appearance code the second view supplies exactly one thing: the **within-body noise floor** `noise[t]` = mean Bhattacharyya distance between pairs of views of the same body, per region type. It enters the decision in two places: the usable-signal gate `gap[t] = dsep[t] − noise[t] ≥ D_SEP_MIN (0.15)`, and the vote margin `max(0.25·dsep[t], noise[t])`. With one view there is no pair, `noise` is undefined and the frozen code gives that region type **zero weight** (no vote). Two views are therefore required **only to have a pair**; the pair is informative only if it samples genuinely different observation conditions. Two near-identical frames give a near-zero noise estimate, which would pass the gap gate and shrink the vote margin (anti-conservative). So what matters is not elapsed time but **non-redundancy of the two observations**.

## 2. Corrected anchor definition

Everything in section 4 of the detailed design stands (pre-contact only, same shot, after the previous interval's end, never from in-contact or post-contact frames, structural expiry at cut / interval start / tracklet loss, no age cap, bodies defined from tracklets while spatially separate) **except the spacing rule**, replaced by a structural observation-state rule.

**Observation state of a clean view v** (computed from the view's own confident keypoints, `KP_CONF` 0.5, no thresholds, no tuning):
- `Facing(v) = sign(x_5 − x_6)` (left vs right shoulder image order; flips when the body is seen from the other side). If equal or either shoulder is not confident the state is undefined and the view is ineligible as an anchor view.
- `Posture(v) = UPRIGHT` iff `|y_h − y_s| > |x_h − x_s|`, where s and h are the shoulder-midpoint and hip-midpoint (keypoints 5, 6 and 11, 12, all confident); otherwise NONUPRIGHT (torso axis closer to horizontal). Equality or a missing keypoint makes the view ineligible.
- `State(v) = (Facing, Posture)`.

**Two views are independent iff their `State` differs in at least one component.** (Different state implies different frames; a duplicate observation has the same state.)

**Anchor for body b** = a pair of independent clean views of tracklet `t_b`: scanning backward from the interval onset (within the pre-contact, same-shot, post-previous-interval span), take the most recent clean view v1, then the most recent earlier clean view v2 whose `State` differs from `State(v1)`. Deterministic. Each body (α and each β_k) needs its own independent pair (stricter than the frozen minimum, which pools pairs across both bodies; chosen so that each body's own variation is represented). If no such pair exists → `NO_INDEPENDENT_ANCHOR_VIEWS` → WITHHOLD.

## 3. Justification
1. It follows from section 1: the pair exists to measure within-body variation across observation conditions, and the rule requires a change in the view/pose state that most directly changes which body surfaces and regions are visible (side seen; torso orientation), using only frame-internal coordinate comparisons.
2. No time, frame count or tolerance enters the rule; nothing is borrowed from a different subsystem.
3. It is fail-closed: bodies that stay in the same state before contact have no anchor and are withheld.

## 4. Does it introduce a new constant? No numeric constant.
It introduces definitions (shoulder order; torso axis closer to vertical than horizontal) and two structural choices: strict inequality, and "differ in at least one component". The `|Δy| > |Δx|` comparison carries an implicit 45° convention, disclosed as a convention, not a tuned threshold. Honest limitations: a pose-detector left/right keypoint swap, or a torso near 45°, can produce a spurious state difference (false independence); the state is a proxy, not a guarantee that the noise estimate is adequate. Residual protections: the frozen `gap` gate, the clean-view requirement (SINGLE_BODY_SUPPORTED), the anchor audit on fresh data, and the reported noise values.

**If the reviewer rejects this rule**, a new anchor-spacing constant would be required. It would have to be chosen label-free, before any fresh data, by a pre-registered decorrelation estimate on development clips using only pre-contact clean frames, appearance distances and frame lags — no ownership, anatomy or correctness verdicts, no contact flags. The estimator itself needs a plateau criterion that is a constant of its own, so this fallback is strictly worse in parameter terms; I do not recommend it unless S proves unusable. It would be run only after an explicit ruling.

## 5. Consequences
- **Determinism:** unchanged in kind: state is derived from cached frozen keypoints by sign comparisons; anchor selection is a fixed backward scan; ties (equal coordinates) make a view ineligible, not tie-broken. No float tolerance enters the rule.
- **Feasibility:** unknown and potentially lower or different from the spacing rule: bodies that stay upright and facing the same way until contact have no anchor, while a short fast turn can give an anchor from frames only a few frames apart. The authorized geometry-only feasibility counts will report, per clip, the numbers of intervals, bodies with a valid independent pair, bodies excluded because no state difference existed, and the pooled-minimum count (one pooled pair, the frozen minimum) as a **reported-only** figure. These counts will not change this rule or any constant; a change would need a new reviewer ruling.
- No change to the evidence families, hypothesis set, margin rule, C0 comparator, outcome map or usefulness floors (Y ≥ 10%, R2 ≥ 50 judgeable rescued frames, reviewer-set utility criteria rather than empirically derived thresholds).

## 6. Updated constants audit
| constant | value | source |
|---|---|---|
| keypoint confidence (landmarks and state computation) | 0.5 | frozen V1 `pose.KP_CONF` |
| appearance keypoint confidence | 0.3 | frozen `appearance.KP_CONF` |
| overlap, duplicate, shared-joint tests | IoU 0.3; cover 0.5; ≥3 joints inside; dup IoU 0.5; ≥3 joints within 0.05·diag | frozen `integrity` section |
| mask tolerance 4 px; duplicate-mask IoU 0.8; min landmarks 4; opponent-landmark min n 3; unexplained ≤ 0.25 | as listed | frozen `ownership` section |
| appearance gate/vote/pixel limits and region geometry | D_SEP_MIN 0.15; VOTE_DELTA 0.25; REGION_MIN_PIX 120; MODEL_MIN_PIX 300; REGION_MASS | frozen `appearance` section |
| min torso / total joints for a clean view | 3 / 6 | frozen `REL_MIN_TORSO_JOINTS` / `REL_MIN_JOINTS` |
| pose stride | 3 | frozen |
| structural: two independent views per body (minimum information for a noise pair); ≤3 anchored bodies; 1-pose-frame interval extension; zero contradictions; ≥1 positive source per landmark; strict inequalities | — | structural, not tuned |
| **REMOVED:** `MIN_GAP = 60` view spacing | — | withdrawn |
| **ADDED:** observation-state definitions (shoulder order, torso axis vertical vs horizontal) | no numeric constant | structural definitions |

The constants-audit test is updated accordingly (no literal 60 may be read by the C3 module).

## 7. Requested ruling
Approve the observation-state independence rule and the removal of `MIN_GAP`, or direct the fallback (new label-free decorrelation constant). On approval, C3 implementation + synthetic tests may proceed (no fresh evaluation, no R3 resumption).

STOP for reviewer ruling.
