from langgraph.graph import StateGraph, END
from app.graph.state import SupportState
from app.graph.nodes import (
    priority_node,
    turn_count_node,
    escalation_decision,
    router_node,
    faq_node,
    account_node,
    billing_node,
    technical_node,
    escalation_node
)

graph = StateGraph(SupportState)

# Nodes
graph.add_node("priority", priority_node)
graph.add_node("turn_count", turn_count_node)
graph.add_node("router", router_node)

graph.add_node("faq", faq_node)
graph.add_node("account", account_node)
graph.add_node("billing", billing_node)
graph.add_node("technical", technical_node)

graph.add_node("escalation", escalation_node)

# Entry
graph.set_entry_point("priority")

# Priority → Turn Count
graph.add_edge("priority", "turn_count")

# Escalation decision
graph.add_conditional_edges(
    "turn_count",
    escalation_decision,
    {
        "ESCALATE": "escalation",
        "CONTINUE": "router"
    }
)

# Agent routing
graph.add_conditional_edges(
    "router",
    lambda s: s["agent"],
    {
        "FAQ_AGENT": "faq",
        "ACCOUNT_AGENT": "account",
        "BILLING_AGENT": "billing",
        "TECHNICAL_AGENT": "technical"
    }
)

# Ends
graph.add_edge("faq", END)
graph.add_edge("account", END)
graph.add_edge("billing", END)
graph.add_edge("technical", END)
graph.add_edge("escalation", END)

support_graph = graph.compile()
