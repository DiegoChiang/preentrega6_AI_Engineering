import pytest
from langchain_core.messages import AIMessage, HumanMessage

from incident_agent.config import Settings
from incident_agent.runner import open_persistent_graph, run_turn


class ConversationCountingModel:
    def bind_tools(self, tools, **kwargs):
        return self

    async def ainvoke(self, messages):
        humans = [message for message in messages if isinstance(message, HumanMessage)]
        return AIMessage(content=f"turnos={len(humans)}")


@pytest.mark.asyncio
async def test_sqlite_persists_and_isolates_threads_after_reopen(tmp_path):
    settings = Settings(
        _env_file=None,
        checkpoint_db=tmp_path / "memory.sqlite",
    )

    async with open_persistent_graph(settings, model=ConversationCountingModel()) as graph:
        first = await run_turn(
            graph,
            question="Primer mensaje",
            thread_id="thread-a",
            recursion_limit=10,
        )
    async with open_persistent_graph(settings, model=ConversationCountingModel()) as graph:
        second = await run_turn(
            graph,
            question="Segundo mensaje",
            thread_id="thread-a",
            recursion_limit=10,
        )
        isolated = await run_turn(
            graph,
            question="Mensaje aislado",
            thread_id="thread-b",
            recursion_limit=10,
        )

    assert first.final_response == "turnos=1"
    assert second.final_response == "turnos=2"
    assert isolated.final_response == "turnos=1"
