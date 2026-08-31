from typing import Literal

from pydantic import BaseModel, Field, field_validator

from dani_api.access import AccessTier
from dani_api.conversation import ConversationMessage


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

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        """Reject whitespace-only questions and normalize surrounding whitespace."""

        normalized = value.strip()

        if not normalized:
            raise ValueError("Message cannot be empty.")

        return normalized

    def to_conversation_history(self) -> list[ConversationMessage]:
        """Convert validated API history to domain conversation messages."""
        return [
            ConversationMessage(
                role=message.role,
                content=message.content,
            )
            for message in self.history
        ]


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
