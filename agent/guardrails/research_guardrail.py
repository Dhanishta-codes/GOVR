"""
Research Guardrail
Validates quality + completeness of company research output
"""

from typing import Dict


def research_guardrail(research_text: str) -> Dict:
    """
    Validate research output quality
    """

    reasons = []
    score = 1.0

    if not research_text:
        return {
            "passed": False,
            "score": 0.0,
            "reasons": ["Research output empty"]
        }

    text = research_text.lower()

    # -------------------------------
    # 1. LENGTH CHECK
    # -------------------------------
    if len(research_text) < 500:
        reasons.append("Research too short")
        score -= 0.25

    # -------------------------------
    # 2. COMPANY CONTEXT CHECK
    # -------------------------------
    company_keywords = [
        "company",
        "platform",
        "provides",
        "offers",
        "solution",
        "service"
    ]

    if not any(word in text for word in company_keywords):
        reasons.append("Missing company business context")
        score -= 0.2

    # -------------------------------
    # 3. PAIN POINT CHECK
    # -------------------------------
    pain_keywords = [
        "challenge",
        "pain",
        "problem",
        "risk",
        "competition"
    ]

    if not any(word in text for word in pain_keywords):
        reasons.append("Missing company pain point analysis")
        score -= 0.2

    # -------------------------------
    # 4. PRODUCT / SERVICE CLARITY
    # -------------------------------
    product_keywords = [
        "product",
        "feature",
        "tool",
        "technology",
        "api"
    ]

    if not any(word in text for word in product_keywords):
        reasons.append("Missing product or service clarity")
        score -= 0.2

    # -------------------------------
    # 5. STRUCTURE QUALITY CHECK
    # -------------------------------
    if research_text.count("\n") < 5:
        reasons.append("Research output poorly structured")
        score -= 0.15

    passed = score >= 0.6

    return {
        "passed": passed,
        "score": round(score, 2),
        "reasons": reasons
    }
