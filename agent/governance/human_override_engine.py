# ==========================================================
# HUMAN OVERRIDE ENGINE
# Allows human to override governance decisions
# ==========================================================

from datetime import datetime


def apply_human_override(state):

    override = state.get("human_override")

    if not override:
        return state

    decision = override.get("decision")
    reason = override.get("reason", "No reason provided")

    print("\n👤 Human Override Applied")
    print(f"Override Decision: {decision}")
    print(f"Reason: {reason}")

    # Log override history
    state.setdefault("override_history", []).append({
        "timestamp": datetime.utcnow().isoformat(),
        "original_decision": state.get("control_summary", {}).get("decision"),
        "override_decision": decision,
        "reason": reason
    })

    # Apply override
    if decision == "FORCE_ALLOW":
        state["status"] = "override_allowed"

    elif decision == "FORCE_STOP":
        state["status"] = "blocked_by_human"

    elif decision == "FORCE_REWRITE":
        state.setdefault("control_flags", []).append({
            "node": "generate_email",
            "action": "RETRY"
        })

    return state
