"""Herramientas funcionales y acotadas de los agentes especialistas."""

from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.tools import tool
from pydantic import BaseModel, Field

_KNOWLEDGE_BASE: tuple[dict[str, Any], ...] = (
    {
        "source_id": "runbook-checkout-01",
        "title": "Runbook de errores del checkout",
        "summary": (
            "Una tasa de error superior a 8% durante mas de 10 minutos exige escalar al equipo "
            "de pagos. El primer control es verificar el pool de conexiones y el proveedor externo."
        ),
        "metrics": {"error_rate_pct": 12.4, "duration_minutes": 18.0},
        "tags": ["checkout", "errores", "pagos", "runbook"],
    },
    {
        "source_id": "telemetry-checkout-02",
        "title": "Telemetria consolidada del incidente",
        "summary": (
            "El p95 de checkout alcanzo 2450 ms, 1840 usuarios encontraron fallos y el servicio "
            "de catalogo se mantuvo dentro de sus objetivos."
        ),
        "metrics": {"latency_p95_ms": 2450.0, "affected_users": 1840.0},
        "tags": ["checkout", "latencia", "usuarios", "telemetria"],
    },
    {
        "source_id": "postmortem-payments-03",
        "title": "Postmortem de saturacion del adaptador de pagos",
        "summary": (
            "Un patron comparable se resolvio limitando reintentos, ampliando el pool y activando "
            "el circuito de degradacion mientras se recuperaba el proveedor."
        ),
        "metrics": {"retry_multiplier": 3.1, "recovery_minutes": 27.0},
        "tags": ["pagos", "checkout", "reintentos", "mitigacion"],
    },
    {
        "source_id": "runbook-search-04",
        "title": "Runbook de busqueda de productos",
        "summary": "La busqueda se degrada cuando el indice supera cinco minutos de atraso.",
        "metrics": {"index_lag_minutes": 7.0},
        "tags": ["busqueda", "catalogo", "indice"],
    },
)


class SearchInput(BaseModel):
    query: str = Field(min_length=3, description="Solicitud o tema que se debe investigar")
    limit: int = Field(default=3, ge=1, le=4)


class PriorityInput(BaseModel):
    error_rate_pct: float = Field(ge=0, le=100)
    latency_p95_ms: float = Field(ge=0)
    affected_users: int = Field(ge=0)
    duration_minutes: float = Field(ge=0)


def _terms(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.casefold()))


@tool(args_schema=SearchInput)
def search_incident_knowledge(query: str, limit: int = 3) -> str:
    """Busca evidencia operativa en una base documental local simulada."""

    query_terms = _terms(query)
    ranked: list[tuple[int, dict[str, Any]]] = []
    for document in _KNOWLEDGE_BASE:
        searchable = " ".join(
            [document["title"], document["summary"], " ".join(document["tags"])]
        )
        score = len(query_terms & _terms(searchable))
        ranked.append((score, document))
    ranked.sort(key=lambda item: item[0], reverse=True)
    matches = [document for score, document in ranked if score > 0][:limit]
    if not matches:
        matches = [ranked[0][1]]
    return json.dumps(matches, ensure_ascii=False)


@tool(args_schema=PriorityInput)
def calculate_incident_priority(
    error_rate_pct: float,
    latency_p95_ms: float,
    affected_users: int,
    duration_minutes: float,
) -> str:
    """Calcula un puntaje reproducible y una prioridad operativa P1-P4."""

    error_component = min(error_rate_pct / 15.0, 1.0) * 35
    latency_component = min(latency_p95_ms / 3000.0, 1.0) * 25
    users_component = min(affected_users / 2000.0, 1.0) * 25
    duration_component = min(duration_minutes / 30.0, 1.0) * 15
    score = round(error_component + latency_component + users_component + duration_component, 1)
    if score >= 75:
        priority = "P1"
    elif score >= 50:
        priority = "P2"
    elif score >= 25:
        priority = "P3"
    else:
        priority = "P4"
    return json.dumps(
        {
            "priority": priority,
            "risk_score": score,
            "components": {
                "errors": round(error_component, 1),
                "latency": round(latency_component, 1),
                "users": round(users_component, 1),
                "duration": round(duration_component, 1),
            },
        },
        ensure_ascii=False,
    )
