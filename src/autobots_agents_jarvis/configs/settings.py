# ABOUTME: Pydantic settings for jarvis-chat configuration.
# ABOUTME: Extends DynagentSettings with Jarvis-specific API keys, OAuth, and app settings.

from autobots_devtools_shared_lib.dynagent import DynagentSettings, set_dynagent_settings
from pydantic import Field


class JarvisSettings(DynagentSettings):
    """Jarvis application settings: Dynagent base + Jarvis-specific env vars."""

    # GitHub OAuth settings for Chainlit
    oauth_github_client_id: str = Field(default="", description="GitHub OAuth client ID")
    oauth_github_client_secret: str = Field(default="", description="GitHub OAuth client secret")
    chainlit_auth_secret: str = Field(default="", description="Chainlit auth secret")

    # Application settings
    app_name: str = Field(default="jarvis", description="Application name")
    port: int = Field(default=1337, description="Application port")
    debug: bool = Field(default=False, description="Enable debug mode")

    def is_oauth_configured(self) -> bool:
        """Check if GitHub OAuth is properly configured."""
        return bool(
            self.oauth_github_client_id
            and self.oauth_github_client_secret
            and self.chainlit_auth_secret
        )


def get_jarvis_settings() -> JarvisSettings:
    """Get Jarvis settings instance."""
    return JarvisSettings()


def init_jarvis_settings() -> JarvisSettings:
    """Load Jarvis settings and register them with the shared-lib so dynagent uses this instance. Call at app startup."""
    s = get_jarvis_settings()
    set_dynagent_settings(s)
    return s
