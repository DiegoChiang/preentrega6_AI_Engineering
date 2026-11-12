"""Construccion del modelo de lenguaje."""

from langchain_openai import ChatOpenAI

from multi_agent_orchestrator.config import Settings


def build_model(settings: Settings) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=settings.llm_temperature,
        timeout=settings.llm_timeout_seconds,
        max_retries=settings.llm_max_retries,
    )
