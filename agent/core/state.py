from typing import TypedDict


class AgentState(TypedDict):
    company_name: str
    search_results: str
    company_research: str
    qualification_score: int
    qualification_reasoning: str

    guardrail_results: dict
    workflow_guardrail_summary: dict

    decision_maker_titles: list[str]
    outreach_email: str

    status: str
    error: str | None

    control_summary: dict

    evaluation_results: dict
    workflow_evaluation_summary: dict

    control_flags: list
    contacts: list[dict]
    emails_sent: list[dict]
    linkedin_requests: list[dict]
    sheets_logged: bool

    human_override: dict
    override_history: list[dict]

