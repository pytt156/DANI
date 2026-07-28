from functools import lru_cache

from dani_api.rag.service import RagService


@lru_cache
def get_rag_service() -> RagService:
    """Return the shared RAG service instance."""
    return RagService()
