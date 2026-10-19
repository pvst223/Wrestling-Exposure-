"""PROSPECTIVE reference contract (planning artifact, NOT executed on real video, NOT part of the locked V0.6.1 implementation).
Specifies how identity states and ownership/pose states combine into ONE per-skeleton record class.
Principle: correct anatomical ownership is not evidence of correct wrestler identity; identity uncertainty is never erased downstream."""
ID_STATES = ("ACCEPT_A", "ACCEPT_B", "ABSTAIN_AMBIGUOUS", "REJECT_NONTARGET", "NO_IDENTITY_EVAL")
OWN_STATES = ("SINGLE_BODY_SUPPORTED", "MIXED_BODY_SUSPECTED", "OWNERSHIP_UNCERTAIN", "OWNERSHIP_NOT_EVALUATED")
POSE = ("MEASURED", "NONE")
MAX_CARRY = 3  # same as locked identity renderer (frame_status.MAX_CARRY)
CLASSES = ("ASSIGNED_A", "ASSIGNED_B", "UNASSIGNED_IDENTITY_AMBIGUOUS", "NONTARGET", "INVALID_NUMERIC",
           "WITHHELD_MIXED_BODY", "WITHHELD_OWNERSHIP_UNCERTAIN", "WITHHELD_OWNERSHIP_NOT_EVALUATED", "NO_IDENTITY_EVAL", "NO_POSE")

def classify(identity, numeric_failure, ownership, pose):
    """Precedence (fail-closed, first match wins):
    NO_POSE > INVALID_NUMERIC > WITHHELD_MIXED_BODY > WITHHELD_OWNERSHIP_* > identity-based class.
    landmarks_emitted is True only for ASSIGNED_* and UNASSIGNED_IDENTITY_AMBIGUOUS-with-SINGLE_BODY (shown neutral, never as A or B)."""
    assert identity in ID_STATES and ownership in OWN_STATES and pose in POSE
    if pose == "NONE": cls = "NO_POSE"
    elif numeric_failure: cls = "INVALID_NUMERIC"
    elif ownership == "MIXED_BODY_SUSPECTED": cls = "WITHHELD_MIXED_BODY"
    elif ownership == "OWNERSHIP_UNCERTAIN": cls = "WITHHELD_OWNERSHIP_UNCERTAIN"
    elif ownership == "OWNERSHIP_NOT_EVALUATED": cls = "WITHHELD_OWNERSHIP_NOT_EVALUATED"
    elif identity == "ACCEPT_A": cls = "ASSIGNED_A"
    elif identity == "ACCEPT_B": cls = "ASSIGNED_B"
    elif identity == "ABSTAIN_AMBIGUOUS": cls = "UNASSIGNED_IDENTITY_AMBIGUOUS"
    elif identity == "REJECT_NONTARGET": cls = "NONTARGET"
    else: cls = "NO_IDENTITY_EVAL"
    return dict(record_class=cls,
                assigned_label={"ASSIGNED_A": "A", "ASSIGNED_B": "B"}.get(cls),
                landmarks_emitted=cls in ("ASSIGNED_A", "ASSIGNED_B", "UNASSIGNED_IDENTITY_AMBIGUOUS"),
                identity_state_passthrough=identity,           # always preserved, never overwritten by ownership
                ownership_state_passthrough=ownership,         # always preserved, never overwritten by identity
                numeric_failure=bool(numeric_failure),
                identity_unvalidated_flag=cls in ("ASSIGNED_A", "ASSIGNED_B"))  # component verdict is MODIFY / not validated

def carry(prev_classes_since_anchor, cut_since_anchor):
    """Visualisation-only carry. prev_classes_since_anchor: list of record classes from the last MEASURED anchor to now (anchor first).
    Allowed only if the anchor was ASSIGNED_A/B, age<=MAX_CARRY, no camera cut since anchor. Carried frames are never measurements and never enter metrics."""
    if not prev_classes_since_anchor or cut_since_anchor: return None
    anchor = prev_classes_since_anchor[0]; age = len(prev_classes_since_anchor) - 1
    if anchor not in ("ASSIGNED_A", "ASSIGNED_B") or not (1 <= age <= MAX_CARRY): return None
    return dict(record_class="CARRIED_" + anchor, age=age, measurement=False)
