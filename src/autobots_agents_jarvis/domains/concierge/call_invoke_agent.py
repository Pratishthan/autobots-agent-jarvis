# ABOUT ME: Demonstration service showing how to use invoke_agent and ainvoke_agent
# ABOUT ME: for programmatic agent orchestration without UI dependencies.

import asyncio
import uuid
from typing import TYPE_CHECKING

from autobots_devtools_shared_lib.common.observability import (
    TraceMetadata,
    get_logger,
    init_tracing,
    set_conversation_id,
)
from autobots_devtools_shared_lib.dynagent import ainvoke_agent, invoke_agent
from dotenv import load_dotenv

from autobots_agents_jarvis.domains.concierge.tools import register_concierge_tools

if TYPE_CHECKING:
    from langchain_core.runnables import RunnableConfig

logger = get_logger(__name__)
load_dotenv()


register_concierge_tools()
init_tracing()

APP_NAME = "concierge-invoke-demo"


def call_invoke_agent_sync(
    agent_name: str,
    user_message: str,
    session_id: str | None = None,
    enable_tracing: bool = True,
) -> dict:
    """
    Synchronously invoke an agent and log the results.

    This function demonstrates how to use invoke_agent() for programmatic
    orchestration workflows. It creates an agent, invokes it with a message,
    and logs the results.

    Args:
        agent_name: Name of the agent to invoke (e.g., "joke_agent", "coordinator")
        user_message: Message to send to the agent
        session_id: Optional session ID for tracking (auto-generated if None)
        enable_tracing: Whether to enable Langfuse tracing (default True)

    Returns:
        dict: The complete final state from the agent execution

    Example:
        >>> result = call_invoke_agent_sync("joke_agent", "Tell me a joke")
        >>> print(result["structured_response"])
    """

    if not session_id:
        session_id = str(uuid.uuid4())
    set_conversation_id(session_id)

    logger.info(f"🔑 Generated session_id: {session_id}")

    config: RunnableConfig = {
        "configurable": {
            "thread_id": session_id,
            "agent_name": agent_name,
            "app_name": APP_NAME,
        },
    }

    input_state: dict = {
        "messages": [{"role": "user", "content": user_message}],
        "agent_name": agent_name,
        "session_id": session_id,
    }

    # Prepare trace metadata
    trace_metadata = TraceMetadata(
        session_id=session_id,
        app_name=APP_NAME,
        user_id=APP_NAME,
        tags=[APP_NAME, agent_name, "sync"],
    )

    logger.info(f"Invoking SYNC agent '{agent_name}'")
    result = invoke_agent(
        agent_name=agent_name,
        input_state=input_state,
        config=config,
        trace_metadata=trace_metadata,
        enable_tracing=enable_tracing,
    )

    messages = result.get("messages") or []
    logger.debug(f"#Messages: {len(messages)}")

    if "structured_response" in result:
        logger.info("📦 Structured response received:")
        logger.info(f"   {result['structured_response']}")
    else:
        logger.info("💬 No structured response (text-only agent)")

    return result


async def call_invoke_agent_async(
    agent_name: str,
    user_message: str,
    session_id: str | None = None,
    enable_tracing: bool = True,
) -> dict:
    """
    Asynchronously invoke an agent and log the results.

    This function demonstrates how to use ainvoke_agent() for async
    orchestration workflows. It creates an agent, invokes it with a message,
    and logs the results.

    Args:
        agent_name: Name of the agent to invoke (e.g., "joke_agent", "coordinator")
        user_message: Message to send to the agent
        session_id: Optional session ID for tracking (auto-generated if None)
        enable_tracing: Whether to enable Langfuse tracing (default True)

    Returns:
        dict: The complete final state from the agent execution

    Example:
        >>> result = await call_invoke_agent_async("joke_agent", "Tell me a joke")
        >>> print(result["structured_response"])
    """

    if not session_id:
        session_id = str(uuid.uuid4())
    set_conversation_id(session_id)

    logger.info(f"🔑 Generated session_id: {session_id}")

    config: RunnableConfig = {
        "configurable": {
            "thread_id": session_id,
            "agent_name": agent_name,
            "app_name": APP_NAME,
        },
    }

    input_state: dict = {
        "messages": [{"role": "user", "content": user_message}],
        "agent_name": agent_name,
        "session_id": session_id,
    }

    # Prepare trace metadata
    trace_metadata = TraceMetadata(
        session_id=session_id,
        app_name=APP_NAME,
        user_id=APP_NAME,
        tags=[APP_NAME, agent_name, "async"],
    )

    logger.info(f"Invoking ASYNC agent '{agent_name}'")
    result = await ainvoke_agent(
        agent_name=agent_name,
        input_state=input_state,
        config=config,
        trace_metadata=trace_metadata,
        enable_tracing=enable_tracing,
    )

    messages = result.get("messages") or []
    logger.debug(f"#Messages: {len(messages)}")

    if "structured_response" in result:
        logger.info("📦 Structured response received:")
        logger.info(f"   {result['structured_response']}")
    else:
        logger.info("💬 No structured response (text-only agent)")

    return result


