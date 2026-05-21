# 2. Flows — User Flow Definitions

**Feature**: {{FEATURE_NAME}}
**Last updated**: {{TODAY}}

> Specify the result of every button click (including success/failure branches).
> Authoring principles:
> - Map the result of every click / submit / action to a Screen ID
> - Do not miss success / failure / exception branches
> - The designer should never have to ask "what's the next screen?"

---

## Main Flow 1: Ask Question Flow

```
[Ask Question Flow]

{{DOMAIN_CODE}}-EXPERT-LIST
    └ Click "Ask"
        ├ (not logged in) → {{DOMAIN_CODE}}-EXPERT-MODAL-LOGIN
        └ (logged in)     → {{DOMAIN_CODE}}-EXPERT-WRITE
                              └ Click "Submit"
                                  ├ (success)         → {{DOMAIN_CODE}}-EXPERT-LIST (new question shown)
                                  ├ (insufficient tokens) → {{DOMAIN_CODE}}-EXPERT-MODAL02
                                  └ (network error)   → {{DOMAIN_CODE}}-EXPERT-WRITE-ERROR
```

---

## Main Flow 2: Adopt Answer Flow

```
[Adopt Answer Flow]

{{DOMAIN_CODE}}-EXPERT-DETAIL-UC02 (before adoption)
    └ Click the "Adopt" button on the answer card
        ├ (own question & adoptable)  → confirm modal
        │   └ Click "Confirm adopt"
        │       ├ (success) → {{DOMAIN_CODE}}-EXPERT-DETAIL-UC03 (adopted)
        │       └ (failure) → error toast (modal stays)
        ├ (not own question)          → button disabled (not clickable)
        └ (already adopted)           → button hidden
```

---

## Main Flow 3: Delete Question Flow

```
[Delete Question Flow]

{{DOMAIN_CODE}}-EXPERT-DETAIL-*
    └ Click "Delete" menu (only shown for the question owner)
        └ {{DOMAIN_CODE}}-EXPERT-MODAL01 (delete confirmation)
            ├ Click "Delete"
            │   ├ (success) → {{DOMAIN_CODE}}-EXPERT-LIST (toast: "Deleted")
            │   └ (failure) → error toast (modal stays)
            └ Click "Cancel" → close modal (stay on DETAIL)
```

---

## Authoring principles

- **Map every click / submit / action result to an ID**: even a single click must not be missing a result screen
- **Do not miss success / failure / exception branches**: especially network errors, insufficient permissions, insufficient tokens
- **Represent state transitions as different UCs under the same ID**: e.g., UC01 (no answers) → UC02 (before adoption) → UC03 (adopted)
- **Include hidden screens**: screens reachable only via URL parameters or shown only under specific conditions

---

## Flow diagram (Mermaid — optional)

```mermaid
flowchart LR
    LIST[{{DOMAIN_CODE}}-EXPERT-LIST]
    WRITE[{{DOMAIN_CODE}}-EXPERT-WRITE]
    LOGIN[{{DOMAIN_CODE}}-EXPERT-MODAL-LOGIN]
    LIST_SUCCESS[{{DOMAIN_CODE}}-EXPERT-LIST<br/>new question shown]
    WRITE_ERR[{{DOMAIN_CODE}}-EXPERT-WRITE-ERROR]
    MODAL02[{{DOMAIN_CODE}}-EXPERT-MODAL02]

    LIST -->|"Ask (not logged in)"| LOGIN
    LIST -->|"Ask (logged in)"| WRITE
    WRITE -->|"submit success"| LIST_SUCCESS
    WRITE -->|"network error"| WRITE_ERR
    WRITE -->|"insufficient tokens"| MODAL02
```

---

_TODO (UX): Beyond the 3 flows above, add every additional scenario for this feature (edit, report, bookmark, etc.)._
