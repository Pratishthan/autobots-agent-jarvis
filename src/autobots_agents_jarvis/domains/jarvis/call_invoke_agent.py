# ABOUT ME: Demonstration service showing how to use invoke_agent and ainvoke_agent
# ABOUT ME: for programmatic agent orchestration without UI dependencies.

import asyncio
from typing import Any

from autobots_devtools_shared_lib.common.observability.logging_utils import (
    get_logger,
    set_conversation_id,
)
from autobots_devtools_shared_lib.common.observability.trace_metadata import TraceMetadata
from autobots_devtools_shared_lib.common.observability.tracing import init_tracing
from autobots_devtools_shared_lib.dynagent import ainvoke_agent, invoke_agent
from dotenv import load_dotenv

from autobots_agents_jarvis.domains.jarvis.tools import register_jarvis_tools

logger = get_logger(__name__)
load_dotenv()


register_jarvis_tools()
init_tracing()


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

    if session_id:
        set_conversation_id(session_id)
        logger.info(f"🔑 Using custom session_id: {session_id}")

    logger.info(f"🔵 Starting SYNC invocation for agent: {agent_name}")
    logger.info(f"📝 User message: {user_message}")

    # Prepare input state
    input_state: dict[str, Any] = {}
    input_state["messages"] = [{"role": "user", "content": user_message}]

    if session_id:
        input_state["session_id"] = session_id
        logger.info(f"🔑 Using custom session_id: {session_id}")

    # Prepare config
    config: dict[str, Any] = {}  # type: ignore[assignment]
    config["configurable"] = {"thread_id": f"sync-{agent_name}-example"}

    # Prepare trace metadata
    trace_metadata = TraceMetadata(
        session_id=session_id or TraceMetadata.create().session_id,
        app_name="jarvis-invoke-demo",
        user_id="demo-user",
        tags=["demo", "sync", agent_name],
    )

    # Invoke agent (agent will be created internally)
    logger.info(f"🚀 Invoking agent '{agent_name}' synchronously...")
    result = invoke_agent(
        agent_name=agent_name,
        input_state=input_state,
        config=config,  # type: ignore
        enable_tracing=enable_tracing,
        trace_metadata=trace_metadata,
    )

    # Log results
    logger.info(f"✅ SYNC invocation completed for agent: {agent_name}")
    logger.info(f"📊 Messages in result: {len(result.get('messages', []))}")

    if "structured_response" in result:
        logger.info("📦 Structured response received:")
        logger.info(f"   {result['structured_response']}")
    else:
        logger.info("💬 No structured response (text-only agent)")

    # Log the last AI message
    messages = result.get("messages", [])
    logger.info(f"📨 Total messages in final state: {len(messages)}")

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

    if session_id:
        set_conversation_id(session_id)
        logger.info(f"🔑 Using custom session_id: {session_id}")

    logger.info(f"🟢 Starting ASYNC invocation for agent: {agent_name}")
    logger.info(f"📝 User message: {user_message}")

    # Prepare input state
    input_state: dict[str, Any] = {}
    input_state["messages"] = [{"role": "user", "content": user_message}]

    if session_id:
        input_state["session_id"] = session_id
        logger.info(f"🔑 Using custom session_id: {session_id}")

    # Prepare config
    config: dict[str, Any] = {}  # type: ignore[assignment]
    config["configurable"] = {"thread_id": f"async-{agent_name}-example"}

    # Prepare trace metadata
    trace_metadata = TraceMetadata(
        session_id=session_id or TraceMetadata.create().session_id,
        app_name="jarvis-invoke-demo",
        user_id="demo-user",
        tags=["demo", "async", agent_name],
    )

    # Invoke agent asynchronously (agent will be created internally)
    logger.info(f"🚀 Invoking agent '{agent_name}' asynchronously...")
    result = await ainvoke_agent(
        agent_name=agent_name,
        input_state=input_state,
        config=config,  # type: ignore
        enable_tracing=enable_tracing,
        trace_metadata=trace_metadata,
    )

    # Log results
    logger.info(f"✅ ASYNC invocation completed for agent: {agent_name}")
    logger.info(f"📊 Messages in result: {len(result.get('messages', []))}")

    if "structured_response" in result:
        logger.info("📦 Structured response received:")
        logger.info(f"   {result['structured_response']}")
    else:
        logger.info("💬 No structured response (text-only agent)")

    # Log the last AI message
    messages = result.get("messages", [])
    logger.info(f"📨 Total messages in final state: {len(messages)}")
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
