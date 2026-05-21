# Manual Authoring Expert Guide

Defines the writing principles and style rules to apply when authoring an online service manual. Based on the documentation style guides of Google, Apple, and Microsoft and on UX Writing principles.

## 1. Three Core Principles

### Know Your Audience

- The primary audience of the manual is **non-technical users**
- Write from the perspective of a service user, not a developer
- Do not assume the reader already knows
- Do not use internal jargon, acronyms, or slang

### Clarity First

- Microsoft: "Make every word matter" — every word has a purpose
- Convey one piece of information per sentence
- Use short sentences (recommended within 40 characters for Korean)
- Use concrete instructions instead of ambiguous expressions

### Consistent Tone & Voice

- A professional yet friendly conversational tone
- Maintain the same tone throughout the entire manual
- Use a tone that aligns with the brand identity

## 2. Writing Style Rules

### DO (mandatory)

> The Korean examples below illustrate Korean-language polite-imperative vs. declarative endings (e.g., `클릭하세요` vs. `클릭한다`); for English manuals, follow the rule by using the imperative ("Click the Save button.") rather than third-person declarative ("The user clicks the Save button.").

| Rule | Example (O) | Example (X) |
|------|-------------|-------------|
| Use second-person polite form | "로그인 버튼을 클릭하세요" | "로그인 버튼을 클릭한다" |
| Use active voice | "설정을 변경하세요" | "설정이 변경되어야 합니다" |
| Use plain language | "자동으로 로그인이 유지됩니다" | "인증 토큰이 자동 갱신됩니다" |
| Concrete instruction | "'저장' 버튼을 클릭하세요" | "저장해 주세요" |
| Short sentences | One action per sentence | Multiple actions chained in one sentence |
| Emphasize UI elements | UI labels in **bold** | Quotation marks or plain text |
| Explain the result | "클릭하면 대시보드로 이동합니다" | Just ending with "클릭하세요" |

### DON'T

- Do not use internal jargon, acronyms, or slang
- Do not assume the user knows
- No "wall of text" — always split into steps
- Avoid third-person passive voice
- No subjective expressions like "easy" or "simple"
- Do not mention unreleased features
- No unnecessary technical terms (API, token, session, etc.)

### Additional rules for English manuals

- Address the user directly with "you" ("Click the Save button." O)
- Use the present tense ("The page displays..." O vs. "The page will display..." X)
- Follow American English spelling
- Use the Oxford comma when listing nouns

## 3. Structural Rules

### Chapter structure

```
Chapter title (H1)
├── Chapter intro (1–2 sentences: what you will learn)
├── Section 1 (H2)
│   ├── Overview description (1–2 sentences)
│   ├── Step 1 (step-card)
│   ├── Step 2 (step-card)
│   └── Tips / Cautions (callout)
├── Section 2 (H2)
│   └── ...
└── Summary / Next steps
```

### Step authoring rules

1. **One action per step**
2. Start with a verb ("Click", "Enter", "Select")
3. Mark the target UI element in **bold**
4. Describe the result ("→ The settings screen appears.")
5. Attach a screenshot (when a screenshot is clearer than text)

**Good example:**
```
1. Click **Settings** in the top menu.
   → You are taken to the Settings page.
   [Screenshot: highlight the Settings menu location]

2. Select the **Profile** tab.
   → The profile edit screen appears.
   [Screenshot: Profile tab selected]
```

**Bad example:**
```
After clicking Settings in the top menu and then selecting the Profile tab, you can change your name and email on the profile edit screen.
```

### Screenshot rules

| Rule | Description |
|------|-------------|
| ≤ 3–4 annotations per screenshot | Too many annotations cause confusion |
| Highlight only key UI elements | Emphasize the relevant area, not the whole screen |
| 2–4 frames for multi-step | Entry → key action → final result |
| Mandatory alt text | Use descriptive alt attributes for accessibility |
| Match the current UI | Do not use outdated screenshots |

### Callout (info box) rules

| Type | When to use | Icon |
|------|-------------|------|
| `.callout-tip` | Optional help, productivity tip, shortcut | 💡 |
| `.callout-note` | Extra explanation, reference info | ℹ️ |
| `.callout-warning` | Action requiring caution, data-impacting | ⚠️ |
| `.callout-danger` | Irreversible action, data-loss risk | 🚨 |

**Usage principles:**
- ≤ 2 per section (more is distracting)
- Insert without interrupting the body flow
- Keep concise — 1 to 2 sentences

## 4. Terminology Consistency

### Standard UI element terms

| UI element | Korean standard term | Avoid |
|------------|----------------------|-------|
| Button | 버튼 | 단추, 키 |
| Input field | 입력란 | 입력 필드, 텍스트 박스 |
| Dropdown | 드롭다운 | 선택 상자, 풀다운 |
| Checkbox | 체크박스 | 확인란, 선택 상자 |
| Toggle | 토글 | 스위치, 온오프 |
| Tab | 탭 | 탭 메뉴, 탭 버튼 |
| Modal/Dialog | 팝업 창 | 모달, 다이얼로그 |
| Sidebar | 사이드바 | 측면 메뉴, 왼쪽 패널 |
| Breadcrumb | 이동 경로 | 브레드크럼 |
| Toast/Snackbar | 알림 메시지 | 토스트, 스낵바 |

### Standard action terms

| Action | Korean standard | Avoid |
|--------|-----------------|-------|
| Click | 클릭하세요 | 누르세요, 선택하세요 (mouse) |
| Tap (mobile) | 탭하세요 | 터치하세요, 누르세요 |
| Enter/Type | 입력하세요 | 타이핑하세요, 기입하세요 |
| Select | 선택하세요 | 고르세요, 지정하세요 |
| Scroll | 스크롤하세요 | 내려가세요, 올려보세요 |
| Drag | 드래그하세요 | 끌어다 놓으세요 |
| Toggle | 켜세요/끄세요 | 토글하세요 |
| Navigate | 이동하세요 | 네비게이트하세요 |

## 5. Accessibility Rules

- Include descriptive `alt` text on every screenshot
- Do not convey information by color alone (combine numbers + color in annotations)
- Support keyboard navigation
- Maintain a proper heading hierarchy (H1 → H2 → H3, no skipping)
- Write link text descriptively (no "click here")
- Respect `prefers-reduced-motion`

## 6. FAQ Authoring Rules

- Phrase questions the way real users ask them
- Use the "How do I ...?" format
- Structure answers as steps
- Quote error messages verbatim (for searchability)
- Include links to related chapters

**Example:**
```
Q: I forgot my password. How do I reset it?

A: To reset your password:
1. Click **Forgot password** on the login screen.
2. Enter the email address you signed up with.
3. Click **Send reset link**.
4. Click the reset link in the email and set a new password.

For details, see [02. Login and Authentication](chapters/02-auth-login.html#password-reset).
```

## 7. Manual Quality Checklist

Verify the following after authoring is complete:

- [ ] Are all steps written in the second-person polite form?
- [ ] Is the manual written in plain language without jargon?
- [ ] Is a screenshot attached to every step?
- [ ] Do the screenshots match the current UI?
- [ ] Are UI element terms consistent across the manual?
- [ ] Are tip/caution boxes used appropriately?
- [ ] Is the inter-chapter navigation correct?
- [ ] Can the reader find the desired content via search?
- [ ] Is it readable on mobile?
- [ ] Does the print layout render correctly?
- [ ] Is alt text included on every image?
