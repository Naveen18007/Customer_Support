import os
import requests
from datetime import datetime

TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")

def send_escalation_alert(customer_id: str, message: str):
    if not TEAMS_WEBHOOK_URL:
        raise RuntimeError("TEAMS_WEBHOOK_URL not configured")

    payload = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "FF0000",
        "summary": "🚨 High Priority Customer Issue",
        "title": "🚨 Escalation Alert",
        "sections": [
            {
                "facts": [
                    {"name": "Customer ID", "value": customer_id},
                    {"name": "Priority", "value": "HIGH"},
                    {"name": "Time", "value": datetime.utcnow().isoformat()},
                ],
                "text": f"**User Message:**\n\n{message}"
            }
        ]
    }

    response = requests.post(
        TEAMS_WEBHOOK_URL,
        json=payload,
        timeout=5
    )

    response.raise_for_status()
