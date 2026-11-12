from multi_agent_orchestrator.runner import run_orchestrator
from tests.fakes import ScriptedModel


async def test_full_delegation_flow() -> None:
    state, trace = await run_orchestrator(
        "Investiga el impacto de errores de checkout y calcula su prioridad.",
        model=ScriptedModel(),
    )

    nodes = [item["node"] for item in trace]
    assert nodes == [
        "supervisor",
        "researcher",
        "supervisor",
        "analyst",
        "supervisor",
        "validator",
        "supervisor",
        "synthesizer",
    ]
    assert state["task_completed"] is True
    assert state["analysis_result"]["priority"] == "P1"
    assert state["final_answer"].startswith("Prioridad P1")
    assert state["completed_agents"] == [
        "researcher",
        "analyst",
        "validator",
        "synthesizer",
    ]


async def test_specialists_keep_bounded_toolsets() -> None:
    from multi_agent_orchestrator.agents import AnalysisAgent, ResearchAgent

    research_tools = {item.name for item in ResearchAgent.tools}
    analysis_tools = {item.name for item in AnalysisAgent.tools}

    assert research_tools == {"search_incident_knowledge"}
    assert analysis_tools == {"calculate_incident_priority"}
    assert research_tools.isdisjoint(analysis_tools)
