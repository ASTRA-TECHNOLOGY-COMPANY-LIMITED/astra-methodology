# Sprint 1 Prompt Map

## Sprint Goal
[Describe the business value to be achieved in this sprint]

## Feature 1: {Feature Name}

### 1.1 Design Prompt
```
/feature-dev "Write a design document for {feature description}
at docs/blueprints/{feature-name}.md.
{Detailed requirements}
Refer to docs/database/database-design.md for DB schema.
Do not modify code yet."
```

### 1.2 DB Design Prompt
```
/feature-dev "Add/update {module name} tables in
docs/database/database-design.md:
- {Table list}
- Also update the ERD and FK relationship summary. Follow the standard terminology dictionary.
Do not modify code yet."
```

### 1.3 Test Case Prompt
```
/feature-dev "Based on the functional requirements in docs/blueprints/{feature-name}.md,
write test cases at docs/tests/test-cases/sprint-1/{feature-name}-test-cases.md.
Use Given-When-Then format, include unit/integration/edge cases.
Do not modify code yet."
```

### 1.4 Implementation Prompt
```
/feature-dev "Strictly follow docs/blueprints/{feature-name}.md and
docs/database/database-design.md to proceed with development.
Write tests referencing docs/tests/test-cases/sprint-1/{feature-name}-test-cases.md,
and once implementation is complete, run all tests and
report results to docs/tests/test-reports/."
```

## Feature 2: {Feature Name}

### 2.1 Design Prompt
```
```

### 2.2 DB Design Prompt
```
```

### 2.3 Test Case Prompt
```
```

### 2.4 Implementation Prompt
```
```

---

> **Writing Guide**: VA and PE fill this in together during the Planning meeting.
> 5 elements of a good prompt: What (what to do), Why (purpose), Constraint (restrictions), Reference (references), Acceptance (criteria)
