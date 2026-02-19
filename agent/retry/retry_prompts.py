EMAIL_REWRITE_PROMPT = """
Rewrite the email below to fix the listed issues.

Issues:
{reasons}

Rules:
- Remove exaggerated or spammy claims
- Keep tone professional and human
- Do not add new claims
- Keep under 150 words

Email:
{email}
"""


DECISION_MAKER_REWRITE_PROMPT = """
Refine the decision maker titles below.

Issues:
{reasons}

Rules:
- Only include ICP-aligned roles
- Prefer senior revenue or operations titles
- Return 2–3 titles max

Titles:
{titles}
"""
