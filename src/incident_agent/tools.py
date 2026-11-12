"""Herramientas acotadas para consultar evidencia operativa."""

import asyncio
import json
import re

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class KnowledgeSearchInput(BaseModel):
    query: str = Field(
        min_length=3,
        description=(
            "Consulta específica sobre exactamente un componente técnico, síntoma o procedimiento."
        ),
    )
    purpose: str = Field(
        min_length=3,
        description="Dato concreto que se necesita confirmar antes de responder al usuario.",
    )


KNOWLEDGE_BASE = [
    {
        "source": "runbook-api-pagos",
        "aliases": {"pagos", "payments", "5xx"},
        "evidence": (
            "La API de pagos considera crítico un 5xx superior al 5 % durante diez minutos. "
            "El diagnóstico revisa Grafana, logs correlacionados, PostgreSQL, Redis y lag de Kafka."
        ),
    },
    {
        "source": "guia-redis-idempotencia",
        "aliases": {"redis", "idempotencia", "memoria", "duplicados", "ttl"},
        "evidence": (
            "Redis alerta por memoria al superar 0,80 y entra en nivel crítico sobre 0,92 durante "
            "cinco minutos. Las claves de idempotencia deben conservar TTL de 24 horas."
        ),
    },
    {
        "source": "recuperacion-postgresql",
        "aliases": {"postgresql", "postgres", "wal", "restauracion", "base", "datos"},
        "evidence": (
            "La recuperación usa un respaldo completo y reproducción de WAL. La promoción exige "
            "validaciones contables, integridad referencial y aprobación del responsable de datos."
        ),
    },
]


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-záéíóúñ0-9]+", text.casefold()))


@tool(args_schema=KnowledgeSearchInput)
async def search_technical_knowledge(query: str, purpose: str) -> str:
    """Busca evidencia operativa para un único componente técnico.

    Debe invocarse antes de afirmar umbrales, procedimientos o causas de un incidente. La consulta
    tiene que nombrar un componente o síntoma concreto. Si el resultado indica `incomplete`, se debe
    formular una consulta más específica y volver a invocar la herramienta. En solicitudes con
    varios componentes, se ejecuta una llamada independiente por componente.
    """

    await asyncio.sleep(0)
    query_tokens = _tokens(query)
    matches = [record for record in KNOWLEDGE_BASE if query_tokens & record["aliases"]]
    if not matches:
        result = {
            "status": "incomplete",
            "query": query,
            "purpose": purpose,
            "message": (
                "La consulta no identifica un componente conocido; agrega un nombre técnico."
            ),
            "known_components": ["API de pagos", "Redis", "PostgreSQL"],
        }
    elif len(matches) > 1:
        result = {
            "status": "incomplete",
            "query": query,
            "purpose": purpose,
            "message": (
                "La consulta mezcla varios componentes. Ejecuta una consulta independiente "
                "para cada fuente antes de formular la conclusión."
            ),
            "matched_sources": [record["source"] for record in matches],
        }
    else:
        result = {
            "status": "ok",
            "query": query,
            "purpose": purpose,
            "results": [
                {"source": record["source"], "evidence": record["evidence"]}
                for record in matches
            ],
        }
    return json.dumps(result, ensure_ascii=False)


TOOLS = [search_technical_knowledge]
