# Feature Definition Template

Instantiate this skeleton with the feature-structuring and story-map results, then write it to `{OUTPUT_DIR}/feature-definition.md`. Fill every `{...}` placeholder; keep the ID schemes (FG/FT/SF/RSK), the User Story Map ASCII, and the integrated traceability matrix intact.

## Sections in this template
- §1 Overview
- §2 Feature structure (feature tree)
- §3 User Story Map (ASCII story-map view + release-scope table)
- §4 Feature details (per Feature Group / Feature + sub-feature list)
- §5 Service policy (operation / data-handling / exception-handling)
- §6 Feature priority matrix (MoSCoW)
- §7 Risk analysis (register / response plan / constraints)
- §8 Integrated traceability matrix (feature ↔ requirement ↔ use-case ↔ screen)

~~~markdown
# Feature definition — {feature name}

## 1. Overview

| Item | Content |
|------|---------|
| Feature | {FEATURE_DESCRIPTION} |
| Authored | {today's date} |
| Base documents | market-analysis.md, interview-report.md, requirements-definition.md, usecase-definition.md, ia-screen-design.md |
| Feature Groups | {N} |
| Features | {N} |
| Sub-features | {N} |

## 2. Feature structure

### 2.1 Feature tree

```
{feature name}
├── FG-01: {Feature Group 1}
│   ├── FT-01-01: {Feature 1}
│   │   ├── SF-01-01-01: {Sub-feature 1}
│   │   └── SF-01-01-02: {Sub-feature 2}
│   └── FT-01-02: {Feature 2}
│       ├── SF-01-02-01: {Sub-feature 1}
│       └── SF-01-02-02: {Sub-feature 2}
├── FG-02: {Feature Group 2}
│   └── ...
```

## 3. User Story Map

### 3.1 Story-map view

```
┌─────────────────────────────────────────────────────────────────────┐
│ User          │ {Activity 1}       │ {Activity 2}       │ ...      │
│ Activities    │ (FG-01)            │ (FG-02)            │          │
├───────────────┼────────────────────┼────────────────────┼──────────┤
│ User          │ {Task 1-1}         │ {Task 2-1}         │          │
│ Tasks         │ {Task 1-2}         │ {Task 2-2}         │          │
├═══════════════╪════════════════════╪════════════════════╪══════════┤
│ MVP           │ • {Story 1-1-1}    │ • {Story 2-1-1}    │          │
│ (Release 1)   │ • {Story 1-2-1}    │                    │          │
├───────────────┼────────────────────┼────────────────────┼──────────┤
│ v1.1          │ • {Story 1-1-2}    │ • {Story 2-1-2}    │          │
│ (Release 2)   │                    │ • {Story 2-2-1}    │          │
├───────────────┼────────────────────┼────────────────────┼──────────┤
│ v1.2          │ • {Story 1-2-2}    │ • {Story 2-2-2}    │          │
│ (Release 3)   │                    │                    │          │
└───────────────┴────────────────────┴────────────────────┴──────────┘
```

### 3.2 Release-scope definition

| Release | Included features | Goal | Expected sub-feature count |
|---------|--------------------|------|-----------------------------|
| MVP (Release 1) | {core features list} | {minimum value delivery} | {N} |
| v1.1 (Release 2) | {additional features list} | {usability improvements} | {N} |
| v1.2 (Release 3) | {extended features list} | {sophistication} | {N} |

## 4. Feature details

### FG-01: {Feature Group name}

#### FT-01-01: {Feature name}

| Item | Content |
|------|---------|
| Feature ID | FT-01-01 |
| Name | {Feature name} |
| Description | {feature description} |
| Related requirements | FR-001, FR-002 |
| Related use cases | UC-001 |
| Related screens | SCR-001, SCR-002 |
| Related actors | {actor list} |
| Related KPI | {KPI} |
| Priority | Must / Should / Could |
| Implementation difficulty | high / medium / low |
| Release | MVP / v1.1 / v1.2 |

**Sub-feature list:**

| # | ID | Sub-feature | Description | Input | Output | Business rule / policy | Priority |
|---|----|-------------|-------------|-------|--------|--------------------------|----------|
| 1 | SF-01-01-01 | {sub-feature} | {description} | {input data} | {output data} | {business rule and service policy} | {priority} |
| 2 | SF-01-01-02 | {sub-feature} | {description} | {input data} | {output data} | {business rule and service policy} | {priority} |

(repeat for every Feature Group / Feature)

## 5. Service policy

### 5.1 Service-operation policy

| # | Policy item | Policy content | Related features | Notes |
|---|-------------|----------------|------------------|-------|
| 1 | {policy item} | {concrete policy} | FT-{N} | {notes} |
| 2 | {policy item} | {concrete policy} | FT-{N} | {notes} |

### 5.2 Data-handling policy

| # | Data item | Retention | Processing | Related features |
|---|-----------|-----------|-------------|--------------------|
| 1 | {data} | {duration} | {encryption / masking / deletion, etc.} | FT-{N} |

### 5.3 Exception-handling policy

| # | Exception | Handling | User-facing message | Related features |
|---|-----------|----------|----------------------|--------------------|
| 1 | {exception} | {handling} | {message} | FT-{N} |

## 6. Feature priority matrix (MoSCoW)

| Priority | Feature ID | Feature | Rationale |
|----------|------------|---------|-----------|
| **Must** | FT-01-01 | {Feature} | {rationale} |
| **Should** | FT-01-02 | {Feature} | {rationale} |
| **Could** | FT-02-01 | {Feature} | {rationale} |
| **Won't** | - | - | {reason for exclusion from this scope} |

## 7. Risk analysis

### 7.1 Risk register

| # | Risk ID | Risk | Type | Likelihood (1-5) | Impact (1-5) | Risk score | Response strategy |
|---|---------|------|------|-------------------|---------------|------------|--------------------|
| 1 | RSK-001 | {risk} | tech / schedule / resource / external | {score} | {score} | {likelihood × impact} | {avoid / transfer / mitigate / accept} |
| 2 | RSK-002 | {risk} | {type} | {score} | {score} | {score} | {strategy} |

### 7.2 Response plan

| Risk ID | Response strategy | Concrete actions | Owner | Trigger condition |
|---------|--------------------|-------------------|-------|--------------------|
| RSK-001 | {strategy} | {concrete actions} | {owner} | {when to start the response} |

### 7.3 Constraints

| # | Constraint type | Content | Affected features | Alternatives |
|---|-----------------|---------|---------------------|---------------|
| 1 | Technical | {constraint} | FT-{N} | {alternative} |
| 2 | Business | {constraint} | FT-{N} | {alternative} |

## 8. Feature ↔ requirement ↔ use-case ↔ screen integrated traceability matrix

| Feature ID | Feature | Requirement | JTBD | Use case | Screen | Actor | Pain point | KPI | Priority | Release |
|------------|---------|--------------|------|----------|--------|-------|------------|-----|----------|---------|
| FT-01-01 | {Feature} | FR-001 | J1 | UC-001 | SCR-001 | {actor} | PP-{N} | {KPI} | Must | MVP |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
~~~
