#!/usr/bin/env python3
"""Deterministic response parser for the proposed Gemini procedure (no model calls)."""
LABELS = ("TARGET_A","TARGET_B","REFEREE","STAFF","SPECTATOR","UNLABELABLE")
def parse(raw, blocked_or_refused=False, transport_error=False):
    """Returns (final_label, status). Non-OK content maps to UNLABELABLE with a status
    that is counted and reported; it is never re-prompted. transport_error means NO response
    content was received (the only case in which an identical request may be re-sent)."""
    if transport_error: return (None, "TRANSPORT_ERROR")
    if blocked_or_refused: return ("UNLABELABLE", "REFUSAL_OR_BLOCK")
    if raw is None or raw.strip()=="": return ("UNLABELABLE", "EMPTY")
    t = raw.strip()
    if t in LABELS: return (t, "OK")
    return ("UNLABELABLE", "MALFORMED")
