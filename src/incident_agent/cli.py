"""CLI para conversar con el agente y ejecutar la demostración."""

import argparse
import asyncio
from pathlib import Path

from incident_agent.config import get_settings
from incident_agent.runner import open_persistent_graph, run_turn

DEMO_QUESTION = (
    "Investiga por separado Redis y la API de pagos durante un incidente. "
    "Compara sus umbrales y explica qué revisar primero."
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agente ReAct con memoria persistente")
    subcommands = parser.add_subparsers(dest="command", required=True)

    ask = subcommands.add_parser("ask", help="Enviar un turno al agente")
    ask.add_argument("question")
    ask.add_argument("--thread-id", default="incident-session")
    ask.add_argument("--trace", type=Path)

    demo = subcommands.add_parser("demo", help="Ejecutar una investigación multi-paso")
    demo.add_argument("--thread-id", default="demo-multistep")
    demo.add_argument("--trace", type=Path, default=Path("artifacts/example_trace.json"))
    return parser


async def _run(args: argparse.Namespace) -> None:
    settings = get_settings()
    question = args.question if args.command == "ask" else DEMO_QUESTION
    trace_path = args.trace
    async with open_persistent_graph(settings) as graph:
        trace = await run_turn(
            graph,
            question=question,
            thread_id=args.thread_id,
            recursion_limit=settings.recursion_limit,
            trace_path=trace_path,
        )
    print(trace.final_response)
    print(f"\nHerramientas invocadas: {trace.tool_invocations}")
    if trace_path is not None:
        print(f"Traza: {trace_path}")


def main() -> None:
    asyncio.run(_run(_parser().parse_args()))


if __name__ == "__main__":
    main()
