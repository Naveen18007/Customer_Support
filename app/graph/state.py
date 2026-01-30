from typing import TypedDict, Optional

class SupportState(TypedDict):
    customer_id: str
    message: str
    priority: Optional[str]
    agent: Optional[str]
    response: Optional[str]
    user_turns: Optional[int]
