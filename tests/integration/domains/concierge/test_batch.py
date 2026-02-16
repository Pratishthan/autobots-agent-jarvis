# ABOUTME: Integration tests for Concierge batch processing.

import pytest

from autobots_agents_jarvis.domains.concierge.concierge_batch import concierge_batch


@pytest.fixture(autouse=True)
def setup_concierge(concierge_registered):
    """Ensure Concierge tools are registered before each test."""
    pass


def test_concierge_batch_invalid_agent():
    """Test that concierge_batch raises error for non-batch-enabled agents."""
    with pytest.raises(ValueError, match="not enabled for batch processing"):
        concierge_batch("welcome_agent", ["test prompt"], user_id="test_user")


def test_concierge_batch_empty_records(concierge_registered):
    """Test that concierge_batch raises error for empty records."""
    with pytest.raises(ValueError, match="records must not be empty"):
        concierge_batch("joke_agent", [], user_id="test_user")


@pytest.mark.skipif(
    True,
    reason="Requires GOOGLE_API_KEY and full agent setup - run manually",
)
def test_concierge_batch_joke_agent_smoke(concierge_registered):
    """Smoke test for joke_agent batch processing."""
    prompts = [
        "Tell me a programming joke",
        "What's a funny dad joke?",
    ]

    result = concierge_batch("joke_agent", prompts)

    assert result.total == 2
    assert len(result.results) == 2
    # In real execution, we'd expect successes, but this is marked as manual-only
