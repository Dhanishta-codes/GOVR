# agent/guardrails/schemas.py

from typing import TypedDict, List, Literal


class GuardrailResult(TypedDict):
    allowed: bool
    risk_score: int
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "BLOCKED"]
    reasons: List[str]
    recommended_action: Literal["CONTINUE", "REWRITE", "STOP"]
