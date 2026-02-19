def calculate_confidence_score(state):

    evaluation = state.get("evaluation_results", {})
    guardrails = state.get("guardrail_results", {})

    workflow_score = evaluation.get("workflow", {}).get("score", 50)
    business_score = evaluation.get("business_effectiveness", {}).get("score", 50)
    benchmark_gap = evaluation.get("benchmark", {}).get("gap_score", 0)

    # Count retries across nodes
    total_retries = 0
    for value in guardrails.values():
        total_retries += value.get("retry_count", 0)

    fallback_count = len(state.get("dependency_fallbacks", []))

    # -----------------------------
    # Confidence Formula
    # -----------------------------
    confidence = (
        (workflow_score * 0.4) +
        (business_score * 0.4) +
        ((100 - benchmark_gap) * 0.2)
    )

    # Penalize instability
    confidence -= total_retries * 3
    confidence -= fallback_count * 5

    confidence = max(0, min(100, confidence))

    if confidence >= 75:
        level = "HIGH"
    elif confidence >= 50:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "confidence_score": round(confidence, 2),
        "confidence_level": level
    }
