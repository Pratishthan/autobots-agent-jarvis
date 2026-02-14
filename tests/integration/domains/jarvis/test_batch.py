# ABOUTME: Integration tests for Jarvis batch processing.

import pytest

from autobots_agents_jarvis.domains.jarvis.jarvis_batch import jarvis_batch


@pytest.fixture(autouse=True)
def setup_jarvis(jarvis_registered):
    """Ensure Jarvis tools are registered before each test."""
    pass


def test_jarvis_batch_invalid_agent():
    """Test that jarvis_batch raises error for non-batch-enabled agents."""
    with pytest.raises(ValueError, match="not enabled for batch processing"):
        jarvis_batch("welcome_agent", ["test prompt"])


def test_jarvis_batch_empty_records(jarvis_registered):
    """Test that jarvis_batch raises error for empty records."""
    with pytest.raises(ValueError, match="records must not be empty"):
        jarvis_batch("joke_agent", [])


@pytest.mark.skipif(
    True,
    reason="Requires GOOGLE_API_KEY and full agent setup - run manually",
)
def test_jarvis_batch_joke_agent_smoke(jarvis_registered):
    """Smoke test for joke_agent batch processing."""
    prompts = [
        "Tell me a programming joke",
        "What's a funny dad joke?",
    ]

    result = jarvis_batch("joke_agent", prompts)

    assert result.total == 2
    assert len(result.results) == 2
    # In real execution, we'd expect successes, but this is marked as manual-only
