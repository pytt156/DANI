from collections.abc import Sequence
from functools import lru_cache

import mlflow
import structlog
from mlflow.genai import load_prompt
from openai import OpenAI

from dani_api.access import AccessTier
from dani_api.config import settings
from dani_api.conversation import ConversationMessage
from dani_api.mlflow_tracking import (
    configure_mlflow_client,
    mlflow_server_available,
)
from dani_api.prompts import (
    DEFAULT_SYSTEM_PROMPT,
    GROUNDING_GUARD,
    NO_ANSWER_PREFIX,
)

PROMPT_NAME = "dani-system-prompt"
PROMPT_ALIAS = "production"

logger = structlog.get_logger(__name__)


@lru_cache(maxsize=1)
def load_system_prompt() -> str:
    """Load DANI's system prompt, with a local fallback."""

    if not settings.mlflow_enabled:
        return DEFAULT_SYSTEM_PROMPT

    if not mlflow_server_available():
        return DEFAULT_SYSTEM_PROMPT

    try:
        configure_mlflow_client()

        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)

        prompt = load_prompt(
            f"prompts:/{PROMPT_NAME}@{PROMPT_ALIAS}",
        )
        if not isinstance(prompt.template, str):
            raise TypeError("DANI system prompt must be registered as a text prompt.")

        template = prompt.template.strip()

        if not template:
            raise ValueError("DANI system prompt is empty.")

        return template

    except Exception:
        logger.exception(
            "mlflow_prompt_load_failed",
            prompt_name=PROMPT_NAME,
            prompt_alias=PROMPT_ALIAS,
        )

        return DEFAULT_SYSTEM_PROMPT


def clean_model_answer(answer: str) -> str:
    """Remove internal control markers from a model answer."""
    normalized_answer = answer.strip()

    if normalized_answer.startswith(NO_ANSWER_PREFIX):
        normalized_answer = normalized_answer[len(NO_ANSWER_PREFIX) :].lstrip()

    return normalized_answer


class LanguageModel:
    """Generates grounded answers using OpenAI or OpenRouter."""

    def __init__(
        self,
        tier: AccessTier = AccessTier.FREE,
        model: str | None = None,
        client: OpenAI | None = None,
    ) -> None:
        self.tier = tier
        self.provider = self._provider_for_tier()

        if client is not None:
            self.client = client
            self.model = model or self._default_model()
            return

        self.client, self.model = self._create_client_and_model(model)

    def _provider_for_tier(self) -> str:
        """Return the provider used by the selected access tier."""

        if self.tier is AccessTier.PREMIUM:
            return "openai"

        return "openrouter"

    def _default_model(self) -> str:
        """Return the default model for the selected access tier."""

        if self.tier is AccessTier.PREMIUM:
            return settings.openai_chat_model

        return settings.openrouter_chat_model

    def _create_client_and_model(
        self,
        model: str | None,
    ) -> tuple[OpenAI, str]:
        """Create the API client and model for the selected access tier."""

        if self.tier is AccessTier.PREMIUM:
            if settings.openai_api_key is None:
                raise ValueError("OPENAI_API_KEY is not configured.")

            return (
                OpenAI(
                    api_key=settings.openai_api_key.get_secret_value(),
                    timeout=settings.provider_timeout_seconds,
                    max_retries=settings.provider_max_retries,
                ),
                model or settings.openai_chat_model,
            )

        if settings.openrouter_api_key is None:
            raise ValueError("OPENROUTER_API_KEY is not configured.")

        openrouter_model = model or settings.openrouter_chat_model

        if not openrouter_model:
            raise ValueError("OPENROUTER_CHAT_MODEL is not configured.")

        return (
            OpenAI(
                api_key=settings.openrouter_api_key.get_secret_value(),
                base_url=settings.openrouter_base_url,
                timeout=settings.provider_timeout_seconds,
                max_retries=settings.provider_max_retries,
            ),
            openrouter_model,
        )

    def _load_system_prompt(self) -> str:
        """Return the configured DANI system prompt."""

        return load_system_prompt()

    def generate_answer(
        self,
        question: str,
        context: str,
        history: Sequence[ConversationMessage] = (),
    ) -> str:
        """Generate an answer grounded in supplied context."""

        normalized_question = question.strip()
        normalized_context = context.strip()

        if not normalized_question:
            raise ValueError("Question cannot be empty.")

        if not normalized_context:
            raise ValueError("Context cannot be empty.")

        system_instructions = f"{self._load_system_prompt()}\n\n{GROUNDING_GUARD}"

        history_text = "\n".join(
            f"{message.role.capitalize()}: {message.content.strip()}"
            for message in history
            if message.content.strip()
        )

        input_text = f"Knowledge context:\n\n{normalized_context}\n\n"

        if history_text:
            input_text += f"Conversation history:\n\n{history_text}\n\n"

        input_text += f"Current user question:\n{normalized_question}"

        response = self.client.responses.create(
            model=self.model,
            instructions=system_instructions,
            input=input_text,
            store=False,
        )

        answer = clean_model_answer(response.output_text)

        if not answer:
            raise ValueError("The language model returned an empty answer.")

        return answer
