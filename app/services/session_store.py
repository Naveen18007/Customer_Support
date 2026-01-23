from collections import defaultdict
from typing import List, Dict

# customer_id -> list of messages
SESSION_MEMORY: Dict[str, List[dict]] = defaultdict(list)

MAX_HISTORY = 10

def get_history(customer_id: str) -> List[dict]:
    return SESSION_MEMORY[customer_id][-MAX_HISTORY:]


def append_message(customer_id: str, role: str, content: str):
    SESSION_MEMORY[customer_id].append({
        "role": role,
        "content": content
    })
