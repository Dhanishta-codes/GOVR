# ============================================================
# CONTROL DECISION ENGINE (SINGLE SOURCE OF TRUTH)
# Enterprise Governance + Revenue-Aware Control
# ============================================================

from agent.governance.risk_engine import calculate_risk_score
from agent.governance.confidence_engine import calculate_confidence_score
from agent.governance.dependency_engine import calculate_dependency_health
from agent.governance.adaptive_threshold_engine import get_adaptive_thresholds


def control_decision_engine(state: dict) -> dict:
    """
    Final and only authority for workflow decisions.
    """

    # --------------------------------------------------
    # 1️⃣ Collect Signals
    # --------------------------------------------------

    risk = calculate_risk_score(state)
    confidence = calculate_confidence_score(state)
    dependency = calculate_dependency_health(state)

    business_score = (
        state.get("evaluation_results", {})
        .get("business_effectiveness", {})
        .get("business_score", 0)
    )

    thresholds = get_adaptive_thresholds()
    reasons = []

    # --------------------------------------------------
    # 2️⃣ HARD STOP CONDITIONS (Non-negotiable)
    # --------------------------------------------------

    if not dependency["dependencies_valid"]:
        reasons.extend(dependency["structural_errors"])

    if risk["risk_level"] == "HIGH":
        reasons.append("High governance risk")

    if dependency["dependency_level"] == "FRAGILE":
        reasons.append("Fragile dependency health")

    if reasons:
        return {
            "decision": "STOP",
            "risk_score": risk["risk_score"],
            "risk_level": risk["risk_level"],
            "confidence_score": confidence["confidence_score"],
            "dependency_score": dependency["dependency_score"],
            "business_score": business_score,
            "reasons": reasons,
            "thresholds_used": thresholds
        }

    # --------------------------------------------------
    # 3️⃣ SOFT CONTROL (Rewrite / Review)
    # --------------------------------------------------

    if confidence["confidence_score"] < thresholds["rewrite_confidence"]:
        return {
            "decision": "REWRITE",
            "risk_score": risk["risk_score"],
            "risk_level": risk["risk_level"],
            "confidence_score": confidence["confidence_score"],
            "dependency_score": dependency["dependency_score"],
            "business_score": business_score,
            "reasons": ["Confidence below rewrite threshold"],
            "thresholds_used": thresholds
        }

    # --------------------------------------------------
    # 4️⃣ ALLOW
    # --------------------------------------------------

    return {
        "decision": "ALLOW",
        "risk_score": risk["risk_score"],
        "risk_level": risk["risk_level"],
        "confidence_score": confidence["confidence_score"],
        "dependency_score": dependency["dependency_score"],
        "business_score": business_score,
        "thresholds_used": thresholds
    }
