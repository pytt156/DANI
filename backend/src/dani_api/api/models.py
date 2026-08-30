from typing import Literal

from dani_api.access import AccessTier
from pydantic import BaseModel, Field


class ChatHistoryMessage(BaseModel):
    """A previous message supplied as conversational context."""

    role: Literal["user", "assistant"]

    content: str = Field(
        min_length=1,
        max_length=4000,
    )


class ChatRequest(BaseModel):
    """Request body for a DANI chat question."""

    message: str = Field(
        min_length=1,
        max_length=2000,
        examples=["Which projects has Daniela worked on?"],
    )

    history: list[ChatHistoryMessage] = Field(
        default_factory=list,
        max_length=8,
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
