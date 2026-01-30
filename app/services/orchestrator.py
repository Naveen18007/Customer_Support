import os
import re
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.services.session_store import get_history
from app.utils.logger import logger

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PHONE_REGEX = r"\+?\d{8,15}"

SYSTEM_PROMPT = """You are a customer support priority analyzer. Your task is to classify user messages as HIGH or LOW priority based ONLY on the severity and impact of the issue, NOT on sentiment, tone, or politeness.

CRITICAL RULE: Ignore sentiment completely. Polite, neutral, or angry language should NOT affect priority. Focus solely on the actual problem severity.

HIGH PRIORITY - Assign when the issue:
1. BLOCKS ACCESS OR USAGE:
   - Cannot login, sign in, or authenticate
   - Account locked, suspended, or inaccessible
   - System completely unusable
   - Service outage or downtime

2. CAUSES FUNCTIONAL FAILURES:
   - Critical features not working (payments, uploads, downloads, saves)
   - Data corruption, loss, or deletion
   - Incorrect data being displayed or saved
   - Transactions failing or not processing

3. PAYMENT OR FINANCIAL ISSUES:
   - Payment failures or declined transactions
   - Unauthorized charges or billing errors
   - Refund requests that are urgent
   - Subscription cancellations that need immediate attention
   - Payment methods not working

4. SECURITY CONCERNS:
   - Suspected account compromise or unauthorized access
   - Security breaches or data exposure concerns

5. PRODUCTION OR CRITICAL IMPACT:
   - Affects multiple users or systems
   - Prevents completion of critical business workflows
   - System-wide errors or crashes

LOW PRIORITY - Assign when the issue:
1. INFORMATIONAL OR GUIDANCE:
   - How-to questions or tutorials
   - General information requests
   - Feature explanations or documentation requests
   - "What is", "How do I", "Where can I" questions

2. ACCOUNT MANAGEMENT (Non-critical):
   - Profile updates (phone, DOB, preferences)
   - Viewing account information
   - Settings changes
   - Non-critical account modifications

3. BILLING INQUIRIES (Non-urgent):
   - Viewing billing history or invoices
   - Checking order status (when not urgent)
   - General pricing questions
   - Past transaction inquiries

4. COSMETIC OR MINOR ISSUES:
   - UI/display preferences
   - Minor visual glitches that don't block functionality
   - Non-critical feature requests
   - General feedback or suggestions

5. GENERAL QUESTIONS:
   - FAQs and help articles
   - Product information
   - Feature availability questions
   - General support inquiries

EXAMPLES:
- "I cannot login" → HIGH (blocks access)
- "How do I reset my password?" → LOW (informational)
- "My payment failed" → HIGH (payment failure)
- "Can you show me my billing history?" → LOW (informational inquiry)
- "I lost all my data" → HIGH (data loss)
- "What features are available?" → LOW (informational)
- "I want to update my phone number" → LOW (account update)
- "The system crashed and I lost my work" → HIGH (critical failure)
- "Where can I find my orders?" → LOW (informational)

Return ONLY one word: HIGH or LOW"""

