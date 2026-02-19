import agent.infra.config as config
from agent.guardrails.schemas import GuardrailResult


def decision_maker_guardrail(titles: list[str]) -> GuardrailResult:
    """
    Validates decision maker selection
    """

    reasons = []
    valid_titles = []

    if not titles:
        return {
            "passed": False,
            "reasons": ["No decision maker titles returned"],
            "risk_level": "high",
            "score": None,
            "validated_output": []
        }

    # ---------- ICP Alignment ----------
    icp_titles = [
        t.lower() for t in config.ICP_CRITERIA["decision_maker_titles"]
    ]

    senior_keywords = [
        "vp", "head", "chief", "director", "cxo", "cro", "cmo"
    ]

    for title in titles:

        title_lower = title.lower()

        # ICP Match
        if any(icp in title_lower for icp in icp_titles):
            valid_titles.append(title)
            continue

        # Senior fallback
        if any(keyword in title_lower for keyword in senior_keywords):
            valid_titles.append(title)

    # ---------- Risk / Validation ----------
    if not valid_titles:
        reasons.append("No ICP-aligned or senior decision makers found")

    if len(titles) > 10:
        reasons.append("Too many decision makers generated — possible hallucination")

    # ---------- Risk Level ----------
    risk_level = "low"

    if reasons:
        risk_level = "medium"

        if not valid_titles:
            risk_level = "high"

    return GuardrailResult(
        allowed=len(reasons) == 0,
        risk_score=30 if reasons else 0,
        risk_level="MEDIUM" if reasons else "LOW",
        reasons=reasons,
        recommended_action="REWRITE" if reasons else "CONTINUE"
    )

