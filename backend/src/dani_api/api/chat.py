from typing import Annotated

from dani_api.access import resolve_access_tier
from dani_api.api.dependencies import get_rag_service
from dani_api.api.models import ChatRequest, ChatResponse, SourceResponse
from dani_api.rag.service import RagService
from fastapi import APIRouter, Depends, Header, HTTPException, status

router = APIRouter(prefix="/api/chat", tags=["chat"])

RagServiceDependency = Annotated[RagService, Depends(get_rag_service)]


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
def chat(
    request: ChatRequest,
    rag_service: RagServiceDependency,
    access_key: Annotated[str | None, Header(alias="X-DANI-Access-Key")] = None,
) -> ChatResponse:
    """Answer a question using knowledge base."""
    access_tier = resolve_access_tier(access_key)

    try:
        result = rag_service.answer(request.message)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
    except Exception as error:
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
