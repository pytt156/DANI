from functools import lru_cache

from dani_api.rag.service import RagService
from dani_api.rag.vector_store import VectorStore


@lru_cache
def get_rag_service() -> RagService:
    """Return the shared RAG service instance."""
    return RagService()


@lru_cache
def get_vector_store() -> VectorStore:
    """Return the shared vector store instance."""
    return VectorStore()
