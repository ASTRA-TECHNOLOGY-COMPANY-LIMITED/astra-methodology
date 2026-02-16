---
name: astra-global-setup
description: "ASTRA 방법론의 전역 개발환경(Step 0.0)을 설정합니다. ~/.claude/settings.json, MCP 서버, 필수 플러그인을 구성합니다."
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# ASTRA Step 0.0: 전역 개발환경 설정

당신은 ASTRA 방법론의 전역 개발환경 설정 전문가입니다.
개발자 머신에 ASTRA에 필요한 전역 설정을 구성합니다.

## 실행 절차

### 1단계: 현재 설정 확인

다음 파일들의 현재 상태를 확인합니다:
- `~/.claude/settings.json` (전역 설정)
- `~/.claude/.mcp.json` (MCP 서버 설정)

### 2단계: 전역 설정 구성

`~/.claude/settings.json`에 다음 설정이 포함되어 있는지 확인하고, 누락된 항목을 추가합니다:

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

**중요**: 기존 설정을 보존하면서 ASTRA 필수 항목만 병합합니다. 기존 값과 충돌하는 경우 사용자에게 확인합니다.

### 3단계: MCP 서버 등록

`~/.claude/.mcp.json`에 다음 3개 MCP 서버가 등록되어 있는지 확인합니다:

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

이미 등록된 서버는 건너뛰고, 누락된 서버만 추가합니다.

### 4단계: 사전 요구사항 확인

다음 도구가 설치되어 있는지 확인합니다:
- Node.js (`node --version`)
- npm/npx (`npx --version`)
- Git (`git --version`)
- GitHub CLI (`gh --version`)

누락된 도구가 있으면 설치 안내를 제공합니다.

### 5단계: 플러그인 설치 안내

다음 플러그인 설치 명령어를 안내합니다 (직접 실행하지 않음):

```bash
# 공식 마켓플레이스 등록
claude plugins marketplace add claude-plugins-official --github anthropics/claude-plugins-official

# standard-enforcer 마켓플레이스 등록
claude plugins marketplace add standard-enforcer --github zeanxai/standard-enforcer

# 필수 플러그인 설치 (8개)
claude plugins install code-review@claude-plugins-official
claude plugins install commit-commands@claude-plugins-official
claude plugins install feature-dev@claude-plugins-official
claude plugins install frontend-design@claude-plugins-official
claude plugins install hookify@claude-plugins-official
claude plugins install security-guidance@claude-plugins-official
claude plugins install context7@claude-plugins-official
claude plugins install standard-enforcer@standard-enforcer
```

### 6단계: 설정 확인 결과 출력

```
## ASTRA 전역 개발환경 설정 결과

### 전역 설정 (~/.claude/settings.json)
- [ ] Agent Teams 환경변수: {상태}
- [ ] 권한 모드 (bypassPermissions): {상태}
- [ ] Always Thinking: {상태}

### MCP 서버 (~/.claude/.mcp.json)
- [ ] chrome-devtools: {상태}
- [ ] postgres: {상태}
- [ ] context7: {상태}

### 사전 요구사항
- [ ] Node.js: {버전 또는 미설치}
- [ ] npx: {버전 또는 미설치}
- [ ] Git: {버전 또는 미설치}
- [ ] GitHub CLI: {버전 또는 미설치}

### 플러그인 (수동 설치 필요)
- 위 명령어를 터미널에서 실행하세요.
```

## 주의사항

- 기존 설정 파일을 덮어쓰지 않습니다. 항상 병합합니다.
- `bypassPermissions` 설정의 보안 영향을 사용자에게 안내합니다.
- 플러그인 설치는 사용자가 직접 실행하도록 명령어만 안내합니다.
