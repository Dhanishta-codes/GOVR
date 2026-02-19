from typing import Dict


def evaluate_email(email_text: str, company_research: str) -> Dict:

    score = 0
    reasons = []

    # -------------------------
    # Personalization Check
    # -------------------------
    if any(word.lower() in email_text.lower() for word in company_research.split()[:10]):
        score += 2
    else:
        reasons.append("Email lacks company personalization")

    # -------------------------
    # Value Proposition Clarity
    # -------------------------
    if "help" in email_text.lower() or "solve" in email_text.lower():
        score += 2
    else:
        reasons.append("Value proposition unclear")

    # -------------------------
    # CTA Presence
    # -------------------------
    if "meeting" in email_text.lower() or "call" in email_text.lower():
        score += 2
    else:
        reasons.append("Weak or missing CTA")

    # -------------------------
    # Length Optimization
    # -------------------------
    if 80 <= len(email_text.split()) <= 180:
        score += 2
    else:
        reasons.append("Email length not optimized")

    # -------------------------
    # Tone Safety
    # -------------------------
    spam_words = ["buy now", "act fast", "limited offer"]

    if not any(word in email_text.lower() for word in spam_words):
        score += 2
    else:
        reasons.append("Spam-like tone detected")

    return {
        "score": score,
        "max_score": 10,
        "recommended_action": "CONTINUE" if score >= 6 else "REWRITE",
        "reasons": reasons
    }
