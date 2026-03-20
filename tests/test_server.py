"""Tests for gh-cli-mcp-server."""

import json
import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock

from gh_cli_mcp_server.server import call_gh, suggest_gh_commands, _gh_available, _run_gh


@pytest.mark.asyncio
async def test_call_gh_prepends_gh():
    """Commands without 'gh ' prefix get it added."""
    with patch("gh_cli_mcp_server.server._run_gh", new_callable=AsyncMock) as mock:
        mock.return_value = {"command": "gh repo list", "exit_code": 0, "output": ""}
        await call_gh("repo list")
        mock.assert_called_once_with("repo list", 60)


@pytest.mark.asyncio
async def test_call_gh_returns_json_string():
    """call_gh returns a JSON-serialized string."""
    with patch("gh_cli_mcp_server.server._run_gh", new_callable=AsyncMock) as mock:
        mock.return_value = {"command": "gh repo list", "exit_code": 0, "output": "stuff"}
        result = await call_gh("gh repo list")
        parsed = json.loads(result)
        assert parsed["exit_code"] == 0
        assert parsed["output"] == "stuff"


@pytest.mark.asyncio
async def test_run_gh_no_cli():
    """Returns error when gh is not installed."""
    with patch("gh_cli_mcp_server.server._gh_available", return_value=False):
        result = await _run_gh("gh repo list")
        assert "error" in result
        assert "not installed" in result["error"]


@pytest.mark.asyncio
async def test_run_gh_success():
    """Successful command returns parsed JSON output."""
    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate.return_value = (b'{"login":"testuser"}', b"")

    with patch("gh_cli_mcp_server.server._gh_available", return_value=True), \
         patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        result = await _run_gh("gh api /user")
        assert result["exit_code"] == 0
        assert result["output"] == {"login": "testuser"}


@pytest.mark.asyncio
async def test_run_gh_plain_text_output():
    """Non-JSON output is returned as plain string."""
    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate.return_value = (b"some plain text", b"")

    with patch("gh_cli_mcp_server.server._gh_available", return_value=True), \
         patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        result = await _run_gh("gh repo list")
        assert result["output"] == "some plain text"


@pytest.mark.asyncio
async def test_run_gh_command_failure():
    """Failed command includes error message."""
    mock_proc = AsyncMock()
    mock_proc.returncode = 1
    mock_proc.communicate.return_value = (b"", b"not found")

    with patch("gh_cli_mcp_server.server._gh_available", return_value=True), \
         patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        result = await _run_gh("gh repo view nonexistent")
        assert result["exit_code"] == 1
        assert "not found" in result["error"]


@pytest.mark.asyncio
async def test_suggest_gh_commands_repos():
    """Suggests repo commands for repo-related queries."""
    result = await suggest_gh_commands("list my repos")
    parsed = json.loads(result)
    assert any("repo" in s for s in parsed["suggestions"])


@pytest.mark.asyncio
async def test_suggest_gh_commands_fallback():
    """Returns all categories when no match found."""
    result = await suggest_gh_commands("xyzzy nonsense")
    parsed = json.loads(result)
    assert len(parsed["suggestions"]) > 5  # all categories returned


def test_gh_available():
    """_gh_available returns bool based on shutil.which."""
    with patch("shutil.which", return_value="/usr/local/bin/gh"):
        assert _gh_available() is True
    with patch("shutil.which", return_value=None):
        assert _gh_available() is False


@pytest.mark.asyncio
async def test_run_gh_blocks_shell_injection():
    """Shell operators are blocked."""
    with patch("gh_cli_mcp_server.server._gh_available", return_value=True):
        result = await _run_gh("gh repo list; rm -rf /")
        assert "error" in result
        assert "shell operator" in result["error"]


@pytest.mark.asyncio
async def test_run_gh_blocks_pipe():
    """Pipe operator is blocked."""
    with patch("gh_cli_mcp_server.server._gh_available", return_value=True):
        result = await _run_gh("gh repo list | cat")
        assert "error" in result
        assert "shell operator" in result["error"]


@pytest.mark.asyncio
async def test_run_gh_blocks_command_substitution():
    """Command substitution is blocked."""
    with patch("gh_cli_mcp_server.server._gh_available", return_value=True):
        result = await _run_gh("gh repo list $(whoami)")
        assert "error" in result
        assert "shell operator" in result["error"]
