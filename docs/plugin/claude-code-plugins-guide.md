# Claude Code Official Plugins Guide

> Authored: 2026-03-27 | Installation environment: macOS Darwin 25.3.0

## Table of Contents

- [Plugin Management Commands](#plugin-management-commands)
- [Official Plugins (claude-plugins-official)](#official-plugins-claude-plugins-official)
  - [Development Workflow](#development-workflow)
  - [Code Quality](#code-quality)
  - [Plugin / Skill Development](#plugin--skill-development)
  - [LSP (Language Server Protocol)](#lsp-language-server-protocol)
  - [Output Styles](#output-styles)
  - [External Integrations](#external-integrations)
- [Knowledge Work Plugins (knowledge-work-plugins)](#knowledge-work-plugins-knowledge-work-plugins)
  - [Engineering](#engineering)
  - [Product / Project Management](#product--project-management)
  - [Design](#design)
  - [Data Analysis](#data-analysis)
  - [Sales / Marketing](#sales--marketing)
  - [Business Operations](#business-operations)
  - [Legal / Finance / HR](#legal--finance--hr)
  - [Productivity](#productivity)
- [Installation Summary](#installation-summary)

---

## Plugin Management Commands

```bash
# List installed plugins
claude plugins list

# Install a plugin (global)
claude plugin install <plugin-name>@<marketplace> -s user

# Install a plugin (project scope)
claude plugin install <plugin-name>@<marketplace> -s project

# Uninstall a plugin
claude plugin uninstall <plugin-name>@<marketplace>

# Update plugins
claude plugins update
```

### Marketplace List

| Marketplace | Source | Description |
|-------------|--------|-------------|
| `claude-plugins-official` | `anthropics/claude-plugins-official` | Official Anthropic development tools |
| `knowledge-work-plugins` | `anthropics/knowledge-work-plugins` | Anthropic Knowledge Work productivity tools |

---

## Official Plugins (claude-plugins-official)

### Development Workflow

---

#### commit-commands

A bundle of commit/push/PR commands that simplifies Git workflows.

**Install**
```bash
claude plugin install commit-commands@claude-plugins-official -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/commit` | Create a Git commit (analyzes changes and drafts a commit message automatically) |
| `/commit-push-pr` | Commit + push + create PR in one go |
| `/clean_gone` | Bulk clean up local branches whose remote has been deleted |

**Usage examples**
```
/commit                    # Create a commit from current changes
/commit-push-pr            # Commit → push → create PR in one go
/clean_gone                # Clean up stale branches
```

---

#### feature-dev

A systematic development workflow that guides the entire feature lifecycle through 7 stages.

**Install**
```bash
claude plugin install feature-dev@claude-plugins-official -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/feature-dev` | Run the 7-stage feature development workflow |

**7-stage workflow**
1. **Discovery** — clarify requirements
2. **Codebase Exploration** — 2–3 exploration agents analyze the existing codebase in parallel
3. **Clarifying Questions** — questions about ambiguities before design
4. **Architecture Design** — 2–3 design agents propose different architectures + compare trade-offs
5. **Implementation** — implement according to the chosen design
6. **Quality Review** — 3 reviewers check simplicity / bugs / convention
7. **Summary** — document the implementation result

**Dedicated agents**

| Agent | Description |
|-------|-------------|
| `code-explorer` | Deep codebase analysis (execution path tracing, architecture mapping) |
| `code-architect` | Architecture design (file structure, component design, data flow) |
| `code-reviewer` | Reviews bugs, security, quality, convention |

**Usage examples**
```
/feature-dev add user profile editing feature
/feature-dev implement API rate limiting
```

---

#### frontend-design

A design skill that produces production-grade, high-quality frontend UI.

**Install**
```bash
claude plugin install frontend-design@claude-plugins-official -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/frontend-design` | Generate distinctive, polished frontend interfaces |

**Features**
- 20+ aesthetic directions (minimalist, brutalist, art deco, organic, luxury, etc.)
- Custom typography (avoids generic fonts)
- Motion/animation (staggered reveal, scroll-trigger, hover states)
- Asymmetric layout, overlap, diagonal flow
- Background effects (gradient, noise, texture, geometric pattern)
- **Avoids generic AI aesthetics** — produces distinctive designs

**Usage examples**
```
/frontend-design SaaS dashboard landing page
/frontend-design e-commerce product detail page (luxury style)
```

---

#### ralph-loop

A self-referential loop that runs the same prompt repeatedly to incrementally improve quality (Ralph Wiggum technique).

**Install**
```bash
claude plugin install ralph-loop@claude-plugins-official -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/ralph-loop` | Start a Ralph loop (iterative self-improvement) |
| `/cancel-ralph` | Cancel an active Ralph loop |

**How it works**
1. Run a prompt → Claude performs the task
2. A Stop hook intercepts the exit attempt
3. The same prompt feeds back → improve on top of the previous result
4. Terminates upon detecting a completion promise
5. Includes a maximum-iteration safety bound

**Usage examples**
```
/ralph-loop raise coverage of this test file to 95%
/ralph-loop improve this UI component to meet accessibility standards
```

---

### Code Quality

---

#### code-review

An automation tool where 5 specialist agents perform code review on a PR in parallel.

**Install**
```bash
claude plugin install code-review@claude-plugins-official -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/code-review` | Run automated multi-agent code review on a PR |

**Review agents (5 in parallel)**
- CLAUDE.md compliance checkers (2)
- Bug detector
- History analyzer (based on git blame)
- Comment analyzer

**Features**
- Confidence-based scoring (0-100); reports only at threshold 80 or higher
- Automatic false-positive filtering
- Auto-posts review comments to GitHub PR

---

#### pr-review-toolkit

A bundle of 6 specialist review agents that analyze various quality dimensions of a PR.

**Install**
```bash
claude plugin install pr-review-toolkit@claude-plugins-official -s user
```

**Dedicated agents**

| Agent | Analysis area |
|-------|---------------|
| `comment-analyzer` | Code comment accuracy and maintainability |
| `pr-test-analyzer` | Test coverage quality and completeness |
| `silent-failure-hunter` | Error handling and silent failure detection |
| `type-design-analyzer` | Type design quality and immutability verification |
| `code-reviewer` | CLAUDE.md compliance and bug detection |
| `code-simplifier` | Code simplification and refactoring |

---

#### code-simplifier

An agent that automatically improves clarity, consistency, and maintainability of recently modified code.

**Install**
```bash
claude plugin install code-simplifier@claude-plugins-official -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/simplify` | Review and improve reusability, quality, and efficiency of changed code |

**Features**
- Automatically focuses on recently modified code
- Removes duplication, reduces complexity
- Applies project standards (ES modules, React patterns, etc.)
- Preserves functionality 100%

---

#### security-guidance

A hook-based plugin that automatically detects security vulnerabilities and warns when files are edited.

**Install**
```bash
claude plugin install security-guidance@claude-plugins-official -s user
```

**Detection items**
- Command Injection
- XSS (Cross-Site Scripting)
- Unsafe code patterns

**Features**
- Hook-based; auto-triggers on file edits
- Works in the background without a dedicated command

---

### Plugin / Skill Development

---

#### plugin-dev

A comprehensive tool that guides every aspect of Claude Code plugin development.

**Install**
```bash
claude plugin install plugin-dev@claude-plugins-official -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/plugin-structure` | Guide for setting up plugin directory structure |
| `/skill-development` | Skill (SKILL.md) creation and development |
| `/command-development` | Slash command (.md) development |
| `/agent-development` | Subagent (.md) creation and development |
| `/hook-development` | Hook (hooks.json) creation and configuration |
| `/mcp-integration` | MCP server integration setup |
| `/plugin-settings` | Plugin configuration (plugin.json) management |

**Usage examples**
```
/plugin-structure         # Create a new plugin project structure
/skill-development        # Author a new SKILL.md
/agent-development        # Author a subagent definition
```

---

#### skill-creator

Manages the full skill development lifecycle — creation, testing, benchmarking, iterative improvement.

**Install**
```bash
claude plugin install skill-creator@claude-plugins-official -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/skill-creator` | Create a new skill, improve an existing skill, measure performance |

**Workflow**
1. Capture skill intent and interview
2. Explore edge cases
3. Author SKILL.md (including metadata)
4. Generate test cases
5. Run evaluation and benchmarking
6. Quantitative metrics analysis
7. Iterative skill improvement

---

#### mcp-server-dev

A comprehensive skill that guides MCP server design and implementation. Includes deployment models, tool patterns, authentication, etc.

**Install**
```bash
claude plugin install mcp-server-dev@claude-plugins-official -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/build-mcp-server` | MCP server development entry point (use case analysis → deployment model decision → tool pattern selection) |
| `/build-mcp-app` | Develop an MCP app with interactive UI widgets |
| `/build-mcpb` | Develop an MCPB (bundled local server) |

**Supported deployment models**
- Remote HTTP (CloudFlare Workers)
- MCPB (bundled local server)
- Local stdio
- MCP Apps (interactive UI)

**Supported authentication methods**: API Key, OAuth 2.0, CIMD, DCR

---

#### claude-code-setup

An analysis tool that analyzes a codebase and recommends the optimal Claude Code automation.

**Install**
```bash
claude plugin install claude-code-setup@claude-plugins-official -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/claude-automation-recommender` | Analyze codebase and recommend automations (hooks, skills, MCP, agents, plugins) |

**Recommendation categories**
- MCP servers (context7, Playwright, Supabase, GitHub, Slack, etc.)
- Skills (based on available plugins)
- Hooks (automation rules)
- Subagents
- Plugins

---

#### claude-md-management

A tool that audits and improves the quality of CLAUDE.md files.

**Install**
```bash
claude plugin install claude-md-management@claude-plugins-official -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/claude-md-improver` | Audit and improve the CLAUDE.md file |

**Evaluation criteria (6 axes, A–F grade)**
1. Command/workflow specification
2. Architectural clarity
3. Explanation of non-obvious patterns
4. Conciseness
5. Up-to-dateness
6. Actionability

---

#### hookify

A tool that analyzes conversation patterns and creates hooks to prevent unwanted behaviors.

**Install**
```bash
claude plugin install hookify@claude-plugins-official -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/hookify` | Detect behaviors to prevent through conversation analysis and create hooks |
| `/writing-rules` | Guide for writing hook rules |
| `/list` | List configured hook rules |
| `/configure` | Enable/disable hook rules |
| `/help` | Help |

**Supported event types**: `bash`, `file`, `stop`, `prompt`, `all`
**Condition types**: `regex_match`, `contains`, `equals`, `not_contains`, `starts_with`, `ends_with`
**Actions**: `warn`, `block`

---

### LSP (Language Server Protocol)

Language server plugins that enhance code intelligence. Provide code completion, type checking, error detection, etc.

---

#### typescript-lsp

**Install**
```bash
claude plugin install typescript-lsp@claude-plugins-official -s user
```

| Item | Content |
|------|---------|
| Language | TypeScript / JavaScript |
| Features | Code completion, type checking, error detection, refactoring |
| Dedicated command | None (auto-enabled) |

---

#### jdtls-lsp

**Install**
```bash
claude plugin install jdtls-lsp@claude-plugins-official -s user
```

| Item | Content |
|------|---------|
| Language | Java |
| Features | Code completion, error checking, refactoring, dependency analysis |
| Dedicated command | None (auto-enabled) |

---

#### pyright-lsp

**Install**
```bash
claude plugin install pyright-lsp@claude-plugins-official -s user
```

| Item | Content |
|------|---------|
| Language | Python |
| Features | Code completion, type checking, error detection |
| Dedicated command | None (auto-enabled) |

---

### Output Styles

---

#### learning-output-style

An interactive learning mode that requests code contribution from the user at decision points.

**Install**
```bash
claude plugin install learning-output-style@claude-plugins-official -s user
```

**Features**
- Does not write all code automatically; requests user input at key decision points
- Learning-centric workflow
- Applied as an output style without a dedicated command

---

### External Integrations

---

#### context7

An MCP server that fetches the latest official documentation and code examples of libraries/frameworks in real time.

**Install**
```bash
claude plugin install context7@claude-plugins-official -s user
```

**Features**
- Version-specific documentation lookup (React, Express, FastAPI, Django, Prisma, Stripe, AWS SDK, etc.)
- Extracts code examples directly from source repositories
- Auto-used via MCP tools without a dedicated command

---

#### telegram

An MCP server that connects Claude Code to the Telegram messenger. Supports two-way messaging via a bot.

**Install**
```bash
claude plugin install telegram@claude-plugins-official -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/telegram:configure` | Configure the Telegram bot token and channel |
| `/telegram:access` | Manage access control (pairing approval, allowlist, DM/group policy) |

**MCP tools**
- `reply` — send text/file to a Telegram chat (up to 50 MB)
- `react` — add an emoji reaction
- `edit_message` — edit a previous message

**Required environment variables**: `TELEGRAM_BOT_TOKEN`

---

## Knowledge Work Plugins (knowledge-work-plugins)

> All Knowledge Work plugins follow a **Standalone + Supercharged** design.
> They work on manual input alone but are significantly enhanced when external tools are connected via MCP.

### Engineering

---

#### engineering

End-to-end engineering workflow — standups, code review, architecture decisions, incident response, technical documentation.

**Install**
```bash
claude plugin install engineering@knowledge-work-plugins -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/standup` | Generate standup updates from recent activity (commits, PRs, tickets) |
| `/review` | Review code changes (security, performance, style, accuracy) |
| `/debug` | Structured debugging session (reproduce → isolate → diagnose → fix) |
| `/architecture` | Create or evaluate Architecture Decision Records (ADRs) |
| `/incident` | Incident response workflow (triage → communication → mitigation → postmortem) |
| `/deploy-checklist` | Pre-deployment checklist (tests, change review, dependencies, rollback plan) |

**Integratable tools**: GitHub/GitLab, Linear/Jira, Datadog/New Relic, PagerDuty, Slack/Teams, Notion/Confluence

---

### Product / Project Management

---

#### product-management

Covers full product management — feature spec authoring, roadmap management, user research synthesis, competitive analysis.

**Install**
```bash
claude plugin install product-management@knowledge-work-plugins -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/write-spec` | Author a feature spec/PRD from a problem definition |
| `/roadmap-update` | Create, update, re-prioritize roadmaps |
| `/stakeholder-update` | Stakeholder updates (weekly, monthly, launch) |
| `/synthesize-research` | Synthesize user research from interviews, surveys, tickets |
| `/competitive-brief` | Generate competitive analysis brief |
| `/metrics-review` | Review and analyze product metrics |
| `/brainstorm` | Brainstorming partner for product ideas / problem space |

**Integratable tools**: Slack, Linear/Asana/Jira, Notion, Figma, Amplitude/Pendo, Intercom

---

### Design

---

#### design

Design critique, design system management, UX copywriting, accessibility audit, developer handoff, and more.

**Install**
```bash
claude plugin install design@knowledge-work-plugins -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/critique` | Design feedback (usability, visual hierarchy, accessibility, consistency) |
| `/design-system` | Design system audit, documentation, extension |
| `/handoff` | Generate developer handoff specs (measurements, tokens, states, interactions) |
| `/ux-copy` | Author/review UX copy (microcopy, error messages, onboarding) |
| `/accessibility` | Accessibility audit (WCAG 2.1 AA, color contrast, keyboard navigation) |
| `/research-synthesis` | Synthesize user research (interviews, surveys, usability tests) |

**Integratable tools**: Figma, Intercom/Productboard, Linear/Asana/Jira, Notion, Amplitude/Mixpanel

---

### Data Analysis

---

#### data

Covers all data work: SQL authoring, data exploration, visualization, dashboard building, statistical analysis.

**Install**
```bash
claude plugin install data@knowledge-work-plugins -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/analyze` | Answer data questions (from simple lookup to full analysis) |
| `/explore-data` | Dataset profiling (shape, quality, patterns) |
| `/write-query` | Author dialect-optimized SQL (Snowflake, BigQuery, PostgreSQL, etc.) |
| `/create-viz` | Generate publication-grade visualizations in Python (matplotlib, seaborn, plotly) |
| `/build-dashboard` | Build interactive HTML dashboards (Chart.js, filters, tables) |
| `/validate` | Analysis QA — methodology, accuracy, bias check |

**Integratable tools**: Snowflake/BigQuery/Databricks, Amplitude/Looker, Jupyter, Google Sheets

---

#### enterprise-search

Unified search across all connected tools. Search email, chat, documents, and wiki in one place.

**Install**
```bash
claude plugin install enterprise-search@knowledge-work-plugins -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/search` | Unified search across all connected sources |
| `/digest` | Generate daily/weekly activity digest |

**Integratable tools**: Slack/Teams, Gmail/Microsoft 365, Google Drive/OneDrive/Box, Notion/Confluence, Linear/Asana/Jira, HubSpot/Salesforce

---

### Sales / Marketing

---

#### sales

Full sales lifecycle — prospecting, outreach, pipeline management, call prep/wrap-up, forecasting.

**Install**
```bash
claude plugin install sales@knowledge-work-plugins -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/call-summary` | Process call notes/transcripts → extract action items, draft follow-up email |
| `/forecast` | Weighted sales forecast (best/likely/worst scenarios) |
| `/pipeline-review` | Pipeline health analysis, deal prioritization, weekly action plan |
| `/draft-outreach` | Author personalized outreach after prospect research |
| `/call-prep` | Sales call preparation (account context, attendee research, agenda) |
| `/daily-briefing` | Daily sales briefing (meetings, pipeline alerts, email priorities) |
| `/account-research` | Company/people research — sales intelligence |
| `/competitive-intelligence` | Competitor research and battlecard generation |
| `/create-an-asset` | Generate custom sales assets (landing pages, decks, one-pagers) |

**Integratable tools**: HubSpot/Salesforce, Fireflies/Gong, Clay/ZoomInfo, Slack, Gmail

---

#### marketing

Content authoring, campaign planning, brand review, competitive analysis, performance reporting, SEO audit.

**Install**
```bash
claude plugin install marketing@knowledge-work-plugins -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/draft-content` | Author blogs, social media, email, landing pages, press releases, case studies |
| `/campaign-plan` | Generate campaign briefs (objectives, channels, content calendar, success metrics) |
| `/brand-review` | Review content against brand voice / style guide |
| `/competitive-brief` | Competitive positioning and messaging comparison |
| `/performance-report` | Marketing performance report (key metrics, trends, optimization recommendations) |
| `/seo-audit` | SEO audit (keywords, on-page, content gaps, technical checks) |
| `/email-sequence` | Design multi-email sequences (onboarding, nurture, re-engagement) |

**Integratable tools**: Slack, Canva, Figma, HubSpot, Amplitude, Notion, Ahrefs, Klaviyo

---

### Business Operations

---

#### operations

Vendor management, process documentation, change management, capacity planning, compliance tracking.

**Install**
```bash
claude plugin install operations@knowledge-work-plugins -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/vendor-review` | Vendor evaluation (cost analysis, risk assessment, renewal recommendation) |
| `/process-doc` | Document business processes (flowcharts, RACI, SOPs) |
| `/change-request` | Change management request (impact analysis, rollback plan, approval routing) |
| `/capacity-plan` | Resource capacity planning (workload analysis, headcount modeling, utilization projection) |
| `/status-report` | Status report (project updates, KPIs, risks, action items) |
| `/runbook` | Create/update operational runbooks (step-by-step procedures for recurring tasks) |

**Integratable tools**: ServiceNow/Zendesk, Asana/Jira, Notion/Confluence, Slack/Teams

---

#### customer-support

End-to-end CS workflows: ticket triage, customer response, escalation, knowledge-base management.

**Install**
```bash
claude plugin install customer-support@knowledge-work-plugins -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/triage` | Ticket classification, prioritization (P1-P4), routing |
| `/research` | Multi-source research for customer questions |
| `/draft-response` | Author professional customer response messages |
| `/escalate` | Escalation package for engineering/product/leadership |
| `/kb-article` | Author knowledge-base articles from resolved issues |

**Integratable tools**: Slack, Intercom, HubSpot, Guru/Notion, Jira

---

### Legal / Finance / HR

---

#### legal

Contract review, NDA triage, compliance, legal risk assessment, vendor check.

**Install**
```bash
claude plugin install legal@knowledge-work-plugins -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/review-contract` | Contract review (detect deviations from negotiation playbook, generate redlines) |
| `/triage-nda` | Quick NDA triage (GREEN/YELLOW/RED classification) |
| `/vendor-check` | Unified lookup of vendor's existing contract status |
| `/brief` | Generate legal briefings (daily, topic-based, incident) |
| `/respond` | Generate template-based responses to common legal inquiries |

**Integratable tools**: Slack/Teams, Box/Egnyte, Microsoft 365, Jira/Confluence, CLM, CRM

---

#### finance

Journal entries, account reconciliation, financial statements, variance analysis, SOX audit support.

**Install**
```bash
claude plugin install finance@knowledge-work-plugins -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/journal-entry` | Author journal entries (accruals, depreciation, prepayments, payroll, revenue recognition) |
| `/reconciliation` | Account reconciliation (GL↔sub-ledger, bank, third-party data) |
| `/income-statement` | Generate income statement (period comparison, variance analysis) |
| `/variance-analysis` | Variance/movement analysis (price/volume, ratio/mix decomposition, waterfall charts) |
| `/sox-testing` | SOX compliance testing (sample selection, test workpapers, control assessment) |

**Integratable tools**: NetSuite/SAP, Snowflake/BigQuery, Google Sheets/Excel, Tableau/Looker

---

#### human-resources

Recruiting, onboarding, performance review, compensation analysis, policy lookup, people analytics.

**Install**
```bash
claude plugin install human-resources@knowledge-work-plugins -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/draft-offer` | Author offer letters (compensation, start date, terms) |
| `/onboarding` | Generate onboarding checklist and first-week plan |
| `/performance-review` | Structure performance review (self-assessment, manager template, calibration) |
| `/policy-lookup` | Look up and explain company policies (PTO, benefits, expenses, remote work) |
| `/comp-analysis` | Compensation analysis (benchmarking, band placement, equity refresh) |
| `/people-report` | People report (headcount, turnover, diversity, organizational health) |

**Integratable tools**: Workday/BambooHR, Greenhouse/Lever, Pave/Radford, Slack/Teams

---

### Productivity

---

#### productivity

Task management, daily planning, building memory for important work context.

**Install**
```bash
claude plugin install productivity@knowledge-work-plugins -s user
```

**Commands**

| Command | Description |
|---------|-------------|
| `/start` | Initialize tasks + memory, open dashboard |
| `/update` | Triage stale items, check memory gaps, sync external tools |
| `/update --comprehensive` | Deep scan of email/calendar/chat, detect missing TODOs |

**Features**
- **TASKS.md** — markdown-based task tracking
- **2-tier memory** — CLAUDE.md (working memory) + memory/ (long-term storage)
- HTML dashboard (board view)

**Integratable tools**: Slack, Microsoft 365, Notion, Asana/Linear/Jira

---

## Installation Summary

### Per-Marketplace Status

| Marketplace | Installed | Not installed | Total |
|-------------|:---------:|:-------------:|:-----:|
| claude-plugins-official (built-in) | 20 | 12 | 32 |
| claude-plugins-official (external) | 2 | 15 | 17 |
| knowledge-work-plugins | 13 | 2 | 15 |
| **Total** | **35** | **29** | **64** |

### Per-Category Status

| Category | Plugins | Count |
|----------|---------|:-----:|
| Development workflow | commit-commands, feature-dev, frontend-design, ralph-loop | 4 |
| Code quality | code-review, pr-review-toolkit, code-simplifier, security-guidance | 4 |
| Plugin / Skill development | plugin-dev, skill-creator, mcp-server-dev, claude-code-setup, claude-md-management, hookify | 6 |
| LSP | typescript-lsp, jdtls-lsp, pyright-lsp | 3 |
| Output styles | learning-output-style | 1 |
| External integrations | context7, telegram | 2 |
| Engineering | engineering | 1 |
| Product management | product-management | 1 |
| Design | design | 1 |
| Data | data, enterprise-search | 2 |
| Sales / Marketing | sales, marketing | 2 |
| Business operations | operations, customer-support | 2 |
| Legal / Finance / HR | legal, finance, human-resources | 3 |
| Productivity | productivity | 1 |

### Not Installed Plugins (for reference)

**claude-plugins-official built-in (not installed)**
`agent-sdk-dev`, `clangd-lsp`, `csharp-lsp`, `explanatory-output-style`, `gopls-lsp`, `kotlin-lsp`, `lua-lsp`, `math-olympiad`, `php-lsp`, `playground`, `ruby-lsp`, `rust-analyzer-lsp`, `swift-lsp`

**claude-plugins-official external (not installed)**
`asana`, `discord`, `fakechat`, `firebase`, `github`, `gitlab`, `greptile`, `imessage`, `laravel-boost`, `linear`, `playwright`, `serena`, `slack`, `supabase`, `terraform`

**knowledge-work-plugins (not installed)**
`bio-research`, `cowork-plugin-management`
