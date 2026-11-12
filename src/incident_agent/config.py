"""Configuración del agente desde variables de entorno."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    openai_api_key: SecretStr | None = None
    openai_model: str = Field(default="gpt-5.4-mini", min_length=1)
    llm_temperature: float = Field(default=0, ge=0, le=2)
    llm_timeout_seconds: float = Field(default=45, gt=0)
    llm_max_retries: int = Field(default=2, ge=0, le=5)

    checkpoint_db: Path = Path("state/agent_checkpoints.sqlite")
    trace_dir: Path = Path("artifacts")
    recursion_limit: int = Field(default=10, ge=4, le=25)

    def require_openai_key(self) -> str:
        if self.openai_api_key is None:
            raise ValueError("Falta la variable de entorno OPENAI_API_KEY")
        value = self.openai_api_key.get_secret_value().strip()
        if not value:
            raise ValueError("Falta la variable de entorno OPENAI_API_KEY")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
