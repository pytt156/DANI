from fastapi import FastAPI

from dani_api.api.chat import router as chat_router

app = FastAPI(
    title="DANI API",
    description="AI-powered portfolio interface for Daniela.",
    version="0.1.0",
)

app.include_router(chat_router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Return a basic application health response."""
    return {"status": "ok"}
