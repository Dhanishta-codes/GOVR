def evaluate_research(text: str) -> dict:

    reasons = []
    score = 1.0

    if not text or len(text) < 500:
        score -= 0.3
        reasons.append("Research too short")

    if "pain" not in text.lower() and "challenge" not in text.lower():
        score -= 0.2
        reasons.append("Missing pain point analysis")

    if "product" not in text.lower() and "service" not in text.lower():
        score -= 0.2
        reasons.append("Missing product clarity")

    passed = score >= 0.6

    if score >= 0.8:
        action = "CONTINUE"
    elif score >= 0.6:
        action = "REWRITE"
    else:
        action = "STOP"

    return {
        "score": round(score, 2),
        "passed": passed,
        "confidence": round(score, 2),
        "reasons": reasons,
        "recommended_action": action
    }
