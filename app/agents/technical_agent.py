from app.services.technical_service import create_technical_issue

ISSUE_TYPE_KEYWORDS = {
    "login_error": ["login", "sign in", "password", "credentials"],
    "upload_error": ["upload", "file", "attachment"],
    "performance": ["slow", "lag", "performance", "freeze"],
    "api_error": ["api", "timeout", "request", "endpoint"],
    "sync_error": ["sync", "synchronization"],
    "display_error": ["ui", "display", "screen", "layout"],
    "notification_error": ["notification", "email", "alert"],
    "integration_error": ["integration", "slack", "webhook"],
    "storage_error": ["storage", "file access", "disk"],
    "search_error": ["search", "find", "results"],
    "billing_action": ["cancel", "cancellation", "refund", "dispute", "subscription"]
}

def classify_issue_type(message: str) -> str:
    message_lower = message.lower()

    for issue_type, keywords in ISSUE_TYPE_KEYWORDS.items():
        if any(keyword in message_lower for keyword in keywords):
            return issue_type

    return "general_technical_issue"

def has_failure_intent(message: str) -> bool:
    message = message.lower()

    failure_patterns = [
        "cannot",
        "can't",
        "cant",
        "unable",
        "not able",
        "cant able",
        "failed",
        "failing",
        "error",
        "issue",
        "problem",
        "broken",
        "not working",
        "does not work",
        "is not working"
    ]

    return any(pattern in message for pattern in failure_patterns)

def has_billing_action_intent(message: str) -> bool:
    """Check if the message is about a billing/subscription action that needs processing."""
    message = message.lower()
    
    billing_action_patterns = [
        "cancel",
        "cancellation",
        "cancel my",
        "want to cancel",
        "need to cancel",
        "refund",
        "i want a refund",
        "need a refund",
        "dispute",
        "dispute this",
        "stop subscription",
        "end subscription",
        "terminate subscription"
    ]
    
    return any(pattern in message for pattern in billing_action_patterns)


def generate_technical_response(customer_id: str, message: str) -> str:

    # Check if it's a billing action (subscription cancellation, refund, etc.)
    if has_billing_action_intent(message):
        issue_type = classify_issue_type(message)
        # Override to billing_action if subscription/billing keywords found
        if "cancel" in message.lower() or "subscription" in message.lower():
            issue_type = "billing_action"
        
        create_technical_issue(
            customer_id=customer_id,
            issue_type=issue_type,
            description=message
        )
        
        # Special response for subscription cancellations
        if "cancel" in message.lower() and "subscription" in message.lower():
            return (
                "✅ Your subscription cancellation request has been received and logged.\n\n"
                "Issue Type: Subscription Cancellation\n"
                "Status: Processing\n\n"
                "Our billing team will process your cancellation request and contact you shortly "
                "to confirm the cancellation and discuss any final steps."
            )
        # Special response for refunds
        elif "refund" in message.lower():
            return (
                "✅ Your refund request has been received and logged.\n\n"
                "Issue Type: Refund Request\n"
                "Status: Under Review\n\n"
                "Our billing team will review your refund request and contact you within 2-3 business days "
                "with an update on the status of your refund."
            )
        # Generic billing action response
        else:
            return (
                "✅ Your billing request has been received and logged.\n\n"
                f"Issue Type: {issue_type}\n"
                "Status: Processing\n\n"
                "Our billing team will review your request and contact you shortly."
            )

    # 🛑 Guardrail: do NOT handle non-failure questions
    if not has_failure_intent(message):
        return (
            "This looks like a general question.\n\n"
            "Please ask how-to or informational questions normally, "
            "and I'll help you right away."
        )

    issue_type = classify_issue_type(message)

    create_technical_issue(
        customer_id=customer_id,
        issue_type=issue_type,
        description=message
    )

    # Provide specific responses based on issue type
    if issue_type == "login_error":
        return (
            "🔐 I understand you're having trouble logging in. I've logged this issue for our technical team.\n\n"
            "**Issue Type:** Login/Authentication Error\n"
            "**Status:** Open - Under Investigation\n\n"
            "**Quick Troubleshooting Steps:**\n"
            "• Make sure you're using the correct email and password\n"
            "• Try clearing your browser cache and cookies\n"
            "• Check if Caps Lock is enabled\n"
            "• Try using a different browser or incognito mode\n\n"
            "Our technical team is investigating this issue and will contact you shortly with a resolution. "
            "If this is urgent, please reply and I'll escalate it immediately."
        )
    else:
        return (
            "🛠️ Your technical issue has been logged successfully.\n\n"
            f"**Issue Type:** {issue_type.replace('_', ' ').title()}\n"
            "**Status:** Open - Under Investigation\n\n"
            "Our technical team will investigate and update you soon. "
            "If this is urgent, please reply and I'll escalate it immediately."
        )
