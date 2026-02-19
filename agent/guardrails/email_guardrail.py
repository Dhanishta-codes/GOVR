from agent.guardrails.schemas import GuardrailResult


BANNED_PHRASES = [
    "guarantee results",
    "100% success",
    "instant ROI",
    "no risk"
]

SPAM_WORDS = [
    "BUY NOW",
    "LIMITED OFFER",
    "ACT FAST"
]


def email_guardrail(email_text: str) -> GuardrailResult:

    reasons = []
    score = 1.0

    if not email_text or len(email_text.strip()) < 30:
        reasons.append("Email content missing or too short")
        score -= 0.3

    # ---------- Overpromise Detection ----------
    for phrase in BANNED_PHRASES:
        if phrase.lower() in email_text.lower():
            reasons.append(f"Overpromise phrase detected: {phrase}")
            score -= 0.25

    # ---------- Spam Tone Detection ----------
    for word in SPAM_WORDS:
        if word in email_text.upper():
            reasons.append(f"Spam tone detected: {word}")
            score -= 0.25

    # ---------- Length Safety ----------
    if len(email_text) > 1200:
        reasons.append("Email too long")
        score -= 0.2

    # ---------- Risk Classification ----------
    if score >= 0.8:
        risk = "low"
    elif score >= 0.6:
        risk = "medium"
    else:
        risk = "high"

    return GuardrailResult(
        allowed=len(reasons) == 0,
        risk_score=60 if reasons else 0,
        risk_level="HIGH" if reasons else "LOW",
        reasons=reasons,
        recommended_action="REWRITE" if reasons else "CONTINUE"
  )

