# agent/guardrails/guardrail_aggregator.py


RISK_WEIGHTS = {
    "LOW": 1,
    "MEDIUM": 3,
    "HIGH": 6
}


def aggregate_guardrails(state) -> dict:
    """
    Aggregates all guardrail results across workflow
    """

    results = state.get("guardrail_results", {})

    total_risk_score = 0
    highest_risk = "LOW"
    violation_count = 0
    all_reasons = []

    for node, result in results.items():

        risk_level = result.get("risk_level", "LOW")
        reasons = result.get("reasons", [])

        total_risk_score += RISK_WEIGHTS.get(risk_level, 1)

        if risk_level == "HIGH":
            highest_risk = "HIGH"
        elif risk_level == "MEDIUM" and highest_risk != "HIGH":
            highest_risk = "MEDIUM"

        if reasons:
            violation_count += len(reasons)
            all_reasons.extend([f"{node}: {r}" for r in reasons])

    workflow_passed = highest_risk != "HIGH"

    return {
        "workflow_passed": workflow_passed,
        "workflow_risk_level": highest_risk,
        "workflow_risk_score": total_risk_score,
        "total_violations": violation_count,
        "reasons": all_reasons
    }
