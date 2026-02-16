---
name: astra-setup
description: "Sets up the ASTRA methodology global development environment (Step 0.0). Configures ~/.claude/settings.json, MCP servers, and required plugins."
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# ASTRA Step 0.0: Global Development Environment Setup

You are an expert in setting up the ASTRA methodology global development environment.
You configure the global settings required for ASTRA on the developer's machine.

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

Verify that the following 3 MCP servers are registered in `~/.claude/.mcp.json`:

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

If any tools are missing, provide installation instructions.

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

### MCP Servers (~/.claude/.mcp.json)
- [ ] chrome-devtools: {status}
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
