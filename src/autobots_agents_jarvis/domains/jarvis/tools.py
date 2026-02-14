# ABOUTME: Jarvis use-case tools — the 4 tools that Jarvis registers.
# ABOUTME: Provides joke and weather functionality for demonstration purposes.

from autobots_devtools_shared_lib.common.observability.logging_utils import (
    get_logger,
    set_conversation_id,
)
from autobots_devtools_shared_lib.dynagent import Dynagent
from langchain.tools import ToolRuntime, tool

from autobots_agents_jarvis.domains.jarvis.services import get_forecast as weather_get_forecast
from autobots_agents_jarvis.domains.jarvis.services import get_joke, list_categories
from autobots_agents_jarvis.domains.jarvis.services import get_weather as weather_get_weather

logger = get_logger(__name__)


# --- @tool wrappers ---


@tool
def tell_joke(runtime: ToolRuntime[None, Dynagent], category: str) -> str:
    """Tell a joke from the specified category.

    Args:
        category: The joke category (programming, general, knock-knock, dad-joke)

    Returns:
        A formatted joke string
    """
    session_id = runtime.state.get("session_id", "default")
    set_conversation_id(session_id)
    logger.info(f"Telling joke for session {session_id}, category: {category}")

    joke_data = get_joke(category)
    if "error" in joke_data:
        return joke_data["error"]

    return f"{joke_data['joke_text']} (Category: {joke_data['category']}, Rating: {joke_data['rating']}/5)"


@tool
def get_joke_categories() -> str:
    """Get the list of available joke categories.

    Returns:
        A comma-separated list of available joke categories
    """
    categories = list_categories()
    return f"Available joke categories: {', '.join(categories)}"


@tool
def get_weather(runtime: ToolRuntime[None, Dynagent], location: str) -> str:
    """Get current weather information for a location.

    Args:
        location: The location to get weather for (e.g., "San Francisco", "New York")

    Returns:
        Formatted weather information
    """
    session_id = runtime.state.get("session_id", "default")
    set_conversation_id(session_id)
    logger.info(f"Getting weather for session {session_id}, location: {location}")

    weather_data = weather_get_weather(location)
    if "error" in weather_data:
        return weather_data["error"]

    temp = weather_data["temperature"]
    return (
        f"Weather in {weather_data['location']}: "
        f"{weather_data['conditions']}, "
        f"{temp['value']}°{temp['unit'][0].upper()}"
    )


@tool
def get_forecast(runtime: ToolRuntime[None, Dynagent], location: str, days: int = 3) -> str:
    """Get weather forecast for a location.

    Args:
        location: The location to get forecast for (e.g., "San Francisco", "New York")
        days: Number of days to forecast (default: 3, max: 7)

    Returns:
        Formatted weather forecast
    """
    session_id = runtime.state.get("session_id", "default")
    set_conversation_id(session_id)
    logger.info(f"Getting forecast for session {session_id}, location: {location}, days: {days}")

    forecast_data = weather_get_forecast(location, days)
    if "error" in forecast_data:
        return forecast_data["error"]

    forecast_items = "\n  ".join(
        f"Day {i + 1}: {item}" for i, item in enumerate(forecast_data["forecast"])
    )
    return f"Weather forecast for {forecast_data['location']}:\n  {forecast_items}"


# --- Registration entry-point (called once at app startup) ---


def register_jarvis_tools() -> None:
    """Register all 4 Jarvis tools into the dynagent usecase pool."""
    from autobots_devtools_shared_lib.dynagent import register_usecase_tools

    register_usecase_tools(
        [
            tell_joke,
            get_joke_categories,
            get_weather,
            get_forecast,
        ]
    )
