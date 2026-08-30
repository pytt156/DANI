from collections.abc import Sequence

from dani_api.config import settings
from qdrant_client import QdrantClient, models

DEFAULT_VECTOR_SIZE = 1536
DEFAULT_UPSERT_BATCH_SIZE = 100


class VectorStore:
    """Handles the connection to the Qdrant vector database"""

    def __init__(
        self,
        url: str | None = None,
        collection_name: str | None = None,
        vector_size: int = DEFAULT_VECTOR_SIZE,
        client: QdrantClient | None = None,
    ) -> None:
        self.url = url or settings.qdrant_url
        self.collection_name = collection_name or settings.qdrant_collection
        self.vector_size = vector_size
        self.client = client or QdrantClient(url=self.url)

    def health_check(self) -> bool:
        """Verify that Qdrant is reachable"""
        self.client.get_collections()
        return True

    def collection_exists(self) -> bool:
        """Return whether the configured collection exists."""
        return self.client.collection_exists(self.collection_name)

    def search(
        self,
        query_vector: list[float],
        limit: int = 5,
        score_threshold: float | None = None,
    ) -> list[models.ScoredPoint]:
        """Search for the points most similar to a query vector."""
        if limit <= 0:
            raise ValueError("limit must be greater than zero.")

        if len(query_vector) != self.vector_size:
            raise ValueError(
                f"Query vector has {len(query_vector)} dimensions; "
                f"expected {self.vector_size}."
            )

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            with_payload=True,
            with_vectors=False,
        )

        return response.points

    def ensure_collection(self) -> bool:
        """
        Create the Qdrant collection if it does not already exists.

        Returns:
            True if the collection was created
            False if the collection already existed
        """
        if self.client.collection_exists(self.collection_name):
            return False

        self._create_collection()
        return True

    def reset_collection(self) -> None:
        """Delete and recreate the collection."""
        if self.client.collection_exists(self.collection_name):
            self.client.delete_collection(self.collection_name)

        self._create_collection()

    def upsert_points(
        self,
        point_ids: Sequence[str],
        vectors: Sequence[list[float]],
        payloads: Sequence[dict[str, object]],
        batch_size: int = DEFAULT_UPSERT_BATCH_SIZE,
    ) -> int:
        """Insert or replace points in batches."""
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than zero.")

        if not (len(point_ids) == len(vectors) == len(payloads)):
            raise ValueError("point_ids, vectors and payloads must have equal lengths.")
        for index, vector in enumerate(vectors):
            if len(vector) != self.vector_size:
                raise ValueError(
                    f"Vector at index {index} has {len(vector)} dimensions; "
                    f"expected {self.vector_size}."
                )
        total_points = len(point_ids)

        for start_index in range(0, total_points, batch_size):
            end_index = start_index + batch_size

            points = [
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
                for point_id, vector, payload in zip(
                    point_ids[start_index:end_index],
                    vectors[start_index:end_index],
                    payloads[start_index:end_index],
                    strict=True,
                )
            ]

            self.client.upsert(
                collection_name=self.collection_name, points=points, wait=True
            )

        return total_points

    def count_points(self) -> int:
        """Return the number of scored points."""
        result = self.client.count(collection_name=self.collection_name, exact=True)

        return result.count

    def _create_collection(self) -> None:
        """Create the configured Qdrant collection."""
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=self.vector_size, distance=models.Distance.COSINE
            ),
        )


if __name__ == "__main__":
    vector_store = VectorStore()

    try:
        vector_store.health_check()
        created = vector_store.ensure_collection()
    except Exception as error:
        raise SystemExit(
            f"Could not connect to Qdrant at {vector_store.url}: {error}"
        ) from error

    if created:
        print(
            f"Created collection '{vector_store.collection_name}'"
            f"with vector size {vector_store.vector_size}."
        )
    else:
        print(
            f"Collection '{vector_store.collection_name}' already exists."
            f"with {vector_store.count_points()} points."
        )
