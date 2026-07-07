# Requirements Definition Template

Instantiate this skeleton with the selected ideas and KPI/OKR/JTBD analysis, then write it to `{OUTPUT_DIR}/requirements-definition.md`. Fill every `{...}` placeholder; keep the ID schemes (O/KR/J/FR/NFR/IDEA/PP) and the traceability matrix intact.

```markdown
# Requirements definition — {feature name}

## 1. Overview

| Item | Content |
|------|---------|
| Feature | {FEATURE_DESCRIPTION} |
| Authored | {today's date} |
| Base documents | market-analysis.md, interview-report.md |
| Selected ideas | {N} |

## 2. Success metrics (KPI / OKR)

### 2.1 Business objectives

| # | Objective | Description | Related strategy |
|---|-----------|-------------|------------------|
| O1 | {objective} | {description} | {refer to SWOT strategy} |
| O2 | {objective} | {description} | {refer to SWOT strategy} |

### 2.2 Key results

| # | Parent objective | Key result | Current | Target | Measurement |
|---|------------------|------------|---------|--------|-------------|
| KR1 | O1 | {measurable result} | {baseline or N/A} | {target} | {method} |
| KR2 | O1 | {measurable result} | {baseline or N/A} | {target} | {method} |
| KR3 | O2 | {measurable result} | {baseline or N/A} | {target} | {method} |

### 2.3 KPI dashboard items

| # | KPI | Description | Cadence | Target threshold | Related KR |
|---|-----|-------------|---------|-------------------|------------|
| 1 | {KPI} | {description} | daily/weekly/monthly | {threshold} | KR{N} |

## 3. JTBD (Jobs-to-be-Done) summary

| # | Job Statement | Related pain points | Current resolution | Expected resolution | Related ideas |
|---|---------------|----------------------|---------------------|---------------------|----------------|
| J1 | When {context}, I want to {motivation}, so I can {outcome} | PP-{N} | {1-5} | {1-5} | IDEA-{N} |
| J2 | When {context}, I want to {motivation}, so I can {outcome} | PP-{N} | {1-5} | {1-5} | IDEA-{N} |

## 4. Functional requirements

### FR-001: {requirement title}

| Item | Content |
|------|---------|
| ID | FR-001 |
| Name | {title} |
| Description | {detailed description} |
| Related idea | IDEA-{N} |
| Related pain point | PP-{N} |
| Related JTBD | J{N} |
| Related actors | {actor list} |
| Priority | Must / Should / Could |
| Acceptance criteria | {acceptance criteria list} |
| Related KPI | {KPI} |

(repeat for every requirement)

## 5. Non-functional requirements

### NFR-001: {requirement title}

| Item | Content |
|------|---------|
| ID | NFR-001 |
| Type | performance / security / usability / accessibility / compatibility |
| Name | {title} |
| Description | {detailed description} |
| Measurement criterion | {measurable criterion} |
| Priority | Must / Should / Could |

## 6. Requirements traceability matrix

| Req ID | Name | Pain point | JTBD | Idea | Actor | KPI | Priority |
|--------|------|------------|------|------|-------|-----|----------|
| FR-001 | {title} | PP-{N} | J{N} | IDEA-{N} | {actor} | {KPI} | {priority} |
| ... | ... | ... | ... | ... | ... | ... | ... |
```
