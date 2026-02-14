# ABOUTME: Sales domain services — mock implementations for lead qualification and product recommendations.
# ABOUTME: Provides in-memory storage for demo purposes.

from datetime import datetime
from typing import Any

# ==================== LEAD QUALIFICATION SERVICE ====================

# In-memory lead storage (resets on restart - demo only)
_LEADS: dict[str, dict[str, Any]] = {}
_LEAD_COUNTER = 5000


def _calculate_lead_score(budget: str, timeline: str, team_size: int) -> tuple[int, str]:
    """Calculate lead score and category based on inputs.

    Args:
        budget: Budget range or amount
        timeline: Timeline for decision/implementation
        team_size: Number of team members/users

    Returns:
        Tuple of (score, category)
    """
    score = 0

    # Budget scoring (0-40 points)
    budget_lower = budget.lower()
    if any(marker in budget_lower for marker in ["100k", "100000", "million"]):
        score += 40
    elif any(marker in budget_lower for marker in ["50k", "50000"]):
        score += 30
    elif any(marker in budget_lower for marker in ["10k", "10000", "20k", "30k"]):
        score += 20
    else:
        score += 10

    # Timeline scoring (0-30 points)
    timeline_lower = timeline.lower()
    if any(
        marker in timeline_lower
        for marker in ["asap", "immediately", "urgent", "1 month", "2 month"]
    ):
        score += 30
    elif any(marker in timeline_lower for marker in ["3 month", "quarter", "q1", "q2"]):
        score += 20
    elif any(marker in timeline_lower for marker in ["6 month", "half year"]):
        score += 10
    else:
        score += 5

    # Team size scoring (0-30 points)
    if team_size >= 100:
        score += 30
    elif team_size >= 20:
        score += 20
    elif team_size >= 5:
        score += 10
    else:
        score += 5

    # Determine category
    if score >= 70:
        category = "hot"
    elif score >= 40:
        category = "warm"
    else:
        category = "cold"

    return score, category


def qualify_lead(company: str, budget: str, timeline: str, team_size: int = 1) -> dict[str, Any]:
    """Qualify a new lead.

    Args:
        company: Company name
        budget: Budget range or amount
        timeline: Timeline for decision/implementation
        team_size: Number of team members/users (default 1)

    Returns:
        Dict containing lead qualification details including score and category
    """
    global _LEAD_COUNTER
    _LEAD_COUNTER += 1
    lead_id = f"LEAD-{_LEAD_COUNTER}"

    score, category = _calculate_lead_score(budget, timeline, team_size)

    # Generate next steps based on category
    if category == "hot":
        next_steps = [
            "Schedule demo with sales engineer",
            "Prepare custom proposal",
            "Arrange executive meeting",
            "Fast-track contract review",
        ]
    elif category == "warm":
        next_steps = [
            "Send product information packet",
            "Schedule discovery call",
            "Share case studies",
            "Provide pricing details",
        ]
    else:  # cold
        next_steps = [
            "Add to nurture campaign",
            "Share educational content",
            "Schedule follow-up in 3 months",
            "Offer free trial or demo",
        ]

    timestamp = datetime.now().isoformat()
    lead = {
        "lead_id": lead_id,
        "company": company,
        "budget": budget,
        "timeline": timeline,
        "team_size": team_size,
        "score": score,
        "category": category,
        "next_steps": next_steps,
        "qualified_at": timestamp,
    }

    _LEADS[lead_id] = lead
    return lead


def get_lead_score(lead_id: str) -> dict[str, Any]:
    """Get lead qualification details.

    Args:
        lead_id: Unique identifier for the lead

    Returns:
        Lead dict with qualification details or error dict
    """
    if lead_id not in _LEADS:
        return {"error": f"Lead {lead_id} not found"}

    return _LEADS[lead_id].copy()


# ==================== PRODUCT CATALOG SERVICE ====================

