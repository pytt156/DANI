from openai import OpenAI

from dani_api.config import settings

SYSTEM_INSTRUCTIONS = """
You are DANI, an AI interface representing Daniela professionally.

Answer the user's question using only the supplied knowledge context.

Rules:
- Do not invent information.
- Do not use outside knowledge about Daniela.
- If the context does not contain enough information, say so clearly.
- Answer in the same language as the user's question.
- Write naturally and professionally.
- Refer to Daniela in the third person.
- Do not mention that you are reading chunks, embeddings or a vector database.
- When useful, cite supporting context using markers such as [Source 1].
""".strip()


class LanguageModel:
    """Generates grounded answers using the OpenAI Responses API."""

    def __init__(
        self,
        model: str | None = None,
        client: OpenAI | None = None,
    ) -> None:
        if settings.openai_api_key is None:
            raise ValueError("OPENAI_API_KEY is not configured.")

        self.model = model or settings.openai_chat_model
        self.client = client or OpenAI(
            api_key=settings.openai_api_key.get_secret_value()
        )

    def generate_answer(
        self,
        question: str,
        context: str,
    ) -> str:
        """Generate an answer grounded in supplied context."""
        normalized_question = question.strip()
        normalized_context = context.strip()

        if not normalized_question:
            raise ValueError("Question cannot be empty.")

        if not normalized_context:
            raise ValueError("Context cannot be empty.")

        response = self.client.responses.create(
            model=self.model,
            instructions=SYSTEM_INSTRUCTIONS,
            input=(
                "Knowledge context:\n\n"
                f"{normalized_context}\n\n"
                "User question:\n"
                f"{normalized_question}"
            ),
            store=False,
        )

        answer = response.output_text.strip()

        if not answer:
            raise ValueError("The language model returned an empty answer.")

        return answer
