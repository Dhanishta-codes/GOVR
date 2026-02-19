# agent/control/risk_engine.py

def calculate_risk_score(state) -> dict:
    """
    Dynamic workflow risk scoring engine
    """

    score = 0
    reasons = []

    guardrails = state.get("guardrail_results", {})

    # -----------------------------
    # Guardrail Failure Signals
    # -----------------------------
    for node, result in guardrails.items():

        if not result.get("passed", True):
            score += 30
            reasons.append(f"Guardrail failed at {node}")

        # Retry Risk Signal
        if result.get("attempts", 0) >= 2:
            score += 10
            reasons.append(f"Multiple retries at {node}")

    # -----------------------------
    # Missing Core Outputs
    # -----------------------------
    if not state.get("decision_maker_titles"):
        score += 25
        reasons.append("No decision makers identified")

    if not state.get("outreach_email"):
        score += 20
        reasons.append("Email not generated")

    # -----------------------------
    # Risk Level Mapping
    # -----------------------------
    if score >= 50:
        risk_level = "HIGH"
    elif score >= 25:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "reasons": reasons,
    }
