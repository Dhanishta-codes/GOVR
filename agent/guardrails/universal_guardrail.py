# agent/guardrails/universal_guardrail.py

from agent.core.nodes import AgentState

BLOCKLISTED_PHRASES = [
    "guaranteed results",
    "100% success",
    "no risk",
]

MAX_EMAILS_PER_RUN = 3


def universal_guardrail(
    *,
    state: AgentState,
    node_name: str,
) -> dict:
    """
    Global trust & safety guardrail.
    Applies to ALL nodes.
    """

    reasons = []
    risk_score = 0

    # -----------------------------
    # 1. Marketing Claim Safety
    # -----------------------------
    email = state.get("outreach_email")

    if email:
        email_lower = email.lower()

        for phrase in BLOCKLISTED_PHRASES:
            if phrase in email_lower:
                reasons.append(f"Blocked marketing claim: '{phrase}'")
                risk_score += 40

    # -----------------------------
    # 2. Spam Volume Protection
    # -----------------------------
    if len(state.get("emails_sent", [])) > MAX_EMAILS_PER_RUN:
        reasons.append("Exceeded safe email volume")
        risk_score += 30

    # -----------------------------
    # 3. Hallucinated Social Proof
    # -----------------------------
    if email and "we helped companies like" in email.lower():
        reasons.append("Potential hallucinated social proof")
        risk_score += 25

    # -----------------------------
    # Risk Level Classification
    # -----------------------------
    if risk_score >= 70:
        risk_level = "HIGH"
    elif risk_score >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "passed": risk_score < 70,
        "reasons": reasons,
        "risk_level": risk_level,
        "metadata": {
            "risk_score": risk_score,
            "node": node_name
        }
    }
