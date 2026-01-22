from utils.supabase_client import supabase

def get_billing_by_customer(customer_id: str):
    response = (
        supabase
        .table("billing")
        .select("*")
        .eq("customer_id", customer_id)
        .execute()
    )
    return response.data
