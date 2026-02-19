def calculate_dependency_health(state):

    evaluation = state.get("evaluation_results", {})
    guardrails = state.get("guardrail_results", {})

    dependency_score = 100
    reasons = []
    structural_errors = []

    # =====================================================
    # HARD STRUCTURAL VALIDATION
    # =====================================================

    if not state.get("company_research"):
        structural_errors.append("Missing research")

    if state.get("qualification_score", 0) <= 0:
        structural_errors.append("Invalid qualification score")

    if state.get("outreach_email") and not state.get("decision_maker_titles"):
        structural_errors.append("Email exists without persona")

    if state.get("contacts") and not state.get("outreach_email"):
        structural_errors.append("Contacts exist without email")

    # =====================================================
    # SOFT HEALTH SCORING
    # =====================================================

    if not state.get("company_research"):
        dependency_score -= 30
        reasons.append("Missing research")

    if state.get("qualification_score", 0) < 5:
        dependency_score -= 20
        reasons.append("Weak qualification score")

    if state.get("dependency_fallbacks"):
        dependency_score -= 15
        reasons.append("Fallback persona used")

    total_retries = 0
    for node in guardrails.values():
        total_retries += node.get("retry_count", 0)

    if total_retries >= 3:
        dependency_score -= 15
        reasons.append("High retry instability")

    dependency_score = max(0, dependency_score)

    if dependency_score >= 75:
        level = "HEALTHY"
    elif dependency_score >= 50:
        level = "MODERATE"
    else:
        level = "FRAGILE"

    return {
        "dependencies_valid": len(structural_errors) == 0,
        "structural_errors": structural_errors,
        "dependency_score": dependency_score,
        "dependency_level": level,
        "reasons": reasons
    }
