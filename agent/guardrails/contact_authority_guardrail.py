import re
import agent.infra.config as config


FREE_EMAIL_DOMAINS = {
    "gmail.com",
    "yahoo.com",
    "outlook.com",
    "hotmail.com",
    "icloud.com"
}


def contact_authority_guardrail(
    contacts: list[dict],
    company_name: str
) -> dict:
    """
    Validates whether contacts are legitimate, relevant, and safe to outreach.
    Standardized Guardrail Contract.
    """

    reasons = []
    validated_contacts = []
    score = 1.0

    if not contacts:
        return {
            "passed": False,
            "reasons": ["No contacts found"],
            "risk_level": "high",
            "score": 0.0,
            "validated_output": []
        }

    company_tokens = company_name.lower().split()

    allowed_titles = [
        t.lower() for t in config.ICP_CRITERIA["decision_maker_titles"]
    ]

    for contact in contacts:

        email = contact.get("email", "")
        name = contact.get("name", "")
        title = contact.get("title", "")

        # -------------------------
        # Completeness Check
        # -------------------------
        if not email or not name:
            score -= 0.15
            continue

        # -------------------------
        # Email Format Check
        # -------------------------
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            score -= 0.15
            continue

        domain = email.split("@")[-1].lower()

        # -------------------------
        # Block Free Domains
        # -------------------------
        if domain in FREE_EMAIL_DOMAINS:
            score -= 0.20
            continue

        # -------------------------
        # Company Domain Alignment
        # -------------------------
        if not any(token in domain for token in company_tokens):
            score -= 0.20
            continue

        # -------------------------
        # Role Authority Check
        # -------------------------
        if title:
            title_lower = title.lower()

            if not any(t in title_lower for t in allowed_titles):
                score -= 0.10
                continue

        validated_contacts.append(contact)

    # -------------------------
    # Failure Conditions
    # -------------------------
    if not validated_contacts:
        reasons.append("No authoritative contacts passed validation")
        score = max(score, 0.0)

    # -------------------------
    # Risk Level Mapping
    # -------------------------
    if score >= 0.8:
        risk = "low"
    elif score >= 0.6:
        risk = "medium"
    else:
        risk = "high"

    return {
        "passed": len(validated_contacts) > 0,
        "reasons": reasons,
        "risk_level": risk,
        "score": round(score, 2),
        "validated_output": validated_contacts
    }
