import re
from app.services.faq_service import fetch_best_faq_match

def tokenize(text: str) -> list[str]:
    """
    Enhanced tokenizer for keyword matching.
    Preserves important phrases and extracts both words and phrases.
    """
    text = text.lower()
    # Remove punctuation but keep spaces
    text = re.sub(r"[^a-z0-9\s]", "", text)
    
    # Split into words
    words = text.split()
    
    # Create tokens: individual words + important 2-word phrases
    tokens = set(words)  # Start with individual words
    
    # Add 2-word phrases (bigrams) for better matching
    # This helps match phrases like "end subscription", "change plan", etc.
    for i in range(len(words) - 1):
        phrase = f"{words[i]} {words[i+1]}"
        tokens.add(phrase)
    
    return list(tokens)


def is_greeting(message: str) -> bool:
    """Check if the message is a greeting or casual conversation."""
    message_lower = message.lower().strip()
    
    greetings = [
        "hi", "hello", "hey", "hii", "hiii", "hi there", "hello there",
        "good morning", "good afternoon", "good evening", "greetings",
        "what's up", "whats up", "sup", "yo"
    ]
    
    # Check if message is just a greeting
    if message_lower in greetings:
        return True
    
    # Check if message starts with greeting
    for greeting in greetings:
        if message_lower.startswith(greeting + " ") or message_lower == greeting:
            return True
    
    return False

def is_personal_statement(message: str) -> bool:
    """Check if the message is a personal statement without a clear request."""
    message_lower = message.lower().strip()
    
    personal_patterns = [
        "my name is",
        "i am",
        "i'm",
        "call me",
        "this is"
    ]
    
    # Check if it's a personal introduction without a question or request
    for pattern in personal_patterns:
        if pattern in message_lower:
            # If it's just a statement without a question mark or request, it's personal
            if "?" not in message and not any(req in message_lower for req in ["want", "need", "help", "can you", "please"]):
                return True
    
    return False

def generate_faq_response(customer_id: str, message: str) -> str:
    # Handle greetings
    if is_greeting(message):
        return (
            "Hello! 👋 I'm here to help you with your customer support needs.\n\n"
            "I can assist you with:\n"
            "• Account information and updates\n"
            "• Billing and subscription questions\n"
            "• Technical issues\n"
            "• General how-to questions\n\n"
            "What can I help you with today?"
        )
    
    # Handle personal statements
    if is_personal_statement(message):
        return (
            "Nice to meet you! 😊\n\n"
            "I'm here to help you with your account, billing, technical issues, or any questions you might have.\n\n"
            "What would you like help with today?"
        )
    
    tokens = tokenize(message)

    faq = fetch_best_faq_match(tokens)

    if faq:
        return faq["answer"]

    return (
        "I couldn't find an exact answer to your question in our help articles.\n\n"
        "Could you please rephrase your question or be a bit more specific?\n\n"
        "I can help you with:\n"
        "• Account updates (phone, date of birth)\n"
        "• Billing information and invoices\n"
        "• Technical issues\n"
        "• How-to questions and instructions"
    )
