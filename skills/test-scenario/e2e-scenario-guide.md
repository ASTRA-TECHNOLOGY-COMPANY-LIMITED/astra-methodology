# E2E Test Scenario Design Guide

> Reference guide for designing comprehensive E2E test scenarios.
> Used by the `test-scenario` skill during scenario generation.

## 1. Scenario Types

### 1.1 Happy Path
- **Definition**: The standard, expected user flow that achieves the primary goal
- **Coverage**: Must cover 100% of core business scenarios
- **Priority**: Always Critical or High
- **Example**: User signs up with valid data -> receives confirmation -> can log in

### 1.2 Alternative Path
- **Definition**: Valid but non-standard flows that still achieve the goal
- **Coverage**: Cover the most common alternative paths
- **Priority**: Typically Medium
- **Example**: User signs up using social login instead of email/password

### 1.3 Edge Case
- **Definition**: Boundary conditions, empty states, and unusual but valid inputs
- **Coverage**: Focus on data boundaries and state transitions
- **Priority**: Medium or Low
- **Examples**:
  - Empty list display (no items yet)
  - Maximum length input values
  - Concurrent access to the same resource
  - Timezone-sensitive date operations
  - Unicode/special character handling

### 1.4 Error Path
- **Definition**: Invalid inputs, unauthorized access, and failure recovery
- **Coverage**: Cover all user-visible error states
- **Priority**: High for security-related, Medium for validation errors
- **Examples**:
  - Invalid form submission (missing required fields)
  - Unauthorized access to protected pages
  - API server error handling (500 responses)
  - Network timeout behavior
  - Session expiration handling

### 1.5 Security Scenarios
- **Definition**: Authentication bypass, authorization escalation, injection attempts
- **Coverage**: Cover OWASP Top 10 relevant to the feature
- **Priority**: Critical or High
- **Examples**:
  - Access admin pages without admin role
  - Modify another user's data via API
  - XSS input in form fields
  - CSRF token validation

### 1.6 Performance Scenarios
- **Definition**: Load time, response time, and resource usage under normal conditions
- **Coverage**: Cover key user-facing pages and operations
- **Priority**: Medium
- **Examples**:
  - Page load time under 3 seconds
  - API response time under 1 second
  - List page with 100+ items renders smoothly

## 2. User Journey Mapping

### 2.1 Mapping Process

```
1. Identify user roles (guest, member, admin, etc.)
2. For each role, list the primary goals
3. For each goal, trace the page-by-page journey
4. At each page, identify:
   - Entry conditions (how the user arrives)
   - Actions available (buttons, forms, links)
   - Exit conditions (where the user goes next)
   - Data changes (API calls, DB writes)
```

### 2.2 Journey Documentation Pattern

```
User Journey: {Journey Name}
  Role: {user role}
  Goal: {what the user wants to achieve}

  Page 1: {page name} ({URL})
    -> Action: {user action}
    -> API: {API call triggered}
    -> DB: {data change}
    -> Next: Page 2

  Page 2: {page name} ({URL})
    -> Action: {user action}
    -> ...
```

### 2.3 Common Journey Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| CRUD Flow | Create -> Read -> Update -> Delete | Post management |
| Auth Flow | Register -> Login -> Access -> Logout | User authentication |
| Wizard Flow | Step 1 -> Step 2 -> ... -> Confirm | Multi-step form |
| Search Flow | Search -> Filter -> Sort -> Select | Product catalog |
| Transaction Flow | Select -> Confirm -> Process -> Receipt | Payment processing |

## 3. Verification Points by Layer

### 3.1 Frontend (UI) Verification

| Check Point | Verification Method | Example |
|-------------|-------------------|---------|
| Page rendered correctly | snapshot | All key elements present |
| Form validation messages | snapshot | Error message displayed for invalid input |
| Loading states | snapshot | Spinner shown during API call |
| Navigation | snapshot | Correct page after button click |
| Responsive layout | snapshot + resize | Layout intact at mobile/tablet/desktop |
| Accessibility | snapshot (verbose) | ARIA labels, keyboard navigation |

