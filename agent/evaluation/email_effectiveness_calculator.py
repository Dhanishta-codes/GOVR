# agent/evaluation/email_effectiveness_evaluator.py

from typing import Dict


def evaluate_email_effectiveness(
    email_text: str,
    company_name: str,
    persona: str
) -> Dict:

    scores = {}
    reasons = []

    # ----------------------------
    # Personalization Score
    # ----------------------------
    personalization_score = 0

    if company_name.lower() in email_text.lower():
        personalization_score += 5

    if persona.lower() in email_text.lower():
        personalization_score += 5

    scores["personalization"] = personalization_score


    # ----------------------------
    # Value Proposition Score
    # ----------------------------
    value_keywords = [
        "help",
        "improve",
        "increase",
        "automate",
        "optimize"
    ]

    value_score = sum(
        1 for k in value_keywords if k in email_text.lower()
    ) * 2

    scores["value_proposition"] = min(value_score, 10)


    # ----------------------------
    # CTA Strength
    # ----------------------------
    cta_keywords = [
        "call",
        "chat",
        "meeting",
        "schedule",
        "connect"
    ]

    cta_score = sum(
        1 for k in cta_keywords if k in email_text.lower()
    ) * 2

    scores["cta_strength"] = min(cta_score, 10)


    # ----------------------------
    # Persuasion Score
    # ----------------------------
    persuasion_keywords = [
        "results",
        "impact",
        "outcomes",
        "growth",
        "efficiency"
    ]

    persuasion_score = sum(
        1 for k in persuasion_keywords if k in email_text.lower()
    ) * 2

    scores["persuasion"] = min(persuasion_score, 10)


    # ----------------------------
    # FINAL SCORE
    # ----------------------------
    effectiveness_score = sum(scores.values()) / len(scores)

    if effectiveness_score < 5:
        reasons.append("Low overall persuasion quality")

    return {
        "effectiveness_score": effectiveness_score,
        "dimension_scores": scores,
        "recommended_action": (
            "REWRITE" if effectiveness_score < 5 else "CONTINUE"
        ),
        "reasons": reasons
    }
