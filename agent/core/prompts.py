"""Prompt templates for the SDR agent"""

RESEARCH_PROMPT = """You are a sales researcher. Your job is to research a company and identify key information that would be useful for sales outreach.

Company to research: {company_name}

Using the search results provided, extract and summarize:
1. What does this company do? (products/services)
2. Company size (employees, revenue if available)
3. Recent news or developments
4. Pain points or challenges they might face
5. Technology stack (if mentioned)

Be concise but thorough. Focus on information relevant to sales outreach.

Search results:
{search_results}
"""

DECISION_MAKER_PROMPT = """Based on the company research below, identify the most likely decision-makers for a sales tool/service.

Company: {company_name}
Research: {company_research}

Provide 2-3 potential job titles of people we should reach out to, and explain why they'd be good contacts.
Consider our ICP: {icp_criteria}

Format your response as:
Title: [Job Title]
Why: [Brief explanation]
"""

EMAIL_GENERATION_PROMPT = """You are an expert sales copywriter. Write a personalized cold outreach email.

Company: {company_name}
Decision Maker Title: {decision_maker_title}
Company Research: {company_research}

Our company: {our_company_name}
What we do: {our_value_prop}

Write a short, personalized email (max 150 words) that:
1. Opens with a specific observation about their company
2. Identifies a likely pain point
3. Briefly mentions how we can help
4. Ends with a soft CTA (low-pressure ask)

Keep it conversational, not salesy. No buzzwords. Be human.
"""

QUALIFICATION_PROMPT = """Based on the company research, determine if this company is a good fit for outreach.

Company: {company_name}
Research: {company_research}

Our ICP criteria:
{icp_criteria}

Score this lead from 1-10 (10 = perfect fit) and explain your reasoning.
If score is below 5, recommend skipping this lead.

Format:
Score: [1-10]
Reasoning: [explanation]
Recommendation: [PROCEED or SKIP]
"""
