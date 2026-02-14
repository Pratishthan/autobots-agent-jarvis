# ABOUTME: Pytest fixtures for Jarvis domain unit tests.

import pytest
from tests.helpers import jarvis_tools_registered


@pytest.fixture
def jarvis_registered():
    """Register Jarvis tools; reset after test."""
    yield from jarvis_tools_registered()
