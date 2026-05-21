# 9. IA / Sitemap — Information Architecture

**Feature**: {{FEATURE_NAME}}
**Last updated**: {{TODAY}}

> **Why is this needed?** If designers/developers don't know the **rationale** for the menu structure, they arbitrarily rearrange it or add new entry points. The IA is the skeleton of the whole product, so it is managed as a separate document.

---

## What to include

- Full sitemap (tree structure)
- GNB / LNB / Bottom Tab structure
- Menu depth policy (max 3 depth Recommended)
- URL conventions (`/{{DOMAIN_CODE}}/expert/[id]`)
- Per-permission menu exposure rules
- Review procedure for adding a new menu (UX approval required)

---

## Full sitemap

```
{{PROJECT_NAME}}
├── /academy                       Home (marketing mode / feed mode)
├── /academy/courses               Education
│   └── /[id]                     Course detail
│       ├── /apply               Apply
│       └── /learn               Learn
├── /academy/insight               Trade insights
│   ├── ?tab=insight              AI insights
│   └── ?tab=notice               Notices
├── /academy/community             Community
│   ├── /[id]                    Post detail
│   ├── /write                   Write post
│   └── /bookmarks               Bookmarks
├── /academy/expert                Expert Q&A  ← scope of this handoff
│   ├── /[id]                    Question detail
│   ├── /ask                     Ask question
│   └── /dashboard               My-questions dashboard
└── /academy/tools                 Trade tools
```

---

## GNB / LNB / Bottom Tab structure

### GNB (Global Navigation Bar)
- **Desktop**: fixed top (logo / 1-depth menu / search / notifications / profile)
- **Tablet**: fixed top + hamburger menu (2-depth access)
- **Mobile**: fixed top (logo + notifications + profile only) + Bottom Tab Bar

### LNB (Left Navigation Bar)
- **Desktop**: left sidebar (2–3 depth menu)
- **Tablet**: included within the hamburger menu
- **Mobile**: not used → replaced by Bottom Tab

### Bottom Tab (Mobile only)
- Max 5 tabs
- Current plan: Home / Education / Q&A / Community / Profile
- Badge after the tab: notification count or NEW badge

---

## Menu-depth policy

- **Max 3 depth**: beyond that, use sidebar expand/collapse or accordions
- **Expose up to 2 depth directly in GNB/LNB**; 3 depth is handled by tabs/filters after entering the sub-page
- **When depth is exceeded**: consider restructuring the IA after UX review

---

## URL conventions

| Pattern | Purpose | Example |
|---------|---------|---------|
| `/{{DOMAIN_CODE}}` | Home | `/academy` |
| `/{{DOMAIN_CODE}}/{resource}` | List | `/academy/expert` |
| `/{{DOMAIN_CODE}}/{resource}/[id]` | Detail | `/academy/expert/123` |
| `/{{DOMAIN_CODE}}/{resource}/create` or `/ask` | Create | `/academy/expert/ask` |
| `/{{DOMAIN_CODE}}/{resource}/[id]/edit` | Edit | `/academy/expert/123/edit` |
| `?tab={value}` | Tab filter | `/academy/insight?tab=notice` |
| `?category={value}&sort={value}` | List filter | `/academy/expert?category=fta&sort=latest` |

**Principles**:
- kebab-case (e.g., `/my-dashboard`, not `/myDashboard`)
- Plural resource names (e.g., `/courses`, not `/course`)
- Filters as query parameters
- Minimize verbs (express state as a tab/state within the detail page)

---

## Per-permission menu exposure

| Menu | Not logged in | Regular | Pro | Admin |
|------|---------------|---------|-----|-------|
| Home (/academy) | ✅ | ✅ | ✅ | ✅ |
| Education | ✅ | ✅ | ✅ | ✅ |
| Insights | ✅ (free only) | ✅ (free only) | ✅ (all) | ✅ |
| Community | ✅ (view only) | ✅ | ✅ | ✅ |
| Expert Q&A | ✅ (view only) | ✅ | ✅ | ✅ |
| Trade tools | ❌ | ✅ (some) | ✅ (all) | ✅ |
| Admin dashboard | ❌ | ❌ | ❌ | ✅ |

---

## Procedure for adding a new menu

1. **Proposal**: PM/UX proposes in the Slack #fect-academy-design channel
2. **Review**: UX Lead reviews (IA impact / duplication / permission policy)
3. **Approval**: when UX Lead approves, update `9-ia-sitemap.md`
4. **Registry update**: add the new screen ID to `1-screen-registry.md`
5. **Share**: record the decision in `11-decision-log.md`
6. **Notify**: share in Slack (UI/Dev acknowledge)

---

## Principles

- IA changes **require UX approval** (including simple page additions)
- URL changes **must be agreed with the dev team in advance** (SEO + external-link impact)
- When changing an existing URL, **keep a 301 redirect** for at least 6 months

---

_TODO (UX): The sitemap above is an example written against {{PROJECT_NAME}}. Keep only the IA parts that connect to this feature and remove the rest._
