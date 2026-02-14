# ABOUTME: Customer Support use-case tools — tools for ticket and knowledge base operations.
# ABOUTME: Wraps customer support services for use by agents.

import logging

from autobots_devtools_shared_lib.dynagent import Dynagent
from langchain.tools import ToolRuntime, tool

from autobots_agents_jarvis.domains.customer_support.services import (
    create_ticket as service_create_ticket,
)
from autobots_agents_jarvis.domains.customer_support.services import (
    get_article as service_get_article,
)
from autobots_agents_jarvis.domains.customer_support.services import (
    search_knowledge_base as service_search_kb,
)
from autobots_agents_jarvis.domains.customer_support.services import (
    search_tickets as service_search_tickets,
)
from autobots_agents_jarvis.domains.customer_support.services import (
    update_ticket as service_update_ticket,
)

logger = logging.getLogger(__name__)


# --- @tool wrappers for Ticket Operations ---


@tool
def create_ticket(
    runtime: ToolRuntime[None, Dynagent], title: str, description: str, priority: str = "medium"
) -> str:
    """Create a new support ticket.

    Args:
        title: Brief title/subject of the ticket
        description: Detailed description of the issue
        priority: Priority level (low, medium, high, urgent) - defaults to medium

    Returns:
        A formatted message with ticket details
    """
    session_id = runtime.state.get("session_id", "default")
    logger.info(f"Creating ticket for session {session_id}: {title}")

    ticket = service_create_ticket(title, description, priority)

    return (
        f"✅ Ticket created successfully!\n\n"
        f"**Ticket ID:** {ticket['ticket_id']}\n"
        f"**Title:** {ticket['title']}\n"
        f"**Status:** {ticket['status']}\n"
        f"**Priority:** {ticket['priority']}\n"
        f"**Created:** {ticket['created_at']}\n\n"
        f"We'll get back to you as soon as possible."
    )


@tool
def update_ticket(runtime: ToolRuntime[None, Dynagent], ticket_id: str, status: str) -> str:
    """Update the status of an existing ticket.

    Args:
        ticket_id: Unique identifier for the ticket (e.g., TKT-1001)
        status: New status (open, in-progress, resolved, closed)

    Returns:
        A formatted message with update confirmation or error
    """
    session_id = runtime.state.get("session_id", "default")
    logger.info(f"Updating ticket {ticket_id} for session {session_id}: status={status}")

    ticket = service_update_ticket(ticket_id, status)

    if "error" in ticket:
        return f"❌ {ticket['error']}"

    return (
        f"✅ Ticket updated successfully!\n\n"
        f"**Ticket ID:** {ticket['ticket_id']}\n"
        f"**New Status:** {ticket['status']}\n"
        f"**Last Updated:** {ticket['updated_at']}"
    )


@tool
def search_tickets(runtime: ToolRuntime[None, Dynagent], query: str) -> str:
    """Search for tickets by keyword or ID.

    Args:
        query: Search query (matches against ticket ID, title, or description)

    Returns:
        A formatted list of matching tickets or message if none found
    """
    session_id = runtime.state.get("session_id", "default")
    logger.info(f"Searching tickets for session {session_id}: query={query}")

    tickets = service_search_tickets(query)

    if not tickets:
        return f"No tickets found matching '{query}'"

    result = f"Found {len(tickets)} ticket(s) matching '{query}':\n\n"
    for ticket in tickets:
        result += (
            f"📋 **{ticket['ticket_id']}**: {ticket['title']}\n"
            f"   Status: {ticket['status']} | Priority: {ticket['priority']}\n"
            f"   Created: {ticket['created_at']}\n\n"
        )

    return result.strip()


# --- @tool wrappers for Knowledge Base Operations ---


@tool
def search_knowledge_base(runtime: ToolRuntime[None, Dynagent], query: str) -> str:
    """Search the knowledge base for relevant articles.

    Args:
        query: Search query for finding help articles

    Returns:
        A formatted list of matching articles with summaries
    """
    session_id = runtime.state.get("session_id", "default")
    logger.info(f"Searching knowledge base for session {session_id}: query={query}")

    articles = service_search_kb(query, max_results=3)

    if not articles:
        return (
            f"No articles found for '{query}'. "
            f"Try different keywords or create a support ticket for assistance."
        )

    result = f"📚 Found {len(articles)} article(s) matching '{query}':\n\n"
    for article in articles:
        relevance = int(article["relevance_score"] * 100)
        result += (
            f"**{article['title']}** (ID: {article['article_id']}, Relevance: {relevance}%)\n"
            f"{article['summary']}\n\n"
        )

    result += (
        "Would you like me to show you the full content of any article? Just ask for it by ID!"
    )

    return result.strip()


@tool
def get_article(runtime: ToolRuntime[None, Dynagent], article_id: str) -> str:
    """Get the full content of a specific knowledge base article.

    Args:
        article_id: Unique identifier for the article (e.g., KB001)

    Returns:
        The full article content or error message
    """
    session_id = runtime.state.get("session_id", "default")
    logger.info(f"Getting article {article_id} for session {session_id}")

    article = service_get_article(article_id)

    if "error" in article:
        return f"❌ {article['error']}"

    return (
        f"📖 **{article['title']}** (ID: {article['article_id']})\n\n"
        f"{article['content']}\n\n"
        f"---\n"
        f"Category: {article['category']}"
    )


# --- Registration entry-point (called once at app startup) ---


def register_customer_support_tools() -> None:
    """Register all 5 Customer Support tools into the dynagent usecase pool."""
    from autobots_devtools_shared_lib.dynagent import register_usecase_tools

    register_usecase_tools(
        [
            create_ticket,
            update_ticket,
            search_tickets,
            search_knowledge_base,
            get_article,
        ]
    )
