# ABOUTME: Shared test fixture helpers importable by domain-level conftest.py files.

from collections.abc import Generator


def jarvis_tools_registered() -> Generator[None, None, None]:
    """Register Jarvis tools for testing; reset after use.

    Usage in conftest.py:
        from tests.helpers import jarvis_tools_registered

        @pytest.fixture
        def jarvis_registered():
            yield from jarvis_tools_registered()
    """
    from autobots_devtools_shared_lib.dynagent import AgentMeta
    from autobots_devtools_shared_lib.dynagent.tools.tool_registry import (
        _reset_usecase_tools,
    )

    from autobots_agents_jarvis.domains.jarvis.tools import register_jarvis_tools

    _reset_usecase_tools()
    AgentMeta.reset()
    register_jarvis_tools()
    yield
    _reset_usecase_tools()
    AgentMeta.reset()
