"""Agent nodes - individual steps in the SDR workflow"""

from langchain_core.messages import HumanMessage
import agent.infra.config as config
from agent.core import prompts
from agent.guardrails.email_guardrail import email_guardrail
from tools import research

from agent.core.llm_factory import get_llm
from agent.core.state import AgentState

from agent.guardrails.research_guardrail import research_guardrail
from agent.guardrails.qualification_guardrail import qualification_guardrail
from agent.guardrails.decision_maker_guardrail import decision_maker_guardrail
from agent.guardrails.contact_authority_guardrail import contact_authority_guardrail
from agent.guardrails.guardrail_aggregator import aggregate_guardrails

from agent.retry.retry_engine import retry_with_guardrail
from agent.retry.retry_strategies import (
    rewrite_qualification,
    rewrite_research,
    rewrite_email,
    rewrite_decision_makers
)

from agent.evaluation.research_evaluator import evaluate_research
from agent.evaluation.email_evaluator import evaluate_email
from agent.evaluation.workflow_evaluator import evaluate_workflow



# ======================================================
# NODE 1 — COMPANY RESEARCH
# ======================================================
def research_node(state: AgentState) -> AgentState:

    # ---------- DEPENDENCY CHECK ----------
    if not state.get("company_research"):

        print("🚨 Qualification blocked — missing research")

        state["status"] = "blocked_by_dependency"

        state.setdefault("dependency_failures", []).append({
            "node": "qualification",
            "reason": "Missing company research"
        })

        return state

    print(f"\n🔍 Researching {state['company_name']}...")

    info = research.search_company_info(state["company_name"])
    news = research.search_company_news(state["company_name"])

    if not info["success"]:
        state["status"] = "failed"
        state["error"] = info["error"]
        return state

    results = info["results"] + news.get("results", [])
    formatted = research.format_search_results(results)

    state["search_results"] = formatted

    prompt = prompts.RESEARCH_PROMPT.format(
        company_name=state["company_name"],
        search_results=formatted
    )

    def attempt():
        llm = get_llm()
        return llm.invoke([HumanMessage(content=prompt)]).content

    result = retry_with_guardrail(
        attempt_fn=attempt,
        guardrail_fn=research_guardrail,
        rewrite_fn=rewrite_research,
        max_retries=2
    )

    state.setdefault("guardrail_results", {})
    state["guardrail_results"]["research"] = {
        "passed": result["passed"],
        "reasons": result.get("error", []),
        "retry_count": result.get("attempts", 0)
    }

    if not result["passed"]:
        state["status"] = "blocked_by_guardrail"
        state["error"] = "Research failed quality checks"
        return state

    state["company_research"] = result["output"]

    # ---------- Evaluation ----------
    evaluation = evaluate_research(result["output"])

    state.setdefault("evaluation_results", {})
    state["evaluation_results"]["research"] = evaluation

    if evaluation["recommended_action"] != "CONTINUE":
        state.setdefault("control_flags", [])
        state["control_flags"].append({
            "node": "research",
            "action": evaluation["recommended_action"],
            "reasons": evaluation["reasons"]
        })

    print("✅ Research completed")
    return state


# ======================================================
# NODE 2 — QUALIFICATION
# ======================================================
def qualification_node(state: AgentState) -> AgentState:

    # ---------- DEPENDENCY CHECK ----------
    if not state.get("company_research"):
        
        print("🚨 Qualification blocked — missing research")
        
        state["status"] = "blocked_by_dependency"
        
        state.setdefault("dependency_failures", []).append({
            "node": "qualification",
            "reason": "Missing company research"
        })
        
        return state

    print("\n📊 Qualifying lead...")

    def attempt():
        llm = get_llm()

        prompt = prompts.QUALIFICATION_PROMPT.format(
            company_name=state["company_name"],
            company_research=state["company_research"],
            icp_criteria=str(config.ICP_CRITERIA)
        )

        return llm.invoke([HumanMessage(content=prompt)]).content

    def guardrail_wrapper(output):

        try:
            score = int(output.split("Score:")[1].split("/")[0].strip())
        except Exception:
            score = None

        return qualification_guardrail(score, output)

    result = retry_with_guardrail(
        attempt_fn=attempt,
        guardrail_fn=guardrail_wrapper,
        rewrite_fn=rewrite_qualification
    )

    state.setdefault("guardrail_results", {})
    state["guardrail_results"]["qualification_retry"] = result

    if not result["passed"]:
        state["status"] = "blocked_by_guardrail"
        state["error"] = "Qualification failed after retries"
        return state

    final_output = result["output"]

    try:
        score = int(final_output.split("Score:")[1].split("/")[0].strip())
    except Exception:
        score = 5

    state["qualification_score"] = score
    state["qualification_reasoning"] = final_output
    state["status"] = "qualified" if score >= 5 else "disqualified"

    print(f"✅ Qualification passed after {result['attempts']} retries")
    return state


