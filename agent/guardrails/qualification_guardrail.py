def qualification_guardrail(score: int, reasoning: str) -> dict:
    """
    Validates qualification output
    """

    reasons = []

    # ----- Score validity -----
    if score is None:
        reasons.append("Qualification score missing")

    if not isinstance(score, int):
        reasons.append("Qualification score is not integer")

    if isinstance(score, int) and not (0 <= score <= 10):
        reasons.append("Qualification score outside 0-10 range")

    # ----- Reasoning checks -----
    if not reasoning or len(reasoning.strip()) < 50:
        reasons.append("Qualification reasoning too weak")

    # ICP mention check (simple heuristic)
    if "ICP" not in reasoning and "criteria" not in reasoning.lower():
        reasons.append("Reasoning does not reference ICP alignment")

    return {
        "passed": len(reasons) == 0,
        "reasons": reasons
    }
