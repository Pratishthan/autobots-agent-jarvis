# ABOUTME: Common validation tools — shared utilities for data validation across all domains.
# ABOUTME: Can be used by any domain agent (customer support, sales, jarvis, etc.).

import re
from urllib.parse import urlparse

from langchain.tools import tool


@tool
def validate_email(email: str) -> str:
    """Validate email address format.

    This tool can be used by any agent across all domains to validate email addresses.

    Args:
        email: Email address to validate

    Returns:
        Validation result message indicating if email is valid or not
    """
    # Basic email validation regex
    # Matches: user@domain.tld
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if re.match(pattern, email):
        return f"✅ Valid email address: {email}"
    return f"❌ Invalid email address: {email}. Please provide a valid email format (e.g., user@example.com)"


@tool
def validate_phone(phone: str) -> str:
    """Validate phone number format.

    This tool can be used by any agent across all domains to validate phone numbers.
    Accepts various formats: (123) 456-7890, 123-456-7890, 1234567890, +1-123-456-7890

    Args:
        phone: Phone number to validate

    Returns:
        Validation result message indicating if phone number is valid or not
    """
    # Remove common separators and whitespace
    cleaned = re.sub(r"[\s\-\(\)\+\.]", "", phone)

    # Check if we have 10-15 digits (allowing for country codes)
    if re.match(r"^\d{10,15}$", cleaned):
        return f"✅ Valid phone number: {phone} (normalized: {cleaned})"
    return (
        f"❌ Invalid phone number: {phone}. "
        f"Please provide a valid phone number (e.g., 123-456-7890 or +1-123-456-7890)"
    )


@tool
def validate_url(url: str) -> str:
    """Validate URL format.

    This tool can be used by any agent across all domains to validate URLs.
    Checks for proper URL structure including scheme and domain.

    Args:
        url: URL to validate

    Returns:
        Validation result message indicating if URL is valid or not
    """
    try:
        result = urlparse(url)
        # Check if URL has scheme (http/https) and netloc (domain)
        if all([result.scheme, result.netloc]):
            # Ensure scheme is http or https
            if result.scheme in ["http", "https"]:
                return f"✅ Valid URL: {url}"
            return f"⚠️  URL has non-standard scheme: {result.scheme}. Expected http or https."
        else:  # noqa: RET505
            return (
                f"❌ Invalid URL: {url}. "
                f"Please provide a complete URL with protocol (e.g., https://example.com)"
            )
    except Exception as e:
        return f"❌ Invalid URL: {url}. Error: {e!s}"


# --- Registration entry-point (called by domains that want to use validation tools) ---


def register_validation_tools() -> None:
    """Register common validation tools into the dynagent usecase pool.

    Any domain can call this to make validation tools available to their agents.
    """
    from autobots_devtools_shared_lib.dynagent import register_usecase_tools

    register_usecase_tools(
        [
            validate_email,
            validate_phone,
            validate_url,
        ]
    )
