# ABOUTME: Sales use-case tools — tools for lead qualification and product recommendations.
# ABOUTME: Wraps sales services for use by agents.


from autobots_devtools_shared_lib.common.observability.logging_utils import (
    get_logger,
    set_conversation_id,
)
from autobots_devtools_shared_lib.dynagent import Dynagent
from langchain.tools import ToolRuntime, tool

from autobots_agents_jarvis.domains.sales.services import check_inventory as service_check_inventory
from autobots_agents_jarvis.domains.sales.services import get_lead_score as service_get_lead_score
from autobots_agents_jarvis.domains.sales.services import (
    get_product_catalog as service_get_product_catalog,
)
from autobots_agents_jarvis.domains.sales.services import qualify_lead as service_qualify_lead
from autobots_agents_jarvis.domains.sales.services import (
    recommend_products as service_recommend_products,
)

logger = get_logger(__name__)


# --- @tool wrappers for Lead Qualification Operations ---


@tool
def qualify_lead(
    runtime: ToolRuntime[None, Dynagent],
    company: str,
    budget: str,
    timeline: str,
    team_size: int = 1,
) -> str:
    """Qualify a new sales lead.

    Args:
        company: Company name
        budget: Budget range or amount (e.g., "$50K", "100000", "under 10k")
        timeline: Timeline for decision/implementation (e.g., "3 months", "Q2", "ASAP")
        team_size: Number of team members/users (default 1)

    Returns:
        A formatted message with lead qualification details
    """
    session_id = runtime.state.get("session_id", "default")
    set_conversation_id(session_id)
    logger.info(f"Qualifying lead for session {session_id}: {company}")

    lead = service_qualify_lead(company, budget, timeline, team_size)

    next_steps_str = "\n".join([f"   - {step}" for step in lead["next_steps"]])

    return (
        f"✅ Lead Qualified Successfully!\n\n"
        f"**Lead ID:** {lead['lead_id']}\n"
        f"**Company:** {lead['company']}\n"
        f"**Score:** {lead['score']}/100\n"
        f"**Category:** {lead['category'].upper()}\n\n"
        f"**Details:**\n"
        f"   - Budget: {lead['budget']}\n"
        f"   - Timeline: {lead['timeline']}\n"
        f"   - Team Size: {lead['team_size']} users\n\n"
        f"**Recommended Next Steps:**\n{next_steps_str}\n\n"
        f"Qualified at: {lead['qualified_at']}"
    )


@tool
def get_lead_score(runtime: ToolRuntime[None, Dynagent], lead_id: str) -> str:
    """Get qualification details for an existing lead.

    Args:
        lead_id: Unique lead identifier (e.g., LEAD-5001)

    Returns:
        A formatted message with lead details or error message
    """
    session_id = runtime.state.get("session_id", "default")
    set_conversation_id(session_id)
    logger.info(f"Getting lead score for session {session_id}: {lead_id}")

    lead = service_get_lead_score(lead_id)

    if "error" in lead:
        return f"❌ {lead['error']}"

    next_steps_str = "\n".join([f"   - {step}" for step in lead["next_steps"]])

    return (
        f"📊 Lead Details: {lead['lead_id']}\n\n"
        f"**Company:** {lead['company']}\n"
        f"**Score:** {lead['score']}/100\n"
        f"**Category:** {lead['category'].upper()}\n\n"
        f"**Qualification Details:**\n"
        f"   - Budget: {lead['budget']}\n"
        f"   - Timeline: {lead['timeline']}\n"
        f"   - Team Size: {lead['team_size']} users\n\n"
        f"**Recommended Next Steps:**\n{next_steps_str}\n\n"
        f"Qualified at: {lead['qualified_at']}"
    )


# --- @tool wrappers for Product Catalog Operations ---


