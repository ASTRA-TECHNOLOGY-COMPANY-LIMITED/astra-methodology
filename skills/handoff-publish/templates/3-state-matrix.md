# 3. State Matrix — State + Permission Definitions

**Feature**: {{FEATURE_NAME}}
**Last updated**: {{TODAY}}

> Every screen is defined not as a static screen but as a combination of **State × Permission × Device**.

---

## 11.1 State definitions (common to every data screen)

| State | Definition | Design required |
|-------|------------|-----------------|
| `LOADING` | Awaiting API response (skeleton) | ✅ required |
| `EMPTY` | Zero data | ✅ required |
| `DEFAULT` | Has data (base case) | ✅ required |
| `ERROR` | Data load failure | ✅ required |
| `PARTIAL` | Only partial permission (when applicable) | conditional |

> **Rule**: if any of the 4 states above is missing a design, DoD is not met. Register a separate ID per state in the Registry.

---

## 11.2 Permission matrix example (question detail)

| Action | Not logged in | Regular user | Question owner | Answerer | Admin |
|--------|---------------|--------------|----------------|----------|-------|
| View | ✅ | ✅ | ✅ | ✅ | ✅ |
| Write answer | ❌ | ✅ | ❌ | ✅ | ✅ |
| Edit | ❌ | ❌ | ✅ | ❌ | ✅ |
| Delete | ❌ | ❌ | ✅ | ❌ | ✅ |
| Adopt | ❌ | ❌ | ✅ | ❌ | ❌ |
| Report | ❌ | ✅ | ❌ | ❌ | ✅ |
| View edit history | ❌ | ❌ | ✅ | ❌ | ✅ |

→ **When UI differs by permission**, split the ID or specify it in the "State/Case" column of `1-screen-registry.md`.

---

## State × Permission combinations

For each Registry ID, enumerate the possible combinations:

| Screen ID | State | Permission | Design required | Notes |
|-----------|-------|------------|------------------|-------|
| `{{DOMAIN_CODE}}-EXPERT-LIST` | DEFAULT | not logged in | ✅ | progress/bookmark hidden |
| `{{DOMAIN_CODE}}-EXPERT-LIST` | DEFAULT | logged in | ✅ | progress/bookmark shown |
| `{{DOMAIN_CODE}}-EXPERT-LIST-LOADING` | LOADING | common | ✅ | skeleton |
| `{{DOMAIN_CODE}}-EXPERT-LIST-EMPTY` | EMPTY | common | ✅ | "Write your first question" CTA |
| `{{DOMAIN_CODE}}-EXPERT-LIST-ERROR` | ERROR | common | ✅ | "Retry" button |
| `{{DOMAIN_CODE}}-EXPERT-DETAIL-UC01` | DEFAULT | question owner | ✅ | edit/delete menu shown |
| `{{DOMAIN_CODE}}-EXPERT-DETAIL-UC02` | DEFAULT | question owner | ✅ | adopt button enabled |
| `{{DOMAIN_CODE}}-EXPERT-DETAIL-UC03` | DEFAULT | common | ✅ | adopted badge |

---

## State implementation principles (Dev reference)

Developers must implement explicit state branching for every data screen:

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

**Forbidden patterns**:
- ❌ Rendering immediately without a LOADING state (causes flicker)
- ❌ Treating EMPTY and ERROR with the same UI (user confusion)
- ❌ Handling permission branching only on the client (server-side validation required)

---

_TODO (UX): Beyond the permission matrix example (question detail) above, author a permission matrix for every major screen of this feature._
