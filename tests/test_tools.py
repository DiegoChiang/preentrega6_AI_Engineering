import json

import pytest

from incident_agent.tools import search_technical_knowledge


@pytest.mark.asyncio
async def test_tool_returns_structured_evidence_for_specific_component():
    raw = await search_technical_knowledge.ainvoke(
        {"query": "Redis memoria y TTL", "purpose": "confirmar umbral crítico"}
    )
    result = json.loads(raw)

    assert result["status"] == "ok"
    assert result["results"][0]["source"] == "guia-redis-idempotencia"
    assert "0,92" in result["results"][0]["evidence"]


@pytest.mark.asyncio
async def test_tool_requests_a_more_specific_query():
    raw = await search_technical_knowledge.ainvoke(
        {"query": "incidente general", "purpose": "buscar evidencia"}
    )
    result = json.loads(raw)

    assert result["status"] == "incomplete"
    assert result["known_components"] == ["API de pagos", "Redis", "PostgreSQL"]


@pytest.mark.asyncio
async def test_tool_requires_one_component_per_call():
    raw = await search_technical_knowledge.ainvoke(
        {"query": "Redis y API de pagos", "purpose": "comparar umbrales"}
    )
    result = json.loads(raw)

    assert result["status"] == "incomplete"
    assert set(result["matched_sources"]) == {
        "guia-redis-idempotencia",
        "runbook-api-pagos",
    }
