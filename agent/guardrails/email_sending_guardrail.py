# agent/guardrails/email_sending_guardrail.py

FREE_EMAIL_DOMAINS = {
    "gmail.com",
    "yahoo.com",
    "outlook.com",
    "hotmail.com",
    "icloud.com"
}

MAX_EMAILS_PER_RUN = 3


def email_sending_guardrail(state: dict) -> dict:
    """
    Final execution safety guardrail before sending emails.
    Standard Guardrail Contract.
    """

    reasons = []
    validated_contacts = []
    score = 1.0

    # -------------------------
    # 1. Workflow Status Safety
    # -------------------------
    if state.get("status") == "disqualified":
        reasons.append("Lead disqualified")
        score -= 0.4

    if state.get("status") == "blocked_by_guardrail":
        reasons.append("Workflow already blocked")
        score -= 0.6

    # -------------------------
    # 2. Email Content Safety
    # -------------------------
    email_body = state.get("outreach_email", "")

    if not email_body or len(email_body.strip()) < 50:
        reasons.append("Outreach email too short or missing")
        score -= 0.3

    # -------------------------
    # 3. Contact Validation
    # -------------------------
    contacts = state.get("contacts", [])

    if not contacts:
        reasons.append("No contacts available")
        score -= 0.4
    else:
        for contact in contacts:

            email = (contact.get("email") or "").lower()

            if not email:
                score -= 0.1
                continue

            domain = email.split("@")[-1]

            if domain in FREE_EMAIL_DOMAINS:
                score -= 0.2
                continue

            validated_contacts.append(contact)

    if not validated_contacts:
        reasons.append("No valid corporate contacts available")

    # -------------------------
    # 4. Volume Safety
    # -------------------------
    if len(validated_contacts) > MAX_EMAILS_PER_RUN:
        validated_contacts = validated_contacts[:MAX_EMAILS_PER_RUN]

    # -------------------------
    # 5. Risk Classification
    # -------------------------
    if score >= 0.8:
        risk = "low"
    elif score >= 0.6:
        risk = "medium"
    else:
        risk = "high"

    return {
        "passed": score >= 0.6 and len(validated_contacts) > 0,
        "reasons": reasons,
        "risk_level": risk,
        "score": round(score, 2),
        "validated_output": validated_contacts
    }
