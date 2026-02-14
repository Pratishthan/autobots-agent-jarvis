# ABOUTME: Unit tests for customer support tools.

from unittest.mock import MagicMock

import pytest
from autobots_devtools_shared_lib.dynagent import Dynagent
from langchain.tools import ToolRuntime

from autobots_agents_jarvis.domains.customer_support.tools import (
    create_ticket,
    get_article,
    search_knowledge_base,
    search_tickets,
    update_ticket,
)


@pytest.fixture
def mock_runtime() -> ToolRuntime:
    """Create a mock runtime for testing tools."""
    runtime = MagicMock(spec=ToolRuntime)
    runtime.state = Dynagent(session_id="test-session")
    runtime.context = None
    runtime.model_dump = MagicMock(
        return_value={"state": {"session_id": "test-session"}, "context": None}
    )
    return runtime


def test_create_ticket_tool(mock_runtime):
    """Test create_ticket tool."""
    result = create_ticket.func(
        mock_runtime, title="Test Ticket", description="Test description", priority="high"
    )

    assert isinstance(result, str)
    assert "✅ Ticket created successfully" in result
    assert "TKT-" in result  # Ticket ID format
    assert "Test Ticket" in result
    assert "high" in result
    assert "open" in result


def test_create_ticket_tool_default_priority(mock_runtime):
    """Test create_ticket with default priority."""
    result = create_ticket.func(mock_runtime, title="Default Priority", description="Test")

    assert "medium" in result


def test_update_ticket_tool_success(mock_runtime):
    """Test update_ticket tool with existing ticket."""
    # Create a ticket first
    create_result = create_ticket.func(mock_runtime, title="To Update", description="Test")
    # Extract ticket ID from the result (format: "**Ticket ID:** TKT-XXXX")
    ticket_id = create_result.split("**Ticket ID:** ")[1].split("\n")[0]

    # Update it
    result = update_ticket.func(mock_runtime, ticket_id=ticket_id, status="resolved")

    assert isinstance(result, str)
    assert "✅ Ticket updated successfully" in result
    assert ticket_id in result
    assert "resolved" in result


def test_update_ticket_tool_not_found(mock_runtime):
    """Test update_ticket with nonexistent ticket."""
    result = update_ticket.func(mock_runtime, ticket_id="NONEXISTENT", status="closed")

    assert "❌" in result
    assert "not found" in result


def test_search_tickets_tool(mock_runtime):
    """Test search_tickets tool."""
    # Create some test tickets
    create_ticket.func(mock_runtime, title="Password Reset Issue", description="Can't reset")
    create_ticket.func(mock_runtime, title="Login Problem", description="Can't login")

    # Search
    result = search_tickets.func(mock_runtime, query="password")

    assert isinstance(result, str)
    assert "Found" in result
    assert "ticket(s)" in result
    # Should contain ticket information
    assert "TKT-" in result


def test_search_tickets_tool_no_results(mock_runtime):
    """Test search_tickets with no matches."""
    result = search_tickets.func(mock_runtime, query="xyzabc123nonexistent")

    assert "No tickets found" in result


def test_search_knowledge_base_tool(mock_runtime):
    """Test search_knowledge_base tool."""
    result = search_knowledge_base.func(mock_runtime, query="password")

    assert isinstance(result, str)
    assert "Found" in result
    assert "article(s)" in result
    assert "KB" in result  # Article IDs start with KB


def test_search_knowledge_base_tool_no_results(mock_runtime):
    """Test search_knowledge_base with no matches."""
    result = search_knowledge_base.func(mock_runtime, query="xyzabc123nonexistent")

    assert "No articles found" in result


def test_get_article_tool_success(mock_runtime):
    """Test get_article tool with existing article."""
    result = get_article.func(mock_runtime, article_id="KB001")

    assert isinstance(result, str)
    assert "KB001" in result
    assert "How to Reset Your Password" in result  # Article title
    assert "account" in result  # Category


def test_get_article_tool_not_found(mock_runtime):
    """Test get_article with nonexistent article."""
    result = get_article.func(mock_runtime, article_id="NONEXISTENT")

    assert "❌" in result
    assert "not found" in result


@pytest.mark.parametrize(
    "article_id",
    ["KB001", "KB002", "KB003", "KB004"],
)
def test_get_all_articles_tool(mock_runtime, article_id: str):
    """Test retrieving all KB articles via tool."""
    result = get_article.func(mock_runtime, article_id=article_id)

    assert isinstance(result, str)
    assert article_id in result
    assert len(result) > 100  # Should have substantial content
