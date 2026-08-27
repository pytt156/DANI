from collections.abc import Sequence

from dani_api.config import settings
from openai import OpenAI

DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_VECTOR_SIZE = 1536
DEFAULT_BATCH_SIZE = 100


class EmbeddingService:
    """Creates text embeddings using the OpenAI API"""

    def __init__(
        self,
        model: str | None = None,
        vector_size: int = DEFAULT_VECTOR_SIZE,
        client: OpenAI | None = None,
    ) -> None:
        self.model = model or settings.openai_embedding_model
        self.vector_size = vector_size

        if client is not None:
            self.client = client
            return

        if settings.openai_api_key is None:
            raise ValueError(
                "OPENAI_API_KEY is missing. Add it to the project root .env file."
            )

        self.client = OpenAI(api_key=settings.openai_api_key.get_secret_value())

    def embed_text(self, text: str) -> list[float]:
        """Create one embedding vector from a non-empty text."""
        normalized_text = text.strip()

        if not normalized_text:
            raise ValueError("Cannot create an embedding from empty text.")

        response = self.client.embeddings.create(
            model=self.model, input=normalized_text, encoding_format="float"
        )

        embedding = response.data[0].embedding
        self._validate_embeddings(embedding)

        return embedding

    def embed_texts(
        self, texts: Sequence[str], batch_size: int = DEFAULT_BATCH_SIZE
    ) -> list[list[float]]:
        """
        Create embeddings for several texts while preserving input order.

        Requests are split into batches to avoid sending the complete
        knowledge base in one API call.
        """
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than zero.")

        normalized_texts = [text.strip() for text in texts]

        if not normalized_texts:
            return []

        empty_indexes = [
            index for index, text in enumerate(normalized_texts) if not text
        ]

        if empty_indexes:
            raise ValueError(
                "cannot create embeddings from empty text. "
                f"Empty input indexes: {empty_indexes}"
            )

        embeddings: list[list[float]] = []

        for start_index in range(0, len(normalized_texts), batch_size):
            batch = normalized_texts[start_index : start_index + batch_size]

            response = self.client.embeddings.create(
                model=self.model, input=batch, encoding_format="float"
            )

            ordered_data = sorted(response.data, key=lambda item: item.index)

            if len(ordered_data) != len(batch):
                raise RuntimeError(
                    "OpenAI returned a different number of embeddings "
                    "than the number of submitted texts."
                )

            for item in ordered_data:
                self._validate_embeddings(item.embedding)
                embeddings.append(item.embedding)

        return embeddings

    def _validate_embeddings(self, embedding: list[float]) -> None:
        """Verify that an embedding matches the Qdrant collection."""
        if len(embedding) != self.vector_size:
            raise ValueError(
                "Embedding dimension does not match the configured "
                f"vector size: expected {self.vector_size}, "
                f"recieved {len(embedding)}."
            )


if __name__ == "__main__":
    service = EmbeddingService()

    try:
        embedding = service.embed_text("Daniela is studying AI and MLOps Engineering.")
    except Exception as error:
        raise SystemExit(
            f"Could not create embedding with model '{service.model}': {error}"
        ) from error

    print(
        f"Created embedding with model '{service.model}' "
        f"and {len(embedding)} dimensions."
    )
