from utils.supabase_client import supabase

def get_open_issues(customer_id: str):
    response = (
        supabase
        .table("technical_issues")
        .select("*")
        .eq("customer_id", customer_id)
        .eq("status", "open")
        .execute()
    )
    return response.data