@tool
def get_product_catalog(runtime: ToolRuntime[None, Dynagent], category: str | None = None) -> str:
    """Browse the product catalog, optionally filtered by category.

    Args:
        category: Filter by category (Enterprise, SMB, Starter) or leave empty for all products

    Returns:
        A formatted list of products
    """
    session_id = runtime.state.get("session_id", "default")
    set_conversation_id(session_id)
    logger.info(f"Getting product catalog for session {session_id}: category={category}")

    products = service_get_product_catalog(category)

    if not products:
        return (
            f"No products found in category '{category}'" if category else "No products available"
        )

    category_msg = f" in category '{category}'" if category else ""
    result = f"📦 Product Catalog{category_msg} ({len(products)} products):\n\n"

    for product in products:
        features_str = "\n      - ".join(product["features"])
        availability = (
            "✅ In Stock"
            if product["in_stock"]
            else f"⏳ {product['lead_time_days']} days lead time"
        )

        result += (
            f"**{product['name']}** ({product['category']})\n"
            f"   - Product ID: {product['product_id']}\n"
            f"   - Price: ${product['price']:,}\n"
            f"   - Availability: {availability}\n"
            f"   - Features:\n"
            f"      - {features_str}\n\n"
        )

    return result.strip()


@tool
def recommend_products(runtime: ToolRuntime[None, Dynagent], requirements: str) -> str:
    """Get personalized product recommendations based on customer requirements.

    Args:
        requirements: Description of customer needs and requirements

    Returns:
        A formatted list of recommended products with match scores
    """
    session_id = runtime.state.get("session_id", "default")
    set_conversation_id(session_id)
    logger.info(f"Recommending products for session {session_id}: {requirements[:50]}...")

    recommendations = service_recommend_products(requirements, max_results=3)

    if not recommendations:
        return (
            f"No products found matching your requirements: '{requirements}'. "
            f"Try browsing the full catalog or refine your requirements."
        )

    result = f'🎯 Product Recommendations based on: "{requirements}"\n\n'
    result += f"Found {len(recommendations)} matching product(s):\n\n"

    for idx, product in enumerate(recommendations, 1):
        features_str = ", ".join(product["features"][:3])  # Top 3 features
        match_pct = int(product["match_score"] * 100)
        availability = (
            "✅ In Stock"
            if product["in_stock"]
            else f"⏳ {product['lead_time_days']} days lead time"
        )

        result += (
            f"**{idx}. {product['name']}** ({product['category']})\n"
            f"   - Match Score: {match_pct}%\n"
            f"   - Price: ${product['price']:,}\n"
            f"   - Availability: {availability}\n"
            f"   - Key Features: {features_str}\n"
            f"   - Product ID: {product['product_id']}\n\n"
        )

    result += "Would you like more details on any of these products?"

    return result.strip()


@tool
def check_inventory(runtime: ToolRuntime[None, Dynagent], product_id: str) -> str:
    """Check inventory availability for a specific product.

    Args:
        product_id: Unique product identifier (e.g., PROD-ENT-001)

    Returns:
        A formatted message with inventory details or error message
    """
    session_id = runtime.state.get("session_id", "default")
    set_conversation_id(session_id)
    logger.info(f"Checking inventory for session {session_id}: {product_id}")

    inventory = service_check_inventory(product_id)

    if "error" in inventory:
        return f"❌ {inventory['error']}"

    status_icon = "✅" if inventory["in_stock"] else "⏳"

    return (
        f"{status_icon} Inventory Status\n\n"
        f"**Product:** {inventory['name']}\n"
        f"**Product ID:** {inventory['product_id']}\n"
        f"**Availability:** {inventory['availability']}\n\n"
        f"{'Ready to ship immediately!' if inventory['in_stock'] else f'Available in {inventory["lead_time_days"]} days.'}"
    )


# --- Registration entry-point (called once at app startup) ---


def register_sales_tools() -> None:
    """Register all 5 Sales tools into the dynagent usecase pool."""
    from autobots_devtools_shared_lib.dynagent import register_usecase_tools

    register_usecase_tools(
        [
            qualify_lead,
            get_lead_score,
            get_product_catalog,
            recommend_products,
            check_inventory,
        ]
    )
