# 컴포넌트 스타일 가이드

> DSA가 프로젝트에 맞게 커스터마이즈합니다.
> AI가 UI를 생성할 때 이 가이드를 참조합니다.

## 1. 버튼 (Button)

### 변형 (Variants)
| 변형 | 용도 | 배경 | 텍스트 |
|------|------|------|--------|
| Primary | 주요 액션 (저장, 확인) | `--color-primary-600` | `--color-text-inverse` |
| Secondary | 보조 액션 (취소, 돌아가기) | transparent, border | `--color-text-primary` |
| Danger | 삭제, 위험한 액션 | `--color-error-600` | `--color-text-inverse` |
| Ghost | 텍스트 버튼 | transparent | `--color-primary-600` |

### 크기 (Sizes)
| 크기 | 높이 | 패딩 | 폰트 크기 |
|------|------|------|----------|
| sm | 32px | `--spacing-2` `--spacing-3` | `--font-size-sm` |
| md | 40px | `--spacing-2` `--spacing-4` | `--font-size-base` |
| lg | 48px | `--spacing-3` `--spacing-6` | `--font-size-lg` |

### 상태 (States)
- **Hover**: 배경색 한 단계 어둡게 (예: 600 → 700)
- **Active**: 배경색 두 단계 어둡게 (예: 600 → 800)
- **Disabled**: opacity 0.5, cursor: not-allowed
- **Loading**: 스피너 아이콘 + 텍스트 유지

### 아이콘
- 아이콘은 텍스트 왼쪽에 배치 (기본)
- 아이콘과 텍스트 간격: `--spacing-2`
- 아이콘만 있는 버튼: 정사각형, 동일한 높이/너비

## 2. 입력 필드 (Input)

### 기본 스타일
- 높이: 40px (md)
- 패딩: `--spacing-2` `--spacing-3`
- 테두리: `--border-width-default` `--color-border-default`
- 라운드: `--radius-md`
- 포커스: `--color-primary-500` 테두리 + ring

### 라벨
- 위치: 입력 필드 위
- 간격: `--spacing-1`
- 폰트: `--font-size-sm` `--font-weight-medium`

### 에러 상태
- 테두리: `--color-error-500`
- 에러 메시지: `--font-size-sm` `--color-error-500`
- 에러 메시지 간격: `--spacing-1`

### 도움말 텍스트
- 폰트: `--font-size-sm` `--color-text-tertiary`
- 간격: `--spacing-1`

## 3. 카드 (Card)

### 기본 스타일
- 배경: `--color-bg-primary`
- 테두리: `--border-width-default` `--color-border-default`
- 라운드: `--radius-lg`
- 그림자: `--shadow-sm`
- 패딩: `--spacing-6`

### 변형
| 변형 | 그림자 | 호버 |
|------|--------|------|
| Default | `--shadow-sm` | 없음 |
| Elevated | `--shadow-md` | `--shadow-lg` |
| Outlined | 없음, 테두리만 | 테두리 강조 |
| Interactive | `--shadow-sm` | `--shadow-md` + translateY(-1px) |

## 4. 모달 (Modal)

### 기본 스타일
- 백드롭: rgba(0, 0, 0, 0.5)
- 모달: `--color-bg-primary`, `--radius-xl`, `--shadow-xl`
- 최대 너비: 480px (sm), 640px (md), 800px (lg)
- 패딩: `--spacing-6`

### 구조
```
┌─────────────────────────────┐
│ 헤더 (제목 + 닫기 버튼)      │
├─────────────────────────────┤
│                             │
│ 본문 (스크롤 가능)           │
│                             │
├─────────────────────────────┤
│ 푸터 (액션 버튼)             │
└─────────────────────────────┘
```

- 헤더: `--font-size-xl` `--font-weight-semibold`
- 섹션 간 구분: `--color-border-default`
- 푸터 버튼: 오른쪽 정렬, 간격 `--spacing-3`

## 5. 테이블 (Table)

### 기본 스타일
- 헤더: `--color-bg-secondary`, `--font-weight-semibold`, `--font-size-sm`
- 행: `--color-bg-primary`, hover 시 `--color-bg-secondary`
- 셀 패딩: `--spacing-3` `--spacing-4`
- 테두리: 하단만, `--color-border-default`

### 반응형
- 모바일: 가로 스크롤 또는 카드 형태로 전환
- 태블릿+: 기본 테이블 레이아웃

## 6. 네비게이션 (Navigation)

### GNB (Global Navigation Bar)
- 높이: 64px
- 배경: `--color-bg-primary`
- 하단 테두리: `--color-border-default`
- z-index: `--z-sticky`
- 로고: 왼쪽, 메뉴: 중앙 또는 왼쪽, 유저 메뉴: 오른쪽

### 사이드바
- 너비: 240px (열림), 64px (접힘)
- 배경: `--color-bg-secondary`
- 메뉴 아이템 높이: 40px
- 활성 상태: `--color-primary-50` 배경 + `--color-primary-600` 텍스트

### 탭
- 하단 인디케이터: `--color-primary-600`, 2px
- 탭 간격: `--spacing-6`
- 비활성: `--color-text-tertiary`
- 활성: `--color-text-primary`

## 7. 알림/토스트 (Toast/Alert)

### 변형
| 변형 | 좌측 색상 | 아이콘 |
|------|----------|--------|
| Success | `--color-success-500` | 체크 |
| Warning | `--color-warning-500` | 경고 삼각형 |
| Error | `--color-error-500` | X 원형 |
| Info | `--color-info-500` | i 원형 |

### 토스트 위치
- 기본: 우상단
- z-index: `--z-toast`
- 자동 닫힘: 5초

## 8. 뱃지/태그 (Badge/Tag)

### 크기
| 크기 | 높이 | 폰트 크기 | 패딩 |
|------|------|----------|------|
| sm | 20px | `--font-size-xs` | `--spacing-1` `--spacing-2` |
| md | 24px | `--font-size-sm` | `--spacing-1` `--spacing-2` |

### 색상
- 상태 뱃지: Semantic 컬러 사용
- 카테고리 태그: Primary 컬러 변형 사용

---

> **DSA 체크포인트**: 이 가이드의 각 컴포넌트가 프로젝트 브랜딩과 일치하는지 확인합니다.
> 필요 시 design-tokens.css의 토큰 값을 먼저 조정한 후 이 가이드를 업데이트합니다.
