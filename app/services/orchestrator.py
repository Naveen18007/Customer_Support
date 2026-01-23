import os
from groq import Groq
from app.services.session_store import get_history

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """

You are a customer support priority analyzer.

Determine the priority of the user’s message ONLY based on the seriousness and impact of the problem, not on sentiment, tone, or wording.

Classification rules:

Assign HIGH priority if the issue:

Blocks system access or usage

Involves service outages, crashes, or errors

Causes data loss, missing data, or incorrect data

Involves payment failures, refunds, or cancellations

Affects multiple users, customers, or production systems

Prevents completion of critical workflows

Assign LOW priority if the issue:

Is related to FAQs, how-to questions, or general guidance

Involves account details, profile updates, or settings

Is cosmetic, informational, or non-blocking

Does not impact core functionality or business operations

Ignore sentiment completely.
Polite, neutral, or angry language should not affect the priority.

Return ONLY one word:
HIGH or LOW

"""

def analyze_priority(customer_id: str, message: str) -> str:
    history = get_history(customer_id)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": message}
    ]

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0,
        max_tokens=5
    )

    output = response.choices[0].message.content.strip().upper()

    return "HIGH" if "HIGH" in output else "LOW"
