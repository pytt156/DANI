import os

from qdrant_client import QdrantClient, models

DEFAULT_QDRANT_URL = "http://localhost:6333"
DEFAULT_COLLECTION_NAME = "dani_knowledge"
DEFAULT_VECTOR_SIZE = 1536


class VectorStore:
    """Handles the connection to the Qdrant vector database"""

    def __init__(
        self,
        url: str | None = None,
        collection_name: str | None = None,
        vector_size: int = DEFAULT_VECTOR_SIZE,
    ) -> None:
        self.url = url or os.getenv("QDRANT_URL", DEFAULT_QDRANT_URL)
        self.collection_name = collection_name or os.getenv(
            "QDRANT_COLLECTION", DEFAULT_COLLECTION_NAME
        )
        self.vector_size = vector_size
        self.client = QdrantClient(url=self.url)

    def ensure_collection(self) -> bool:
        """
        Create the Qdrant collection if it does not already exists.

        Returns:
            True if a new collection was created
            False if the collection already existed
        """
        if self.client.collection_exists(self.collection_name):
            return False

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=self.vector_size, distance=models.Distance.COSINE
            ),
        )

        return True

    def health_check(self) -> bool:
        """Verify that Qdrant is reachable"""
        self.client.get_collections()
        return True


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
        print(f"Collection '{vector_store.collection_name}' already exists.")