# Mock product catalog
_PRODUCT_CATALOG: dict[str, dict[str, Any]] = {
    "PROD-ENT-001": {
        "product_id": "PROD-ENT-001",
        "name": "Enterprise Suite Pro",
        "category": "Enterprise",
        "price": 99999,
        "features": [
            "Unlimited users",
            "Advanced analytics",
            "24/7 premium support",
            "Custom integrations",
            "Dedicated account manager",
            "SLA guarantee",
        ],
        "in_stock": True,
        "lead_time_days": 0,
    },
    "PROD-ENT-002": {
        "product_id": "PROD-ENT-002",
        "name": "Enterprise Platform",
        "category": "Enterprise",
        "price": 149999,
        "features": [
            "Everything in Pro",
            "Multi-region deployment",
            "Advanced security features",
            "Compliance certifications",
            "Custom development support",
        ],
        "in_stock": True,
        "lead_time_days": 0,
    },
    "PROD-SMB-001": {
        "product_id": "PROD-SMB-001",
        "name": "Business Standard",
        "category": "SMB",
        "price": 19999,
        "features": [
            "Up to 100 users",
            "Standard analytics",
            "Email support",
            "API access",
            "Standard integrations",
        ],
        "in_stock": True,
        "lead_time_days": 0,
    },
    "PROD-SMB-002": {
        "product_id": "PROD-SMB-002",
        "name": "Business Plus",
        "category": "SMB",
        "price": 29999,
        "features": [
            "Up to 100 users",
            "Advanced analytics",
            "Priority support",
            "Custom workflows",
            "Extended integrations",
        ],
        "in_stock": False,
        "lead_time_days": 14,
    },
    "PROD-START-001": {
        "product_id": "PROD-START-001",
        "name": "Starter Package",
        "category": "Starter",
        "price": 4999,
        "features": [
            "Up to 10 users",
            "Basic analytics",
            "Community support",
            "Core features",
        ],
        "in_stock": True,
        "lead_time_days": 0,
    },
    "PROD-START-002": {
        "product_id": "PROD-START-002",
        "name": "Starter Plus",
        "category": "Starter",
        "price": 7999,
        "features": [
            "Up to 10 users",
            "Standard analytics",
            "Email support",
            "Enhanced features",
            "Basic integrations",
        ],
        "in_stock": True,
        "lead_time_days": 0,
    },
}


def get_product_catalog(category: str | None = None) -> list[dict[str, Any]]:
    """Get product catalog, optionally filtered by category.

    Args:
        category: Filter by category (Enterprise, SMB, Starter) or None for all

    Returns:
        List of products matching the filter
    """
    products = list(_PRODUCT_CATALOG.values())

    if category:
        products = [p for p in products if p["category"].lower() == category.lower()]

    # Sort by price (descending)
    products.sort(key=lambda x: x["price"], reverse=True)

    return products


def recommend_products(requirements: str, max_results: int = 3) -> list[dict[str, Any]]:
    """Recommend products based on customer requirements.

    Args:
        requirements: Customer requirements description
        max_results: Maximum number of recommendations to return

    Returns:
        List of recommended products with match scores
    """
    requirements_lower = requirements.lower()
    scored_products = []

    for product in _PRODUCT_CATALOG.values():
        score = 0.0

        # Category matching
        if (
            ("enterprise" in requirements_lower and product["category"] == "Enterprise")
            or (
                any(word in requirements_lower for word in ["smb", "business", "medium"])
                and product["category"] == "SMB"
            )
            or (
                any(word in requirements_lower for word in ["starter", "small", "basic"])
                and product["category"] == "Starter"
            )
        ):
            score += 0.4

        # Feature matching
        for feature in product["features"]:
            feature_lower = feature.lower()
            if any(word in requirements_lower for word in feature_lower.split()):
                score += 0.1

        # Team size hints
        if "100" in requirements_lower or "large" in requirements_lower:
            if product["category"] == "Enterprise":
                score += 0.2
        elif (
            any(word in requirements_lower for word in ["10", "small", "few"])
            and product["category"] == "Starter"
        ):
            score += 0.2

        if score > 0:
            product_with_score = product.copy()
            product_with_score["match_score"] = min(score, 1.0)
            scored_products.append(product_with_score)

    # Sort by match score (highest first)
    scored_products.sort(key=lambda x: x["match_score"], reverse=True)

    return scored_products[:max_results]


def check_inventory(product_id: str) -> dict[str, Any]:
    """Check inventory for a specific product.

    Args:
        product_id: Unique product identifier

    Returns:
        Product inventory details or error dict
    """
    if product_id not in _PRODUCT_CATALOG:
        return {"error": f"Product {product_id} not found in catalog"}

    product = _PRODUCT_CATALOG[product_id].copy()
    return {
        "product_id": product["product_id"],
        "name": product["name"],
        "in_stock": product["in_stock"],
        "lead_time_days": product["lead_time_days"],
        "availability": "In Stock" if product["in_stock"] else f"{product['lead_time_days']} days",
    }
