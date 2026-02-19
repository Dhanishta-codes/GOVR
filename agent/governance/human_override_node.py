# ============================================================
# HUMAN OVERRIDE NODE
# Final manual governance checkpoint
# ============================================================

from agent.core.state import AgentState


def human_override_node(state: AgentState) -> AgentState:
    """
    Allows manual override when workflow is blocked by control layer.
    """

    print("\n🧑‍⚖️ HUMAN OVERRIDE CHECK")

    # Only trigger if blocked
    if state.get("status") != "blocked_by_control":
        return state

    override = state.get("human_override", {}) or {}

    # Expected structure:
    # state["human_override"] = {
    #   "approved": True/False,
    #   "reason": "Optional explanation"
    # }

    if override.get("approved") is True:
        print("✅ Human override APPROVED")

        state["status"] = "approved_by_human"
        state.setdefault("control_summary", {})
        state["control_summary"]["human_override"] = {
            "approved": True,
            "reason": override.get("reason", "Manual approval")
        }

    else:
        print("❌ Human override NOT approved")
        state.setdefault("control_summary", {})
        state["control_summary"]["human_override"] = {
            "approved": False,
            "reason": override.get("reason", "No approval given")
        }

    return state
