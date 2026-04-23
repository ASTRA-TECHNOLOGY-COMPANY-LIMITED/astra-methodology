---
description: Selects the working language (Korean/Vietnamese/English) for ASTRA workflow document generation, templates, and user-facing messages
argument-hint: "[ko | vi | en] (optional — interactive prompt is shown if omitted)"
allowed-tools: AskUserQuestion
---

# Language Selection for ASTRA Workflow

Select the language to use for all generated documents, templates, and user-facing messages in the current ASTRA workflow. This command is intended to be reusable across any skill that produces multilingual deliverables (e.g., `/project-init`, `/sprint-plan`, `/manual-generator`, `/catalog-generator`, `/service-planner`).

## Procedure

### Step 1: Parse Argument (if provided)

If `$ARGUMENTS` is provided, normalize and resolve it without showing an interactive prompt:

| Input (case-insensitive) | Resolved Language | Code | Locale |
|---|---|---|---|
| `ko`, `kor`, `korean`, `한국어` | 한국어 (Korean) | `ko` | `ko-KR` |
| `vi`, `vie`, `vietnamese`, `tiếng việt`, `tieng viet` | Tiếng Việt (Vietnamese) | `vi` | `vi-VN` |
| `en`, `eng`, `english` | English | `en` | `en-US` |

If the argument is unrecognized, fall through to Step 2 (interactive prompt).

### Step 2: Interactive Prompt (if no argument or unrecognized argument)

Use `AskUserQuestion` to present the trilingual prompt below. The question text MUST stay trilingual so that any user — regardless of which language they read — can understand the choice on first sight.

```
프로젝트에 사용할 언어를 선택해 주세요.
Vui lòng chọn ngôn ngữ để sử dụng cho dự án.
Please select a language to use for the project.

1. 한국어 (Korean)
2. Tiếng Việt (Vietnamese)
3. English
```

Map the user's choice as follows:

| User Choice | Resolved Language | Code | Locale |
|---|---|---|---|
| 1 | 한국어 (Korean) | `ko` | `ko-KR` |
| 2 | Tiếng Việt (Vietnamese) | `vi` | `vi-VN` |
| 3 | English | `en` | `en-US` |

### Step 3: Output the Selection

Output the result in the following exact structured format. This format is the **contract** that calling skills/commands rely on to parse the selected language — do not change the field names or markdown structure.

```
## Selected Language

- **Language Name**: {한국어 / Tiếng Việt / English}
- **Language Code**: {ko / vi / en}
- **Locale**: {ko-KR / vi-VN / en-US}

All subsequent generated documents, templates, and user-facing messages must be written in the selected language. Technical identifiers (tool names, file paths, command names, code identifiers, code comments) remain untranslated.
```

## Usage

### Standalone (user-invoked)

```
/select-language          # interactive trilingual prompt
/select-language ko       # non-interactive — Korean
/select-language vi       # non-interactive — Vietnamese
/select-language en       # non-interactive — English
/select-language Korean   # non-interactive — Korean (full name)
```

### From other skills (Skill tool)

Invoke this command via the `Skill` tool, then parse the `## Selected Language` block from the result. Apply the selected language to all downstream steps in the calling skill.

Example call sites:
- `/project-init` — Step 0
- `/sprint-plan` — initial language confirmation
- `/manual-generator` — manual writing language
- `/catalog-generator` — catalog copy language
- `/service-planner` — planning deliverable language

## Notes

- This command does NOT persist the selection to disk. The calling skill is responsible for persisting the language to the project's `CLAUDE.md` (`## Language` section) when appropriate.
- For the "Language Name" field, always use the localized self-name (한국어, Tiếng Việt, English) so that downstream documents render the language label naturally.
- If a calling skill needs the selection to be implicit (e.g., already detected from project `CLAUDE.md`), it should skip invoking this command and reuse the persisted language directly.
