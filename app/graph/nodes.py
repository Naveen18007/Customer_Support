from app.services.orchestrator import analyze_priority, route_query
from app.services.session_store import get_user_turn_count

from app.agents.faq_agent import generate_faq_response
from app.agents.account_agent import generate_account_response
from app.agents.billing_agent import generate_billing_response
from app.agents.technical_agent import generate_technical_response
from app.agents.escalation_agent import send_escalation_alert


# ---------- Priority ----------
def priority_node(state):
    print("🟢 NODE: PRIORITY")

    state["priority"] = analyze_priority(
        customer_id=state["customer_id"],
        message=state["message"]
    )
    return state


# ---------- Turn Count ----------
def turn_count_node(state):
    print("🟢 NODE: TURN COUNT")

    state["user_turns"] = get_user_turn_count(state["customer_id"])
    return state


# ---------- Escalation Decision ----------
def escalation_decision(state):
    """
    Decide whether to escalate or continue to agent routing.
    Only escalate immediately for critical security issues.
    Let technical agent handle other HIGH priority issues first.
    """
    message_lower = state.get("message", "").lower()
    
    # Critical security issues that need immediate escalation
    critical_security_keywords = [
        "hacked", "breach", "unauthorized access", "security breach",
        "data breach", "compromised", "stolen", "fraud"
    ]
    
    # Check for critical security issues
    if any(keyword in message_lower for keyword in critical_security_keywords):
        return "ESCALATE"
    
    # Escalate if conversation is too long (agent couldn't resolve)
    if state.get("user_turns", 0) > 10:
        return "ESCALATE"
    
    # For other HIGH priority issues, let the agent try first
    # They will be escalated later if unresolved
    return "CONTINUE"


# ---------- Router ----------
def router_node(state):
    print("🟢 NODE: ROUTER")

    state["agent"] = route_query(
        customer_id=state["customer_id"],
        message=state["message"]
    )
    return state


# ---------- Agents ----------
def faq_node(state):
    print("🟢 NODE: FAQ")

    state["response"] = generate_faq_response(
        state["customer_id"], state["message"]
    )
    return state


def account_node(state):
    print("🟢 NODE: ACCOUNT")

    state["response"] = generate_account_response(
        state["customer_id"], state["message"]
    )
    return state


def billing_node(state):
    print("🟢 NODE: BILLING")

    state["response"] = generate_billing_response(
        state["customer_id"], state["message"]
    )
    return state


def technical_node(state):
    print("🟢 NODE: TECHNICAL")

    state["response"] = generate_technical_response(
        state["customer_id"], state["message"]
    )
    return state


# ---------- Escalation ----------
def escalation_node(state):
    print("🟢 NODE: ESCALATION")

    send_escalation_alert(
        customer_id=state["customer_id"],
        message=state["message"]
    )

    state["response"] = (
        "🚨 Your issue could not be resolved automatically.\n"
        "It has been escalated to our Support Team.\n"
        "They will contact you shortly."
    )
    return state
