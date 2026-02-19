# ============================================================
# BUSINESS EFFECTIVENESS ENGINE
# Revenue Conversion Readiness Intelligence
# ============================================================

from typing import Dict


def calculate_business_effectiveness(state: Dict) -> Dict:
    """
    Outputs a normalized business_score (0–100)
    representing revenue readiness.
    """

    workflow_score = (
        state.get("evaluation_results", {})
        .get("workflow", {})
        .get("workflow_score", 0)
    )

    qualification_score = state.get("qualification_score", 0) * 10
    contact_count = len(state.get("contacts", []))

    benchmark_position = (
        state.get("evaluation_results", {})
        .get("benchmark", {})
        .get("benchmark_position", "MARKET_PARITY")
    )

    # --------------------------------------------------
    # Conversion Probability Estimate (0–1)
    # --------------------------------------------------

    conversion_probability = (
        (workflow_score * 0.4) +
        (qualification_score * 0.4) +
        (min(contact_count, 5) * 4)
    ) / 100

    conversion_probability = round(min(conversion_probability, 1.0), 2)

    # --------------------------------------------------
    # Benchmark Multiplier
    # --------------------------------------------------

    benchmark_multiplier = {
        "ELITE": 1.1,
        "STRONG": 1.05,
        "MARKET_PARITY": 1.0,
        "BELOW_MARKET_STANDARD": 0.9
    }.get(benchmark_position, 1.0)

    # --------------------------------------------------
    # Final Business Score (0–100)
    # --------------------------------------------------

    business_score = round(
        conversion_probability * 100 * benchmark_multiplier,
        2
    )

    # --------------------------------------------------
    # Business Signal
    # --------------------------------------------------

    if business_score >= 80:
        signal = "HIGH_REVENUE_POTENTIAL"
    elif business_score >= 60:
        signal = "MODERATE_REVENUE_POTENTIAL"
    else:
        signal = "LOW_REVENUE_POTENTIAL"

    return {
        "business_score": business_score,
        "conversion_probability_estimate": conversion_probability,
        "benchmark_position": benchmark_position,
        "business_signal": signal
    }
