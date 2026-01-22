from app.utils.supabase_client import supabase

def test_faq_connection():
    response = (
        supabase
        .table("faqs")
        .select("id, question")
        .limit(1)
        .execute()
    )

    return response.data
