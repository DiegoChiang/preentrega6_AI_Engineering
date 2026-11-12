"""Ejecuta la investigación multi-paso y guarda su traza."""

import asyncio
from argparse import Namespace
from pathlib import Path

from incident_agent.cli import _run

if __name__ == "__main__":
    asyncio.run(
        _run(
            Namespace(
                command="demo",
                thread_id="demo-multistep",
                trace=Path("artifacts/example_trace.json"),
                question=None,
            )
        )
    )
