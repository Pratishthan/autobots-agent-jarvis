# ABOUTME: Unit tests for joke service.

import pytest

from autobots_agents_jarvis.domains.jarvis.services import get_joke, list_categories


def test_list_categories():
    """Test that list_categories returns expected categories."""
    categories = list_categories()
    assert isinstance(categories, list)
    assert len(categories) == 4
    assert "programming" in categories
    assert "general" in categories
    assert "knock-knock" in categories
    assert "dad-joke" in categories


def test_get_joke_valid_category():
    """Test getting a joke from a valid category."""
    joke = get_joke("programming")
    assert isinstance(joke, dict)
    assert "joke_text" in joke
    assert "category" in joke
    assert "rating" in joke
    assert joke["category"] == "programming"
    assert 1 <= joke["rating"] <= 5


def test_get_joke_invalid_category():
    """Test getting a joke from an invalid category returns error."""
    result = get_joke("invalid_category")
    assert isinstance(result, dict)
    assert "error" in result


@pytest.mark.parametrize(
    "category",
    ["programming", "general", "knock-knock", "dad-joke"],
)
def test_get_joke_all_categories(category: str):
    """Test getting jokes from all valid categories."""
    joke = get_joke(category)
    assert isinstance(joke, dict)
    assert "joke_text" in joke
    assert joke["category"] == category
    assert isinstance(joke["joke_text"], str)
    assert len(joke["joke_text"]) > 0
