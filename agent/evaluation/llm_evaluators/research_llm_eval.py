from agent.core.llm_factory import get_llm
from langchain_core.messages import HumanMessage


def research_llm_evaluator(text: str) -> dict:

    llm = get_llm()

    prompt = f"""
Evaluate this company research for sales intelligence quality.

Score from 0 to 10.
Return JSON with:
score
confidence
strengths
weaknesses
business_impact
optimization_priority

Research:
{text}
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    import json
    result = json.loads(response.content)

    return result
