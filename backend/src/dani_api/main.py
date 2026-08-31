from typing import Annotated

import structlog
from fastapi import Depends, FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from dani_api.api.access import router as access_router
from dani_api.api.chat import router as chat_router
from dani_api.api.dependencies import get_vector_store
from dani_api.config import settings
from dani_api.logging_config import configure_logging
from dani_api.middleware.request_logging import request_logging_middleware
from dani_api.rag.vector_store import VectorStore

configure_logging(settings)

logger = structlog.get_logger(__name__)

VectorStoreDependency = Annotated[
    VectorStore,
    Depends(get_vector_store),
]

app = FastAPI(
    title="DANI API",
    description="AI-powered portfolio interface for Daniela.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(request_logging_middleware)

app.include_router(chat_router)
app.include_router(access_router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Return a basic application health response."""
    return {"status": "ok"}


@app.get("/ready", tags=["health"])
def readiness_check(
    vector_store: VectorStoreDependency,
    response: Response,
) -> dict[str, str]:
    """Return whether DANI is ready to serve chat requests."""

    missing_settings: list[str] = []

    if settings.openai_api_key is None:
        missing_settings.append("OPENAI_API_KEY")

    if settings.openrouter_api_key is None:
        missing_settings.append("OPENROUTER_API_KEY")

    if not settings.openrouter_chat_model.strip():
        missing_settings.append("OPENROUTER_CHAT_MODEL")

    if missing_settings:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        logger.warning(
            "readiness_check_failed",
            reason="configuration",
            missing_settings=missing_settings,
        )

        return {"status": "not_ready"}

    try:
        vector_store.health_check()

        if not vector_store.collection_exists():
            raise RuntimeError("Knowledge collection does not exist.")

        point_count = vector_store.count_points()

        if point_count <= 0:
            raise RuntimeError("Knowledge collection is empty.")

    except Exception as error:  # noqa: BLE001
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        logger.warning(
            "readiness_check_failed",
            reason="vector_store",
            error_type=type(error).__name__,
        )

        return {"status": "not_ready"}

    logger.debug(
        "readiness_check_passed",
        knowledge_points=point_count,
    )

    return {"status": "ready"}
