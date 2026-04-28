# 3. State Matrix — 상태 + 권한 정의

**기능**: {{FEATURE_NAME}}
**최종 수정**: {{TODAY}}

> 모든 화면은 정적 화면이 아니라 **상태(State) × 권한(Permission) × 디바이스(Device)** 의 조합으로 정의합니다.

---

## 11.1 상태 정의 (모든 데이터 화면 공통)

| 상태 | 정의 | 디자인 필수 여부 |
|------|------|-----------------|
| `LOADING` | API 응답 대기 중 (스켈레톤) | ✅ 필수 |
| `EMPTY` | 데이터 0개 | ✅ 필수 |
| `DEFAULT` | 데이터 있음 (기본 케이스) | ✅ 필수 |
| `ERROR` | 데이터 로드 실패 | ✅ 필수 |
| `PARTIAL` | 일부 권한만 있음 (필요 시) | 조건부 |

> **룰**: 위 4개 상태 중 하나라도 디자인이 누락되면 DoD 미달입니다. Registry에 각 상태별 ID를 별도로 등록하세요.

---

## 11.2 권한 매트릭스 예시 (질문 상세)

| 기능 | 비로그인 | 일반 사용자 | 작성자 본인 | 답변자 | 관리자 |
|------|---------|-----------|-----------|------|------|
| 보기 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 답변 작성 | ❌ | ✅ | ❌ | ✅ | ✅ |
| 수정 | ❌ | ❌ | ✅ | ❌ | ✅ |
| 삭제 | ❌ | ❌ | ✅ | ❌ | ✅ |
| 채택 | ❌ | ❌ | ✅ | ❌ | ❌ |
| 신고 | ❌ | ✅ | ❌ | ❌ | ✅ |
| 수정 이력 조회 | ❌ | ❌ | ✅ | ❌ | ✅ |

→ **권한별 UI 차이가 있는 경우** ID를 분리하거나 `1-screen-registry.md` 의 "상태/케이스" 컬럼에 명시

---

## 상태 × 권한 조합 전개

각 Registry ID에 대해 가능한 조합을 확인합니다:

| Screen ID | 상태 | 권한 | 디자인 필수 | 비고 |
|-----------|------|------|-----------|------|
| `{{DOMAIN_CODE}}-EXPERT-LIST` | DEFAULT | 비로그인 | ✅ | 진행률/북마크 숨김 |
| `{{DOMAIN_CODE}}-EXPERT-LIST` | DEFAULT | 로그인 | ✅ | 진행률/북마크 노출 |
| `{{DOMAIN_CODE}}-EXPERT-LIST-LOADING` | LOADING | 공통 | ✅ | 스켈레톤 |
| `{{DOMAIN_CODE}}-EXPERT-LIST-EMPTY` | EMPTY | 공통 | ✅ | "첫 질문 작성하기" CTA |
| `{{DOMAIN_CODE}}-EXPERT-LIST-ERROR` | ERROR | 공통 | ✅ | "다시 시도" 버튼 |
| `{{DOMAIN_CODE}}-EXPERT-DETAIL-UC01` | DEFAULT | 작성자 본인 | ✅ | 수정/삭제 메뉴 노출 |
| `{{DOMAIN_CODE}}-EXPERT-DETAIL-UC02` | DEFAULT | 작성자 본인 | ✅ | 채택 버튼 활성화 |
| `{{DOMAIN_CODE}}-EXPERT-DETAIL-UC03` | DEFAULT | 공통 | ✅ | 채택 완료 배지 |

---

## 상태 구현 원칙 (Dev 참고)

개발자는 모든 데이터 화면에서 상태 분기를 명시적으로 구현해야 합니다:

```tsx
// @feature: {{DOMAIN_CODE}}-EXPERT-LIST
function ExpertList() {
  const { data, isLoading, isError } = useQuery(...)

  if (isLoading) return <ExpertListSkeleton />        // LOADING
  if (isError)   return <ExpertListError onRetry={retry} /> // ERROR
  if (!data?.length) return <ExpertListEmpty />       // EMPTY

  return <ExpertListDefault items={data} />           // DEFAULT
}
```

**금지 패턴**:
- ❌ LOADING 상태 없이 즉시 렌더링 (깜빡임 발생)
- ❌ EMPTY와 ERROR를 같은 UI로 처리 (사용자 혼란)
- ❌ 권한 분기를 클라이언트에서만 처리 (서버 검증 필수)

---

_TODO (UX): 위 권한 매트릭스 예시(질문 상세) 외에 이 기능의 모든 주요 화면에 대해 권한 매트릭스를 작성하세요._
