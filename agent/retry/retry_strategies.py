# agent/retry/retry_strategies.py

from agent.core.llm_factory import get_llm


# ===============================
# EMAIL REWRITE
# ===============================
def rewrite_email(output, guardrail_result):

    llm = get_llm()

    prompt = f"""
Rewrite the following email to fix these issues:

Issues:
{guardrail_result["reasons"]}

Email:
{output}
"""

    return llm.invoke(prompt).content


# ===============================
# DECISION MAKER REWRITE
# ===============================
def rewrite_decision_makers(output, guardrail_result):

    llm = get_llm()

    prompt = f"""
Rewrite decision maker titles to fix:

Issues:
{guardrail_result["reasons"]}

Titles:
{output}
"""

    response = llm.invoke(prompt).content

    return [line.strip() for line in response.split("\n") if line.strip()]


# ===============================
# QUALIFICATION REWRITE
# ===============================
def rewrite_qualification(output, guardrail_result):

    llm = get_llm()

    prompt = f"""
Rewrite qualification analysis to fix:

Issues:
{guardrail_result["reasons"]}

Original Output:
{output}
"""

    return llm.invoke(prompt).content



# ===============================
# RESEARCH REWRITE
# ===============================
def rewrite_research(output, guardrail_result):

    llm = get_llm()

    prompt = f"""
Rewrite the company research to fix these issues:

Issues:
{guardrail_result["reasons"]}

Research:
{output}

Requirements:
- Clear company description
- Pain points
- Product/service clarity
- Structured professional output
"""

    return llm.invoke(prompt).content
