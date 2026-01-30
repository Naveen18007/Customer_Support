from app.utils.supabase_client import supabase

def fetch_best_faq_match(tokens: list[str]):
    """
    Fetch best matching FAQ based on keyword overlap with improved scoring.
    Uses match count and priority to find the best match.
    """
    # Get all FAQs that have at least one matching keyword
    response = (
        supabase
        .table("faqs")
        .select("id, question, answer, keywords, priority")
        .overlaps("keywords", tokens)
        .eq("is_active", True)
        .execute()
    )

    if not response.data:
        return None

    # Score each FAQ based on keyword matches
    # Higher score = better match
    scored_faqs = []
    
    for faq in response.data:
        faq_keywords = [kw.lower() for kw in (faq.get("keywords") or [])]
        user_tokens_lower = [t.lower() for t in tokens]
        
        # Count exact keyword matches
        match_count = sum(1 for keyword in faq_keywords if keyword in user_tokens_lower)
        
        # Check for exact phrase matches (multi-word keywords)
        phrase_matches = 0
        for keyword in faq_keywords:
            if ' ' in keyword:  # Multi-word keyword
                keyword_words = keyword.split()
                # Check if all words in the keyword appear in user tokens
                if all(word in user_tokens_lower for word in keyword_words):
                    phrase_matches += 2  # Multi-word matches are worth more
        
        # Calculate score: match_count + phrase_bonus + priority
        score = match_count + phrase_matches + (faq.get("priority", 5) * 0.1)
        
        scored_faqs.append({
            **faq,
            "match_score": score,
            "match_count": match_count
        })
    
    # Sort by score (highest first), then by priority, then by match_count
    scored_faqs.sort(key=lambda x: (x["match_score"], x.get("priority", 0), x["match_count"]), reverse=True)
    
    # Return the best match
    if scored_faqs:
        best_match = scored_faqs[0]
        # Return in expected format (without scoring fields)
        return {
            "question": best_match["question"],
            "answer": best_match["answer"],
            "priority": best_match.get("priority", 5)
        }
    
    return None
