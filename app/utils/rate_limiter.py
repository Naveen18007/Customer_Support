from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict
from app.utils.logger import logger

# Rate limiting configuration
RATE_LIMIT_WINDOW = timedelta(minutes=1)  # 1 minute window
MAX_REQUESTS_PER_WINDOW = 30  # Max 30 requests per minute per customer

# Track requests: customer_id -> list of request timestamps
REQUEST_TRACKER: Dict[str, list] = defaultdict(list)


def check_rate_limit(customer_id: str) -> tuple[bool, str]:
    """
    Check if customer has exceeded rate limit.
    Returns (is_allowed, message)
    """
    now = datetime.now()
    
    # Get customer's request history
    requests = REQUEST_TRACKER.get(customer_id, [])
    
    # Remove requests outside the time window
    cutoff_time = now - RATE_LIMIT_WINDOW
    recent_requests = [req_time for req_time in requests if req_time > cutoff_time]
    
    # Update tracker
    REQUEST_TRACKER[customer_id] = recent_requests
    
    # Check if limit exceeded
    if len(recent_requests) >= MAX_REQUESTS_PER_WINDOW:
        logger.warning(f"Rate limit exceeded for customer {customer_id}: {len(recent_requests)} requests")
        return False, f"Rate limit exceeded. Maximum {MAX_REQUESTS_PER_WINDOW} requests per minute."
    
    # Record this request
    recent_requests.append(now)
    REQUEST_TRACKER[customer_id] = recent_requests
    
    return True, ""


def get_rate_limit_status(customer_id: str) -> dict:
    """Get current rate limit status for a customer"""
    now = datetime.now()
    requests = REQUEST_TRACKER.get(customer_id, [])
    cutoff_time = now - RATE_LIMIT_WINDOW
    recent_requests = [req_time for req_time in requests if req_time > cutoff_time]
    
    return {
        "requests_in_window": len(recent_requests),
        "max_requests": MAX_REQUESTS_PER_WINDOW,
        "window_minutes": RATE_LIMIT_WINDOW.total_seconds() / 60,
        "remaining_requests": max(0, MAX_REQUESTS_PER_WINDOW - len(recent_requests))
    }


def cleanup_old_entries():
    """Clean up old entries from tracker (called periodically)"""
    now = datetime.now()
    cutoff_time = now - RATE_LIMIT_WINDOW
    
    for customer_id in list(REQUEST_TRACKER.keys()):
        requests = REQUEST_TRACKER[customer_id]
        recent_requests = [req_time for req_time in requests if req_time > cutoff_time]
        
        if recent_requests:
            REQUEST_TRACKER[customer_id] = recent_requests
        else:
            del REQUEST_TRACKER[customer_id]
