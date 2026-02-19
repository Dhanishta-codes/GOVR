from typing import Dict


def evaluate_workflow(state) -> Dict:

    score = 100
    penalties = []

    guardrails = state.get("guardrail_results", {})
    fallbacks = state.get("dependency_fallbacks", [])

    # Guardrail penalties
    for node, result in guardrails.items():
        if not result.get("passed", True):
            score -= 10
            penalties.append(f"{node} failed guardrail")

    # Fallback penalties
    if fallbacks:
        score -= 15
        penalties.append("Dependency fallbacks used")

    # Missing contacts penalty
    if not state.get("contacts"):
        score -= 20
        penalties.append("No validated contacts")

    return {
        "workflow_score": max(score, 0),
        "recommended_action": "CONTINUE" if score >= 60 else "REVIEW",
        "penalties": penalties
    }
