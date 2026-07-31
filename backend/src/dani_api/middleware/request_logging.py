from collections.abc import Awaitable, Callable
from time import perf_counter
from uuid import uuid4

import structlog
from fastapi import Request, Response
from structlog.contextvars import bind_contextvars, clear_contextvars

logger = structlog.get_logger(__name__)

CallNext = Callable[[Request], Awaitable[Response]]

REQUEST_ID_HEADER = "X-Request-ID"


async def request_logging_middleware(request: Request, call_next: CallNext) -> Response:
    """Log HTTP request metadata and attach a request ID."""

    clear_contextvars()

    request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid4())

    bind_contextvars(
        request_id=request_id, http_method=request.method, http_path=request.url.path
    )

    started_at = perf_counter()

    logger.info("http_request_started")

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((perf_counter() - started_at) * 1000, 2)

        logger.exception("http_request_failed", duration_ms=duration_ms)
        raise

    duration_ms = round((perf_counter() - started_at) * 1000, 2)

    response.headers[REQUEST_ID_HEADER] = request_id

    logger.info(
        "http_request_completed",
        status_code=response.status_code,
        duration_ms=duration_ms,
    )

    return response
