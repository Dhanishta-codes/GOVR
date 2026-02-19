# ============================================================
# WORKFLOW INTELLIGENCE ENGINE
# Unified performance + business + benchmark + dependency brain
# ============================================================

from typing import Dict


def calculate_workflow_intelligence(state: Dict) -> Dict:

    evaluation = state.get("evaluation_results", {})
    dependency = state.get("dependency_summary", {})

    workflow_perf = evaluation.get("workflow", {})
    benchmark = evaluation.get("benchmark", {})
    business = evaluation.get("business_effectiveness", {})

    performance_score = workflow_perf.get("overall_score", 0)
    confidence_score = workflow_perf.get("confidence_score", 0.7)
    business_score = business.get("business_score", 0)
    market_position = benchmark.get("benchmark_position", "UNKNOWN")
    dependency_score = dependency.get("dependency_score", 100)

    explanations = []

    # -----------------------------
    # Risk Level Calculation
    # -----------------------------
    risk_score = (
        (100 - performance_score) * 0.4 +
        (100 - business_score) * 0.3 +
        (100 - dependency_score) * 0.3
    )

    if risk_score >= 70:
        risk_level = "HIGH"
    elif risk_score >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # -----------------------------
    # Revenue Alignment
    # -----------------------------
    if business_score >= 80:
        revenue_alignment = "STRONG"
    elif business_score >= 60:
        revenue_alignment = "MODERATE"
    else:
        revenue_alignment = "WEAK"

    # -----------------------------
    # Strategic Recommendation
    # -----------------------------
    if risk_level == "HIGH":
        recommendation = "STOP"
        explanations.append("High governance + performance risk")

    elif revenue_alignment == "WEAK":
        recommendation = "OPTIMIZE"
        explanations.append("Revenue alignment weak")

    elif market_position == "BELOW_MARKET_STANDARD":
        recommendation = "OPTIMIZE"
        explanations.append("Below industry benchmark")

    elif performance_score >= 85 and business_score >= 80:
        recommendation = "SCALE"
        explanations.append("Strong performance and business alignment")

    else:
        recommendation = "CONTINUE"

    return {
        "overall_score": performance_score,
        "confidence_score": round(confidence_score, 2),
        "risk_level": risk_level,
        "market_position": market_position,
        "revenue_alignment": revenue_alignment,
        "strategic_recommendation": recommendation,
        "explanations": explanations
    }
