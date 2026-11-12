"""Interfaz de linea de comandos."""

from __future__ import annotations

import argparse
import asyncio
import json

from multi_agent_orchestrator.runner import run_orchestrator

DEFAULT_QUERY = (
    "Investiga el impacto del aumento de errores en checkout, calcula su prioridad y propone "
    "acciones inmediatas basadas en evidencia."
)


async def _run(query: str, show_trace: bool) -> None:
    state, trace = await run_orchestrator(query)
    if show_trace:
        print(json.dumps(trace, ensure_ascii=False, indent=2))
    print("\nRESPUESTA FINAL\n")
    print(state["final_answer"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Orquestador multi-agente especializado")
    parser.add_argument("query", nargs="?", default=DEFAULT_QUERY)
    parser.add_argument("--trace", action="store_true", help="Muestra la secuencia de nodos")
    args = parser.parse_args()
    asyncio.run(_run(args.query, args.trace))
