# 5. Responsive Guide — 반응형 기준

**기능**: {{FEATURE_NAME}}
**최종 수정**: {{TODAY}}

---

## 12.1 ID 표기 컨벤션

```
Desktop (≥1024):    {{DOMAIN_CODE}}-EXPERT-DETAIL-UC03
Tablet  (768~1023): {{DOMAIN_CODE}}-EXPERT-DETAIL-UC03-T
Mobile  (<768):     {{DOMAIN_CODE}}-EXPERT-DETAIL-UC03-M
```

---

## 12.2 원칙

- **Desktop 기준으로 설계** → Tablet/Mobile은 분기점만 정의
- **구조가 다를 때만 별도 ID 생성** (LNB → Bottom tabs 등)
- **단순 스타일 변경** (폰트 크기, 패딩)은 ID 분리하지 않음 → 같은 ID 안에서 처리

---

## 분기점 상세

| 분기 | 너비 | 주요 변경 |
|------|------|----------|
| Desktop | ≥1024px | 기본 레이아웃. 좌측 LNB + 메인 컨텐츠 + 우측 위젯 (선택) |
| Tablet | 768~1023px | 우측 위젯 제거, 좌측 LNB는 축소 또는 hamburger menu |
| Mobile | <768px | LNB → Bottom Tab 전환, 컨텐츠는 1-column, 카드는 full-width |

---

## 레이아웃 분기 체크리스트

각 화면마다 다음을 확인합니다:

- [ ] **Desktop → Tablet 전환**
  - 우측 위젯/사이드바 처리 방식
  - 테이블의 컬럼 우선순위 (숨길 컬럼)
  - 카드 그리드 columns 변화 (예: 4 → 2)

- [ ] **Tablet → Mobile 전환**
  - 네비게이션 방식 (LNB → Bottom Tab / Drawer)
  - 모달 크기 (전체 화면 모달 전환 여부)
  - 폼 입력 필드 레이아웃 (2-col → 1-col)
  - 액션 버튼 위치 (고정 하단 FAB / Sticky CTA)

---

## Breakpoint 토큰

프로젝트의 디자인 토큰(`src/styles/design-tokens.css` 또는 Tailwind config)과 일치해야 합니다:

```css
/* design-tokens.css 예시 */
--breakpoint-sm: 640px;
--breakpoint-md: 768px;   /* tablet 진입 */
--breakpoint-lg: 1024px;  /* desktop 진입 */
--breakpoint-xl: 1280px;
```

```css
/* Mobile-first 접근 */
.card {
  /* Mobile 기본 스타일 */
}

@media (min-width: 768px) {
  /* Tablet 스타일 */
}

@media (min-width: 1024px) {
  /* Desktop 스타일 */
}
```

---

## 터치 타겟 (Mobile)

- **최소 터치 영역**: 44×44px (iOS HIG) / 48×48dp (Material)
- **간격**: 터치 타겟 사이 최소 8px 여백
- **hover 효과 대체**: Mobile에서는 `:active` / press animation으로 대체

---

## 화면별 분기 ID 목록

| Desktop ID | Tablet 분기 필요? | Mobile 분기 필요? | Mobile ID |
|-----------|-----------------|-----------------|-----------|
| `{{DOMAIN_CODE}}-EXPERT-LIST` | ❌ (컬럼 수만 조정) | ✅ (카드 1-col + Bottom Tab) | `{{DOMAIN_CODE}}-EXPERT-LIST-M` |
| `{{DOMAIN_CODE}}-EXPERT-DETAIL-UC03` | ❌ | ✅ (답변 입력창 Sticky) | `{{DOMAIN_CODE}}-EXPERT-DETAIL-UC03-M` |
| `{{DOMAIN_CODE}}-EXPERT-WRITE` | ❌ | ✅ (전체 화면 폼) | `{{DOMAIN_CODE}}-EXPERT-WRITE-M` |
| `{{DOMAIN_CODE}}-EXPERT-MODAL01` | ❌ | ✅ (Bottom Sheet으로 변환) | `{{DOMAIN_CODE}}-EXPERT-MODAL01-M` |

_TODO (UI 디자이너): 실제 Figma 작업 시 분기 필요 여부를 확정하고 위 표를 업데이트하세요._
