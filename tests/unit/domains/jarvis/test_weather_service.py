# ABOUTME: Unit tests for weather service.

import pytest

from autobots_agents_jarvis.domains.jarvis.services import get_forecast, get_weather


def test_get_weather_valid_location():
    """Test getting weather for a valid location."""
    weather = get_weather("San Francisco")
    assert isinstance(weather, dict)
    assert "location" in weather
    assert "temperature" in weather
    assert "conditions" in weather
    assert weather["location"] == "San Francisco"
    assert "value" in weather["temperature"]
    assert "unit" in weather["temperature"]


def test_get_weather_invalid_location():
    """Test getting weather for an invalid location returns error."""
    result = get_weather("InvalidCity123")
    assert isinstance(result, dict)
    assert "error" in result


@pytest.mark.parametrize(
    "location",
    ["San Francisco", "New York", "London", "Tokyo", "Seattle", "Miami"],
)
def test_get_weather_all_locations(location: str):
    """Test getting weather for all valid locations."""
    weather = get_weather(location)
    assert isinstance(weather, dict)
    assert weather["location"] == location
    assert isinstance(weather["conditions"], str)


def test_get_forecast_valid_location():
    """Test getting forecast for a valid location."""
    forecast = get_forecast("San Francisco", days=3)
    assert isinstance(forecast, dict)
    assert "location" in forecast
    assert "forecast" in forecast
    assert forecast["location"] == "San Francisco"
    assert isinstance(forecast["forecast"], list)
    assert len(forecast["forecast"]) == 3


def test_get_forecast_invalid_location():
    """Test getting forecast for an invalid location returns error."""
    result = get_forecast("InvalidCity123", days=3)
    assert isinstance(result, dict)
    assert "error" in result


def test_get_forecast_day_limits():
    """Test that forecast respects day limits."""
    # Test minimum (1 day)
    forecast = get_forecast("New York", days=0)
    assert len(forecast["forecast"]) == 1

    # Test maximum (7 days)
    forecast = get_forecast("New York", days=10)
    assert len(forecast["forecast"]) == 7

    # Test normal range
    forecast = get_forecast("New York", days=5)
    assert len(forecast["forecast"]) == 5
