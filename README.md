# Github CLI MCP Server

[![PyPI](https://img.shields.io/pypi/v/gh-cli-mcp-server)](https://pypi.org/project/gh-cli-mcp-server)
[![License](https://img.shields.io/pypi/l/gh-cli-mcp-server)](https://github.com/bpmiranda3099/gh-cli-mcp-server/blob/main/LICENSE)

MCP server that wraps the GitHub CLI (`gh`) into two generic tools — similar to how `aws-api-mcp-server` wraps the AWS CLI.

## Why?

Most GitHub MCP servers expose 25+ individual tools — one per API operation. That's a lot of tools for something the `gh` CLI already handles in a single binary.

`aws-api-mcp-server` solved this for AWS by wrapping the entire AWS CLI into one `call_aws` tool. This project does the same for GitHub — two tools instead of dozens:

- `call_gh` — run any `gh` command
- `suggest_gh_commands` — get help with syntax

No need for a dedicated tool per operation. The `gh` CLI already covers repos, issues, PRs, workflows, releases, and more. This just gives MCP clients a way to execute those commands directly.

## Why not just use `gh` through a shell tool?

You can — it works. This server just cleans things up:

- Parses `gh` output into structured JSON when possible, instead of raw terminal text
- Handles timeouts so commands don't hang forever
- Includes a `suggest_gh_commands` tool for when you're unsure about syntax
- Shows up as a dedicated "github" capability instead of generic shell access

Same `gh` CLI underneath, just a smoother wrapper for MCP clients to work with.

## Tools

- `call_gh` — Execute any `gh` CLI command and get structured output
- `suggest_gh_commands` — Get command suggestions from a natural language query

## Prerequisites

- [GitHub CLI](https://cli.github.com/) installed and authenticated (`gh auth login`)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended, for running with `uvx`)

## Installation

```bash
pip install gh-cli-mcp-server
```

## Usage with MCP clients

```json
{
  "mcpServers": {
    "github": {
      "command": "uvx",
      "args": ["gh-cli-mcp-server"]
    }
  }
}
```

## Examples

Just ask your MCP client naturally — it'll use `call_gh` under the hood:

| You say | What runs |
|---|---|
| "List my repos" | `gh repo list --limit 30` |
| "Show open issues on my project" | `gh issue list --repo owner/repo --state open` |
| "Create a PR from this branch to main" | `gh pr create --title '...' --body '...' --base main` |
| "What workflows does this repo have?" | `gh workflow list --repo owner/repo` |
| "Show me the last 5 CI runs" | `gh run list --repo owner/repo --limit 5` |
| "Who am I logged in as?" | `gh auth status` |

If the client isn't sure which command to use, it can call `suggest_gh_commands` with your prompt to get suggestions first.
