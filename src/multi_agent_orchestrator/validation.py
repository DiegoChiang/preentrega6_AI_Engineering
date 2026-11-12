"""Control de suficiencia y conflictos entre aportes."""

from __future__ import annotations

from typing import Any

from multi_agent_orchestrator.state import OrchestratorState


def validate_result(state: OrchestratorState) -> dict[str, Any]:
    findings = state.get("research_findings", [])
    analysis = state.get("analysis_result")
    feedback: list[str] = []

    source_ids = {item["source_id"] for item in findings}
    if len(source_ids) < 2:
        feedback.append("Se necesitan al menos dos fuentes diferenciadas.")
    if analysis is None:
        feedback.append("Falta el resultado del agente de analisis.")
    else:
        unknown = set(analysis["source_ids"]) - source_ids
        if unknown:
            feedback.append(f"El analisis cita fuentes inexistentes: {sorted(unknown)}.")
        if not 0 <= analysis["risk_score"] <= 100:
            feedback.append("El puntaje de riesgo debe estar entre 0 y 100.")
        if len(analysis["drivers"]) < 2:
            feedback.append("El analisis debe explicar al menos dos factores del resultado.")
        if not analysis["recommendation"].strip():
            feedback.append("Falta una recomendacion accionable.")

    passed = not feedback
    summary = (
        "Validacion aprobada: evidencia, calculo y trazabilidad son consistentes."
        if passed
        else "Validacion rechazada: " + " ".join(feedback)
    )
    return {
        "validation_feedback": feedback,
        "task_completed": passed,
        "contributions": [
            {
                "agent": "validator",
                "summary": summary,
                "evidence_ids": sorted(source_ids),
            }
        ],
        "completed_agents": ["validator"],
    }
