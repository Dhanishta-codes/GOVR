# ============================================================
# ADAPTIVE THRESHOLD ENGINE
# Uses learning memory to tune control strictness
# ============================================================

from agent.evaluation.learning_memory_engine import get_learning_signal


def get_adaptive_thresholds() -> dict:
    """
    Dynamically adjusts thresholds based on historical performance.
    """

    learning = get_learning_signal()

    avg_workflow = learning.get("avg_workflow_score", 75)
    avg_business = learning.get("avg_business_score", 70)
    confidence = learning.get("confidence", 0.5)

    # -----------------------------
    # Base thresholds (defaults)
    # -----------------------------
    min_confidence = 0.75
    rewrite_confidence = 0.82

    # -----------------------------
    # Adaptive adjustment
    # -----------------------------
    # High-performing system → more autonomy
    if avg_workflow >= 85 and avg_business >= 80 and confidence >= 0.7:
        min_confidence -= 0.05
        rewrite_confidence -= 0.05

    # Underperforming system → stricter governance
    elif avg_workflow < 70 or avg_business < 65:
        min_confidence += 0.05
        rewrite_confidence += 0.05

    return {
        "min_confidence": round(min_confidence, 2),
        "rewrite_confidence": round(rewrite_confidence, 2),
        "learning_confidence": confidence,
        "avg_workflow_score": avg_workflow,
        "avg_business_score": avg_business
    }
