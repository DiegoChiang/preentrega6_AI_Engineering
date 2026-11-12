import pytest
from pydantic import ValidationError

from incident_agent.config import Settings


def test_settings_define_safe_cycle_limit_and_sqlite_path():
    settings = Settings(_env_file=None)

    assert settings.recursion_limit == 10
    assert settings.checkpoint_db.name == "agent_checkpoints.sqlite"


def test_recursion_limit_rejects_unsafe_values():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, recursion_limit=2)


def test_missing_openai_key_has_controlled_error():
    settings = Settings(_env_file=None)

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        settings.require_openai_key()
