# ABOUTME: Unit tests for sales services.

import pytest

from autobots_agents_jarvis.domains.sales.services import (
    check_inventory,
    get_lead_score,
    get_product_catalog,
    qualify_lead,
    recommend_products,
)


def test_qualify_lead_hot():
    """Test qualifying a hot lead (high budget, urgent timeline)."""
    result = qualify_lead(
        company="Tech Corp",
        budget="$1 million",
        timeline="immediately ASAP",
        team_size=100,
    )

    assert isinstance(result, dict)
    assert "score" in result
    assert "category" in result
    assert "company" in result
    assert result["category"] == "hot"
    assert result["score"] >= 70  # Hot leads have score >= 70


def test_qualify_lead_warm():
    """Test qualifying a warm lead (medium budget, moderate timeline)."""
    result = qualify_lead(
        company="Medium Co",
        budget="$50k",
        timeline="3-6 months",
        team_size=25,
    )

    assert result["category"] == "warm"
    assert 40 <= result["score"] < 70  # Warm leads have 40-69


def test_qualify_lead_cold():
    """Test qualifying a cold lead (low budget, long timeline)."""
    result = qualify_lead(
        company="Small Startup",
        budget="$5k",
        timeline="next year",
        team_size=5,
    )

    assert result["category"] == "cold"
    assert result["score"] < 40  # Cold leads have score < 40


def test_get_lead_score_existing():
    """Test getting score for an existing lead."""
    # First qualify a lead
    qualified = qualify_lead(
        company="Test Corp",
        budget="$100k",
        timeline="immediate",
        team_size=50,
    )
    lead_id = qualified["lead_id"]

    # Get the score
    result = get_lead_score(lead_id)

    assert "error" not in result
    assert result["lead_id"] == lead_id
    assert "score" in result
    assert "category" in result


def test_get_lead_score_nonexistent():
    """Test getting score for nonexistent lead."""
    result = get_lead_score("NONEXISTENT")
    assert "error" in result


def test_get_product_catalog_all():
    """Test getting entire product catalog."""
    catalog = get_product_catalog()

    assert isinstance(catalog, list)
    assert len(catalog) == 6  # We have 6 products
    assert all("product_id" in p for p in catalog)
    assert all("name" in p for p in catalog)
    assert all("category" in p for p in catalog)


def test_get_product_catalog_by_category():
    """Test filtering catalog by category."""
    enterprise = get_product_catalog(category="Enterprise")

    assert isinstance(enterprise, list)
    assert len(enterprise) == 2  # 2 enterprise products
    assert all(p["category"] == "Enterprise" for p in enterprise)


def test_get_product_catalog_invalid_category():
    """Test filtering by invalid category."""
    result = get_product_catalog(category="NonexistentCategory")
    assert isinstance(result, list)
    assert len(result) == 0


@pytest.mark.parametrize(
    "category,expected_count",
    [
        ("Enterprise", 2),
        ("SMB", 2),
        ("Starter", 2),
    ],
)
def test_get_product_catalog_all_categories(category: str, expected_count: int):
    """Test getting products from all categories."""
    products = get_product_catalog(category=category)
    assert len(products) == expected_count


def test_recommend_products_enterprise():
    """Test product recommendations for enterprise requirements."""
    recommendations = recommend_products("Need solution for 500+ users with advanced analytics")

    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    # Should recommend enterprise products
    assert any(p["category"] == "Enterprise" for p in recommendations)


def test_recommend_products_starter():
    """Test product recommendations for starter requirements."""
    recommendations = recommend_products("Small team of 10 users, budget-friendly solution")

    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    # Should recommend starter products
    assert any(p["category"] == "Starter" for p in recommendations)


def test_check_inventory_in_stock():
    """Test checking inventory for in-stock product."""
    result = check_inventory("PROD-ENT-001")

    assert "error" not in result
    assert result["product_id"] == "PROD-ENT-001"
    assert result["in_stock"] is True
    assert "name" in result


def test_check_inventory_out_of_stock():
    """Test checking inventory for out-of-stock product."""
    result = check_inventory("PROD-SMB-002")

    assert "error" not in result
    assert result["product_id"] == "PROD-SMB-002"
    assert result["in_stock"] is False


def test_check_inventory_nonexistent():
    """Test checking inventory for nonexistent product."""
    result = check_inventory("NONEXISTENT")
    assert "error" in result


@pytest.mark.parametrize(
    "product_id",
    [
        "PROD-ENT-001",
        "PROD-ENT-002",
        "PROD-SMB-001",
        "PROD-SMB-002",
        "PROD-START-001",
        "PROD-START-002",
    ],
)
def test_check_all_products_inventory(product_id: str):
    """Test checking inventory for all products."""
    result = check_inventory(product_id)
    assert "error" not in result
    assert result["product_id"] == product_id
    assert "in_stock" in result
    assert isinstance(result["in_stock"], bool)
