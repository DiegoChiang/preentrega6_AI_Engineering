"""Construcción del modelo que decide las llamadas de herramienta."""

from typing import Any

from incident_agent.config import Settings


def configure_certificate_store() -> None:
    try:
        import truststore

        truststore.inject_into_ssl()
    except (ImportError, RuntimeError):
        return


def build_chat_model(settings: Settings) -> Any:
    configure_certificate_store()
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Instala la dependencia 'langchain-openai'") from exc
    return ChatOpenAI(
        api_key=settings.require_openai_key(),
        model=settings.openai_model,
        temperature=settings.llm_temperature,
        timeout=settings.llm_timeout_seconds,
        max_retries=settings.llm_max_retries,
    )
