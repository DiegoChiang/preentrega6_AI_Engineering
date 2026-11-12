"""Sintesis final de los aportes validados."""

from __future__ import annotations

import json
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from multi_agent_orchestrator.state import OrchestratorState


class Synthesizer:
    def __init__(self, model: Any) -> None:
        self._model = model

    async def __call__(self, state: OrchestratorState) -> dict[str, Any]:
        if not state.get("task_completed"):
            raise RuntimeError("La sintesis requiere una validacion aprobada.")
        response = await self._model.ainvoke(
            [
                SystemMessage(
                    content=(
                        "Integra la evidencia validada en espanol. Incluye: hallazgo principal, "
                        "prioridad y puntaje, factores, acciones inmediatas y fuentes entre "
                        "corchetes. Cita unicamente los source_id exactos de research; el analisis "
                        "no es una fuente. No agregues datos que no aparezcan en el contexto."
                    )
                ),
                HumanMessage(
                    content=json.dumps(
                        {
                            "request": state["request"],
                            "research": state["research_findings"],
                            "analysis": state["analysis_result"],
                            "validated": state["task_completed"],
                        },
                        ensure_ascii=False,
                    )
                ),
            ]
        )
        content = response.content if isinstance(response.content, str) else str(response.content)
        return {
            "final_answer": content,
            "messages": [AIMessage(content=content)],
            "contributions": [
                {
                    "agent": "synthesizer",
                    "summary": "Respuesta final creada a partir de aportes validados.",
                    "evidence_ids": [
                        item["source_id"] for item in state["research_findings"]
                    ],
                }
            ],
            "completed_agents": ["synthesizer"],
        }
