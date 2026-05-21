# 7. Business Rules — Per-Screen Business Rules / Exposure Policy

**Feature**: {{FEATURE_NAME}}
**Last updated**: {{TODAY}}

> **Why is this needed?** Separately from how a screen looks (design), there must be a policy for **"what is shown"** — exposure conditions, sorting, count limits, data filters, permission branching, etc.

---

## 15.1 Authoring format (example)

## `{{DOMAIN_CODE}}-COURSES-LIST-POPULAR` — Popular Courses List

### Exposure policy
- **Sort**: enrolled-students count over the last 30 days DESC
- **Filter**: active courses only; exclude private
- **Count**: 12 (3 rows × 4 cols)
- **Pagination**: "Load more" button (12 at a time)

### Components used
- `CourseCard` (medium size)
- Displayed props: `title`, `thumbnail`, `instructor`, `rating`, `studentCount`, `price`
- Additional display: `isBest` badge (every card)
- Not displayed: `progress` (this screen is for comparison)

### Per-permission branching
- **Not logged in**: no progress shown + "Log in to enroll" CTA
- **Logged in**: progress shown + "Continue learning" CTA

### When no data
- "No popular courses yet" + "See all courses" link

### Data source (API)
- `GET /api/courses?sort=popular&limit=12`
- **Caching**: 5 minutes (CDN)
- **Auth**: optional (if the auth header is present, the response includes progress)

---

## `{{DOMAIN_CODE}}-EXPERT-LIST` — Expert Q&A List

### Exposure policy
- **Sort**: newest (createdAt DESC) — default tab
- **Filter**: category tabs (All / FTA / Customs / Tariff / ...)
- **Count**: 20 per page
- **Pagination**: Mobile → LoadMore / Desktop → Numbered

### Components used
- `QuestionCard` (Medium size)
- Displayed props: `title`, `excerpt`, `author`, `createdAt`, `answerCount`, `viewCount`
- Additional display: `isAccepted`, `isHot`, `category`
- Not displayed: —

### Per-permission branching
- **Not logged in**: "Ask" CTA → on click, login modal
- **Regular user**: "Ask" CTA → check remaining tokens → write page
- **Answerer role**: highlight categories the user can answer

### When no data
- Overall EMPTY: "No questions yet. [Write your first question]"
- Category EMPTY: "No questions in this category yet"

### Data source (API)
- `GET /api/expert/questions?category={cat}&sort=latest&page={n}&limit=20`
- **Caching**: 1 minute (stale-while-revalidate)

---

## `{{DOMAIN_CODE}}-EXPERT-DETAIL-UC03` — Question Detail (Adopted)

### Exposure policy
- **Answer sort**: adopted answer at the top → upvoted → newest
- **Answer count limit**: none (infinite scroll)
- **Body**: Markdown rendering; images max 5MB × 10

### Components used
- `QuestionHeader` (author, date, category, view/answer counts)
- `AnswerCard` (answer list)
- `AcceptedBadge` (highlight the adopted answer)

### Per-permission branching
| Role | Edit/delete question | Write answer | Adopt answer | Edit answer |
|------|-----------------------|--------------|--------------|-------------|
| Not logged in | ❌ | ❌ | ❌ | ❌ |
| Regular user | ❌ | ✅ | ❌ | ❌ (own answer only) |
| Question owner | ✅ | ❌ (cannot answer own post) | ❌ (already adopted) | ❌ |
| Answerer | ❌ | ✅ | ❌ | ✅ (own answer) |
| Admin | ✅ (all) | ✅ | ❌ | ✅ (all) |

### When no data
- If there are 0 answers, branch to UC01 (separate ID)
- In UC03 there must be at least 1 answer

### Data source (API)
- `GET /api/expert/questions/{id}` — question + answer list (in one call)
- **Caching**: none (real-time)
- **Auth**: optional (when logged in, response includes `canEdit`, `canAnswer` flags)

---

## 15.2 Authoring item checklist

For every screen ID, all of the following must be defined:

- [ ] Exposure condition (what data is shown)
- [ ] Sort / filter / count limit
- [ ] Components used + props to display
- [ ] Per-permission branching (when applicable)
- [ ] Handling when no data
- [ ] Data source (API endpoint, caching)
- [ ] Time/event-driven changes (e.g., NEW badge 7-day rule)

---

## Common policies

### Badge exposure criteria
- `isNew`: within 7 days of registration
- `isHot`: 5+ answers within 24 hours or 100+ views
- `isBest`: top 10% within its category
- `isAccepted`: the answer adopted by the question owner
- `isPremium`: Pro-plan-only content

### Caching policy
| Data type | TTL | Invalidation trigger |
|-----------|-----|----------------------|
| Popular list | 5 min | manual admin purge |
| List (newest) | 1 min (SWR) | new post written |
| Detail | none (real-time) | — |
| User profile | 10 min | self-edit |

---

_TODO (UX/PM): Author business rules in the format above for every Registry ID of this feature. Once written, developers **must reference** this document while implementing._
