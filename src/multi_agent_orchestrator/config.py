"""Configuracion del prototipo."""

from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Variables necesarias para ejecutar el grafo."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = Field(min_length=1)
    openai_model: str = "gpt-5.4-mini"
    llm_temperature: float = Field(default=0, ge=0, le=2)
    llm_timeout_seconds: float = Field(default=45, gt=0)
    llm_max_retries: int = Field(default=2, ge=0, le=10)
    supervisor_max_steps: int = Field(default=8, ge=4, le=20)
    recursion_limit: int = Field(default=30, ge=10, le=100)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv()
    return Settings()  # type: ignore[call-arg]
