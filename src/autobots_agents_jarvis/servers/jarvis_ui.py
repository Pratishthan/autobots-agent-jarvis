# ABOUTME: Jarvis-specific Chainlit entry point for the jarvis_chat use case.
# ABOUTME: Wires tracing, OAuth, and the shared streaming helper.

from typing import TYPE_CHECKING, Any

import chainlit as cl
from autobots_devtools_shared_lib.common.observability.logging_utils import get_logger
from autobots_devtools_shared_lib.common.observability.tracing import (
    flush_tracing,
    get_langfuse_handler,
    init_tracing,
)
from autobots_devtools_shared_lib.dynagent.agents.base_agent import create_base_agent
from autobots_devtools_shared_lib.dynagent.ui.ui_utils import stream_agent_events
from dotenv import load_dotenv
from langfuse import propagate_attributes

from autobots_agents_jarvis.tools.jarvis_tools import register_jarvis_tools
from autobots_agents_jarvis.utils.formatting import format_structured_output

if TYPE_CHECKING:
    from langchain_core.runnables import RunnableConfig

# Load environment variables from .env file
load_dotenv()

logger = get_logger(__file__)

# Application name for tracing and identification
APP_NAME = "jarvis_chat"

# Registration must precede AgentMeta.instance() (called inside create_base_agent).
register_jarvis_tools()


@cl.oauth_callback  # type: ignore[arg-type]
def oauth_callback(
    provider_id: str,
    token: str,  # noqa: ARG001
    raw_user_data: dict,
    default_user: cl.User,
) -> cl.User | None:
    """Handle OAuth callback from GitHub.

    Args:
        provider_id: The OAuth provider ID (e.g., "github").
        token: The OAuth access token.
        raw_user_data: Raw user data from the provider.
        default_user: Default user object created by Chainlit.

    Returns:
        The authenticated user or None if authentication fails.
    """
    if provider_id != "github":
        logger.warning(f"Unsupported OAuth provider: {provider_id}")
        return None

    username = raw_user_data.get("login", "unknown")
    logger.info(f"User authenticated via GitHub: {username}")
    return default_user


@cl.on_chat_start
async def start():
    """Initialize the chat session with the welcome agent."""
    # Create agent instance once and store it in session
    init_tracing()
    agent = create_base_agent(agent_name=APP_NAME)
    cl.user_session.set("agent", agent)
    await cl.Message(content="Hello! I'm Jarvis. How can I help you today?").send()


@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages from the user."""
    config: RunnableConfig = {
        "configurable": {
            "thread_id": cl.context.session.thread_id,
        },
        "recursion_limit": 50,
        "run_name": APP_NAME,  # Set trace name for Langfuse
    }

    # Add Langfuse handler if available
    langfuse_handler = get_langfuse_handler()
    if langfuse_handler:
        config["callbacks"] = [langfuse_handler]

    # Reuse the same agent instance from session
    agent = cl.user_session.get("agent")
    user = cl.user_session.get("user")

    if not agent or not user:
        await cl.Message(content="Error: Session initialization failed. Please refresh.").send()
        return

    user_name = user.identifier

    input_state: dict[str, Any] = {
        "messages": [{"role": "user", "content": message.content}],
        "user_name": user_name,
        "app_name": APP_NAME,
        "session_id": cl.context.session.thread_id,
    }

    try:
        # Use propagate_attributes to tag user and session for Langfuse tracking
        with propagate_attributes(
            user_id=user_name[:200],  # Ensure ≤200 chars as per Langfuse requirements
            session_id=cl.context.session.thread_id[:200],  # Use thread_id as session
            tags=[APP_NAME],  # Tag with app name for filtering in Langfuse
        ):
            await stream_agent_events(
                agent,
                input_state,
                config,
                on_structured_output=format_structured_output,
            )
    finally:
        flush_tracing()


@cl.on_stop
def on_stop() -> None:
    """Handle chat stop."""
    flush_tracing()
    logger.info("Chat session stopped")


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
