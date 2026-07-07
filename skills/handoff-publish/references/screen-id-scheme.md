# Screen ID Issuance Scheme (handoff-publish Step 2 detail)

Read this when designing or converting Screen IDs in Step 2.

## A. Screen ID format (PDF §6.1)

```
{DOMAIN}-{PAGE}-{SECTION}-UC{NN}
────   ─────   ───────   ────
domain page    section   use-case number (2 digits)

Example: ACAD-EXPERT-DETAIL-UC03
         ACAD-EXPERT-LIST
         ACAD-EXPERT-LIST-EMPTY
         ACAD-EXPERT-MODAL01
```

Detailed rules:
- `DOMAIN`: product abbreviation (decided in Step 1-B)
- `PAGE`: menu/route unit (uppercase Latin letters; hyphens allowed when necessary)
- `SECTION`: screen type — LIST / DETAIL / FORM / MODAL / DASHBOARD / SETTINGS, etc. Omit if not needed.
- `UC{NN}`: **state/case discriminator** on the same page (e.g., UC01=default, UC02=before adoption, UC03=adopted)
- State suffix: `-LOADING`, `-EMPTY`, `-ERROR` may be appended directly instead of UC

## B. Conversion rules for legacy SCR-NNN

If `docs/planner/.../ia-screen-design.md` contains `SCR-001`-style IDs, convert with these rules:

1. Read the screen's `Related UC`, `Type`, and `Screen Name` columns
2. PAGE = route or main feature keyword (e.g., `Expert Q&A list` → `EXPERT-LIST`)
3. SECTION = type mapping (list→LIST, detail→DETAIL, form→WRITE, modal→MODAL)
4. UC{NN} = the `Related UC` number, 2-digit zero-padded (UC-1 → UC01)
5. **Record the old/new mapping table as the first entry in `11-decision-log.md`** after conversion.

Example: `SCR-005` (question detail, adopted, UC-3) → `ACAD-EXPERT-DETAIL-UC03`

## C. Required screens (PDF §9.2)

Minimum screens that must be included in the Registry:

- Default screen (DEFAULT)
- All states (LOADING / EMPTY / DEFAULT / ERROR) — State Matrix expansion
- All modals (Confirm / Form / Error included)
- Edge-case screens
- Hidden screens reachable only via URL parameters

If the planning document's screen list does not cover the above, warn the user:

```
⚠️ The following screens are missing from the planning document:
- {SCREEN-ID}-LOADING (loading state)
- {SCREEN-ID}-EMPTY (empty state)
- {SCREEN-ID}-ERROR (error state)

They will be added to the Registry as placeholders with "🔄 not started" status.
Proceed? (yes/no)
```
