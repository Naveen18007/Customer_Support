from utils.supabase_client import supabase

def search_faqs(keyword: str, limit: int = 3):
    response = (
        supabase
        .table("faqs")
        .select("question, answer, category, priority")
        .ilike("question", f"%{keyword}%")
        .eq("is_active", True)
        .order("priority", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data
