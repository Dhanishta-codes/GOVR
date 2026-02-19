# ============================================================
# WORKFLOW PERFORMANCE ENGINE
# Revenue Conversion Focused + Enterprise Governance Balanced
# ============================================================

from typing import Dict

WEIGHTS = {
    "research": 0.15,
    "qualification": 0.20,
    "decision_maker": 0.15,
    "email": 0.25,
    "contact": 0.10,
    "governance": 0.15
}


def clamp(value: float, min_v=0, max_v=100) -> float:
    return max(min(value, max_v), min_v)


def calculate_workflow_performance(state: Dict) -> Dict:
    """
    Produces a unified, revenue-aware workflow performance score.
    """

    evaluation = state.get("evaluation_results", {})
    guardrails = state.get("guardrail_results", {})
    control = state.get("control_summary", {})

    # --------------------------------------------------
    # Extract dimension scores (0–100)
    # --------------------------------------------------

    research_score = evaluation.get("research", {}).get("score", 0) * 100
    qualification_score = state.get("qualification_score", 0) * 10
    email_score = evaluation.get("email", {}).get("effectiveness_score", 0) * 10
    contact_score = 80 if state.get("contacts") else 40
    decision_maker_score = 85 if state.get("decision_maker_titles") else 40

    governance_risk = control.get("risk_score", 0)
    governance_score = clamp(100 - governance_risk)

    # Clamp all
    research_score = clamp(research_score)
    qualification_score = clamp(qualification_score)
    email_score = clamp(email_score)
    contact_score = clamp(contact_score)
    decision_maker_score = clamp(decision_maker_score)

    # --------------------------------------------------
    # Dimension Breakdown
    # --------------------------------------------------

    dimension_breakdown = {
        "research": int(research_score),
        "qualification": int(qualification_score),
        "decision_maker": int(decision_maker_score),
        "email": int(email_score),
        "contact": int(contact_score),
        "governance": int(governance_score)
    }

    # --------------------------------------------------
    # Weighted Performance Score
    # --------------------------------------------------

    overall_score = (
        research_score * WEIGHTS["research"] +
        qualification_score * WEIGHTS["qualification"] +
        decision_maker_score * WEIGHTS["decision_maker"] +
        email_score * WEIGHTS["email"] +
        contact_score * WEIGHTS["contact"] +
        governance_score * WEIGHTS["governance"]
    )

    overall_score = round(clamp(overall_score), 2)

    # --------------------------------------------------
    # Confidence Score (stability signal)
    # --------------------------------------------------

    retry_penalty = sum(
        v.get("retry_count", 0) for v in guardrails.values()
    ) * 3

    confidence_score = clamp(overall_score - retry_penalty)

    # --------------------------------------------------
    # Classification
    # --------------------------------------------------

    if overall_score >= 85:
        performance_level = "HIGH_PERFORMING"
        recommendation = "SCALE"
    elif overall_score >= 70:
        performance_level = "STABLE"
        recommendation = "OPTIMIZE"
    elif overall_score >= 55:
        performance_level = "UNDERPERFORMING"
        recommendation = "REWRITE"
    else:
        performance_level = "CRITICAL"
        recommendation = "STOP"

    return {
        "overall_score": overall_score,
        "confidence_score": round(confidence_score, 2),
        "dimension_breakdown": dimension_breakdown,
        "performance_level": performance_level,
        "strategic_recommendation": recommendation
    }