# ======================================================
# NODE 3 — DECISION MAKERS
# ======================================================
def identify_decision_makers_node(state: AgentState) -> AgentState:

    if state["status"] == "disqualified":
        return state
    
    # ---------- DEPENDENCY CHECK ----------
    if not state.get("company_research"):
        
        print("⚠ Missing research — using heuristic persona discovery")
        
        state.setdefault("dependency_fallbacks", []).append({
            "node": "identify_decision_makers",
            "reason": "Missing research context"
        })
        
        # Lightweight fallback persona
        state["decision_maker_titles"] = [
            "Head of Sales",
            "VP Revenue",
            "Growth Lead"
        ]
        return state

    print("\n👔 Finding decision makers...")

    def attempt():

        llm = get_llm()

        prompt = prompts.DECISION_MAKER_PROMPT.format(
            company_name=state["company_name"],
            company_research=state["company_research"],
            icp_criteria=str(config.ICP_CRITERIA)
        )

        response = llm.invoke([HumanMessage(content=prompt)])

        return [
            line.replace("Title:", "").strip()
            for line in response.content.split("\n")
            if line.startswith("Title:")
        ]

    result = retry_with_guardrail(
        attempt_fn=attempt,
        guardrail_fn=decision_maker_guardrail,
        rewrite_fn=rewrite_decision_makers
    )

    state.setdefault("guardrail_results", {})
    state["guardrail_results"]["decision_maker_retry"] = result

    if not result["passed"]:
        state["status"] = "blocked_by_guardrail"
        state["error"] = "Decision maker selection failed after retries"
        return state

    validated = decision_maker_guardrail(result["output"])["validated_titles"]
    state["decision_maker_titles"] = validated

    print(f"✅ Decision makers selected after {result['attempts']} retries")
    return state


# ======================================================
# NODE 4 — EMAIL GENERATION
# ======================================================
def generate_email_node(state: AgentState) -> AgentState:

    if state["status"] == "disqualified":
        return state
    
     # ---------- DEPENDENCY CHECK ----------
    if not state.get("decision_maker_titles"):
        print("⚠ No decision makers found — falling back to default persona")
        state["decision_maker_titles"] = ["Head of Sales"]
        state.setdefault("dependency_fallbacks", []).append({
            "node": "generate_email",
            "reason": "Missing decision makers"
        })

    print("\n✍️ Generating email...")

    def attempt():
        llm = get_llm()

        prompt = prompts.EMAIL_GENERATION_PROMPT.format(
            company_name=state["company_name"],
            decision_maker_title=state["decision_maker_titles"][0],
            company_research=state["company_research"],
            our_company_name=config.YOUR_COMPANY["name"],
            our_value_prop=config.YOUR_COMPANY["value_proposition"]
        )

        return llm.invoke([HumanMessage(content=prompt)]).content

    result = retry_with_guardrail(
        attempt_fn=attempt,
        guardrail_fn=email_guardrail,
        rewrite_fn=rewrite_email
    )

    state.setdefault("guardrail_results", {})
    state["guardrail_results"]["email_retry"] = result

    if not result["passed"]:
        state["status"] = "blocked_by_guardrail"
        state["error"] = "Email failed after retries"
        return state

    state["outreach_email"] = result["output"]

    from agent.evaluation.email_effectiveness_evaluator import evaluate_email_effectiveness
    evaluation = evaluate_email_effectiveness(
        email_text=result["output"],
        company_name=state["company_name"],
        persona=state["decision_maker_titles"][0]
    )

    state.setdefault("evaluation_results", {})
    state["evaluation_results"]["email"] = evaluation

    if evaluation["recommended_action"] == "REWRITE":
        state.setdefault("control_flags", []).append({
            "node": "email",
            "reasons": evaluation["reasons"]
        })
    
    state["status"] = "email_ready"

    print(f"✅ Email passed after {result['attempts']} retries")
    return state


