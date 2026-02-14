# ABOUTME: Pytest fixtures and configuration for jarvis-chat tests.
# ABOUTME: Provides shared fixtures for settings and test utilities.

import os
from collections.abc import Generator
from pathlib import Path

import pytest

from autobots_agents_jarvis.configs.settings import JarvisSettings

_JARVIS_CONFIG_CANDIDATES = [
    Path("agent_configs/jarvis"),
    Path("autobots-agents-jarvis/agent_configs/jarvis"),
    Path("../autobots-agents-jarvis/agent_configs/jarvis"),
    Path(__file__).parent.parent / "agent_configs" / "jarvis",
]
_JARVIS_CONFIG_DIR: Path | None = None
for _c in _JARVIS_CONFIG_CANDIDATES:
    if (_c / "agents.yaml").exists():
        _JARVIS_CONFIG_DIR = _c
        break


def has_real_google_key() -> bool:
    """Check if a real Google API key is available."""
    key = os.environ.get("GOOGLE_API_KEY", "")
    return len(key) > 20


requires_google_api = pytest.mark.skipif(
    not has_real_google_key(),
    reason="Requires real GOOGLE_API_KEY environment variable",
)


@pytest.fixture(autouse=True)
def _dynagent_env(monkeypatch):
    """Reset agent-config cache and point env vars at the real jarvis config."""
    from autobots_devtools_shared_lib.dynagent.agents.agent_config_utils import (
        _reset_agent_config,
    )

    _reset_agent_config()
    # Reset the cached settings instance so it will re-read env vars on next access
    import autobots_devtools_shared_lib.dynagent.config.dynagent_settings as settings_module

    settings_module._settings = None

    if _JARVIS_CONFIG_DIR is not None:
        monkeypatch.setenv("DYNAGENT_CONFIG_ROOT_DIR", str(_JARVIS_CONFIG_DIR))
        monkeypatch.setenv("SCHEMA_BASE", str(_JARVIS_CONFIG_DIR / "schemas"))
    yield
    _reset_agent_config()
    # Reset settings after test
    settings_module._settings = None


@pytest.fixture
def test_settings() -> JarvisSettings:
    """Create settings for testing with minimal configuration."""
    return JarvisSettings(
        google_api_key=os.environ.get("GOOGLE_API_KEY", "test-google-key"),
        langfuse_enabled=False,
        langfuse_public_key="",
        langfuse_secret_key="",
        oauth_github_client_id="",
        oauth_github_client_secret="",
        chainlit_auth_secret="",
        debug=True,
    )


@pytest.fixture
def langfuse_settings() -> JarvisSettings:
    """Create settings with Langfuse configuration."""
    return JarvisSettings(
        google_api_key=os.environ.get("GOOGLE_API_KEY", "test-google-key"),
        langfuse_enabled=True,
        langfuse_public_key="test-public-key",
        langfuse_secret_key="test-secret-key",
        langfuse_host="https://test.langfuse.com",
        debug=True,
    )


@pytest.fixture
def oauth_settings() -> JarvisSettings:
    """Create settings with OAuth configuration."""
    return JarvisSettings(
        google_api_key=os.environ.get("GOOGLE_API_KEY", "test-google-key"),
        langfuse_enabled=False,
        oauth_github_client_id="test-client-id",
        oauth_github_client_secret="test-client-secret",
        chainlit_auth_secret="test-auth-secret",
        debug=True,
    )


@pytest.fixture
def clean_env() -> Generator[None, None, None]:
    """Temporarily clear environment variables for testing."""
    env_vars = [
        "GOOGLE_API_KEY",
        "LANGFUSE_PUBLIC_KEY",
        "LANGFUSE_SECRET_KEY",
        "LANGFUSE_HOST",
        "LANGFUSE_ENABLED",
        "OAUTH_GITHUB_CLIENT_ID",
        "OAUTH_GITHUB_CLIENT_SECRET",
        "CHAINLIT_AUTH_SECRET",
        "PORT",
        "DEBUG",
    ]

    old_values = {var: os.environ.get(var) for var in env_vars}

    for var in env_vars:
        os.environ.pop(var, None)

    yield

    for var, value in old_values.items():
        if value is not None:
            os.environ[var] = value
        else:
            os.environ.pop(var, None)
