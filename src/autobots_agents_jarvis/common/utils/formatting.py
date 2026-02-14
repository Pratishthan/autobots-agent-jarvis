# ABOUTME: Formatting utilities for converting structured outputs to Markdown.
# ABOUTME: Designed for displaying agent responses in the Jarvis chat UI.

from typing import Any

# Re-exported from the shared dynagent UI layer so existing imports keep working.
from autobots_devtools_shared_lib.dynagent.ui import (
    format_dict_item,
    structured_to_markdown,
)

# Ensure the re-exports are visible to linters / type-checkers that analyse __all__.
__all__ = ["format_dict_item", "structured_to_markdown"]


def format_joke_output(data: dict[str, Any]) -> str:
    """Specialized formatter for joke output."""
    lines = ["## 😄 Joke\n"]

    joke_text = data.get("joke_text", "No joke available")
    category = data.get("category", "unknown")
    rating = data.get("rating", 0)

    lines.append(f"{joke_text}\n")
    lines.append(f"**Category:** {category}")
    lines.append(f"**Rating:** {'⭐' * rating} ({rating}/5)")

    return "\n".join(lines)


def format_weather_output(data: dict[str, Any]) -> str:
    """Specialized formatter for weather output."""
    lines = ["## 🌤️ Weather Information\n"]

    location = data.get("location", "Unknown")
    lines.append(f"**Location:** {location}\n")

    if temp := data.get("temperature"):
        value = temp.get("value", 0)
        unit = temp.get("unit", "celsius")
        unit_symbol = "°F" if unit == "fahrenheit" else "°C"
        lines.append(f"**Temperature:** {value}{unit_symbol}")

    conditions = data.get("conditions", "Unknown")
    lines.append(f"**Conditions:** {conditions}\n")

    if forecast := data.get("forecast"):
        lines.append("### Forecast\n")
        for idx, day_forecast in enumerate(forecast, 1):
            lines.append(f"**Day {idx}:** {day_forecast}")

    return "\n".join(lines)


# Mapping of output types to specialized formatters
OUTPUT_FORMATTERS = {
    "joke": format_joke_output,
    "weather": format_weather_output,
}


def format_structured_output(data: dict[str, Any], output_type: str | None = None) -> str:
    """
    Format structured output for UI display.

    Args:
        data: Structured response dict
        output_type: Optional type hint (e.g., "joke", "weather")

    Returns:
        Markdown-formatted string for display
    """
    # Use specialized formatter if available
    if output_type and output_type in OUTPUT_FORMATTERS:
        return OUTPUT_FORMATTERS[output_type](data)

    # Fall back to generic formatter
    return structured_to_markdown(data)
