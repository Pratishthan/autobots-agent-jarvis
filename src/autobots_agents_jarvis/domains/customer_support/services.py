# ABOUTME: Customer Support domain services — mock implementations for tickets and knowledge base.
# ABOUTME: Provides in-memory storage for demo purposes.

from datetime import datetime
from typing import Any

# ==================== TICKET SERVICE ====================

# In-memory ticket storage (resets on restart - demo only)
_TICKETS: dict[str, dict[str, Any]] = {}
_TICKET_COUNTER = 1000


def create_ticket(title: str, description: str, priority: str = "medium") -> dict[str, Any]:
    """Create a new support ticket.

    Args:
        title: Brief title/subject of the ticket
        description: Detailed description of the issue
        priority: Priority level (low, medium, high, urgent)

    Returns:
        Dict containing ticket details including ticket_id
    """
    global _TICKET_COUNTER
    _TICKET_COUNTER += 1
    ticket_id = f"TKT-{_TICKET_COUNTER}"

    timestamp = datetime.now().isoformat()
    ticket = {
        "ticket_id": ticket_id,
        "title": title,
        "description": description,
        "status": "open",
        "priority": priority,
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    _TICKETS[ticket_id] = ticket
    return ticket


def update_ticket(ticket_id: str, status: str) -> dict[str, Any]:
    """Update ticket status.

    Args:
        ticket_id: Unique identifier for the ticket
        status: New status (open, in-progress, resolved, closed)

    Returns:
        Updated ticket dict or error dict
    """
    if ticket_id not in _TICKETS:
        return {"error": f"Ticket {ticket_id} not found"}

    _TICKETS[ticket_id]["status"] = status
    _TICKETS[ticket_id]["updated_at"] = datetime.now().isoformat()

    return _TICKETS[ticket_id]


def search_tickets(query: str) -> list[dict[str, Any]]:
    """Search tickets by keyword or ID.

    Args:
        query: Search query (matches against ticket_id, title, description)

    Returns:
        List of matching tickets
    """
    query_lower = query.lower()

    return [
        ticket
        for ticket in _TICKETS.values()
        if (
            query_lower in ticket["ticket_id"].lower()
            or query_lower in ticket["title"].lower()
            or query_lower in ticket["description"].lower()
        )
    ]


# ==================== KNOWLEDGE BASE SERVICE ====================

# Mock knowledge base articles
_KNOWLEDGE_BASE: dict[str, dict[str, Any]] = {
    "KB001": {
        "article_id": "KB001",
        "title": "How to Reset Your Password",
        "summary": "Step-by-step guide for resetting your account password",
        "content": """
# How to Reset Your Password

Follow these steps to reset your password:

1. Go to the login page
2. Click "Forgot Password?" link
3. Enter your email address
4. Check your email for reset link
5. Click the link and create a new password
6. Confirm your new password

**Note:** Password must be at least 8 characters and include numbers and symbols.
""",
        "category": "account",
        "tags": ["password", "reset", "account", "security"],
    },
    "KB002": {
        "article_id": "KB002",
        "title": "Account Settings Configuration Guide",
        "summary": "Learn how to configure your account settings and preferences",
        "content": """
# Account Settings Configuration

## Accessing Settings

1. Log in to your account
2. Click your profile icon (top right)
3. Select "Settings" from dropdown

## Available Settings

- **Profile Information**: Update name, email, phone
- **Privacy Settings**: Control who can see your information
- **Notification Preferences**: Choose how you receive updates
- **Security Settings**: Two-factor authentication, password changes

## Saving Changes

Always click "Save" button at the bottom of each settings page.
""",
        "category": "account",
        "tags": ["settings", "configuration", "preferences", "profile"],
    },
    "KB003": {
        "article_id": "KB003",
        "title": "Troubleshooting Login Issues",
        "summary": "Common login problems and their solutions",
        "content": """
# Troubleshooting Login Issues

## Common Problems

### "Invalid Credentials" Error
- Double-check username and password
- Ensure Caps Lock is off
- Try resetting your password

### "Account Locked" Message
- Too many failed login attempts
- Wait 15 minutes and try again
- Contact support if problem persists

### Can't Receive Reset Email
- Check spam/junk folder
- Verify email address is correct
- Whitelist noreply@ourcompany.com

## Still Having Issues?

Create a support ticket and we'll help you out!
""",
        "category": "troubleshooting",
        "tags": ["login", "troubleshooting", "account", "password", "error"],
    },
    "KB004": {
        "article_id": "KB004",
        "title": "Getting Started Guide",
        "summary": "Welcome! Here's how to get started with our platform",
        "content": """
# Getting Started Guide

Welcome to our platform! Here's what you need to know:

## First Steps

1. **Complete Your Profile**
   - Add profile picture
   - Fill in contact information
   - Set your preferences

2. **Explore the Dashboard**
   - Overview of all features
   - Quick access to common tasks
   - Customizable layout

3. **Connect Your Tools**
   - Integrate with other services
   - Set up notifications
   - Configure automations

## Need Help?

- Search our knowledge base
- Check out video tutorials
- Contact support team

Happy exploring!
""",
        "category": "getting-started",
        "tags": ["getting started", "welcome", "tutorial", "onboarding"],
    },
}


def search_knowledge_base(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """Search knowledge base for relevant articles.

    Args:
        query: Search query string
        max_results: Maximum number of results to return

    Returns:
        List of matching articles with relevance scores
    """
    query_lower = query.lower()
    scored_articles = []

    for article in _KNOWLEDGE_BASE.values():
        score = 0.0

        # Check title (highest weight)
        if query_lower in article["title"].lower():
            score += 1.0

        # Check tags (medium weight)
        for tag in article["tags"]:
            if query_lower in tag.lower():
                score += 0.5

        # Check summary (lower weight)
        if query_lower in article["summary"].lower():
            score += 0.3

        if score > 0:
            scored_articles.append(
                {
                    "article_id": article["article_id"],
                    "title": article["title"],
                    "summary": article["summary"],
                    "relevance_score": min(score, 1.0),  # Cap at 1.0
                }
            )

    # Sort by relevance score (highest first)
    scored_articles.sort(key=lambda x: x["relevance_score"], reverse=True)

    return scored_articles[:max_results]


def get_article(article_id: str) -> dict[str, Any]:
    """Get full content of a specific article.

    Args:
        article_id: Unique identifier for the article

    Returns:
        Article dict with full content or error dict
    """
    if article_id not in _KNOWLEDGE_BASE:
        return {"error": f"Article {article_id} not found in knowledge base"}

    return _KNOWLEDGE_BASE[article_id].copy()


def list_article_categories() -> list[str]:
    """Get list of available article categories.

    Returns:
        List of unique categories
    """
    categories = {article["category"] for article in _KNOWLEDGE_BASE.values()}
    return sorted(categories)