ROUTER_PROMPT = """You are an intelligent customer support router. Analyze the user's message and conversation context to route to the MOST APPROPRIATE agent.

CRITICAL: Choose EXACTLY ONE agent based on the PRIMARY intent of the message. Consider the full context, not just keywords.

AGENT DESCRIPTIONS:

1. FAQ_AGENT - Use for:
   - Informational questions: "What is...", "How does...", "Where is...", "When can I..."
   - How-to instructions and tutorials
   - General guidance and explanations
   - Feature information and documentation requests
   - Password reset INSTRUCTIONS (how to reset)
   - General usage questions
   - Product or service information
   - Help articles and knowledge base queries
   - Questions about capabilities, features, or processes
   - Questions about HOW to do something (instructions)
   - Greetings and casual conversation: "Hi", "Hello", "Hey"
   - Personal introductions without requests: "My name is...", "I am..."
   - General conversation that doesn't fit other categories
   
   Examples:
   - "How do I reset my password?"
   - "How do I upgrade my plan?"
   - "How do I change my email address?"
   - "How do I cancel my subscription?" (instructions on HOW, not actual cancellation)
   - "How do I add team members?"
   - "How do I export my data?"
   - "How do I change my billing address?"
   - "What features are available?"
   - "Where can I find my settings?"
   - "How does the billing system work?"
   - "What payment methods do you accept?"
   - "Can you explain how to use this feature?"
   - "Hi" or "Hello" (greetings)
   - "My name is John" (personal introduction)

2. BILLING_AGENT - Use for:
   - VIEWING billing information, invoices, or receipts
   - Order history and order details (viewing only)
   - Payment history and transaction records (viewing only)
   - Checking charges, amounts, or pricing (informational)
   - Subscription information and status (viewing only)
   - Invoice or receipt requests (viewing/downloading)
   - Questions about specific orders (by ID or date)
   - Billing-related inquiries (informational only)
   - Payment method information (viewing, not updating)
   - Questions about billing plans, pricing, or payment options (informational)
   - Requests containing billing-related keywords: "billing", "invoice", "receipt", "order", "payment", "subscription" (when viewing)
   
   Examples:
   - "Show me my billing history"
   - "What are my recent orders?"
   - "Can I see my invoice for order #123?"
   - "How much did I pay last month?"
   - "What's the status of my subscription?"
   - "Tell me about my billing"
   - "I want my billing invoice"
   - "Email my billing details"
   - "What payment methods do you accept?" (informational question)
   - "What are your pricing plans?"
   - "Show me my subscription details"
   - "What's my current plan?"
   - "When is my next billing date?"
   
   NOT for: 
   - Payment failures or errors → TECHNICAL_AGENT
   - Subscription cancellations (actual cancellation requests) → TECHNICAL_AGENT
   - Refund requests → TECHNICAL_AGENT
   - Any billing ACTIONS (cancel, refund, dispute) → TECHNICAL_AGENT
   - "How do I cancel..." (instructions) → FAQ_AGENT
   - "How do I upgrade..." (instructions) → FAQ_AGENT
   - Greetings or personal statements → FAQ_AGENT
   - Messages without billing-related keywords → FAQ_AGENT

3. ACCOUNT_AGENT - Use for:
   - UPDATING account information (phone number, date of birth)
   - Changing personal profile details
   - Modifying account settings or preferences
   - Account modification requests
   
   Examples:
   - "I want to update my phone number to +1234567890"
   - "Change my date of birth to 1990-05-15"
   - "Update my profile"
   - "I need to change my phone number"
   
   NOT for: Viewing account info (FAQ_AGENT) or account access issues (TECHNICAL_AGENT)

4. TECHNICAL_AGENT - Use for:
   - Things NOT WORKING or BROKEN
   - Login failures, authentication errors
   - System errors, crashes, or bugs
   - Feature failures (upload, download, save, etc.)
   - Performance issues (slow, freezing, lagging)
   - Data loss or corruption issues
   - API errors or connection problems
   - Payment failures or transaction errors
   - Any functionality that is broken or not working as expected
   - Error messages or technical problems
   - BILLING/SUBSCRIPTION ACTIONS that need processing:
     * Subscription cancellations ("I want to cancel my subscription")
     * Refund requests ("I want a refund")
     * Billing disputes ("I want to dispute this charge")
     * Subscription modifications that require action
   
   Examples:
   - "I cannot login" or "Login is not working"
   - "The upload feature is broken"
   - "I'm getting an error message"
   - "The system crashed"
   - "My payment failed to process"
   - "Nothing is loading"
   - "I lost my data"
   - "The app keeps freezing"
   - "I want to cancel my subscription"
   - "Cancel my subscription"
   - "I need a refund"
   - "I want to dispute this charge"
   
   NOT for: How-to questions about working features (FAQ_AGENT)

DECISION LOGIC (in order of priority - check each step carefully):

1. Is it a GREETING or PERSONAL STATEMENT? → FAQ_AGENT
   - Look for: "hi", "hello", "hey", "hii", "hiii", greetings
   - Look for: "my name is", "i am", "call me" (without a request)
   - These are casual conversation, not support requests
   - Examples: "Hi", "Hello", "My name is John", "Hiii"
   - Key: No clear support request, just conversation

2. Is it a BILLING/SUBSCRIPTION ACTION REQUEST? → TECHNICAL_AGENT
   - Look for ACTION verbs: "I want to cancel", "Cancel my", "I need a refund", "I want to dispute"
   - NOT "How do I cancel..." (that's instructional → FAQ_AGENT)
   - These are DIRECT REQUESTS for action, not questions about how to do it
   - Examples: "I want to cancel my subscription", "Cancel my subscription", "I need a refund"
   - Key: User wants something DONE, not instructions on HOW to do it

3. Is something BROKEN or NOT WORKING? → TECHNICAL_AGENT
   - Look for: "cannot", "can't", "not working", "broken", "error", "failed", "crash", "bug", "is slow", "is hanging"
   - Exception: "How do I fix..." or "What should I do if..." → FAQ_AGENT (instructional)
   - Key: Actual problem vs. asking how to solve a problem

4. Is it about UPDATING/MODIFYING account info? → ACCOUNT_AGENT
   - Look for ACTION verbs: "update", "change", "modify" + account fields (phone, DOB)
   - Must include the actual data to update (phone number, DOB date)
   - NOT for: "How do I update..." → FAQ_AGENT (instructional)
   - NOT for: subscription modifications (those are billing actions → TECHNICAL_AGENT)
   - Key: User provides data to update, not asking how to update

5. Is it about VIEWING billing/orders/payments? → BILLING_AGENT
   - Look for VIEWING verbs: "show", "view", "see", "list", "tell me about", "what is", "what are", "want", "email"
   - Must include billing-related keywords: "billing", "invoice", "receipt", "order", "payment", "subscription"
   - Questions about status, history, details (informational)
   - Must be informational/viewing only, not actions or failures
   - Key distinction: VIEWING vs. TAKING ACTION
   - Examples: "Show me my billing", "What's my subscription status?", "I want my billing invoice", "Email my billing details"
   - CRITICAL: Must have billing-related keywords, otherwise → FAQ_AGENT

6. Is it a HOW-TO or INSTRUCTIONAL question? → FAQ_AGENT
   - Questions starting with "How do I...", "How can I...", "What should I do..."
   - Asking for instructions, guidance, or explanations
   - General information requests
   - Everything else: informational, instructional, or general queries
   - Key: User wants to KNOW HOW, not to DO something
   - Default fallback for unclear queries

EDGE CASES (Critical Routing Examples):
- "Hi" or "Hello" or "Hiii" → FAQ_AGENT (greeting)
- "My name is John" → FAQ_AGENT (personal statement, no request)
- "I can't login" → TECHNICAL_AGENT (broken functionality)
- "How do I login?" → FAQ_AGENT (instructional/how-to)
- "My payment failed" → TECHNICAL_AGENT (broken functionality)
- "Show me my payment history" → BILLING_AGENT (informational/viewing + billing keyword)
- "I want my billing invoice" → BILLING_AGENT (informational/viewing + billing keyword)
- "Email my billing details" → BILLING_AGENT (informational/viewing + billing keyword)
- "I want to cancel my subscription" → TECHNICAL_AGENT (billing action - actual cancellation)
- "How do I cancel my subscription?" → FAQ_AGENT (instructional/how-to question)
- "What's my subscription status?" → BILLING_AGENT (informational/viewing + subscription keyword)
- "Cancel my subscription" → TECHNICAL_AGENT (billing action - direct request)
- "I need a refund" → TECHNICAL_AGENT (billing action)
- "Update my phone to +1234567890" → ACCOUNT_AGENT (modification)
- "What's my phone number?" → FAQ_AGENT (informational, viewing, no billing keyword)
- "The system is slow" → TECHNICAL_AGENT (performance issue)
- "The app is running slow" → TECHNICAL_AGENT (performance issue)
- "How does billing work?" → FAQ_AGENT (informational/how-to question)
- "I want to dispute this charge" → TECHNICAL_AGENT (billing action)
- "How do I upgrade my plan?" → FAQ_AGENT (instructional/how-to)
- "What's my current plan?" → BILLING_AGENT (informational/viewing + plan keyword)
- "I cannot upload files" → TECHNICAL_AGENT (broken functionality)
- "How do I upload files?" → FAQ_AGENT (instructional/how-to)
- "How do I change my email?" → FAQ_AGENT (instructional/how-to)
- "I want to change my email" → ACCOUNT_AGENT (if supported) or FAQ_AGENT (if just asking how)
- "How do I export my data?" → FAQ_AGENT (instructional/how-to)
- "I lost my data" → TECHNICAL_AGENT (data loss issue)

Return ONLY one word:
FAQ_AGENT
ACCOUNT_AGENT
TECHNICAL_AGENT
BILLING_AGENT"""


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception)
)
def _call_groq_api(messages: list, max_tokens: int = 10, model: str = "llama-3.1-8b-instant"):
    """Call Groq API with retry logic"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
            max_tokens=max_tokens,
            timeout=10
        )
        return response
    except Exception as e:
        logger.error(f"Groq API call failed: {e}")
        raise


def analyze_priority(customer_id: str, message: str) -> str:
    """Analyze message priority with retry and fallback logic"""
    try:
        history = get_history(customer_id)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *history,
            {"role": "user", "content": message}
        ]

        response = _call_groq_api(messages, max_tokens=10)
        output = response.choices[0].message.content.strip().upper()
        
        # More robust parsing: check for HIGH priority indicators
        if "HIGH" in output:
            logger.info(f"Priority analysis: HIGH for customer {customer_id}")
            return "HIGH"
        elif "LOW" in output:
            logger.info(f"Priority analysis: LOW for customer {customer_id}")
            return "LOW"
        else:
            # Fallback: if unclear, default to LOW (safer default)
            logger.warning(f"Priority analysis unclear, defaulting to LOW for customer {customer_id}")
            return "LOW"
    except Exception as e:
        logger.error(f"Priority analysis failed for customer {customer_id}: {e}")
        # Fallback: analyze keywords for priority
        message_lower = message.lower()
        high_priority_keywords = [
            "cannot", "can't", "failed", "error", "broken", "crash", 
            "lost", "hacked", "unauthorized", "payment failed", "data loss"
        ]
        if any(kw in message_lower for kw in high_priority_keywords):
            return "HIGH"
        return "LOW"


def fallback_keyword_router(message: str) -> str:
    """
    Fallback router when LLM fails or confidence is low.
    Uses keyword matching as backup for reliability.
    """
    message_lower = message.lower()
    
    # Billing actions (high priority - must check first)
    billing_action_keywords = [
        "cancel subscription", "want to cancel", "need refund", "dispute",
        "cancel my", "i want to cancel", "i need a refund", "i want to dispute"
    ]
    if any(kw in message_lower for kw in billing_action_keywords):
        logger.info("Fallback router: TECHNICAL_AGENT (billing action)")
        return "TECHNICAL_AGENT"
    
    # Technical issues
    technical_keywords = [
        "cannot", "can't", "not working", "broken", "error", "failed", 
        "crash", "bug", "is slow", "is hanging", "lost", "corrupted",
        "not loading", "freezing", "timeout"
    ]
    if any(kw in message_lower for kw in technical_keywords):
        logger.info("Fallback router: TECHNICAL_AGENT (technical issue)")
        return "TECHNICAL_AGENT"
    
    # Account updates (check for phone/DOB with update keywords)
    phone_match = re.search(PHONE_REGEX, message_lower)
    dob_match = re.search(r"\b\d{4}-\d{2}-\d{2}\b", message)
    update_keywords = ["update", "change", "modify", "new", "set"]
    
    if (phone_match or dob_match) and any(kw in message_lower for kw in update_keywords):
        logger.info("Fallback router: ACCOUNT_AGENT (account update)")
        return "ACCOUNT_AGENT"
    
    # Billing viewing (must have billing keywords AND viewing verbs)
    billing_keywords = ["billing", "invoice", "receipt", "order", "payment", "subscription", "plan"]
    viewing_verbs = ["show", "view", "see", "tell", "want", "email", "list", "what", "when"]
    
    if any(kw in message_lower for kw in billing_keywords) and any(kw in message_lower for kw in viewing_verbs):
        logger.info("Fallback router: BILLING_AGENT (billing viewing)")
        return "BILLING_AGENT"
    
    # Default to FAQ
    logger.info("Fallback router: FAQ_AGENT (default)")
    return "FAQ_AGENT"


def route_query(customer_id: str, message: str) -> str:
    """Route query to appropriate agent with retry and fallback logic"""
    logger.info(f"Routing query for customer {customer_id}: {message[:100]}")
    
    # 🔑 HARD OVERRIDE: phone number input (only if it's clearly an update request)
    message_lower = message.lower()
    phone_match = re.search(PHONE_REGEX, message)
    
    # Only route to ACCOUNT_AGENT if phone number is present AND it's an update request
    if phone_match and any(keyword in message_lower for keyword in ["update", "change", "modify", "new", "set"]):
        logger.info(f"Hard override: ACCOUNT_AGENT (phone number detected)")
        return "ACCOUNT_AGENT"

    try:
        history = get_history(customer_id)

        messages = [
            {"role": "system", "content": ROUTER_PROMPT},
            *history,
            {"role": "user", "content": message}
        ]

        response = _call_groq_api(messages, max_tokens=20)
        output = response.choices[0].message.content.strip().upper()
        
        # Extract agent name even if there's extra text
        allowed_agents = {
            "ACCOUNT_AGENT",
            "BILLING_AGENT",
            "TECHNICAL_AGENT",
            "FAQ_AGENT"
        }
        
        # Check if any allowed agent name appears in the output
        for agent in allowed_agents:
            if agent in output:
                logger.info(f"LLM routed to: {agent}")
                return agent
        
        # Fallback: try to match partial agent names
        if "ACCOUNT" in output and "AGENT" in output:
            logger.info(f"Partial match routed to: ACCOUNT_AGENT")
            return "ACCOUNT_AGENT"
        elif "BILLING" in output and "AGENT" in output:
            logger.info(f"Partial match routed to: BILLING_AGENT")
            return "BILLING_AGENT"
        elif "TECHNICAL" in output and "AGENT" in output:
            logger.info(f"Partial match routed to: TECHNICAL_AGENT")
            return "TECHNICAL_AGENT"
        elif "FAQ" in output and "AGENT" in output:
            logger.info(f"Partial match routed to: FAQ_AGENT")
            return "FAQ_AGENT"
        
        # LLM output unclear, use fallback
        logger.warning(f"LLM output unclear: {output}, using fallback router")
        return fallback_keyword_router(message)
        
    except Exception as e:
        logger.error(f"Routing failed for customer {customer_id}: {e}, using fallback router")
        return fallback_keyword_router(message)

