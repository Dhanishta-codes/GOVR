# ============================================================
# LEARNING MEMORY ENGINE
# Stores historical workflow + business performance
# ============================================================

from typing import Dict, List

# Simple in-memory store (MVP)
WORKFLOW_HISTORY: List[Dict] = []


def store_workflow_result(state: Dict) -> None:
    """
    Save workflow performance snapshot.
    """

    snapshot = {
        "workflow_score": state.get("evaluation_results", {})
            .get("workflow", {})
            .get("overall_score", 0),

        "business_score": state.get("evaluation_results", {})
            .get("business_effectiveness", {})
            .get("business_score", 0),

        "benchmark_position": state.get("evaluation_results", {})
            .get("benchmark", {})
            .get("benchmark_position", "UNKNOWN")
    }

    WORKFLOW_HISTORY.append(snapshot)


# ============================================================
# LEARNING MEMORY ENGINE
# Finalized MVP Version
# ============================================================

from typing import Dict, List

WORKFLOW_HISTORY: List[Dict] = []


def store_workflow_result(state: Dict) -> None:
    snapshot = {
        "workflow_score": state.get("evaluation_results", {})
            .get("workflow", {})
            .get("overall_score", 0),

        "business_score": state.get("evaluation_results", {})
            .get("business_effectiveness", {})
            .get("business_score", 0),

        "benchmark_position": state.get("evaluation_results", {})
            .get("benchmark", {})
            .get("benchmark_position", "UNKNOWN")
    }

    WORKFLOW_HISTORY.append(snapshot)


def get_learning_signal() -> Dict:
    """
    Converts historical outcomes into control signals.
    """

    if len(WORKFLOW_HISTORY) < 3:
        return {
            "confidence": 0.5,
            "control_bias": "NEUTRAL"
        }

    avg_workflow = sum(w["workflow_score"] for w in WORKFLOW_HISTORY) / len(WORKFLOW_HISTORY)
    avg_business = sum(w["business_score"] for w in WORKFLOW_HISTORY) / len(WORKFLOW_HISTORY)

    # Confidence reflects stability + effectiveness
    confidence = min(1.0, (avg_workflow + avg_business) / 200)

    if avg_business >= 75:
        bias = "AGGRESSIVE"
    elif avg_business >= 60:
        bias = "NEUTRAL"
    else:
        bias = "CONSERVATIVE"

    return {
        "confidence": round(confidence, 2),
        "control_bias": bias,
        "avg_workflow_score": round(avg_workflow, 1),
        "avg_business_score": round(avg_business, 1)
    }
