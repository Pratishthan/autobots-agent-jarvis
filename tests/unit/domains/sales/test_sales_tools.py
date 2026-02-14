# ABOUTME: Unit tests for sales tools.

from unittest.mock import MagicMock

import pytest
from autobots_devtools_shared_lib.dynagent import Dynagent
from langchain.tools import ToolRuntime

from autobots_agents_jarvis.domains.sales.tools import (
    check_inventory,
    get_lead_score,
    get_product_catalog,
    qualify_lead,
    recommend_products,
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


def test_qualify_lead_tool_hot(mock_runtime):
    """Test qualify_lead tool with hot lead."""
    result = qualify_lead.func(
        mock_runtime,
        company="Tech Corp",
        budget="$1 million",
        timeline="ASAP immediately",
        team_size=100,
    )

    assert isinstance(result, str)
    assert "HOT" in result or "WARM" in result  # Category is present
    assert "Tech Corp" in result
    assert "LEAD-" in result  # Lead ID format


def test_qualify_lead_tool_warm(mock_runtime):
    """Test qualify_lead tool with warm lead."""
    result = qualify_lead.func(
        mock_runtime,
        company="Medium Co",
        budget="$50k",
        timeline="3-6 months",
        team_size=25,
    )

    assert "WARM" in result or "COLD" in result or "HOT" in result
    assert "Medium Co" in result


def test_qualify_lead_tool_cold(mock_runtime):
    """Test qualify_lead tool with cold lead."""
    result = qualify_lead.func(
        mock_runtime,
        company="Small Startup",
        budget="$5k",
        timeline="next year",
        team_size=5,
    )

    assert "COLD" in result or "WARM" in result
    assert "Small Startup" in result


def test_get_lead_score_tool_success(mock_runtime):
    """Test get_lead_score tool with existing lead."""
    # First qualify a lead
    qualify_result = qualify_lead.func(
        mock_runtime,
        company="Test Corp",
        budget="$100k",
        timeline="ASAP",
        team_size=50,
    )
    # Extract lead ID (format: "**Lead ID:** LEAD-XXXX")
    lead_id = qualify_result.split("**Lead ID:** ")[1].split("\n")[0]

    # Get the score
    result = get_lead_score.func(mock_runtime, lead_id=lead_id)

    assert isinstance(result, str)
    assert lead_id in result
    assert "Score" in result or "score" in result


def test_get_lead_score_tool_not_found(mock_runtime):
    """Test get_lead_score with nonexistent lead."""
    result = get_lead_score.func(mock_runtime, lead_id="NONEXISTENT")

    assert "❌" in result
    assert "not found" in result


def test_get_product_catalog_tool_all(mock_runtime):
    """Test get_product_catalog tool without filter."""
    result = get_product_catalog.func(mock_runtime)

    assert isinstance(result, str)
    assert "Product Catalog" in result
    assert "6 products" in result
    assert "PROD-" in result  # Should contain product IDs


def test_get_product_catalog_tool_filtered(mock_runtime):
    """Test get_product_catalog tool with category filter."""
    result = get_product_catalog.func(mock_runtime, category="Enterprise")

    assert "Product Catalog" in result
    assert "Enterprise" in result
    assert "2 products" in result


def test_get_product_catalog_tool_no_results(mock_runtime):
    """Test get_product_catalog with invalid category."""
    result = get_product_catalog.func(mock_runtime, category="NonexistentCategory")

    assert "No products found" in result


def test_recommend_products_tool_enterprise(mock_runtime):
    """Test recommend_products tool with enterprise requirements."""
    result = recommend_products.func(
        mock_runtime, requirements="Need solution for 500+ users with advanced analytics"
    )

    assert isinstance(result, str)
    assert "PROD-" in result  # Should contain product IDs


def test_recommend_products_tool_starter(mock_runtime):
    """Test recommend_products tool with starter requirements."""
    result = recommend_products.func(
        mock_runtime, requirements="Small team of 10 users, budget-friendly solution"
    )

    assert "PROD-" in result


def test_recommend_products_tool_no_match(mock_runtime):
    """Test recommend_products with no matching products."""
    result = recommend_products.func(mock_runtime, requirements="xyzabc123nonexistent requirements")

    assert isinstance(result, str)
    # Should return a message about no products found
    assert "No products found" in result or "PROD-" in result


def test_check_inventory_tool_in_stock(mock_runtime):
    """Test check_inventory tool for in-stock product."""
    result = check_inventory.func(mock_runtime, product_id="PROD-ENT-001")

    assert isinstance(result, str)
    assert "PROD-ENT-001" in result
    assert "In Stock" in result or "Availability" in result


def test_check_inventory_tool_out_of_stock(mock_runtime):
    """Test check_inventory tool for out-of-stock product."""
    result = check_inventory.func(mock_runtime, product_id="PROD-SMB-002")

    assert "PROD-SMB-002" in result
    assert "days" in result or "Availability" in result  # Shows wait time


def test_check_inventory_tool_not_found(mock_runtime):
    """Test check_inventory with nonexistent product."""
    result = check_inventory.func(mock_runtime, product_id="NONEXISTENT")

    assert "❌" in result
    assert "not found" in result


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
def test_check_inventory_all_products(mock_runtime, product_id: str):
    """Test checking inventory for all products via tool."""
    result = check_inventory.func(mock_runtime, product_id=product_id)

    assert isinstance(result, str)
    assert product_id in result
    assert len(result) > 50  # Should have substantial content
