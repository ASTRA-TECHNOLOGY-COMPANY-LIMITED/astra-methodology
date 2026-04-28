# 2. Flows — 사용자 흐름 정의

**기능**: {{FEATURE_NAME}}
**최종 수정**: {{TODAY}}

> 모든 버튼 클릭 후 결과를 명시합니다 (성공/실패 분기 포함).
> 작성 원칙:
> - 모든 클릭/제출/액션의 결과를 Screen ID로 매핑
> - 성공/실패/예외 분기 빠뜨리지 않기
> - 디자이너가 "다음 화면이 없네?" 라고 물어볼 일이 없게

---

## 주요 Flow 1: 질문 작성 Flow

```
[질문 작성 Flow]

{{DOMAIN_CODE}}-EXPERT-LIST
    └ "질문하기" 클릭
        ├ (비로그인) → {{DOMAIN_CODE}}-EXPERT-MODAL-LOGIN
        └ (로그인)   → {{DOMAIN_CODE}}-EXPERT-WRITE
                        └ "등록" 클릭
                            ├ (성공)     → {{DOMAIN_CODE}}-EXPERT-LIST (새 질문 노출)
                            ├ (토큰 부족) → {{DOMAIN_CODE}}-EXPERT-MODAL02
                            └ (네트워크 에러) → {{DOMAIN_CODE}}-EXPERT-WRITE-ERROR
```

---

## 주요 Flow 2: 답변 채택 Flow

```
[답변 채택 Flow]

{{DOMAIN_CODE}}-EXPERT-DETAIL-UC02 (채택 전)
    └ 답변 카드의 "채택" 버튼 클릭
        ├ (본인 질문 & 채택 가능)     → 확인 모달
        │   └ "채택 확정" 클릭
        │       ├ (성공)  → {{DOMAIN_CODE}}-EXPERT-DETAIL-UC03 (채택 완료)
        │       └ (실패)  → 에러 토스트 (유지)
        ├ (본인 질문 아님)            → 버튼 비활성화 (클릭 불가)
        └ (이미 채택 완료)            → 버튼 숨김
```

---

## 주요 Flow 3: 질문 삭제 Flow

```
[질문 삭제 Flow]

{{DOMAIN_CODE}}-EXPERT-DETAIL-*
    └ "삭제" 메뉴 클릭 (본인 질문만 노출)
        └ {{DOMAIN_CODE}}-EXPERT-MODAL01 (삭제 확인)
            ├ "삭제하기" 클릭
            │   ├ (성공)  → {{DOMAIN_CODE}}-EXPERT-LIST (토스트: "삭제되었습니다")
            │   └ (실패)  → 에러 토스트 (모달 유지)
            └ "취소" 클릭 → 모달 닫기 (DETAIL 유지)
```

---

## 작성 원칙

- **모든 클릭/제출/액션의 결과를 ID로 매핑**: 한 개의 클릭이라도 결과 화면이 빠지면 안 됨
- **성공/실패/예외 분기 빠뜨리지 않기**: 특히 네트워크 에러, 권한 부족, 토큰 부족
- **상태 전환은 같은 ID의 다른 UC로 표기**: 예) UC01(답변 없음) → UC02(채택 전) → UC03(채택 완료)
- **숨겨진 화면도 포함**: URL 파라미터로만 접근하거나, 특정 조건에서만 노출되는 화면

---

## Flow 다이어그램 (Mermaid — 선택)

```mermaid
flowchart LR
    LIST[{{DOMAIN_CODE}}-EXPERT-LIST]
    WRITE[{{DOMAIN_CODE}}-EXPERT-WRITE]
    LOGIN[{{DOMAIN_CODE}}-EXPERT-MODAL-LOGIN]
    LIST_SUCCESS[{{DOMAIN_CODE}}-EXPERT-LIST<br/>새 질문 노출]
    WRITE_ERR[{{DOMAIN_CODE}}-EXPERT-WRITE-ERROR]
    MODAL02[{{DOMAIN_CODE}}-EXPERT-MODAL02]

    LIST -->|"질문하기 (비로그인)"| LOGIN
    LIST -->|"질문하기 (로그인)"| WRITE
    WRITE -->|"등록 성공"| LIST_SUCCESS
    WRITE -->|"네트워크 에러"| WRITE_ERR
    WRITE -->|"토큰 부족"| MODAL02
```

---

_TODO (UX): 위 Flow 3개 외에 이 기능의 추가 시나리오(수정, 신고, 북마크 등)를 모두 추가하세요._
