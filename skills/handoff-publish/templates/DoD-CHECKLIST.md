# Definition of Done — 단계별 완료 조건

**기능**: {{FEATURE_NAME}}
**최종 수정**: {{TODAY}}

> 각 역할이 "다 했다"고 말하기 전에 충족해야 할 조건 (PDF §19).
> 체크는 **본인이 직접** 하고, 증빙은 PR 설명 / Figma 링크 / Loom / 테스트 리포트 등으로 남깁니다.

---

## 19.1 UX 단계 DoD

- [ ] Screen Registry (`1-screen-registry.md`) 등록 완료
- [ ] State Matrix (`3-state-matrix.md`) 작성 완료
- [ ] Permission Matrix (`3-state-matrix.md`의 권한 섹션) 작성 완료
- [ ] Business Rules (`7-business-rules.md`) 작성 완료 (모든 Registry ID 대응)
- [ ] Edge Cases (`4-edge-cases.md`) 정리 완료
- [ ] Component Specs (`6-component-specs.md`) 정의 완료 (신규 컴포넌트 시)
- [ ] Decision Log (`11-decision-log.md`) 갱신 (변경 발생 시)
- [ ] Loom 워크스루 녹화 (5-10분) → `walkthrough.loom.md`에 링크 기재

---

## 19.2 UI 디자이너 단계 DoD

- [ ] 모든 Registry ID에 Figma 프레임 생성 (프레임명 = ID)
- [ ] 모든 상태 (LOADING / EMPTY / DEFAULT / ERROR) 디자인
- [ ] 권한별 UI 차이 반영 (해당 화면)
- [ ] Mobile / Tablet 분기점 디자인
- [ ] 색상 대비 검증 (WCAG AA)
  - 본문 텍스트 4.5:1 / 큰 글자 3:1
- [ ] Focus state 디자인
- [ ] Edge Cases 모두 반영
- [ ] 디자인 시스템 토큰만 사용 (커스텀 색상/간격 ❌)

---

## 19.3 개발자 단계 DoD

- [ ] 모든 ID 컴포넌트 구현 + `// @feature: {SCREEN-ID}` 주석
- [ ] 모든 상태 분기 처리 (`isLoading` / `isEmpty` / `isError`)
- [ ] i18n 3개국어(ko/en/vi) 모두 등록 (키 누락 시 빌드 실패)
- [ ] 키보드 / Focus / ARIA 동작 검증
- [ ] Lighthouse 90점 이상 (모바일)
- [ ] 디자인 시스템 클래스만 사용 (inline 스타일 최소화)
- [ ] `npm run lint` / `npx tsc --noEmit` 통과

---

## 19.4 QA 단계 DoD

- [ ] 모든 ID × 상태 × 권한 검증
- [ ] 디바이스 매트릭스 검증 (Chrome/Safari × Desktop/Tablet/Mobile)
- [ ] 다국어 3개 모두 검증 (베트남어 길이 잘림 체크)
- [ ] 접근성 검증 (키보드 / 스크린 리더 샘플링)
- [ ] 회귀 테스트 통과

---

## 검증 명령어 (개발자 — 자동화 가능 항목)

개발자 DoD 중 자동 검증 가능한 항목:

```bash
# Lint / TypeCheck
npm run lint
npx tsc --noEmit

# Lighthouse (Chrome headless)
npx lighthouse https://localhost:3000/{{FEATURE_ROUTE}} \
  --only-categories=performance,accessibility \
  --emulated-form-factor=mobile \
  --throttling-method=devtools

# i18n 키 누락 검증 (프로젝트의 i18n 라이브러리 lint 룰 활용)
npm run i18n:lint

# 색상 대비 검증 (axe-core CLI)
npx @axe-core/cli https://localhost:3000/{{FEATURE_ROUTE}} \
  --tags wcag2aa,wcag21aa
```

---

## 주의: 자동화되지 않는 항목

아래는 **반드시 수동 확인** 필요:

- **Loom 워크스루 녹화** (UX)
- **Figma 프레임과 Registry ID 1:1 매칭** (UX → UI 간 확인)
- **권한별 UI 차이** (실제 다양한 계정으로 로그인 테스트)
- **스크린 리더 테스트** (VoiceOver / NVDA)
- **Figma ↔ 코드 픽셀 일치도** (디자인 리뷰)
- **베트남어 길이 잘림** (실제 데이터로 렌더링 확인)

---

## PR 설명 템플릿 (개발자)

PR을 생성할 때 다음 섹션을 포함하세요:

```markdown
## Handoff 참조

- Handoff 패키지: `{{FEATURE_NAME}}-handoff/`
- 구현한 Screen ID:
  - [ ] `{{DOMAIN_CODE}}-...`
  - [ ] `{{DOMAIN_CODE}}-...`

## DoD 체크

- [ ] 모든 ID에 `@feature` 주석 추가
- [ ] 상태 분기 처리 (isLoading/isEmpty/isError)
- [ ] i18n 3개국어 키 등록 (ko/en/vi)
- [ ] lint + tsc 통과
- [ ] Lighthouse 90+ (스크린샷 첨부)
- [ ] a11y 키보드 테스트 통과
- [ ] Figma ↔ 구현 일치 (리뷰 링크 첨부)

## 미적용 항목 (있는 경우)

- [ ] {적용 불가한 이유 설명}
```

---

_이 파일은 참고용입니다. 수정 가능하지만 항목을 **제거**할 때는 `11-decision-log.md`에 근거를 남기세요._
