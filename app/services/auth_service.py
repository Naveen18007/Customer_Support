from app.utils.supabase_client import supabase

def verify_user(email: str, phone: str):
    response = (
        supabase
        .table("accounts")
        .select("customer_id, name, email, phone")
        .eq("email", email)
        .eq("phone", phone)
        .execute()
    )

    if response.data:
        return {
            "verified": True,
            "customer": response.data[0]
        }

    return {
        "verified": False
    }
