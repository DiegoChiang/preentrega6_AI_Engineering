"""Esquemas y serialización de la traza de ejecución."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, ConfigDict, Field


class MessageTrace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    content: str
    name: str | None = None
    tool_call_id: str | None = None
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)


class NodeTrace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step: int = Field(ge=1)
    node: str
    messages: list[MessageTrace]


class AgentTrace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timestamp: datetime
    thread_id: str
    question: str
    recursion_limit: int
    tool_invocations: int = Field(ge=0)
    final_response: str
    events: list[NodeTrace]


def message_trace(message: BaseMessage) -> MessageTrace:
    content = message.content
    if not isinstance(content, str):
        content = json.dumps(content, ensure_ascii=False, default=str)
    raw_calls = getattr(message, "tool_calls", []) or []
    calls = [dict(call) for call in raw_calls]
    return MessageTrace(
        type=message.type,
        content=content,
        name=getattr(message, "name", None),
        tool_call_id=getattr(message, "tool_call_id", None),
        tool_calls=calls,
    )


def build_trace(
    *,
    thread_id: str,
    question: str,
    recursion_limit: int,
    events: list[NodeTrace],
) -> AgentTrace:
    messages = [message for event in events for message in event.messages]
    tool_invocations = sum(len(message.tool_calls) for message in messages)
    final_response = next(
        (
            message.content
            for message in reversed(messages)
            if message.type == "ai" and not message.tool_calls
        ),
        "",
    )
    return AgentTrace(
        timestamp=datetime.now(UTC),
        thread_id=thread_id,
        question=question,
        recursion_limit=recursion_limit,
        tool_invocations=tool_invocations,
        final_response=final_response,
        events=events,
    )


def write_trace(trace: AgentTrace, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(trace.model_dump_json(indent=2), encoding="utf-8")
