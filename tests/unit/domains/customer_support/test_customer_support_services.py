# ABOUTME: Unit tests for customer support services.

import pytest

from autobots_agents_jarvis.domains.customer_support.services import (
    create_ticket,
    get_article,
    list_article_categories,
    search_knowledge_base,
    search_tickets,
    update_ticket,
)


def test_create_ticket():
    """Test creating a new ticket."""
    ticket = create_ticket(title="Test Ticket", description="Test description", priority="high")

    assert isinstance(ticket, dict)
    assert "ticket_id" in ticket
    assert ticket["title"] == "Test Ticket"
    assert ticket["description"] == "Test description"
    assert ticket["priority"] == "high"
    assert ticket["status"] == "open"
    assert "created_at" in ticket
    assert "updated_at" in ticket


def test_create_ticket_default_priority():
    """Test creating a ticket with default priority."""
    ticket = create_ticket(title="Default Priority", description="Test")

    assert ticket["priority"] == "medium"


def test_update_ticket_existing():
    """Test updating an existing ticket status."""
    # Create a ticket
    ticket = create_ticket(title="To Update", description="Test")
    ticket_id = ticket["ticket_id"]

    # Update it
    updated = update_ticket(ticket_id, status="resolved")

    assert "error" not in updated
    assert updated["status"] == "resolved"
    assert "updated_at" in updated  # Timestamp is updated


def test_update_ticket_nonexistent():
    """Test updating a nonexistent ticket."""
    result = update_ticket("NONEXISTENT", status="closed")
    assert "error" in result


def test_search_tickets():
    """Test searching for tickets."""
    # Create some test tickets
    create_ticket(title="Password Reset Issue", description="Can't reset password")
    create_ticket(title="Login Problem", description="Can't login to account")

    # Search for 'password'
    results = search_tickets("password")

    assert isinstance(results, list)
    assert len(results) > 0
    # Check that at least one result contains 'password'
    assert any("password" in r["title"].lower() for r in results)


def test_search_tickets_no_results():
    """Test searching with no matching tickets."""
    results = search_tickets("xyzabc123nonexistent")
    assert isinstance(results, list)
    assert len(results) == 0


def test_search_knowledge_base():
    """Test searching the knowledge base."""
    results = search_knowledge_base("password")

    assert isinstance(results, list)
    assert len(results) > 0
    # Should find the password reset article
    assert any("password" in r["title"].lower() for r in results)


def test_search_knowledge_base_no_results():
    """Test KB search with no matches."""
    results = search_knowledge_base("xyzabc123nonexistent")
    assert isinstance(results, list)
    assert len(results) == 0


def test_get_article_existing():
    """Test retrieving an existing KB article."""
    article = get_article("KB001")

    assert "error" not in article
    assert article["article_id"] == "KB001"
    assert "title" in article
    assert "content" in article
    assert "category" in article
    assert "tags" in article


def test_get_article_nonexistent():
    """Test retrieving a nonexistent KB article."""
    result = get_article("NONEXISTENT")
    assert "error" in result


@pytest.mark.parametrize(
    "article_id",
    ["KB001", "KB002", "KB003", "KB004"],
)
def test_get_all_articles(article_id: str):
    """Test retrieving all KB articles."""
    article = get_article(article_id)
    assert "error" not in article
    assert article["article_id"] == article_id
    assert isinstance(article["title"], str)
    assert isinstance(article["content"], str)
    assert isinstance(article["tags"], list)


def test_list_article_categories():
    """Test listing article categories."""
    categories = list_article_categories()
    assert isinstance(categories, list)
    assert len(categories) > 0
    assert "account" in categories
    assert "troubleshooting" in categories
