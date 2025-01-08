from typing import Callable
from fastapi import HTTPException
import time
from collections import defaultdict
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)  # user_id -> list of timestamps
    
    def check_rate_limit(self, user_id: str, max_requests: int, window_seconds: int) -> bool:
        """Check if the user has exceeded their rate limit."""
        now = time.time()
        user_requests = self.requests[user_id]
        
        # Remove old requests outside the window
        while user_requests and user_requests[0] < now - window_seconds:
            user_requests.pop(0)
        
        # Check if user has exceeded rate limit
        if len(user_requests) >= max_requests:
            return False
        
        # Add current request
        user_requests.append(now)
        return True

# Global rate limiter instance
_rate_limiter = RateLimiter()

def rate_limit(max_requests: int, window_seconds: int):
    """
    Rate limiting decorator for FastAPI endpoints.
    
    Parameters:
    - max_requests: Maximum number of requests allowed in the window
    - window_seconds: Time window in seconds
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs
            current_user = kwargs.get('current_user')
            if not current_user:
                logger.warning("Rate limit decorator used on endpoint without current_user")
                return await func(*args, **kwargs)
            
            user_id = str(current_user.id)
            
            if not _rate_limiter.check_rate_limit(user_id, max_requests, window_seconds):
                logger.warning(f"Rate limit exceeded for user {user_id}")
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds."
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator 