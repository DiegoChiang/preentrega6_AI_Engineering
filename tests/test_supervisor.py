import pytest

from multi_agent_orchestrator.supervisor import Supervisor
from tests.fakes import ScriptedModel


async def test_supervisor_enforces_step_limit() -> None:
    supervisor = Supervisor(ScriptedModel(), max_steps=1)

    with pytest.raises(RuntimeError, match="limite de 1 decisiones"):
        await supervisor(
            {
                "request": "Analiza el incidente",
                "supervisor_steps": 1,
                "research_findings": [],
                "analysis_result": None,
                "validation_feedback": [],
                "completed_agents": [],
                "task_completed": False,
            }
        )
