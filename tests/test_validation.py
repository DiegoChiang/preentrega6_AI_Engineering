from multi_agent_orchestrator.validation import validate_result


def test_validation_rejects_unknown_source() -> None:
    result = validate_result(
        {
            "research_findings": [
                {
                    "source_id": "source-a",
                    "title": "A",
                    "summary": "A",
                    "metrics": {},
                    "tags": [],
                },
                {
                    "source_id": "source-b",
                    "title": "B",
                    "summary": "B",
                    "metrics": {},
                    "tags": [],
                },
            ],
            "analysis_result": {
                "priority": "P2",
                "risk_score": 60,
                "drivers": ["uno", "dos"],
                "recommendation": "Mitigar y observar.",
                "source_ids": ["source-a", "source-invented"],
            },
        }
    )

    assert result["task_completed"] is False
    assert "source-invented" in result["validation_feedback"][0]
