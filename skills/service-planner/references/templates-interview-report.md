# Interview Report Template

Instantiate this skeleton with the persona-interview and pain-point results, then write it to `{OUTPUT_DIR}/interview-report.md`. Fill every `{...}` placeholder; keep the PP-ID scheme and table structures intact.

```markdown
# Interview report — {feature name}

## 1. Overview

| Item | Content |
|------|---------|
| Feature | {FEATURE_DESCRIPTION} |
| Interview date | {today's date} |
| Actors interviewed | {selected actor list} |
| Number of personas | {actor count × 3} |

## 2. Persona profiles

### 2.1 {actor 1}

#### Persona 1: {name} ({age}, {occupation})
| Item | Content |
|------|---------|
| Tech literacy | {beginner / intermediate / advanced} |
| Usage context | {mobile / desktop / hybrid} |
| Core goal | {goal} |
| Frustrations | {frustrations} |
| Traits | {traits} |

(repeat the same format for persona 2, 3)

### 2.2 {actor 2}
(same format)

## 3. Interview details

### 3.1 {actor 1}

#### Persona 1: {name}

| # | Question | Answer |
|---|----------|--------|
| 1 | {question} | {answer} |
| 2 | {question} | {answer} |
| ... | ... | ... |

(repeat for every persona)

## 4. Pain-point analysis

### 4.1 Per-actor core pain points

#### {actor 1}
| # | Pain point | Severity (1-5) | Frequency (1-5) | Scope of impact |
|---|------------|----------------|------------------|------------------|
| 1 | {pain point} | {score} | {score} | {scope} |
| ... | ... | ... | ... | ... |

### 4.2 Per-actor interest keywords

| Actor | Keyword 1 | Keyword 2 | Keyword 3 | Keyword 4 | Keyword 5 |
|-------|-----------|-----------|-----------|-----------|-----------|

### 4.3 Task analysis

| # | Task | Importance | Time | Frequency | Core pain point |
|---|------|------------|------|-----------|------------------|

### 4.4 Top 10 overall integrated pain points

| PP-ID | Rank | Pain point | Related actor | Severity | Resolution priority |
|-------|------|------------|----------------|----------|---------------------|
| PP-001 | 1 | {pain point} | {actor} | {score} | {high/med/low} |
| PP-002 | 2 | {pain point} | {actor} | {score} | {high/med/low} |
| ... | ... | ... | ... | ... | ... |
```
