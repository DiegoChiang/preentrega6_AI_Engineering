import json

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver

from incident_agent.graph import create_agent_graph
from incident_agent.runner import run_turn


class RetryThenResearchModel:
    def bind_tools(self, tools, **kwargs):
        assert len(tools) == 1
        assert kwargs["parallel_tool_calls"] is False
        return self

    async def ainvoke(self, messages):
        results = [message for message in messages if isinstance(message, ToolMessage)]
        if not results:
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "search_technical_knowledge",
                        "args": {"query": "incidente general", "purpose": "identificar causa"},
                        "id": "call-generic",
                        "type": "tool_call",
                    }
                ],
            )
        if len(results) == 1:
            assert json.loads(results[-1].content)["status"] == "incomplete"
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "search_technical_knowledge",
                        "args": {"query": "Redis memoria", "purpose": "confirmar umbral"},
                        "id": "call-redis",
                        "type": "tool_call",
                    }
                ],
            )
        if len(results) == 2:
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "search_technical_knowledge",
                        "args": {"query": "API pagos 5xx", "purpose": "confirmar severidad"},
                        "id": "call-payments",
                        "type": "tool_call",
                    }
                ],
            )
        return AIMessage(
            content=(
                "Redis es crítico sobre 0,92 y pagos sobre 5 % de 5xx. "
                "Fuentes: guia-redis-idempotencia y runbook-api-pagos."
            )
        )


@pytest.mark.asyncio
async def test_graph_retries_and_calls_tool_at_least_twice(tmp_path):
    graph = create_agent_graph(RetryThenResearchModel(), InMemorySaver())
    trace_path = tmp_path / "trace.json"

    trace = await run_turn(
        graph,
        question="Investiga Redis y pagos",
        thread_id="cycle-test",
        recursion_limit=10,
        trace_path=trace_path,
    )

    assert trace.tool_invocations == 3
    assert [event.node for event in trace.events] == [
        "model",
        "tools",
        "model",
        "tools",
        "model",
        "tools",
        "model",
    ]
    first_tool_result = trace.events[1].messages[0].content
    assert json.loads(first_tool_result)["status"] == "incomplete"
    assert "guia-redis-idempotencia" in trace.final_response
    assert json.loads(trace_path.read_text(encoding="utf-8"))["tool_invocations"] == 3


@pytest.mark.asyncio
async def test_messages_state_keeps_history_for_same_thread():
    graph = create_agent_graph(RetryThenResearchModel(), InMemorySaver())
    config = {"configurable": {"thread_id": "persistent"}, "recursion_limit": 10}

    await graph.ainvoke({"messages": [HumanMessage(content="Primer turno")]}, config=config)
    await graph.ainvoke({"messages": [HumanMessage(content="Segundo turno")]}, config=config)
    snapshot = await graph.aget_state(config)

    human_messages = [
        message for message in snapshot.values["messages"] if isinstance(message, HumanMessage)
    ]
    assert [message.content for message in human_messages] == ["Primer turno", "Segundo turno"]


def test_graph_contains_model_tool_and_conditional_cycle():
    graph = create_agent_graph(RetryThenResearchModel(), InMemorySaver()).get_graph()

    assert {"model", "tools"}.issubset(graph.nodes)
    edges = {(edge.source, edge.target) for edge in graph.edges}
    assert ("tools", "model") in edges
