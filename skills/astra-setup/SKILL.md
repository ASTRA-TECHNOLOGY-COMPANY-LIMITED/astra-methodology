---
name: astra-setup
description: "Sets up the ASTRA methodology global development environment (Step 0.0). Configures ~/.claude/settings.json, MCP servers, and required plugins."
argument-hint: "[--reinstall] (optional — re-runs setup even if already configured)"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# ASTRA Step 0.0: Global Development Environment Setup

> **Korean output style**: for Korean user-facing text (HITL questions, status reports, answers), apply `$CLAUDE_PLUGIN_ROOT/docs/development/korean-style.md` — §"HITL 질문 작성 규칙" and §"답변·보고 원칙". Korean files written to disk are style-checked automatically by the korean-style PostToolUse hook.

## Execution Procedure

### Step 1: Check Current Settings

Check the current state of the following files:
- `~/.claude/settings.json` (global settings)
- `~/.claude/.mcp.json` (MCP server settings)

### Step 2: Configure Global Settings

Verify that `~/.claude/settings.json` contains the following settings, and add any missing items:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "permissions": {
    "defaultMode": "bypassPermissions"
  },
  "alwaysThinkingEnabled": true,
  "skipDangerousModePermissionPrompt": true
}
```

**Important**: Merge only the ASTRA required items while preserving existing settings. If there is a conflict with existing values, confirm with the user.

### Step 3: Register MCP Servers

Verify that the following 3 MCP servers are registered in `~/.claude/.mcp.json`.
`chrome-devtools` is the **fallback browser backend** (the default is the
`ego-browser` CLI — see Step 4); register it so browser-driven skills still work
on hosts without ego, and on multi-session setups attach one shared instance via
`--browser-url` instead of launching per session (profile `SingletonLock`).

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["@anthropic-ai/chrome-devtools-mcp@latest"]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/postgres-mcp@latest"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

Skip servers that are already registered and only add the missing ones.

### Step 4: Check Prerequisites

Verify that the following tools are installed:
- Node.js (`node --version`)
- npm/npx (`npx --version`)
- Git (`git --version`)
- GitHub CLI (`gh --version`)
- **ego (lite) browser** (`ego-browser --version`) — *optional, macOS only*

If any required tool is missing, provide installation instructions.

**About ego (lite)**: it is the **default browser backend** for `/test-run`,
`/user-test`, `/manual-generator`, and `/catalog-generator` (isolated Task Space
per agent — no profile lock contention across concurrent sessions — and inherited
login state). It is third-party and never bundled: install it from
[citrolabs/ego-lite](https://github.com/citrolabs/ego-lite), which puts the
`ego-browser` CLI on `PATH`. When it is absent the skills fall back to Chrome MCP
automatically, so this is a recommendation, not a hard requirement. Backend
policy SSoT: `$CLAUDE_PLUGIN_ROOT/docs/development/browser-backend-policy.md`.

### Step 5: Auto-install Required Plugins

Execute the following commands in order to register the marketplace and install required plugins.
Check the result of each command and skip items that are already installed.

```bash
# Register marketplace
claude plugin marketplace add anthropics/claude-plugins-official

# Install required plugins (9)
claude plugin install claude-code-setup@claude-plugins-official
claude plugin install code-review@claude-plugins-official
claude plugin install code-simplifier@claude-plugins-official
claude plugin install commit-commands@claude-plugins-official
claude plugin install feature-dev@claude-plugins-official
claude plugin install frontend-design@claude-plugins-official
claude plugin install hookify@claude-plugins-official
claude plugin install security-guidance@claude-plugins-official
claude plugin install context7@claude-plugins-official
```

### Step 6: Output Setup Results

```
## ASTRA Global Development Environment Setup Results

### Global Settings (~/.claude/settings.json)
- [ ] Agent Teams environment variable: {status}
- [ ] Permission mode (bypassPermissions): {status}
- [ ] Always Thinking: {status}

### Browser backend
- [ ] ego-browser (default, optional): {version or not installed → Chrome MCP fallback}

### MCP Servers (~/.claude/.mcp.json)
- [ ] chrome-devtools (fallback backend): {status}
- [ ] postgres: {status}
- [ ] context7: {status}

### Prerequisites
- [ ] Node.js: {version or not installed}
- [ ] npx: {version or not installed}
- [ ] Git: {version or not installed}
- [ ] GitHub CLI: {version or not installed}

### Plugins (auto-installed)
- [ ] claude-code-setup: {status}
- [ ] code-review: {status}
- [ ] code-simplifier: {status}
- [ ] commit-commands: {status}
- [ ] feature-dev: {status}
- [ ] frontend-design: {status}
- [ ] hookify: {status}
- [ ] security-guidance: {status}
- [ ] context7: {status}
```

## Notes

- Existing configuration files are never overwritten. Always merge.
- Inform the user about the security implications of the `bypassPermissions` setting.
- When installing plugins, skip already installed plugins and display failed items in the results.
