from app.utils.supabase_client import supabase

def get_user_email(customer_id: str) -> str:
    response = (
        supabase
        .table("accounts")
        .select("email")
        .eq("customer_id", customer_id)
        .single()
        .execute()
    )

    if not response.data:
        raise Exception("User email not found")

    return response.data["email"]
