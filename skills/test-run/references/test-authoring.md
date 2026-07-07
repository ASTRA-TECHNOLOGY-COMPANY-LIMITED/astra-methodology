# Step 4 — Test Case Template & Types

Detail for SKILL.md Step 4C. Write test cases in
`docs/tests/test-cases/sprint-{N}/` on the **current** branch (dev merge is
`/pr-merge`'s job). `{N}` is the highest sprint number found by scanning
`docs/sprints/sprint-{N}-{name}/`.

## Test case template

```markdown
# {Feature Name} Test Cases

## TC-001: {Test Case Title}
- **Preconditions**: {required pre-state}
- **Test Steps**:
  1. {step 1}
  2. {step 2}
- **Expected Result**: {expected outcome}
- **Verification Method**: snapshot / console / network / server-log

## TC-002: {Test Case Title}
...
```

## Test case types

| Type | Description | Example |
|------|------|------|
| Page Load | Page access and rendering verification | Main page 200 response |
| Form Submission | Input validation and submit behavior | Successful registration form submission |
| CRUD Operations | Data create/read/update/delete | Post creation reflected in list |
| Auth Flow | Login/logout/permission verification | Redirect when not logged in |
| Error Handling | Behavior on invalid input/access | 404 page display |
| Responsive | Layout verification per viewport | Menu collapse on mobile |
