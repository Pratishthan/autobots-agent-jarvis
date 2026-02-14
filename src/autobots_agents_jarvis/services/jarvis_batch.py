# ABOUTME: Jarvis-scoped batch entry point — validates against Jarvis's agent set.
# ABOUTME: Delegates to dynagent's batch_invoker after the Jarvis gate passes.

import logging

from autobots_devtools_shared_lib.common.observability.trace_metadata import TraceMetadata
from autobots_devtools_shared_lib.common.observability.tracing import init_tracing
from autobots_devtools_shared_lib.dynagent import BatchResult, batch_invoker
from dotenv import load_dotenv

from autobots_agents_jarvis.configs.settings import init_jarvis_settings

logger = logging.getLogger(__name__)
load_dotenv()
init_jarvis_settings()

# Application name for tracing and identification
APP_NAME = "jarvis_batch"


def _get_jarvis_batch_agents() -> list[str]:
    """Load batch-enabled agents from agents.yaml."""
    from autobots_devtools_shared_lib.dynagent import get_batch_enabled_agents

    return get_batch_enabled_agents()


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def jarvis_batch(agent_name: str, records: list[str]) -> BatchResult:
    """Run a batch through dynagent, gated to Jarvis batch-enabled agents only.

    Args:
        agent_name: Must be a batch-enabled agent from agents.yaml.
        records:    Non-empty list of plain-string prompts.

    Returns:
        BatchResult forwarded from batch_invoker.

    Raises:
        ValueError: If agent_name is not batch-enabled or records is empty.
    """
    jarvis_agents = _get_jarvis_batch_agents()

    if agent_name not in jarvis_agents:
        raise ValueError(
            f"Agent '{agent_name}' is not enabled for batch processing. "
            f"Valid batch-enabled agents: {', '.join(jarvis_agents)}"
        )

    if not records:
        raise ValueError("records must not be empty")

    # Initialize tracing (one-time singleton)
    init_tracing()

    # Jarvis entry logging
    logger.info(
        "jarvis_batch starting: agent=%s records=%d",
        agent_name,
        len(records),
    )
    trace_metadata = TraceMetadata.create(
        app_name=f"{APP_NAME}-batch_invoker",
        user_id="unknown_user",
        tags=[APP_NAME],
    )

    # Delegate to batch_invoker with Jarvis metadata
    result = batch_invoker(agent_name, records, enable_tracing=True, trace_metadata=trace_metadata)

    # Jarvis exit logging
    logger.info(
        "jarvis_batch complete: agent=%s successes=%d failures=%d",
        agent_name,
        len(result.successes),
        len(result.failures),
    )

    return result


# ---------------------------------------------------------------------------
# Manual smoke runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from autobots_agents_jarvis.tools.jarvis_tools import register_jarvis_tools

    register_jarvis_tools()

    smoke_prompts = [
        "Tell me a programming joke",
        "What's a funny dad joke about coding?",
        "Can you tell a knock-knock joke?",
        "Tell me a joke about debugging",
        "What's your best programming joke?",
        "Tell me a general joke",
        "Give me another programming joke",
        "What's a good dad joke?",
        "Tell me a joke about Python",
        "Can you tell me a funny joke about databases?",
    ]

    batch_result = jarvis_batch("joke_agent", smoke_prompts)
    for record in batch_result.results:
        if record.success:
            print(f"Record {record.index} succeeded:\n{record.output}\n")
        else:
            print(f"Record {record.index} failed:\n{record.error}\n")
