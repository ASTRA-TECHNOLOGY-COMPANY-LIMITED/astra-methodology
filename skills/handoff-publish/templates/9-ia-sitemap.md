# 9. IA / Sitemap — 정보 구조

**기능**: {{FEATURE_NAME}}
**최종 수정**: {{TODAY}}

> **왜 필요한가?** 디자이너/개발자가 메뉴 구조의 **결정 근거**를 모르면 임의로 재배치하거나 새 진입점을 추가합니다. IA는 제품 전체의 골격이므로 별도 문서로 관리합니다.

---

## 포함할 내용

- 전체 사이트맵 (트리 구조)
- GNB / LNB / Bottom Tab 구조
- 메뉴 depth 정책 (최대 3 depth 권장)
- URL 컨벤션 (`/{{DOMAIN_CODE}}/expert/[id]`)
- 권한별 메뉴 노출 규칙
- 새 메뉴 추가 시 검토 절차 (UX 승인 필수)

---

## 전체 사이트맵

```
{{PROJECT_NAME}}
├── /academy                       홈 (마케팅 모드 / 피드 모드)
├── /academy/courses               교육
│   └── /[id]                     강의 상세
│       ├── /apply               신청
│       └── /learn               수강
├── /academy/insight               무역 인사이트
│   ├── ?tab=insight              AI 인사이트
│   └── ?tab=notice               공지
├── /academy/community             커뮤니티
│   ├── /[id]                    글 상세
│   ├── /write                   글쓰기
│   └── /bookmarks               북마크
├── /academy/expert                전문가 Q&A  ← 이 Handoff 범위
│   ├── /[id]                    질문 상세
│   ├── /ask                     질문 작성
│   └── /dashboard               내 질문 관리
└── /academy/tools                 무역 도구
```

---

## GNB / LNB / Bottom Tab 구조

### GNB (Global Navigation Bar)
- **Desktop**: 상단 고정 (로고 / 1뎁스 메뉴 / 검색 / 알림 / 프로필)
- **Tablet**: 상단 고정 + 햄버거 메뉴 (2뎁스 접근)
- **Mobile**: 상단 고정 (로고 + 알림 + 프로필만) + Bottom Tab Bar

### LNB (Left Navigation Bar)
- **Desktop**: 좌측 사이드바 (2~3뎁스 메뉴)
- **Tablet**: 햄버거 메뉴 내 포함
- **Mobile**: 사용하지 않음 → Bottom Tab으로 대체

### Bottom Tab (Mobile 전용)
- 최대 5개 탭
- 현재 기획: 홈 / 교육 / Q&A / 커뮤니티 / 프로필
- Tab 뒤 뱃지: 알림 수 또는 NEW 배지

---

## 메뉴 depth 정책

- **최대 3 depth**: 그 이상은 사이드바 확장/축소 또는 아코디언으로 처리
- **2뎁스까지 GNB/LNB에 직접 노출**, 3뎁스는 서브 페이지 진입 후 탭/필터로 전환
- **depth 초과 시**: UX 검토 후 IA 재구성 고려

---

## URL 컨벤션

| 패턴 | 용도 | 예시 |
|------|------|------|
| `/{{DOMAIN_CODE}}` | 홈 | `/academy` |
| `/{{DOMAIN_CODE}}/{resource}` | 리스트 | `/academy/expert` |
| `/{{DOMAIN_CODE}}/{resource}/[id]` | 상세 | `/academy/expert/123` |
| `/{{DOMAIN_CODE}}/{resource}/create` 또는 `/ask` | 생성 | `/academy/expert/ask` |
| `/{{DOMAIN_CODE}}/{resource}/[id]/edit` | 수정 | `/academy/expert/123/edit` |
| `?tab={value}` | 탭 필터 | `/academy/insight?tab=notice` |
| `?category={value}&sort={value}` | 리스트 필터 | `/academy/expert?category=fta&sort=latest` |

**원칙**:
- kebab-case (예: `/my-dashboard`, not `/myDashboard`)
- 복수형 리소스 (예: `/courses`, not `/course`)
- 필터는 쿼리 파라미터로
- 동사 최소화 (상태는 상세 페이지 내 탭/상태로 표현)

---

## 권한별 메뉴 노출

| 메뉴 | 비로그인 | 일반 | Pro | 관리자 |
|------|---------|------|-----|------|
| 홈 (/academy) | ✅ | ✅ | ✅ | ✅ |
| 교육 | ✅ | ✅ | ✅ | ✅ |
| 인사이트 | ✅ (무료만) | ✅ (무료만) | ✅ (전체) | ✅ |
| 커뮤니티 | ✅ (보기만) | ✅ | ✅ | ✅ |
| 전문가 Q&A | ✅ (보기만) | ✅ | ✅ | ✅ |
| 무역 도구 | ❌ | ✅ (일부) | ✅ (전체) | ✅ |
| 관리자 대시보드 | ❌ | ❌ | ❌ | ✅ |

---

## 새 메뉴 추가 절차

1. **제안**: PM/UX가 Slack #fect-academy-design 에 제안
2. **검토**: UX Lead 검토 (IA 영향도 / 중복 여부 / 권한 정책)
3. **승인**: UX Lead 승인 시 `9-ia-sitemap.md` 업데이트
4. **Registry 반영**: `1-screen-registry.md` 에 신규 화면 ID 추가
5. **공유**: `11-decision-log.md` 에 결정 이력 기록
6. **알림**: Slack 공유 (UI/Dev acknowledge)

---

## 원칙

- IA 변경은 **UX 승인 필수** (단순 페이지 추가도 포함)
- URL 변경은 **개발팀과 사전 협의** (SEO + 외부 링크 영향)
- 기존 URL 변경 시 **301 리다이렉트 유지** 최소 6개월

---

_TODO (UX): 위 사이트맵은 {{PROJECT_NAME}} 기준으로 작성된 예시입니다. 실제 이 기능과 연결되는 IA 부분만 남기고 나머지는 정리하세요._
