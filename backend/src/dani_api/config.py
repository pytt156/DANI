from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env."""

    environment: Literal["development", "production", "test"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_json: bool | None = None

    openai_api_key: SecretStr | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-5-mini"

    openrouter_api_key: SecretStr | None = None
    openrouter_chat_model: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    premium_access_key_hashes: str = ""

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "dani_knowledge"

    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def premium_access_key_hash_set(self) -> set[str]:
        """Return configured premium access-key hashes."""
        return {
            value.strip()
            for value in self.premium_access_key_hashes.split(",")
            if value.strip()
        }

    @property
    def use_json_logs(self) -> bool:
        """Return whether logs should be rendered as JSON."""
        if self.log_json is not None:
            return self.log_json

        return self.environment == "production"


settings = Settings()