def call_invoke_agent(
    agent_name: str = "joke_agent",
    user_message: str = "Tell me a joke about Python programming",
) -> None:
    """
    Demonstration function that calls both sync and async agent invocations.

    This function showcases both invoke_agent() and ainvoke_agent() usage
    patterns for orchestration workflows. It runs both versions and logs
    the results for comparison.

    Args:
        agent_name: Name of the agent to invoke (default: "joke_agent")
        user_message: Message to send to the agent

    Example:
        >>> call_invoke_agent("joke_agent", "Tell me a joke")
    """
    logger.info("=" * 80)
    logger.info("🎯 DEMONSTRATION: Agent Invocation Utilities")
    logger.info("=" * 80)
    logger.info(f"Agent: {agent_name}")
    logger.info(f"Message: {user_message}")
    logger.info("=" * 80)

    # Run synchronous invocation
    logger.info("\n" + "=" * 80)
    logger.info("1️⃣  SYNCHRONOUS INVOCATION (invoke_agent)")
    logger.info("=" * 80)
    sync_result = call_invoke_agent_sync(agent_name, user_message)
    logger.info(f"✅ Sync invocation returned {len(sync_result)} state keys")

    # Run asynchronous invocation
    logger.info("\n" + "=" * 80)
    logger.info("2️⃣  ASYNCHRONOUS INVOCATION (ainvoke_agent)")
    logger.info("=" * 80)
    async_result = asyncio.run(call_invoke_agent_async(agent_name, user_message))
    logger.info(f"✅ Async invocation returned {len(async_result)} state keys")

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("📈 SUMMARY")
    logger.info("=" * 80)
    logger.info("✅ Both invocations completed successfully!")
    logger.info(
        f"📊 Sync result: {len(sync_result.get('messages', []))} messages, "
        f"structured={'structured_response' in sync_result}"
    )
    logger.info(
        f"📊 Async result: {len(async_result.get('messages', []))} messages, "
        f"structured={'structured_response' in async_result}"
    )
    logger.info("=" * 80)


if __name__ == "__main__":
    # Example 1: Basic usage with joke_agent
    logger.info("\n🔹 Example 1: Basic usage with joke_agent")
    call_invoke_agent("joke_agent", "Tell me a joke about programming")

    # Example 2: Using welcome_agent agent
    logger.info("\n\n🔹 Example 2: Using welcome_agent agent")
    call_invoke_agent("welcome_agent", "What agents are available in this system?")

    # Example 3: Sync-only invocation
    logger.info("\n\n🔹 Example 3: Sync-only invocation with custom session")
    result = call_invoke_agent_sync(
        agent_name="joke_agent",
        user_message="Tell me a short joke",
        session_id="custom-demo-session-123",
        enable_tracing=False,  # Disable tracing for this example
    )
    logger.info(f"Result keys: \n {result}")

    # Example 4: Async-only invocation
    logger.info("\n\n🔹 Example 4: Async-only invocation")

    async def async_example():
        result = await call_invoke_agent_async(
            agent_name="joke_agent",
            user_message="Tell me a joke about async programming",
        )
        logger.info(f"Result: \n{result}")
        return result

    asyncio.run(async_example())

    logger.info("\n✅ All examples completed!")
