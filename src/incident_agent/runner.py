"""Ejecución asíncrona, memoria SQLite y captura de trazas."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from incident_agent.config import Settings
from incident_agent.graph import create_agent_graph
from incident_agent.model import build_chat_model
from incident_agent.trace import AgentTrace, NodeTrace, build_trace, message_trace, write_trace


@asynccontextmanager
async def open_persistent_graph(
    settings: Settings,
    *,
    model: Any | None = None,
) -> AsyncIterator[Any]:
    settings.checkpoint_db.parent.mkdir(parents=True, exist_ok=True)
    active_model = model or build_chat_model(settings)
    async with AsyncSqliteSaver.from_conn_string(str(settings.checkpoint_db)) as checkpointer:
        yield create_agent_graph(active_model, checkpointer)


async def run_turn(
    graph: Any,
    *,
    question: str,
    thread_id: str,
    recursion_limit: int,
    trace_path: Path | None = None,
) -> AgentTrace:
    clean_question = question.strip()
    clean_thread = thread_id.strip()
    if not clean_question:
        raise ValueError("La pregunta no puede estar vacía")
    if not clean_thread:
        raise ValueError("thread_id no puede estar vacío")

    config = {
        "configurable": {"thread_id": clean_thread},
        "recursion_limit": recursion_limit,
    }
    events: list[NodeTrace] = []
    step = 0
    async for update in graph.astream(
        {"messages": [HumanMessage(content=clean_question)]},
        config=config,
        stream_mode="updates",
    ):
        for node, payload in update.items():
            if not isinstance(payload, dict):
                continue
            raw_messages: list[BaseMessage] = payload.get("messages", [])
            step += 1
            events.append(
                NodeTrace(
                    step=step,
                    node=node,
                    messages=[message_trace(message) for message in raw_messages],
                )
            )

    trace = build_trace(
        thread_id=clean_thread,
        question=clean_question,
        recursion_limit=recursion_limit,
        events=events,
    )
    if trace_path is not None:
        write_trace(trace, trace_path)
    return trace


async def run_persistent_turn(
    settings: Settings,
    *,
    question: str,
    thread_id: str,
    trace_path: Path | None = None,
) -> AgentTrace:
    async with open_persistent_graph(settings) as graph:
        return await run_turn(
            graph,
            question=question,
            thread_id=thread_id,
            recursion_limit=settings.recursion_limit,
            trace_path=trace_path,
        )
