def research_rule_evaluator(text: str) -> dict:

    score = 10.0
    strengths = []
    weaknesses = []
    hints = []

    if len(text) < 500:
        score -= 2
        weaknesses.append("Research too short")
        hints.append("Add deeper company context")

    if "pain" not in text.lower():
        score -= 2
        weaknesses.append("Missing pain point discussion")
        hints.append("Identify business pain areas")

    if "\n" in text:
        strengths.append("Structured output")

    return {
        "score": max(score, 0),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "improvement_hints": hints
    }
