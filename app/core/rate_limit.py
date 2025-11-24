"""SlowAPI rate limiting configuration."""

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.requests import Request
from starlette.responses import JSONResponse


def user_rate_limit_identifier(request: Request) -> str:
    """Return a stable identifier for user-specific rate limiting."""

    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return str(user_id)

    authorization = request.headers.get("Authorization")
    if authorization:
        return authorization

    return get_remote_address(request)


limiter = Limiter(key_func=user_rate_limit_identifier, default_limits=["100/minute"])


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:  # pragma: no cover - HTTP handler
    """Return a JSON response when the client exceeds the allowed rate."""

    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
