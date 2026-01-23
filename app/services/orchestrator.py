import os
from groq import Groq
from app.services.session_store import get_history

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are a sentiment analyzer for customer support.

Analyze the conversation and determine the priority of the user's latest message.

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
