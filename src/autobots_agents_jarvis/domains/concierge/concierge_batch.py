# ABOUTME: Concierge-scoped batch entry point — validates against Concierge's agent set.
# ABOUTME: Delegates to dynagent's batch_invoker after the Concierge gate passes.

import uuid

from autobots_devtools_shared_lib.common.observability import (
    TraceMetadata,
    get_logger,
    init_tracing,
    set_conversation_id,
)
from autobots_devtools_shared_lib.dynagent import BatchResult, batch_invoker
from dotenv import load_dotenv

from autobots_agents_jarvis.domains.concierge.settings import init_concierge_settings

logger = get_logger(__name__)
load_dotenv()
init_concierge_settings()

# Application name for tracing and identification
APP_NAME = "concierge_batch"


def _get_concierge_batch_agents() -> list[str]:
    """Load batch-enabled agents from agents.yaml."""
    from autobots_devtools_shared_lib.dynagent import get_batch_enabled_agents

    return get_batch_enabled_agents()


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def concierge_batch(agent_name: str, records: list[str]) -> BatchResult:
    """Run a batch through dynagent, gated to Concierge batch-enabled agents only.

    Args:
        agent_name: Must be a batch-enabled agent from agents.yaml.
        records:    Non-empty list of plain-string prompts.

    Returns:
        BatchResult forwarded from batch_invoker.

    Raises:
        ValueError: If agent_name is not batch-enabled or records is empty.
    """
    set_conversation_id(str(uuid.uuid4()))
    logger.info(f"concierge_batch starting: agent={agent_name} records={len(records)}")

    concierge_agents = _get_concierge_batch_agents()

    if agent_name not in concierge_agents:
        raise ValueError(
            f"Agent '{agent_name}' is not enabled for batch processing. "
            f"Valid batch-enabled agents: {', '.join(concierge_agents)}"
        )

    if not records:
        raise ValueError("records must not be empty")

    init_tracing()

    # Concierge entry logging
    trace_metadata = TraceMetadata.create(
        app_name=f"{APP_NAME}-batch_invoker",
        user_id="BATCH_USER",
        tags=[APP_NAME, agent_name, "batch"],
    )
    set_conversation_id(agent_name)

    # Delegate to batch_invoker with Concierge metadata
    result = batch_invoker(agent_name, records, enable_tracing=True, trace_metadata=trace_metadata)

    # Concierge exit logging
    logger.info(
        f"concierge_batch complete: agent={agent_name} successes={len(result.successes)} "
        f"failures={len(result.failures)}"
    )

    return result


# ---------------------------------------------------------------------------
# Manual smoke runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from autobots_agents_jarvis.domains.concierge.tools import register_concierge_tools

    register_concierge_tools()

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

    batch_result = concierge_batch("joke_agent", smoke_prompts)
    for record in batch_result.results:
        if record.success:
            print(f"Record {record.index} succeeded:\n{record.output}\n")
        else:
            print(f"Record {record.index} failed:\n{record.error}\n")
