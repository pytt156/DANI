from dataclasses import dataclass
from typing import Literal

ConversationRole = Literal["user", "assistant"]


@dataclass(frozen=True)
class ConversationMessage:
    """One previous message in a chat conversation."""

    role: ConversationRole
    content: str
