import hashlib
import uuid

from dani_api.rag.chunker import KnowledgeChunk, chunk_documents
from dani_api.rag.embeddings import EmbeddingService
from dani_api.rag.loader import load_markdown_documents
from dani_api.rag.vector_store import VectorStore

POINT_ID_NAMESPACE = uuid.UUID("3a62bf14-f732-4a79-9c43-70fa8162a488")


def create_point_id(chunk: KnowledgeChunk) -> str:
    """
    Create a deterministic UUID for a knowledge chunk.

    The ID changes when the chunk content or identifying metadata changes.
    """
    content_hash = hashlib.sha256(chunk.content.encode("utf-8")).hexdigest()

    identity = "|".join(
        [chunk.source, chunk.section or "", str(chunk.chunk_index), content_hash]
    )

    return str(uuid.uuid5(POINT_ID_NAMESPACE, identity))


def create_payload(chunk: KnowledgeChunk) -> dict[str, object]:
    """Create searchable metadata stored with a Qdrant point."""
    return {
        "content": chunk.content,
        "source": chunk.source,
        "title": chunk.title,
        "section": chunk.section,
        "chunk_index": chunk.chunk_index,
    }


def ingest_knowledge_base() -> int:
    """
    Load, chunk, embed and store the complete knowledge base.

    Embeddings are created before the existing collection is replaced so
    that an embedding failure does not erase the current knowledge base.
    """

    print("Loading knowledge documents...")
    documents = load_markdown_documents()

    if not documents:
        raise RuntimeError("No knowledge documents were found.")

    print(f"Loaded {len(documents)} documents.")

    chunks = chunk_documents(documents)

    if not chunks:
        raise RuntimeError("The knowledge documents produced no chunks.")

    print(f"Created {len(chunks)} chunks.")

    embedding_service = EmbeddingService()
    texts = [chunk.content for chunk in chunks]

    print(f"Creating embeddings with '{embedding_service.model}'...")

    vectors = embedding_service.embed_texts(texts)

    if len(vectors) != len(chunks):
        raise RuntimeError(
            "The number of embeddings does not match the number of chunks."
        )

    print(f"Created {len(vectors)} embeddings.")

    point_ids = [create_point_id(chunk) for chunk in chunks]
    payloads = [create_payload(chunk) for chunk in chunks]

    if len(set(point_ids)) != len(point_ids):
        raise RuntimeError("Duplicate Qdrant point IDs were generated.")

    vector_store = VectorStore()
    vector_store.health_check()

    print(f"Replacing collection '{vector_store.collection_name}'...")
    vector_store.reset_collection()

    stored_count = vector_store.upsert_points(
        point_ids=point_ids, vectors=vectors, payloads=payloads
    )

    actual_count = vector_store.count_points()

    if actual_count != stored_count:
        raise RuntimeError(
            f"Qdrant contains {actual_count} points "
            f"in '{vector_store.collection_name}'."
        )

    print(
        f"Ingestion complete: stored {actual_count} points "
        f"in '{vector_store.collection_name}'."
    )

    return actual_count


if __name__ == "__main__":
    try:
        ingest_knowledge_base()
    except Exception as error:
        raise SystemExit(f"Knowledge ingestion failed: {error}") from error
