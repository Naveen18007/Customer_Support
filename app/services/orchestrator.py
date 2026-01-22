from services.faq_service import search_faqs

def handle_query(message: str):
    faqs = search_faqs("password")
    if faqs:
        return faqs[0]["answer"]
    return "No FAQ found"
