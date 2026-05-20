---
description: Slack 채널에서 백로그 항목을 추출하여 요약합니다
argument-hint: "<channel-name or channel-id> [limit]"
allowed-tools: mcp__fect-slack__slack_list_channels, mcp__fect-slack__slack_get_history, mcp__fect-slack__slack_search_channels, mcp__fect-slack__slack_get_user_info, AskUserQuestion
---

# Slack 백로그 추출

Slack 채널의 메시지를 분석하여 개발 백로그 항목으로 정리합니다.

> 블루프린트와 스프린트까지 생성하려면 `/slack-import` 스킬을 사용하세요.

## 입력

`$ARGUMENTS`에서 파싱:

| 위치 | 의미 | 예시 |
|------|------|------|
| 1번째 | 채널 이름 또는 ID | `project-tasks`, `C01234567890` |
| 2번째 (선택) | 조회할 메시지 수 | `30` (기본값: 20) |

인자가 없으면 `mcp__fect-slack__slack_list_channels`로 채널 목록을 보여주고 `AskUserQuestion`으로 선택을 받는다.

## 분석 절차

1. 채널 ID 확인 (이름이면 `mcp__fect-slack__slack_search_channels`로 검색)
2. `mcp__fect-slack__slack_get_history`로 메시지 조회
3. 각 메시지에서 요구사항/태스크/이슈 성격의 내용 식별
4. 고유 user ID에 대해 `mcp__fect-slack__slack_get_user_info` 조회
5. 중복/유사 항목 병합

## 출력 형식

```
## Slack 백로그 — #{channel-name}

조회 기간: {oldest_msg_date} ~ {latest_msg_date}
분석 메시지: {N}개
추출 항목: {M}개

### 백로그 항목

| # | 기능명 | 설명 | 요청자 | 날짜 | 우선순위 | 메시지 |
|---|--------|------|--------|------|----------|--------|
| 1 | 이메일 인증 | 회원가입 시 이메일 인증 코드 발송/검증 | @kim | 03-06 | High | [원문 첫 30자...] |
| 2 | PG 결제 연동 | 이니시스 PG 카드/계좌이체 처리 | @lee | 03-06 | High | [원문 첫 30자...] |
| 3 | 관리자 대시보드 | 관리자 권한별 대시보드 분리 | @park | 03-06 | Medium | [원문 첫 30자...] |

### 추천 다음 단계
- `/slack-import {channel}` — 선택한 항목으로 청사진 + 스프린트 자동 생성 (대량 일괄)
- `/blueprint {feature-slug}` — 개별 기능 청사진 작성 (데이터 플로우·스키마·로직)
- `/sprint-init {feature-slug}` — 청사진이 준비된 후 스프린트 시작
- `/feature-dev "..."` — sprint worktree 안에서 구현 (HITL은 청사진 Section 10에 따름)
```

## 우선순위 판단 기준

| 신호 | 판단 |
|------|------|
| 리액션 수 3개 이상 또는 :fire: :rotating_light: :exclamation: 리액션 | High |
| 스레드 답글 3개 이상 | High |
| "급한", "긴급", "ASAP", "중요" 등 키워드 | High |
| 스레드 답글 1-2개 | Medium |
| 단순 언급, 아이디어 성격 | Low |
