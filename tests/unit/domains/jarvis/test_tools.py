# ABOUTME: Unit tests for Jarvis tools.

from unittest.mock import MagicMock

import pytest
from autobots_devtools_shared_lib.dynagent import Dynagent
from langchain.tools import ToolRuntime

from autobots_agents_jarvis.domains.jarvis.tools import (
    tell_joke,
)


@pytest.fixture
def mock_runtime() -> ToolRuntime:
    """Create a mock runtime for testing tools."""
    runtime = MagicMock(spec=ToolRuntime)
    runtime.state = Dynagent(session_id="test-session")
    runtime.context = None
    # Add model_dump method for pydantic serialization
    runtime.model_dump = MagicMock(
        return_value={"state": {"session_id": "test-session"}, "context": None}
    )
    return runtime


def test_tell_joke_valid_category(mock_runtime):
    """Test tell_joke with a valid category."""
    # Call the underlying function directly rather than using invoke
    result = tell_joke.func(mock_runtime, "programming")
    assert isinstance(result, str)
    assert "Category: programming" in result
    assert "Rating:" in result
