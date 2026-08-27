import mlflow
from mlflow.genai import load_prompt
from openai import OpenAI

from dani_api.access import AccessTier
from dani_api.config import settings

PROMPT_NAME = "dani-system-prompt"
PROMPT_ALIAS = "production"


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
            ),
            openrouter_model,
        )

    def _load_system_prompt(self) -> str:
        """Load the production DANI system prompt from MLflow."""
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)

        prompt = load_prompt(
            f"prompts:/{PROMPT_NAME}@{PROMPT_ALIAS}",
        )

        if not isinstance(prompt.template, str):
            raise TypeError("DANI system prompt must be registered as a text prompt.")

        return prompt.template.strip()

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

        system_instructions = self._load_system_prompt()

        response = self.client.responses.create(
            model=self.model,
            instructions=system_instructions,
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
