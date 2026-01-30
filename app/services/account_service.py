from app.utils.supabase_client import supabase

def get_account(customer_id: str):
    response = (
        supabase
        .table("accounts")
        .select("customer_id, phone, dob")
        .eq("customer_id", customer_id)
        .single()
        .execute()
    )
    return response.data


def update_phone(customer_id: str, new_phone: str):
    return (
        supabase
        .table("accounts")
        .update({"phone": new_phone})
        .eq("customer_id", customer_id)
        .execute()
    )


def update_dob(customer_id: str, new_dob: str):
    return (
        supabase
        .table("accounts")
        .update({"dob": new_dob})
        .eq("customer_id", customer_id)
        .execute()
    )

