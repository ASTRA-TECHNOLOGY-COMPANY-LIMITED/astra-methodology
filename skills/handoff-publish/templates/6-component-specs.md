# 6. Component Specs — 카드/컴포넌트 명세

**기능**: {{FEATURE_NAME}}
**최종 수정**: {{TODAY}}

> **왜 필요한가?** 같은 카드를 여러 화면에서 쓰는데 디자이너/개발자가 화면마다 다르게 만들면 일관성이 깨집니다. 컴포넌트의 **데이터 구조(anatomy)** 를 한 번 정의하고 모든 화면에서 참조합니다.

---

## 14.1 작성 형식 (예시)

## CourseCard

### 필수 props
- `courseId`, `title`, `thumbnail`, `instructor`, `rating`, `studentCount`, `price`

### 조건부 props
- `isNew` (7일 이내 등록 시 표시)
- `isBest` (top 10% 시 표시)
- `progress` (수강 중일 때만)
- `discountPrice` (할인가 있을 때)

### 크기 variants
- `Large` (4:3, 메인 추천)
- `Medium` (16:9, 리스트 기본)
- `Small` (1:1, 사이드바)

### 사용처
- `/academy/courses` (리스트)
- `/academy` (인기 강의 섹션)
- `/academy/courses/[id]` (관련 강의)
- `/academy` (수강 중 카드)

---

## QuestionCard

### 필수 props
- `questionId`, `title`, `excerpt`, `author`, `createdAt`, `answerCount`, `viewCount`

### 조건부 props
- `isAccepted` (채택 완료 시 배지)
- `isHot` (24시간 내 답변 5개 이상)
- `hasImage` (이미지 포함 여부)
- `category` (카테고리 배지)

### 크기 variants
- `Large` (메인 피쳐드)
- `Medium` (리스트 기본)
- `Compact` (사이드바, 관련 질문)

### 사용처
- `/{{DOMAIN_CODE}}/expert` (리스트)
- `/{{DOMAIN_CODE}}/expert/[id]` (관련 질문)
- 대시보드 (내 질문 카드)

---

## InsightCard

### 필수 props
- `insightId`, `title`, `summary`, `thumbnail`, `publishedAt`, `category`

### 조건부 props
- `isPremium` (프리미엄 전용 컨텐츠)
- `readTime` (예상 읽기 시간)

### 크기 variants
- `Feature` (메인 배너)
- `Standard` (리스트 기본)

### 사용처
- `/{{DOMAIN_CODE}}/insight` (리스트)
- `/{{DOMAIN_CODE}}` (메인 추천)

---

## NoticeCard

### 필수 props
- `noticeId`, `title`, `publishedAt`

### 조건부 props
- `isPinned` (상단 고정)
- `isNew` (7일 이내)
- `hasAttachment` (첨부 파일)

### 사용처
- `/{{DOMAIN_CODE}}/insight?tab=notice`
- 헤더 공지 배너 (최신 1건)

---

## Modal 컴포넌트

### 14.2 Modal — 공통

| Variant | 용도 | 구성 요소 |
|---------|------|----------|
| `Confirm` | 파괴적 액션 확인 (삭제, 탈퇴 등) | 제목 + 설명 + 취소 / 확정 버튼 |
| `Form` | 간단한 입력 (신고, 피드백 등) | 제목 + 입력 필드 + 취소 / 제출 버튼 |
| `Error` | 에러 안내 + 복구 액션 | 제목 + 설명 + 다시 시도 / 닫기 |
| `Login Gate` | 로그인 유도 | 제목 + CTA 링크 + 닫기 |

---

## 검색바 / 필터바 / 페이지네이션

### SearchBar
- Props: `placeholder`, `onSearch`, `initialValue`, `debounceMs` (기본 300ms)
- 상태: 포커스 / 입력 중 / 결과 있음 / 결과 없음
- 사용처: 리스트 페이지 상단

### FilterBar
- Props: `filters[]`, `onChange`, `activeFilters`
- 구성: 칩(Chip) 기반 다중 선택
- 사용처: 리스트 페이지

### Pagination
- Props: `currentPage`, `totalPages`, `onChange`
- Variant: `Numbered` (페이지 번호) / `LoadMore` (더보기 버튼) / `Infinite` (무한 스크롤)
- Mobile 기본: LoadMore

---

## 14.3 원칙

- **DRY**: 컴포넌트는 **1번 정의**, 화면 룰에서는 참조만
- **화면별 데이터 매핑**은 `7-business-rules.md` 에 작성
- **새 컴포넌트 추가는 UX 승인 필수** (재사용 가능 여부 판단)

---

## 컴포넌트 구현 체크리스트 (Dev 참고)

각 컴포넌트 구현 시:

- [ ] Props 타입 정의 (TypeScript interface)
- [ ] 필수/선택 props 명확히 구분
- [ ] Variants는 `variant` prop으로 통일 (예: `variant: 'large' | 'medium' | 'small'`)
- [ ] 디자인 토큰만 사용 (하드코딩된 색상/사이즈 금지)
- [ ] `// @feature: COMPONENT-{NAME}` 주석으로 anatomy 링크
- [ ] Storybook 스토리 작성 (모든 variants 포함)
- [ ] 접근성: role, aria-label, keyboard navigation

---

_TODO (UX/UI): 위 예시 외에 이 기능에서 사용하는 모든 공통 컴포넌트를 추가하세요. 기존 글로벌 컴포넌트(`docs/design-system/components.md`에 정의된)는 참조 링크만 남기고 중복 기술하지 마세요._
