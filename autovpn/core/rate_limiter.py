"""Rate limiter for API requests."""

import time
from collections import defaultdict
from typing import Dict, List
from fastapi import HTTPException, Request


class RateLimiter:
    """Simple in-memory rate limiter based on IP address."""

    def __init__(self, requests_per_minute: int = 25):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, ip: str) -> bool:
        """Check if request is allowed for the given IP."""
        current_time = time.time()

        # Clean old requests (older than 1 minute)
        self.requests[ip] = [
            req_time for req_time in self.requests[ip] if current_time - req_time < 60
        ]

        # Check if we're under the limit
        if len(self.requests[ip]) < self.requests_per_minute:
            self.requests[ip].append(current_time)
            return True

        return False

    def get_remaining_requests(self, ip: str) -> int:
        """Get remaining requests for the given IP."""
        current_time = time.time()

        # Clean old requests
        self.requests[ip] = [
            req_time for req_time in self.requests[ip] if current_time - req_time < 60
        ]

        return max(0, self.requests_per_minute - len(self.requests[ip]))


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=25)


def get_client_ip(request: Request) -> str:
    """Extract client IP from request."""
    # Check for forwarded headers first (for proxy setups)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fallback to client host
    return request.client.host if request.client else "unknown"


def check_rate_limit(request: Request):
    """Dependency to check rate limit for incoming requests."""
    client_ip = get_client_ip(request)

    if not rate_limiter.is_allowed(client_ip):
        remaining = rate_limiter.get_remaining_requests(client_ip)
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Limit: 5 per minute. Try again in {60 - int(time.time() % 60)} seconds.",
                "remaining_requests": remaining,
            },
        )
