from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dani_api.api.chat import router as chat_router
from dani_api.config import settings
from dani_api.logging_config import configure_logging
from dani_api.middleware.request_logging import request_logging_middleware

configure_logging(settings)

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


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Return a basic application health response."""
    return {"status": "ok"}
