from dani_api.access import AccessTier
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for a DANI chat question."""

    message: str = Field(
        min_length=1,
        max_length=2000,
        examples=["Which projects has Daniela worked on?"],
    )


class SourceResponse(BaseModel):
    """A source used to generate the answer."""

    title: str
    source: str
    section: str | None
    chunk_index: int
    score: float


class ChatResponse(BaseModel):
    """Grounded answer returned by DANI."""

    answer: str
    sources: list[SourceResponse]
    access_tier: AccessTier
