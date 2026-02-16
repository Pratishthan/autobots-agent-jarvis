# ABOUTME: Sanity tests for Dynagent canary - validates all Dynagent APIs via Concierge.

import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest
import yaml
from langchain_core.messages import AIMessage

from autobots_agents_jarvis.domains.concierge.call_invoke_agent import (
    call_invoke_agent_async,
    call_invoke_agent_sync,
)
from autobots_agents_jarvis.domains.concierge.concierge_batch import concierge_batch
from autobots_agents_jarvis.domains.concierge.get_schema_for_agent import get_schema_for_agent
from tests.conftest import requires_google_api

# Pytest marker for sanity tests
pytestmark = [pytest.mark.sanity, requires_google_api]

CHAINLIT_PORT = 2338
HEADLESS = True


@pytest.fixture(autouse=True)
def setup_concierge(concierge_registered):
    """Ensure Concierge tools are registered before each test."""
    pass


# ---------------------------------------------------------------------------
# Invoke (sync)
# ---------------------------------------------------------------------------


def test_invoke_sync(concierge_registered):
    """Sanity: invoke_agent (sync) via call_invoke_agent_sync."""
    result = call_invoke_agent_sync(
        agent_name="joke_agent",
        user_message="Tell me a short joke",
        enable_tracing=False,
    )
    assert "messages" in result
    assert len(result["messages"]) > 1
    ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
    assert len(ai_messages) > 0


# ---------------------------------------------------------------------------
# Invoke (async)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_invoke_async(concierge_registered):
    """Sanity: ainvoke_agent via call_invoke_agent_async."""
    result = await call_invoke_agent_async(
        agent_name="joke_agent",
        user_message="Tell me a short joke",
        enable_tracing=False,
    )
    assert "messages" in result
    assert len(result["messages"]) > 1
    ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
    assert len(ai_messages) > 0


# ---------------------------------------------------------------------------
# Batch
# ---------------------------------------------------------------------------


def test_batch(concierge_registered):
    """Sanity: batch_invoker via concierge_batch."""
    result = concierge_batch("joke_agent", ["Tell me a joke"], user_id="test_user")
    assert result.total == 1
    assert len(result.results) == 1
    assert result.results[0].success
    assert result.results[0].output is not None
    assert len(result.results[0].output) > 0


# ---------------------------------------------------------------------------
# Get schema
# ---------------------------------------------------------------------------


def test_get_schema(concierge_registered):
    """Sanity: get_schema_for_agent (AgentMeta.schema_map)."""
    schema = get_schema_for_agent("joke_agent")
    assert isinstance(schema, str)
    assert len(schema) > 0
    assert not schema.startswith("Error:")


# ---------------------------------------------------------------------------
# UI (Playwright + predefined script)
# ---------------------------------------------------------------------------


def _start_chainlit_no_auth(concierge_dir: Path, port: int = 2337) -> subprocess.Popen:
    """Start Chainlit with OAuth disabled for sanity test."""
    env = os.environ.copy()
    env["OAUTH_GITHUB_CLIENT_ID"] = ""
    env["OAUTH_GITHUB_CLIENT_SECRET"] = ""
    env["CHAINLIT_AUTH_SECRET"] = ""
    env["DYNAGENT_CONFIG_ROOT_DIR"] = str(concierge_dir / "agent_configs" / "concierge")
    app_path = (
        concierge_dir / "src" / "autobots_agents_jarvis" / "domains" / "concierge" / "server.py"
    )
    return subprocess.Popen(  # noqa: S603
        [
            sys.executable,
            "-m",
            "chainlit",
            "run",
            str(app_path),
            "--port",
            str(port),
            "--host",
            "127.0.0.1",
            "--headless",
        ],
        env=env,
        cwd=str(concierge_dir),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _wait_for_chainlit(port: int, timeout: float = 30.0) -> bool:
    """Wait for Chainlit to be ready."""
    url = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:  # noqa: S310
                if resp.status in (200, 302):
                    return True
        except (OSError, TimeoutError):
            time.sleep(0.5)
    return False


def test_ui_chat_script(concierge_registered):
    """Sanity: stream_agent_events via Chainlit UI + Playwright + predefined script."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip(
            "playwright not installed; run: pip install playwright && playwright install chromium"
        )

    concierge_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
    script_path = Path(__file__).resolve().parent / "fixtures" / "chat_script.yaml"
    with script_path.open() as f:
        script = yaml.safe_load(f)
    messages = script.get("messages", [])

    proc = _start_chainlit_no_auth(concierge_dir, port=CHAINLIT_PORT)
    try:
        if not _wait_for_chainlit(CHAINLIT_PORT):
            pytest.fail("Chainlit did not become ready in time")

        with sync_playwright() as p:
            # Force Chromium headless - unset PWDEBUG so VS Code debug doesn't open headed browser
            pwdebug = os.environ.pop("PWDEBUG", None)
            try:
                browser = p.chromium.launch(headless=HEADLESS)
            finally:
                if pwdebug is not None:
                    os.environ["PWDEBUG"] = pwdebug
            try:
                page = browser.new_page()
                page.set_default_timeout(45000)
                page.goto(f"http://127.0.0.1:{CHAINLIT_PORT}", wait_until="networkidle")
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(2000)

                for item in messages:
                    user_msg = item.get("user", "")
                    assert_contains = item.get("assert_contains", [])
                    if not user_msg:
                        continue

                    textbox = page.locator('[role="textbox"], textarea').first
                    textbox.wait_for(state="visible", timeout=15000)
                    textbox.fill(user_msg)
                    textbox.press("Enter")

                    page.wait_for_timeout(5000)
                    if assert_contains:
                        content = page.content().lower()
                        for substr in assert_contains:
                            assert substr.lower() in content, (
                                f"Expected '{substr}' in response for message '{user_msg}'"
                            )
            finally:
                browser.close()
    finally:
        proc.terminate()
        proc.wait(timeout=5)
