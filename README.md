# gh-cli-mcp-server

MCP server that wraps the GitHub CLI (`gh`) into two generic tools — similar to how `aws-api-mcp-server` wraps the AWS CLI.

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
