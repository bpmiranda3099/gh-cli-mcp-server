# gh-cli-mcp-server

MCP server that wraps the GitHub CLI (`gh`) into two generic tools — similar to how `aws-api-mcp-server` wraps the AWS CLI.

## Why?

Most GitHub MCP servers expose 25+ individual tools — one per API operation. That's a lot of tools for something the `gh` CLI already handles in a single binary.

`aws-api-mcp-server` solved this for AWS by wrapping the entire AWS CLI into one `call_aws` tool. This project does the same for GitHub — two tools instead of dozens:

- `call_gh` — run any `gh` command
- `suggest_gh_commands` — get help with syntax

No need for a dedicated tool per operation. The `gh` CLI already covers repos, issues, PRs, workflows, releases, and more. This just gives MCP clients a way to execute those commands directly.

## Tools

- `call_gh` — Execute any `gh` CLI command and get structured output
- `suggest_gh_commands` — Get command suggestions from a natural language query

## Prerequisites

- [GitHub CLI](https://cli.github.com/) installed and authenticated (`gh auth login`)

## Installation

```bash
pip install gh-cli-mcp-server
```

## Usage with Kiro / MCP clients

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

```
call_gh("gh repo list --limit 5")
call_gh("gh issue list --repo owner/repo --state open")
call_gh("gh pr create --title 'Fix' --body 'Details' --base main")
call_gh("gh api /repos/owner/repo")
```
