# ============================================================
# BENCHMARK SCORING ENGINE (Enterprise + Revenue Weighted)
# Compares workflow performance against industry standards
# Produces unified KPI for Control + Learning layers
# ============================================================

from typing import Dict


# ------------------------------------------------------------
# INDUSTRY BASELINES (Market Reference)
# ------------------------------------------------------------
INDUSTRY_BASELINES = {
    "research": 75,
    "qualification": 70,
    "email": 80,
    "decision_maker": 75,
    "contact": 70,
    "governance": 85
}


# ------------------------------------------------------------
# REVENUE-WEIGHTED DIMENSION IMPORTANCE
# (Higher weight = more impact on revenue conversion)
# ------------------------------------------------------------
DIMENSION_WEIGHTS = {
    "research": 0.15,
    "qualification": 0.15,
    "email": 0.30,
    "decision_maker": 0.15,
    "contact": 0.10,
    "governance": 0.15
}


# ------------------------------------------------------------
# BENCHMARK GAP CALCULATION
# ------------------------------------------------------------
def calculate_benchmark_gap(workflow_performance: Dict) -> Dict:

    breakdown = workflow_performance.get("dimension_breakdown", {})

    if not breakdown:
        return {
            "benchmark_score": 0,
            "benchmark_position": "INSUFFICIENT_DATA",
            "average_gap": 0,
            "dimension_analysis": {},
            "confidence_score": 0
        }

    benchmark_results = {}
    weighted_gap = 0
    total_weight = 0

    for dimension, score in breakdown.items():

        baseline = INDUSTRY_BASELINES.get(dimension, 75)
        weight = DIMENSION_WEIGHTS.get(dimension, 0.1)

        gap = score - baseline

        benchmark_results[dimension] = {
            "score": score,
            "industry_baseline": baseline,
            "gap": round(gap, 2),
            "weight": weight,
            "status": "ABOVE_MARKET" if gap >= 0 else "BELOW_MARKET"
        }

        weighted_gap += gap * weight
        total_weight += weight

    # --------------------------------------------------------
    # Weighted Average Gap
    # --------------------------------------------------------
    avg_gap = round(weighted_gap / total_weight, 2)

    # --------------------------------------------------------
    # Unified Benchmark Score (0–100)
    # Base 50 = Market Parity Anchor
    # --------------------------------------------------------
    benchmark_score = 50 + avg_gap
    benchmark_score = max(0, min(100, benchmark_score))

    # --------------------------------------------------------
    # Competitive Tier Classification
    # --------------------------------------------------------
    if benchmark_score >= 85:
        benchmark_position = "ELITE"
    elif benchmark_score >= 75:
        benchmark_position = "STRONG"
    elif benchmark_score >= 65:
        benchmark_position = "MARKET_PARITY"
    else:
        benchmark_position = "BELOW_MARKET_STANDARD"

    # --------------------------------------------------------
    # Confidence Score (based on completeness of dimensions)
    # --------------------------------------------------------
    expected_dimensions = len(INDUSTRY_BASELINES)
    coverage_ratio = len(breakdown) / expected_dimensions
    confidence_score = round(coverage_ratio * 100, 2)

    return {
        "benchmark_score": round(benchmark_score, 2),
        "benchmark_position": benchmark_position,
        "average_gap": avg_gap,
        "dimension_analysis": benchmark_results,
        "confidence_score": confidence_score
    }