# ======================================================
# NODE 5 — CONTACT DISCOVERY
# ======================================================
def find_contacts_node(state: AgentState) -> AgentState:

    if state["status"] == "disqualified":
        return state
    
    # ---------- DEPENDENCY CHECK ----------
    if not state.get("decision_maker_titles"):

        print("⚠ Missing decision makers — using ICP fallback")

        fallback_titles = config.ICP_CRITERIA.get("decision_maker_titles", ["Head of Sales"])

        state["decision_maker_titles"] = fallback_titles[:3]

        state.setdefault("dependency_fallbacks", []).append({
            "node": "find_contacts",
            "reason": "Missing decision maker titles"
        })
        
    print("\n🔍 Finding contacts...")

    from tools import email_finder

    contacts = email_finder.search_people_at_company(
        state["company_name"],
        state["decision_maker_titles"]
    ) or []

    guardrail = contact_authority_guardrail(
        contacts=contacts,
        company_name=state["company_name"]
    )

    state.setdefault("guardrail_results", {})
    state["guardrail_results"]["contacts"] = guardrail

    if not guardrail["passed"]:
        state["status"] = "blocked_by_guardrail"
        state["error"] = str(guardrail["reasons"])
        return state

    state["contacts"] = guardrail["validated_contacts"]

    print(f"✅ {len(state['contacts'])} authoritative contacts validated")
    return state


# ======================================================
# NODE 6 — EMAIL SENDING
# ======================================================
def send_emails_node(state: AgentState) -> AgentState:

    if not config.ENABLE_EMAIL_SENDING:
        return state
    
    # ---------- DEPENDENCY CHECK ----------
    if not state.get("decision_maker_titles"):

        print("⚠ Missing decision makers — using ICP fallback")

        fallback_titles = config.ICP_CRITERIA.get("decision_maker_titles", ["Head of Sales"])

        state["decision_maker_titles"] = fallback_titles[:3]

        state.setdefault("dependency_fallbacks", []).append({
            "node": "find_contacts",
            "reason": "Missing decision maker titles"
        })

    print("\n📧 Sending emails...")

    from tools import email_sender
    from agent.guardrails.email_sending_guardrail import email_sending_guardrail
    import time

    guardrail = email_sending_guardrail(state)

    state.setdefault("guardrail_results", {})
    state["guardrail_results"]["email_sending"] = guardrail

    if not guardrail["passed"]:
        state["status"] = "blocked_by_guardrail"
        state["error"] = str(guardrail["reasons"])
        return state

    results = []

    for contact in guardrail["validated_contacts"]:
        res = email_sender.send_outreach_email(
            contact=contact,
            email_body=state["outreach_email"]
        )
        results.append(res)
        time.sleep(2)

    state["emails_sent"] = results

    print(f"✅ Sent {len(results)} emails safely")
    return state


# ======================================================
# NODE 7 — LINKEDIN OUTREACH
# ======================================================
def linkedin_outreach_node(state: AgentState) -> AgentState:

    if not config.ENABLE_LINKEDIN_OUTREACH:
        return state
    
    # ---------- DEPENDENCY CHECK ----------
    if not state.get("decision_maker_titles"):

        print("⚠ LinkedIn outreach fallback persona")

        state["decision_maker_titles"] = ["Head of Sales"]

        state.setdefault("dependency_fallbacks", []).append({
            "node": "linkedin_outreach",
            "reason": "Missing persona"
        })
    
    from tools import linkedin_bot

    llm = get_llm()

    msg = llm.invoke([
        HumanMessage(
            content=f"""
Write LinkedIn connection message for {state['company_name']}
Role: {state['decision_maker_titles'][0]}
"""
        )
    ]).content

    state["linkedin_requests"] = [
        linkedin_bot.linkedin_outreach(
            company_name=state["company_name"],
            title=state["decision_maker_titles"][0],
            message=msg,
            max_requests=3
        )
    ]

    return state


# ======================================================
# NODE 8 — SHEETS LOGGING
# ======================================================
def log_to_sheets_node(state: AgentState) -> AgentState:

    if not config.ENABLE_SHEETS_LOGGING:
        return state

    from tools import sheets_logger

    tracker = sheets_logger.init_tracker()

    if tracker:
        for contact in state.get("contacts", []):
            tracker.log_prospect({
                "company": state["company_name"],
                "contact": contact.get("name"),
                "email": contact.get("email"),
                "score": state["qualification_score"]
            })

        state["sheets_logged"] = True

    return state


