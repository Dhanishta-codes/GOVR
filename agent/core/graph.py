"""LangGraph workflow for SDR agent"""

from langgraph.graph import StateGraph, END
from agent.guardrails.universal_guardrail import universal_guardrail
from agent.core.state import AgentState

from agent.core.nodes import evaluation_node
from agent.core.nodes import workflow_effectiveness_node
from agent.governance.human_override_engine import apply_human_override
from agent.governance.human_override_node import human_override_node





from agent.core.nodes import (
    research_node,
    qualification_node,
    identify_decision_makers_node,
    generate_email_node,
    find_contacts_node,
    send_emails_node,
    linkedin_outreach_node,
    log_to_sheets_node,
    guardrail_aggregation_node,
    control_validation_node
)

# ===============================
# UNIVERSAL GUARDRAIL ROUTER
# ===============================
def universal_guardrail_router(state: AgentState, node_name: str) -> str:

    result = universal_guardrail(
        state=state,
        node_name=node_name
    )

    state.setdefault("guardrail_results", {})
    state["guardrail_results"][node_name] = result

    if not result["passed"]:
        state["status"] = "blocked_by_guardrail"
        state["error"] = str(result["reasons"])
        return "end"

    return "continue"


# ===============================
# QUALIFICATION ROUTER
# ===============================
def should_continue_after_qualification(state: AgentState) -> str:
    if state["status"] in ["disqualified", "blocked_by_guardrail"]:
        return "end"
    return "continue"


# ===============================
# AGGREGATION ROUTER
# ===============================
def router_after_aggregation(state: AgentState) -> str:

    summary = state.get("workflow_guardrail_summary", {})

    if not summary.get("workflow_passed", True):
        return "end"

    return "continue"


# ===============================
# CONTROL ROUTER
# ===============================
def router_after_control(state: AgentState) -> str:

    if state.get("status") == "blocked_by_control":
        return "end"

    return "continue"


# ===============================
# GRAPH CREATION
# ===============================
def create_sdr_graph():

    workflow = StateGraph(AgentState)

    # ---------- Phase 1 Nodes ----------
    workflow.add_node("research", research_node)
    workflow.add_node("qualification", qualification_node)
    workflow.add_node("identify_decision_makers", identify_decision_makers_node)
    workflow.add_node("generate_email", generate_email_node)

    # ---------- Governance Nodes ----------
    workflow.add_node("aggregate_guardrails", guardrail_aggregation_node)
    workflow.add_node("control_validation", control_validation_node)
    workflow.add_node("evaluation", evaluation_node)


    # ---------- Phase 2 Nodes ----------
    workflow.add_node("find_contacts", find_contacts_node)
    workflow.add_node("send_emails", send_emails_node)
    workflow.add_node("linkedin_outreach", linkedin_outreach_node)
    workflow.add_node("log_to_sheets", log_to_sheets_node)
    
    workflow.add_node("human_override_gate", human_override_node)




    # ---------- ENTRY ----------
    workflow.set_entry_point("research")

    # ===============================
    # RESEARCH → UNIVERSAL → QUALIFICATION
    # ===============================
    workflow.add_conditional_edges(
        "research",
        lambda s: universal_guardrail_router(s, "research"),
        {
            "continue": "qualification",
            "end": END
        }
    )

    # ===============================
    # QUALIFICATION → DECISION MAKERS
    # ===============================
    workflow.add_conditional_edges(
        "qualification",
        should_continue_after_qualification,
        {
            "continue": "identify_decision_makers",
            "end": END
        }
    )

    # ===============================
    # DECISION MAKERS → EMAIL
    # ===============================
    workflow.add_edge(
        "identify_decision_makers",
        "generate_email"
    )

    workflow.add_edge("generate_email", "aggregate_guardrails")


    # ===============================
    # AGGREGATION → CONTROL
    # ===============================
    workflow.add_edge(
        "aggregate_guardrails",
        "control_validation"
    )
    
    # ===============================
    # CONTROL → HUMAN OVERRIDE
    # ===============================
    workflow.add_edge(
        "control_validation",
        "human_override_gate"
    )
    
    # ===============================
    # HUMAN OVERRIDE → EXECUTION
    # ===============================
    workflow.add_conditional_edges(
        "human_override_gate",
        router_after_control,
        {
            "continue": "find_contacts",
            "end": END
        }
    )
    
    


    # ===============================
    # EXECUTION FLOW
    # ===============================
    workflow.add_edge("find_contacts", "send_emails")
    workflow.add_edge("send_emails", "linkedin_outreach")
    workflow.add_edge("linkedin_outreach", "log_to_sheets")
    workflow.add_edge("log_to_sheets", "evaluation")
    workflow.add_edge("evaluation", END)


    return workflow.compile()


# ===============================
# RUNNER
# ===============================
def run_sdr_agent(company_name: str) -> AgentState:

    graph = create_sdr_graph()

    initial_state = AgentState(
        company_name=company_name,
        search_results="",
        company_research="",
        qualification_score=0,
        qualification_reasoning="",
        decision_maker_titles=[],
        outreach_email="",
        status="starting",
        error=None,
        contacts=[],
        emails_sent=[],
        linkedin_requests=[],
        sheets_logged=False,
        guardrail_results={},
        workflow_guardrail_summary={},
        control_summary={},
        evaluation_results={}
    )

    print(f"\n{'=' * 60}")
    print(f"🚀 Starting SDR Agent for: {company_name}")
    print(f"{'=' * 60}")

    final_state = graph.invoke(initial_state)

    print(f"\n{'=' * 60}")
    print(f"✅ Agent workflow complete!")
    print(f"{'=' * 60}")

    return final_state

