"""Anatomical record classifier (implementation of v061/anatomical_plan/contract.py, same semantics). Pure Python.
The merge guard is DELIBERATELY not an input: classify() has no parameter for it (diagnostic-only, reviewer ruling Q2)."""
ID_STATES = ("ACCEPT_A", "ACCEPT_B", "ABSTAIN_AMBIGUOUS", "REJECT_NONTARGET", "NO_IDENTITY_EVAL")
OWN_STATES = ("SINGLE_BODY_SUPPORTED", "MIXED_BODY_SUSPECTED", "OWNERSHIP_UNCERTAIN", "OWNERSHIP_NOT_EVALUATED")
CLASSES = ("ASSIGNED_A", "ASSIGNED_B", "UNASSIGNED_IDENTITY_AMBIGUOUS", "NONTARGET", "INVALID_NUMERIC", "WITHHELD_MIXED_BODY",
           "WITHHELD_OWNERSHIP_UNCERTAIN", "WITHHELD_OWNERSHIP_NOT_EVALUATED", "NO_IDENTITY_EVAL", "NO_POSE", "CARRIED_ASSIGNED_A", "CARRIED_ASSIGNED_B")
WITHHELD = ("WITHHELD_MIXED_BODY", "WITHHELD_OWNERSHIP_UNCERTAIN", "WITHHELD_OWNERSHIP_NOT_EVALUATED")
ASSIGNED = ("ASSIGNED_A", "ASSIGNED_B")
def classify(identity, numeric_failure, ownership, pose_status):
    assert identity in ID_STATES and ownership in OWN_STATES and pose_status in ("MEASURED", "NONE")
    if pose_status == "NONE": c = "NO_POSE"
    elif numeric_failure: c = "INVALID_NUMERIC"
    elif ownership == "MIXED_BODY_SUSPECTED": c = "WITHHELD_MIXED_BODY"
    elif ownership == "OWNERSHIP_UNCERTAIN": c = "WITHHELD_OWNERSHIP_UNCERTAIN"
    elif ownership == "OWNERSHIP_NOT_EVALUATED": c = "WITHHELD_OWNERSHIP_NOT_EVALUATED"
    elif identity == "ACCEPT_A": c = "ASSIGNED_A"
    elif identity == "ACCEPT_B": c = "ASSIGNED_B"
    elif identity == "ABSTAIN_AMBIGUOUS": c = "UNASSIGNED_IDENTITY_AMBIGUOUS"
    elif identity == "REJECT_NONTARGET": c = "NONTARGET"
    else: c = "NO_IDENTITY_EVAL"
    return dict(record_class=c, assigned_label={"ASSIGNED_A": "A", "ASSIGNED_B": "B"}.get(c),
                landmarks_emitted=c in ASSIGNED + ("UNASSIGNED_IDENTITY_AMBIGUOUS",), identity_state_passthrough=identity,
                ownership_state_passthrough=ownership, numeric_failure=bool(numeric_failure), identity_unvalidated_flag=c in ASSIGNED)
