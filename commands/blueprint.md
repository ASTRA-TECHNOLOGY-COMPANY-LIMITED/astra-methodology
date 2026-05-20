---
description: 청사진(설계 문서)을 데이터 플로우·스키마·로직 설계 중심으로 작성합니다 (구현 코드 제외)
argument-hint: "[feature-slug-or-blueprint-path] [--auto] [--from-planner=<planner-dir>]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Skill, Task, TodoWrite
---

# /blueprint — 청사진 작성 슬래시 커맨드

`Skill('blueprint', '$ARGUMENTS')`를 호출하여 청사진을 작성합니다.

## 사용 예시

```
/blueprint user-auth
/blueprint user-auth --from-planner=docs/planner/003-user-auth
/blueprint user-auth --auto                       # HITL 없이 자동 진행 (autorun 호환)
/blueprint docs/blueprints/003-user-auth/blueprint.md   # 기존 청사진 갱신
```

## 동작 요약

| 단계 | 내용 |
|------|------|
| 1 | `$ARGUMENTS` 파싱 (slug / `--auto` / `--from-planner`) |
| 2 | `docs/planner/{NNN}-{slug}/` 산출물 자동 로드 (있는 경우) |
| 3 | 10개 표준 섹션 자동 초안 작성 (개요 / 기능 명세 / 데이터 모델 / API 계약 / 시퀀스 / 로직 의사코드 / 에러 정책 / 비기능 / 테스트 전략 / **HITL Triggers**) |
| 4 | 핵심 설계 결정 1-3개만 HITL (`--auto` 시 스킵) — PK 전략, 트랜잭션 경계, 외부 호출 동기성 |
| 5 | `data-standard` 자동 스킬로 TB_/`_YMD`·금칙어 검증 (자동 발동) |
| 6 | `blueprint-reviewer` 에이전트로 품질 검증 |

## 출력

- `docs/blueprints/{NNN}-{feature-slug}/blueprint.md` — 청사진 본문 (10개 섹션)
- `docs/blueprints/{NNN}-{feature-slug}/review.md` — blueprint-reviewer 보고서

## /feature-dev와의 관계

청사진의 **Section 10 (HITL Triggers)**는 이후 `/feature-dev`가 구현 단계에서 그대로 따라 *꼭 필요한 결정*에서만 사용자에게 묻도록 합니다. 청사진이 단일 진실 원천(SoT)이므로, prompt-map.md에서 `/feature-dev` 호출 시 청사진 경로만 전달하면 HITL 가드가 자동 발동됩니다.

자세한 단계는 `skills/blueprint/SKILL.md` 참조.
