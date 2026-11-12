import json

from multi_agent_orchestrator.tools import (
    calculate_incident_priority,
    search_incident_knowledge,
)


def test_research_tool_returns_relevant_sources() -> None:
    payload = search_incident_knowledge.invoke(
        {"query": "errores checkout pagos latencia", "limit": 3}
    )
    findings = json.loads(payload)

    assert len(findings) == 3
    assert "runbook-checkout-01" in {item["source_id"] for item in findings}
    assert all(item["metrics"] for item in findings)


def test_priority_tool_is_reproducible() -> None:
    payload = calculate_incident_priority.invoke(
        {
            "error_rate_pct": 12.4,
            "latency_p95_ms": 2450,
            "affected_users": 1840,
            "duration_minutes": 18,
        }
    )
    result = json.loads(payload)

    assert result["priority"] == "P1"
    assert result["risk_score"] == 81.3
    assert set(result["components"]) == {"errors", "latency", "users", "duration"}
