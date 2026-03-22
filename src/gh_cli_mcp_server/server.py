"""MCP server that wraps the GitHub CLI (gh) into generic tools."""

import asyncio
import json
import shlex
import shutil
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("gh-cli-mcp-server")


def _gh_available() -> bool:
    return shutil.which("gh") is not None


async def _run_gh(command: str, timeout: int = 60) -> dict:
    """Execute a gh CLI command and return structured output."""
    if not _gh_available():
        return {"error": "gh CLI is not installed or not in PATH"}

    if not command.startswith("gh "):
        command = f"gh {command}"

    # Split into args and validate the binary is 'gh'
    try:
        args = shlex.split(command)
    except ValueError as e:
        return {"error": f"Invalid command syntax: {e}"}

    if not args or args[0] != "gh":
        return {"error": "Command must start with 'gh'"}

    # Block shell operators that could sneak through
    dangerous = {";", "&&", "||", "|", "`", "$(", "${", ">", "<", ">>"}
    for arg in args:
        for d in dangerous:
            if d in arg:
                return {"error": f"Blocked: shell operator '{d}' not allowed"}

    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=timeout
        )
    except asyncio.TimeoutError:
        return {"error": f"Command timed out after {timeout}s: {command}"}

    result: dict = {"command": command, "exit_code": proc.returncode}
    out = stdout.decode().strip() if stdout else ""
    err = stderr.decode().strip() if stderr else ""

    if proc.returncode != 0:
        result["error"] = err or "Command failed"
        if out:
            result["output"] = out
        return result

    # Try to parse as JSON for structured output
    try:
        result["output"] = json.loads(out)
    except (json.JSONDecodeError, ValueError):
        result["output"] = out

    if err:
        result["stderr"] = err

    return result


@mcp.tool()
async def call_gh(cli_command: str, timeout: int = 60) -> str:
    """Execute a GitHub CLI (gh) command.

    The command must start with 'gh' and follow gh CLI syntax.
    Examples:
      - gh repo list
      - gh issue list --repo owner/repo --state open
      - gh pr create --title "Fix bug" --body "Description"
      - gh api /repos/owner/repo
      - gh workflow list --repo owner/repo

    Args:
        cli_command: The full gh CLI command to execute.
        timeout: Max seconds to wait for the command (default 60).
    """
    result = await _run_gh(cli_command, timeout)
    return json.dumps(result, indent=2, default=str)




@mcp.tool()
async def suggest_gh_commands(query: str) -> str:
    """Suggest gh CLI commands based on a natural language description.

    Useful when you're unsure about the exact gh command syntax.

    Args:
        query: Natural language description of what you want to do.
    """
    commands_dir = Path(__file__).parent / "commands"
    suggestions: dict[str, list[str]] = {}
    for f in sorted(commands_dir.glob("*.json")):
        suggestions[f.stem] = json.loads(f.read_text())

    q = query.lower()
    matched = []
    for category, cmds in suggestions.items():
        if category in q or any(kw in q for kw in category):
            matched.extend(cmds)

    if not matched:
        matched = [f"# {cat}\n" + "\n".join(cmds) for cat, cmds in suggestions.items()]

    return json.dumps({"query": query, "suggestions": matched}, indent=2)




def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
