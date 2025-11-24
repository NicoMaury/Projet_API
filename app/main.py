"""Rail Traffic Analytics FastAPI entrypoint."""

import logging
import time

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.routes import api_router
from app.core.config import get_settings
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from app.core.database import SessionLocal, init_db
from app.models.db import RequestLog

logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.API_TITLE, version=settings.API_VERSION)

    init_db()

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = int((time.perf_counter() - start_time) * 1000)

        session = SessionLocal()
        try:
            log_entry = RequestLog(
                method=request.method,
                path=request.url.path,
                user_id=getattr(request.state, "user_id", None),
                status_code=response.status_code,
                duration_ms=duration_ms,
            )
            session.add(log_entry)
            session.commit()
        except Exception:  # pragma: no cover - defensive logging
            session.rollback()
            logger.exception("Failed to persist request log")
        finally:
            session.close()

        return response

    @app.get("/", include_in_schema=False)
    async def root():
        """Redirection automatique vers la documentation interactive."""
        return RedirectResponse(url="/docs")

    app.include_router(api_router)

    return app


app = create_application()
