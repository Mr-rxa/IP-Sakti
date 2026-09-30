import time
from collections import defaultdict
from fastapi import Request
from fastapi.responses import JSONResponse
from app.config import settings

class InMemoryRateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        window_start = now - self.window_seconds
        # Clean old timestamps
        valid_timestamps = [t for t in self.requests[client_ip] if t > window_start]
        if not valid_timestamps:
            self.requests.pop(client_ip, None)
        else:
            self.requests[client_ip] = valid_timestamps
        
        if len(self.requests.get(client_ip, [])) >= self.max_requests:
            return False
        
        self.requests[client_ip].append(now)
        return True

limiter = InMemoryRateLimiter(settings.RATE_LIMIT_REQUESTS, settings.RATE_LIMIT_WINDOW_SECONDS)

async def rate_limit_middleware(request: Request, call_next):
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "127.0.0.1"

    if not limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=429,
            content={"error_code": "RATE_LIMIT_EXCEEDED", "message": "Too many requests. Please try again later."},
            headers={"Retry-After": str(settings.RATE_LIMIT_WINDOW_SECONDS)},
        )
    response = await call_next(request)
    return response
