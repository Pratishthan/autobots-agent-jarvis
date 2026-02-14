# ABOUTME: Jarvis domain services — mock implementations for jokes and weather.
# ABOUTME: Combines joke_service and weather_service for the Jarvis domain.

import random
from typing import Any

# ==================== JOKE SERVICE ====================

# Mock joke database
JOKES: dict[str, list[dict[str, Any]]] = {
    "programming": [
        {
            "joke_text": "Why do programmers prefer dark mode? Because light attracts bugs!",
            "category": "programming",
            "rating": 4,
        },
        {
            "joke_text": "How many programmers does it take to change a light bulb? None, it's a hardware problem!",
            "category": "programming",
            "rating": 3,
        },
        {
            "joke_text": "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'",
            "category": "programming",
            "rating": 5,
        },
        {
            "joke_text": "There are 10 types of people in the world: those who understand binary and those who don't.",
            "category": "programming",
            "rating": 4,
        },
        {
            "joke_text": "Why do Python programmers wear glasses? Because they can't C!",
            "category": "programming",
            "rating": 3,
        },
    ],
    "general": [
        {
            "joke_text": "Why don't scientists trust atoms? Because they make up everything!",
            "category": "general",
            "rating": 4,
        },
        {
            "joke_text": "What do you call a fake noodle? An impasta!",
            "category": "general",
            "rating": 3,
        },
        {
            "joke_text": "Why did the scarecrow win an award? He was outstanding in his field!",
            "category": "general",
            "rating": 3,
        },
    ],
    "knock-knock": [
        {
            "joke_text": "Knock knock. Who's there? Interrupting cow. Interrupting cow w— MOOOOO!",
            "category": "knock-knock",
            "rating": 2,
        },
        {
            "joke_text": "Knock knock. Who's there? Tank. Tank who? You're welcome!",
            "category": "knock-knock",
            "rating": 3,
        },
    ],
    "dad-joke": [
        {
            "joke_text": "I'm afraid for the calendar. Its days are numbered.",
            "category": "dad-joke",
            "rating": 4,
        },
        {
            "joke_text": "What do you call a bear with no teeth? A gummy bear!",
            "category": "dad-joke",
            "rating": 3,
        },
        {
            "joke_text": "Why don't eggs tell jokes? They'd crack each other up!",
            "category": "dad-joke",
            "rating": 3,
        },
        {
            "joke_text": "I used to hate facial hair, but then it grew on me.",
            "category": "dad-joke",
            "rating": 4,
        },
    ],
}


def get_joke(category: str) -> dict[str, Any]:
    """Get a random joke from the specified category.

    Args:
        category: The joke category (programming, general, knock-knock, dad-joke)

    Returns:
        A dictionary containing joke_text, category, and rating
    """
    if category not in JOKES:
        return {
            "error": f"Invalid category '{category}'. Use get_joke_categories to see available categories."
        }

    return random.choice(JOKES[category])  # noqa: S311 - random is fine for joke selection


def list_categories() -> list[str]:
    """Get the list of available joke categories.

    Returns:
        List of available category names
    """
    return list(JOKES.keys())


# ==================== WEATHER SERVICE ====================

# Mock weather database with synthetic data
WEATHER_DATA: dict[str, dict[str, Any]] = {
    "san francisco": {
        "location": "San Francisco",
        "temperature": {"value": 62, "unit": "fahrenheit"},
        "conditions": "Foggy",
    },
    "new york": {
        "location": "New York",
        "temperature": {"value": 55, "unit": "fahrenheit"},
        "conditions": "Partly Cloudy",
    },
    "london": {
        "location": "London",
        "temperature": {"value": 12, "unit": "celsius"},
        "conditions": "Rainy",
    },
    "tokyo": {
        "location": "Tokyo",
        "temperature": {"value": 18, "unit": "celsius"},
        "conditions": "Clear",
    },
    "seattle": {
        "location": "Seattle",
        "temperature": {"value": 50, "unit": "fahrenheit"},
        "conditions": "Rainy",
    },
    "miami": {
        "location": "Miami",
        "temperature": {"value": 82, "unit": "fahrenheit"},
        "conditions": "Sunny",
    },
}

# Forecast templates for different conditions
FORECAST_TEMPLATES: dict[str, list[str]] = {
    "Foggy": [
        "Foggy morning clearing to partly cloudy",
        "Continued fog with light winds",
        "Fog dissipating by midday",
    ],
    "Partly Cloudy": [
        "Mostly sunny",
        "Increasing clouds",
        "Cloudy with chance of rain",
    ],
    "Rainy": [
        "Light rain continuing",
        "Heavy rain expected",
        "Rain tapering off",
        "Scattered showers",
    ],
    "Clear": [
        "Clear skies continuing",
        "Partly cloudy",
        "Mostly sunny",
        "Clear and pleasant",
    ],
    "Sunny": ["Sunny and warm", "Hot and sunny", "Clear skies", "Bright sunshine"],
}


def get_weather(location: str) -> dict[str, Any]:
    """Get current weather information for a location.

    Args:
        location: The location to get weather for (e.g., "San Francisco", "New York")

    Returns:
        A dictionary containing location, temperature, and conditions
    """
    location_key = location.lower()

    if location_key not in WEATHER_DATA:
        return {
            "error": f"Weather data not available for '{location}'. Try: San Francisco, New York, London, Tokyo, Seattle, or Miami."
        }

    return WEATHER_DATA[location_key].copy()


def get_forecast(location: str, days: int = 3) -> dict[str, Any]:
    """Get weather forecast for a location.

    Args:
        location: The location to get forecast for
        days: Number of days to forecast (default: 3, max: 7)

    Returns:
        A dictionary containing location and forecast array
    """
    location_key = location.lower()

    if location_key not in WEATHER_DATA:
        return {
            "error": f"Weather data not available for '{location}'. Try: San Francisco, New York, London, Tokyo, Seattle, or Miami."
        }

    # Limit days to reasonable range
    days = min(max(days, 1), 7)

    # Get current conditions and generate forecast based on it
    current = WEATHER_DATA[location_key]
    conditions = current["conditions"]
    forecast_options = FORECAST_TEMPLATES.get(conditions, ["Conditions vary"])

    # Generate forecast days - using list comprehension for performance
    forecast_list = [
        random.choice(forecast_options)  # noqa: S311
        for _ in range(days)
    ]

    return {
        "location": current["location"],
        "forecast": forecast_list,
    }
