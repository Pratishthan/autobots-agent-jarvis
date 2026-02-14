# ABOUTME: Customer Support-specific Chainlit entry point for the customer_support_chat use case.
# ABOUTME: Wires tracing, OAuth, and the shared streaming helper.

import os
from typing import TYPE_CHECKING, Any

import chainlit as cl
from autobots_devtools_shared_lib.common.observability.logging_utils import get_logger
from autobots_devtools_shared_lib.common.observability.trace_metadata import TraceMetadata
from autobots_devtools_shared_lib.common.observability.tracing import flush_tracing, init_tracing
from autobots_devtools_shared_lib.dynagent import create_base_agent
from autobots_devtools_shared_lib.dynagent.ui import stream_agent_events
from dotenv import load_dotenv

from autobots_agents_jarvis.common.tools.validation_tools import register_validation_tools
from autobots_agents_jarvis.common.utils.formatting import format_structured_output
from autobots_agents_jarvis.configs.settings import init_jarvis_settings
from autobots_agents_jarvis.domains.customer_support.tools import register_customer_support_tools

if TYPE_CHECKING:
    from langchain_core.runnables import RunnableConfig

# Load environment variables from .env file
load_dotenv()

logger = get_logger(__file__)

# Application name for tracing and identification
APP_NAME = "customer_support_chat"

# Register settings so shared-lib (dynagent) uses the same instance.
init_jarvis_settings()

# Registration must precede AgentMeta.instance() (called inside create_base_agent).
register_validation_tools()  # Register shared validation tools from common/
register_customer_support_tools()  # Register domain-specific tools


# Check if OAuth is configured
OAUTH_ENABLED = bool(
    os.getenv("OAUTH_GITHUB_CLIENT_ID")
    and os.getenv("OAUTH_GITHUB_CLIENT_SECRET")
    and os.getenv("CHAINLIT_AUTH_SECRET")
)

# Only register OAuth callback if OAuth is enabled
if OAUTH_ENABLED:

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
else:
    # No OAuth - anonymous access
    logger.info("OAuth is not configured - anonymous access")
    pass


def _get_user_identifier() -> str:
    """User ID for tracing and state; defaults to anonymous when OAuth is off."""
    user = cl.user_session.get("user")
    if user:
        return user.identifier[:200]
    return f"anonymous-{cl.context.session.thread_id}"[:200]


@cl.on_chat_start
async def start():
    """Initialize the chat session with the default customer support coordinator agent."""
    # Create agent instance once and store it in session
    init_tracing()
    base_agent = create_base_agent()
    cl.user_session.set("base_agent", base_agent)

    # Prepare trace metadata for Langfuse observability (session-level)
    user_id = _get_user_identifier()
    cl.user_session.set("user_id", user_id)

    trace_metadata = TraceMetadata.create(
        session_id=cl.context.session.thread_id,
        app_name=APP_NAME,
        user_id=user_id,
        tags=[APP_NAME],
    )
    cl.user_session.set("trace_metadata", trace_metadata)

    await cl.Message(
        content="Hello! I'm your Customer Support assistant. How can I help you today?"
    ).send()


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

    # Reuse the same agent instance from session
    base_agent = cl.user_session.get("base_agent")
    if not base_agent:
        await cl.Message(content="Error: Session initialization failed. Please refresh.").send()
        return

    user_id = cl.user_session.get("user_id")

    input_state: dict[str, Any] = {
        "messages": [{"role": "user", "content": message.content}],
        "user_id": user_id,
        "app_name": APP_NAME,
        "session_id": cl.context.session.thread_id,
    }

    # Retrieve trace metadata from session
    trace_metadata = cl.user_session.get("trace_metadata")

    result = await stream_agent_events(
        agent=base_agent,
        input_state=input_state,
        config=config,
        on_structured_output=format_structured_output,
        enable_tracing=True,
        trace_metadata=trace_metadata,
    )
    logger.debug(f"Agent execution completed with result: {result}")


@cl.on_stop
def on_stop() -> None:
    """Handle chat stop."""
    flush_tracing()
    logger.info("Chat session stopped")


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
