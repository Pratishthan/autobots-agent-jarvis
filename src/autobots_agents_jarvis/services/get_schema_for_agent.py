# ABOUT ME: Toy function to show how schema json can be retrieved for an agent.

from autobots_devtools_shared_lib.common.observability.logging_utils import get_logger
from autobots_devtools_shared_lib.dynagent import AgentMeta
from dotenv import load_dotenv

from autobots_agents_jarvis.tools.jarvis_tools import register_jarvis_tools

logger = get_logger(__name__)
load_dotenv()


register_jarvis_tools()


def get_schema_for_agent(agent_name: str) -> str:
    """
    Get the schema for a given agent.

    Args:
        agent_name (str): The name of the agent.
    Returns:
        dict: The schema for the agent.
    """
    meta = AgentMeta.instance()
    schema = meta.schema_map.get(agent_name)

    if schema is None:
        return f"Error: no output schema configured for agent '{agent_name}'"

    logger.info(f"convert_format: agent={agent_name}, schema={schema}")

    return str(schema)


if __name__ == "__main__":
    # Example usage
    agent_name = "joke_agent"
    schema = get_schema_for_agent(agent_name)
    print(f"Schema for agent '{agent_name}': {schema}")
