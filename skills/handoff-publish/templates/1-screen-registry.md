# 1. Screen Registry — 화면 등록부

**Owner**: {{OWNER}} (UX) — **ID 발행 단독 권한**
**기능**: {{FEATURE_NAME}}
**도메인 코드**: `{{DOMAIN_CODE}}`
**최종 수정**: {{TODAY}}

> **이 문서는 Single Source of Truth (SSoT)입니다.**
> 모든 Screen ID는 이 표에서 생성됩니다. Figma 프레임명, 코드의 `@feature:` 주석, 스크린샷 파일명은 모두 이 표의 ID를 따라야 합니다.
> **UX 외의 역할이 임의로 ID를 생성하는 것은 무효입니다.** 반드시 이 표에 등록한 후 사용하세요.

---

## 기본 구조

| ID | 화면명 | 상태/케이스 | 트리거 | 디자인 상태 |
|------|--------|---------|--------|-----------|
| `{{DOMAIN_CODE}}-EXPERT-LIST` | 리스트 | 기본 | GNB > 전문가 Q&A | 🔄 |
| `{{DOMAIN_CODE}}-EXPERT-LIST-EMPTY` | 리스트 | 데이터 없음 | 새 카테고리 | 🔄 |
| `{{DOMAIN_CODE}}-EXPERT-LIST-LOADING` | 리스트 | 스켈레톤 | 진입 직후 |  🔄 |
| `{{DOMAIN_CODE}}-EXPERT-LIST-ERROR` | 리스트 | 에러 | API 실패 | 🔄 |
| `{{DOMAIN_CODE}}-EXPERT-DETAIL-UC01` | 질문 상세 | 답변 없음 | 카드 클릭 (답변 0건) | 🔄 |
| `{{DOMAIN_CODE}}-EXPERT-DETAIL-UC02` | 질문 상세 | 채택 전 | 카드 클릭 (답변 있음) | 🔄 |
| `{{DOMAIN_CODE}}-EXPERT-DETAIL-UC03` | 질문 상세 | 채택 완료 | 카드 클릭 (채택 완료) | 🔄 |
| `{{DOMAIN_CODE}}-EXPERT-WRITE` | 질문 작성 | 기본 | "질문하기" 버튼 | 🔄 |
| `{{DOMAIN_CODE}}-EXPERT-WRITE-ERROR` | 질문 작성 | 검증 실패 | 필수 입력 누락 | 🔄 |
| `{{DOMAIN_CODE}}-EXPERT-MODAL01` | 삭제 확인 | Confirm | 본인 질문 > 삭제 | ❌ |
| `{{DOMAIN_CODE}}-EXPERT-MODAL-LOGIN` | 로그인 유도 | Gate | 비로그인 > 질문하기 | 🔄 |

**디자인 상태 표기**:
- ✅ 완료
- 🔄 진행 중 / 미착수
- ❌ 해당 없음 (진행 불가)
- 🔁 변경됨 (YYYY-MM-DD)

---

## 9.2 반드시 포함

다음 화면은 **누락 없이** Registry에 등록되어야 합니다:

- [ ] 기본 화면 (DEFAULT)
- [ ] 모든 상태 (LOADING / EMPTY / DEFAULT / ERROR)
- [ ] 모든 모달 (Confirm / Form / Error 포함)
- [ ] Edge case 화면
- [ ] URL 파라미터로만 진입하는 숨은 화면
- [ ] 권한별 UI 차이가 있는 경우 별도 ID 또는 "상태/케이스" 컬럼에 명시

---

## Screen ID 명명 규칙

```
{DOMAIN}-{PAGE}-{SECTION}-{UC}
────    ─────   ───────   ────
도메인   페이지   섹션      유즈케이스 (2자리, 상태/케이스 구분)

{{DOMAIN_CODE}}-EXPERT-DETAIL-UC03
```

- `DOMAIN`: 프로덕트 약어 (2~6자 대문자) — `{{DOMAIN_CODE}}`
- `PAGE`: 메뉴/라우트 단위 대문자
- `SECTION`: LIST / DETAIL / FORM / WRITE / MODAL / DASHBOARD / SETTINGS (생략 가능)
- `UC{NN}` 또는 상태 접미사 (`-LOADING`, `-EMPTY`, `-ERROR`): 같은 페이지의 상태/케이스 구분

**반응형 분기 (구조가 다를 때만 별도 ID)**:
```
Desktop (≥1024):  {{DOMAIN_CODE}}-EXPERT-DETAIL-UC03
Tablet  (768~1023): {{DOMAIN_CODE}}-EXPERT-DETAIL-UC03-T
Mobile  (<768):   {{DOMAIN_CODE}}-EXPERT-DETAIL-UC03-M
```
→ 단순 스타일 변경(폰트, 패딩)은 ID 분리하지 않음 (`5-responsive-guide.md` 참조)

---

## 변경 기록

ID 변경/추가/삭제는 반드시 `11-decision-log.md` 에 기록합니다.
- 변경된 ID는 `🔁 changed YYYY-MM-DD` 표기
- 삭제된 ID는 표에서 제거하지 말고 `❌ deprecated YYYY-MM-DD` 표기

---

_이 문서는 UX (`{{OWNER}}`)가 관리합니다. 다른 역할이 수정 요청 시 Slack 또는 이슈로 요청하세요._
