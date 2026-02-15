# ABOUTME: Pydantic settings for application configuration.
# ABOUTME: Extends DynagentSettings with app-level settings (OAuth, app name, port, etc.).

from autobots_devtools_shared_lib.dynagent import DynagentSettings, set_dynagent_settings
from pydantic import Field


class AppSettings(DynagentSettings):
    """Pydantic settings for application configuration.
    Extends DynagentSettings with app-level settings."""

    # GitHub OAuth settings for Chainlit
    oauth_github_client_id: str = Field(default="", description="GitHub OAuth client ID")
    oauth_github_client_secret: str = Field(default="", description="GitHub OAuth client secret")
    chainlit_auth_secret: str = Field(default="", description="Chainlit auth secret")

    # Application settings
    app_name: str = Field(default="", description="Application name")
    port: int = Field(default=2337, description="Application port")
    debug: bool = Field(default=False, description="Enable debug mode")

    def is_oauth_configured(self) -> bool:
        """Check if GitHub OAuth is properly configured."""
        return bool(
            self.oauth_github_client_id
            and self.oauth_github_client_secret
            and self.chainlit_auth_secret
        )


def get_app_settings() -> AppSettings:
    """Get application settings instance."""
    return AppSettings()


def init_app_settings(settings: AppSettings | None = None) -> AppSettings:
    """Initialize app settings and register with shared-lib so dynagent uses this instance.

    Args:
        settings: Optional AppSettings instance or subclass. If None, creates default AppSettings.

    Returns:
        The initialized settings instance.

    Call at app startup.
    """
    s = settings if settings is not None else get_app_settings()
    set_dynagent_settings(s)
    return s