### 3.2 Backend (API) Verification

| Check Point | Verification Method | Example |
|-------------|-------------------|---------|
| Correct HTTP status | network | 200 for success, 401 for unauthorized |
| Response body structure | network | Required fields present in JSON |
| Request headers | network | Authorization token sent |
| API call sequence | network | Correct order of dependent calls |
| Error response format | network | Consistent error response structure |

### 3.3 Database Verification

| Check Point | Verification Method | Example |
|-------------|-------------------|---------|
| Record created | server-log / db-query | New row in users table |
| Record updated | server-log / db-query | Status changed from PENDING to ACTIVE |
| Record deleted | server-log / db-query | Soft delete flag set |
| Referential integrity | server-log / db-query | FK constraints maintained |
| Audit trail | server-log / db-query | Created/updated timestamps set |

### 3.4 Server Log Verification

| Check Point | Verification Method | Example |
|-------------|-------------------|---------|
| No unexpected errors | server-log | No ERROR/FATAL in logs |
| SQL queries executed | server-log | Expected queries logged |
| N+1 query detection | server-log | No repeated similar queries |
| Response time | server-log | Within acceptable range |
| Security events | server-log | Login attempts logged |

## 4. Priority Decision Criteria

| Priority | Criteria | Examples |
|----------|----------|---------|
| **Critical** | Core business flow; failure = service unusable | Login, payment, data creation |
| **High** | Important feature; failure = significant user impact | Search, form validation, auth errors |
| **Medium** | Supporting feature; failure = degraded experience | Sorting, filtering, responsive layout |
| **Low** | Nice-to-have; failure = minor inconvenience | Animations, tooltips, empty states |

### Priority Assignment Rules

1. All Happy Path scenarios for core features: **Critical**
2. All Error Path scenarios for security features: **Critical** or **High**
3. All Happy Path scenarios for secondary features: **High**
4. All Alternative Path scenarios: **Medium**
5. All Edge Case scenarios: **Medium** or **Low**
6. Performance scenarios: **Medium**

## 5. Integration with test-run Skill

### 5.1 Scenario-to-Test Mapping

The E2E scenarios generated by `test-scenario` are designed to be directly executable by the `/test-run` skill:

| Scenario Element | test-run Execution |
|-----------------|----------------------|
| User Journey steps | Chrome MCP navigation + interaction |
| UI Expected Results | `take_snapshot` verification |
| API Expected Results | `list_network_requests` + `get_network_request` |
| DB Expected Results | Server log analysis |
| Server Log Expected Results | `TaskOutput` log checking |

### 5.2 Execution Workflow

```
1. /test-scenario auth                <- Generate scenarios
2. /test-run auth                      <- Execute scenarios in browser
3. test-coverage-analyzer agent     <- Verify coverage
```

### 5.3 Verification Method Reference

| Method | Tool | When to Use |
|--------|------|-------------|
| `snapshot` | `take_snapshot` | Verify page content and structure |
| `console` | `list_console_messages` | Check for JavaScript errors |
| `network` | `list_network_requests` | Verify API calls and responses |
| `server-log` | `TaskOutput` | Check backend logs for errors/queries |
| `db-query` | Server log SQL analysis | Verify data persistence |

## 6. Test Data Guidelines

### 6.1 Test Data Principles

- Use realistic but clearly fake data (e.g., `test-user@example.com`, not real emails)
- Include boundary values (min, max, empty, null)
- Cover different character sets if internationalization is relevant
- Avoid hardcoding sensitive data (passwords, tokens)

### 6.2 Common Test Data Patterns

| Data Type | Valid Examples | Invalid Examples |
|-----------|--------------|-----------------|
| Email | `user@example.com` | `invalid-email`, `@no-local.com` |
| Phone (E.164) | `+821012345678` | `010-1234-5678`, `12345` |
| Password | `Test@1234!` (meets policy) | `123` (too short), `password` (too weak) |
| Date | `2024-01-15` (ISO 8601) | `01/15/2024`, `yesterday` |
| Amount | `10000`, `0`, `999999999` | `-1`, `abc`, `1.234` |
