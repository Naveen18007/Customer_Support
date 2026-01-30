from collections import defaultdict
from typing import List, Dict
from datetime import datetime, timedelta

# customer_id → message history (for LLM context)
SESSION_MEMORY: Dict[str, List[dict]] = defaultdict(list)

# customer_id → total user turns (for escalation logic)
USER_TURN_COUNT: Dict[str, int] = defaultdict(int)

# customer_id → last activity timestamp (for cleanup)
SESSION_TIMESTAMPS: Dict[str, datetime] = {}

MAX_HISTORY = 10
SESSION_TTL = timedelta(hours=24)  # Sessions expire after 24 hours
CLEANUP_INTERVAL = 100  # Cleanup every 100 messages


def cleanup_old_sessions():
    """Remove sessions older than TTL to prevent memory leaks"""
    now = datetime.now()
    to_remove = [
        customer_id for customer_id, timestamp in SESSION_TIMESTAMPS.items()
        if now - timestamp > SESSION_TTL
    ]
    
    for customer_id in to_remove:
        if customer_id in SESSION_MEMORY:
            del SESSION_MEMORY[customer_id]
        if customer_id in USER_TURN_COUNT:
            del USER_TURN_COUNT[customer_id]
        if customer_id in SESSION_TIMESTAMPS:
            del SESSION_TIMESTAMPS[customer_id]


def append_message(customer_id: str, role: str, content: str):
    # Periodic cleanup to prevent memory leaks
    if len(SESSION_MEMORY) % CLEANUP_INTERVAL == 0:
        cleanup_old_sessions()
    
    # Append message with timestamp
    SESSION_MEMORY[customer_id].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
    
    # Update session timestamp
    SESSION_TIMESTAMPS[customer_id] = datetime.now()

    # 🔥 IMPORTANT: track user turns separately
    if role == "user":
        USER_TURN_COUNT[customer_id] += 1


def get_history(customer_id: str) -> List[dict]:
    """Get conversation history for LLM context (last MAX_HISTORY messages)"""
    # Clean up old sessions first
    cleanup_old_sessions()
    
    # Return only recent messages (without timestamps for LLM)
    messages = SESSION_MEMORY.get(customer_id, [])
    recent_messages = messages[-MAX_HISTORY:]
    
    # Return in format expected by LLM (without timestamp)
    return [
        {"role": msg["role"], "content": msg["content"]}
        for msg in recent_messages
    ]


def get_user_turn_count(customer_id: str) -> int:
    """Get user turn count for escalation logic"""
    return USER_TURN_COUNT.get(customer_id, 0)


def clear_session(customer_id: str):
    """Clear session for a specific customer (useful for testing or logout)"""
    if customer_id in SESSION_MEMORY:
        del SESSION_MEMORY[customer_id]
    if customer_id in USER_TURN_COUNT:
        del USER_TURN_COUNT[customer_id]
    if customer_id in SESSION_TIMESTAMPS:
        del SESSION_TIMESTAMPS[customer_id]


def get_session_stats() -> dict:
    """Get statistics about active sessions (useful for monitoring)"""
    cleanup_old_sessions()
    return {
        "active_sessions": len(SESSION_MEMORY),
        "total_messages": sum(len(msgs) for msgs in SESSION_MEMORY.values()),
        "oldest_session": min(SESSION_TIMESTAMPS.values()).isoformat() if SESSION_TIMESTAMPS else None
    }
