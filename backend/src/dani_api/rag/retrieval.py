import argparse
from dataclasses import dataclass
from typing import Any

from dani_api.rag.embeddings import EmbeddingService
from dani_api.rag.vector_store import VectorStore

DEFAULT_RESULT_LIMIT = 5


@dataclass(frozen=True)
class RetrievalResult:
    """A knowledge chunk returned by semantic search."""

    content: str
    source: str
    title: str
    section: str | None
    chunk_index: int
    score: float


def payload_string(
    payload: dict[str, Any],
    key: str,
) -> str:
    """Read a required string value from Qdrant payload."""
    value = payload.get(key)

    if not isinstance(value, str):
        raise TypeError(f"Qdrant payload field '{key}' must be a string")

    return value


def payload_optional_string(
    payload: dict[str, Any],
    key: str,
) -> str | None:
    """Read an optional string value from a Qdrant payload."""
    value = payload.get(key)

    if value is None:
        return None

    if not isinstance(value, str):
        raise TypeError(f"Qdrant payload field '{key}' must be a string or null.")

    return value


def payload_integer(payload: dict[str, Any], key: str) -> int:
    """Read a required integer value from a Qdrant payload."""
    value = payload.get(key)

    if not isinstance(value, int):
        raise TypeError(f"Qdrant payload field '{key}' must be an integer.")

    return value


class KnowledgeRetriever:
    """Retrieves relevant knowledge chunks for a text query."""

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        vector_store: VectorStore | None = None,
    ) -> None:
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or VectorStore()

    def retrieve(
        self,
        query: str,
        limit: int = DEFAULT_RESULT_LIMIT,
        score_threshold: float | None = None,
    ) -> list[RetrievalResult]:
        """Retrieve the knowledge chunks most relevant to a query."""
        normalized_query = query.strip()

        if not normalized_query:
            raise ValueError("Query cannot be empty.")

        query_vector = self.embedding_service.embed_text(normalized_query)

        scored_points = self.vector_store.search(
            query_vector=query_vector, limit=limit, score_threshold=score_threshold
        )

        results: list[RetrievalResult] = []

        for point in scored_points:
            payload = point.payload

            if payload is None:
                raise ValueError(f"Qdrant point '{point.id}' has no payload.")

            results.append(
                RetrievalResult(
                    content=payload_string(payload, "content"),
                    source=payload_string(payload, "source"),
                    title=payload_string(payload, "title"),
                    section=payload_optional_string(payload, "section"),
                    chunk_index=payload_integer(payload, "chunk_index"),
                    score=float(point.score),
                )
            )

        return results


def build_argument_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(description="Search the DANI knowledge base")
    parser.add_argument("query", help="Question or search text.")
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_RESULT_LIMIT,
        help="Maximum number of results.",
    )
    parser.add_argument(
        "--score-threshold",
        type=float,
        default=None,
        help="Optional minimum similarity score.",
    )

    return parser


if __name__ == "__main__":
    arguments = build_argument_parser().parse_args()
    retriever = KnowledgeRetriever()

    try:
        matches = retriever.retrieve(
            query=arguments.query,
            limit=arguments.limit,
            score_threshold=arguments.score_threshold,
        )
    except Exception as error:
        raise SystemExit(f"Knowledge retrieval failed: {error}") from error

    if not matches:
        print("No matching knowledge chunks found.")
        raise SystemExit(0)

    print(f"Retrieved {len(matches)} knowledge chunks:\n")

    for position, match in enumerate(matches, start=1):
        print(f"{position}. {match.title} [score={match.score:.4f}]")
        print(f"    Source: {match.source}")
        print(f"    Section: {match.section or 'No section'}")
        print(f"    Chunk: {match.chunk_index}")
        print(f"    Content: {match.content}\n")
