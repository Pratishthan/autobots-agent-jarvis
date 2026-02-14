# ABOUTME: Unit tests for common validation tools.

from autobots_agents_jarvis.common.tools.validation_tools import (
    validate_email,
    validate_phone,
    validate_url,
)


def test_validate_email_valid():
    """Test validate_email with valid email addresses."""
    # Test using the tool's underlying function
    result = validate_email.func("user@example.com")
    assert "✅ Valid email" in result
    assert "user@example.com" in result


def test_validate_email_invalid():
    """Test validate_email with invalid email addresses."""
    result = validate_email.func("not-an-email")
    assert "❌ Invalid email" in result


def test_validate_phone_valid():
    """Test validate_phone with valid phone numbers."""
    # Test various formats
    test_cases = [
        "1234567890",
        "123-456-7890",
        "(123) 456-7890",
        "+1-123-456-7890",
    ]

    for phone in test_cases:
        result = validate_phone.func(phone)
        assert "✅ Valid phone" in result


def test_validate_phone_invalid():
    """Test validate_phone with invalid phone numbers."""
    result = validate_phone.func("123")  # Too short
    assert "❌ Invalid phone" in result


def test_validate_url_valid():
    """Test validate_url with valid URLs."""
    test_cases = [
        "https://example.com",
        "http://example.com",
        "https://example.com/path?query=value",
    ]

    for url in test_cases:
        result = validate_url.func(url)
        assert "✅ Valid URL" in result


def test_validate_url_invalid():
    """Test validate_url with invalid URLs."""
    test_cases = [
        "not-a-url",
        "example.com",  # Missing protocol
        "ftp://example.com",  # Non-standard protocol
    ]

    for url in test_cases:
        result = validate_url.func(url)
        assert "❌ Invalid" in result or "⚠️" in result
