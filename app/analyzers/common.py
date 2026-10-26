from __future__ import annotations

from app.models import Evidence


def fuse_evidence(evidence: list[Evidence]) -> tuple[int, str, str]:
    """Transparent baseline fusion. This is a risk index, NOT a probability."""
    raw = 8.0
    positive_signal_count = 0
    verified_high = 0

    severity_multiplier = {
        "info": 0.15,
        "low": 0.35,
        "medium": 0.7,
        "high": 1.0,
    }

    for item in evidence:
        contribution = max(0.0, item.weight) * severity_multiplier[item.severity] * 32
        raw += contribution
        if item.weight > 0.15:
            positive_signal_count += 1
        if item.evidence_class == "verified" and item.severity == "high" and item.weight > 0:
            verified_high += 1

    risk_index = max(0, min(100, round(raw)))
    if risk_index >= 80:
        level = "critical"
    elif risk_index >= 55:
        level = "high"
    elif risk_index >= 30:
        level = "guarded"
    else:
        level = "low"

    if verified_high >= 2 or positive_signal_count >= 4:
        confidence = "high"
    elif positive_signal_count >= 2:
        confidence = "medium"
    else:
        confidence = "low"

    return risk_index, level, confidence
