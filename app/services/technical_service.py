from datetime import datetime
from app.utils.supabase_client import supabase

def create_technical_issue(
    customer_id: str,
    issue_type: str,
    description: str
):
    response = (
        supabase
        .table("technical_issues")
        .insert({
            "customer_id": customer_id,
            "issue_type": issue_type,
            "description": description,
            "status": "open",
            "solution": None,
            "created_at": datetime.utcnow().isoformat(),
            "resolved_at":None
        })
        .execute()
    )

    return response.data
