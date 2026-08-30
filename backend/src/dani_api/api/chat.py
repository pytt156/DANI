from typing import Annotated

import structlog
from dani_api.access import resolve_access_tier
from dani_api.api.dependencies import get_rag_service
from dani_api.api.models import ChatRequest, ChatResponse, SourceResponse
from dani_api.conversation import ConversationMessage
from dani_api.rag.service import RagService
from fastapi import APIRouter, Depends, Header, HTTPException, status

router = APIRouter(prefix="/api/chat", tags=["chat"])

logger = structlog.get_logger(__name__)

RagServiceDependency = Annotated[
    RagService,
    Depends(get_rag_service),
]


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
def chat(
    request: ChatRequest,
    rag_service: RagServiceDependency,
    access_key: Annotated[
        str | None,
        Header(alias="X-DANI-Access-Key"),
    ] = None,
) -> ChatResponse:
    """Answer a question using the knowledge base."""

    access_tier = resolve_access_tier(access_key)

    history = [
        ConversationMessage(
            role=message.role,
            content=message.content.strip(),
        )
        for message in request.history
        if message.content.strip()
    ]

    try:
        result = rag_service.answer(
            request.message,
            tier=access_tier,
            history=history,
        )

    except Exception as error:
        logger.exception(
            "chat_request_failed",
            access_tier=access_tier.value,
            error_type=type(error).__name__,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The knowledge service is temporarily unavailable",
        ) from error

    return ChatResponse(
        answer=result.answer,
        sources=[
            SourceResponse(
                title=source.title,
                source=source.source,
                section=source.section,
                chunk_index=source.chunk_index,
                score=source.score,
            )
            for source in result.sources
        ],
        access_tier=access_tier,
    )
