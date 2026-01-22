from utils.supabase_client import supabase

def get_account_by_email(email: str):
    response = (
        supabase
        .table("accounts")
        .select("*")
        .eq("email", email)
        .execute()
    )
    return response.data