# ======================================================
# GUARDRAIL AGGREGATION
# ======================================================
def guardrail_aggregation_node(state: AgentState) -> AgentState:

    print("\n🛡 Aggregating guardrail results...")

    state.setdefault("evaluation_results", {})

    # -----------------------------------------
    # 1️⃣ Workflow Performance Evaluation
    # -----------------------------------------
    from agent.evaluation.workflow_performance_engine import calculate_workflow_performance

    performance = calculate_workflow_performance(state)
    state["evaluation_results"]["workflow"] = performance

    # -----------------------------------------
    # 2️⃣ Benchmark Analysis
    # -----------------------------------------
    from agent.evaluation.benchmark_engine import calculate_benchmark_gap

    benchmark = calculate_benchmark_gap(performance)
    state["evaluation_results"]["benchmark"] = benchmark

    # -----------------------------------------
    # 3️⃣ Business Effectiveness Intelligence
    # -----------------------------------------
    from agent.evaluation.business_effectiveness_engine import calculate_business_effectiveness

    business = calculate_business_effectiveness(state)
    state["evaluation_results"]["business_effectiveness"] = business

    from agent.evaluation.learning_memory_engine import store_workflow_result

    store_workflow_result(state)


    from agent.evaluation.workflow_intelligence_engine import calculate_workflow_intelligence

    intelligence = calculate_workflow_intelligence(state)

    state.setdefault("evaluation_results", {})
    state["evaluation_results"]["workflow_intelligence"] = intelligence



    # -----------------------------------------
    # 4️⃣ Guardrail Aggregation (Safety Layer)
    # -----------------------------------------
    aggregation = aggregate_guardrails(state)
    state["workflow_guardrail_summary"] = aggregation

    if not aggregation["workflow_passed"]:
        state["status"] = "blocked_by_guardrail"
        state["error"] = str(aggregation["reasons"])

    return state


# ======================================================
# CONTROL VALIDATION
# ======================================================
def control_validation_node(state: AgentState) -> AgentState:

    print("\n🧭 Running Adaptive Control Engine...")

    from agent.governance.control_engine import control_decision_engine

    decision = control_decision_engine(state)

    state["control_summary"] = decision

    print(f"Decision: {decision['decision']}")
    print(f"Risk Level: {decision['risk_level']}")
    print(f"Confidence: {decision['confidence_score']}")

    if decision["decision"] == "STOP":
        state["status"] = "blocked_by_control"
        state["error"] = decision["reasons"]

    elif decision["decision"] == "REWRITE_EMAIL":
        state.setdefault("control_flags", []).append({
            "node": "generate_email",
            "action": "RETRY"
        })
    

    
    return state


# ======================================================
# PRE-SENDING CONTROL
# ======================================================
def control_pre_sending_node(state: AgentState) -> AgentState:

    print("\n🧭 Running Pre-Sending Control Validation...")

    from agent.governance.workflow_validator import validate_workflow_readiness

    control_result = validate_workflow_readiness(state)

    if not control_result["workflow_allowed"]:
        state["status"] = "blocked_by_control"
        state["error"] = str(control_result["reasons"])

    return state


def evaluation_node(state: AgentState) -> AgentState:
    """
    Final reporting + learning trend node.
    No scoring logic here.
    """

    print("\n📊 Final Evaluation Summary")

    from agent.evaluation.learning_memory import calculate_performance_trend

    trend = calculate_performance_trend()

    state.setdefault("evaluation_results", {})
    state["evaluation_results"]["learning_trend"] = trend

    print(f"Performance Trend: {trend}")

    return state


def workflow_effectiveness_node(state: AgentState) -> AgentState:

    print("\n📊 Evaluating overall workflow effectiveness...")

    from agent.evaluation.workflow_effectiveness_evaluator import evaluate_workflow_effectiveness

    evaluation = evaluate_workflow_effectiveness(state)

    state.setdefault("evaluation_results", {})
    state["evaluation_results"]["workflow"] = evaluation

    print(f"Workflow Score: {evaluation['workflow_score']}")
    print(f"Recommended Action: {evaluation['recommended_action']}")

    if evaluation["recommended_action"] != "CONTINUE":
        state.setdefault("control_flags", []).append({
            "node": "workflow_effectiveness",
            "action": evaluation["recommended_action"],
            "reasons": evaluation["reasons"]
        })

    return state


from agent.evaluation.learning_memory_engine import store_workflow_result

