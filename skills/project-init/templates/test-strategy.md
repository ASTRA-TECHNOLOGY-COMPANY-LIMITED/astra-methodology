# Test Strategy

> Defines the project's test scope, strategy, and criteria.
> Feature-specific test case documents are added under `docs/tests/test-cases/sprint-{N}/` during feature sprints.

## 1. Test Level Definitions

### 1.1 Unit Test

- **Scope**: Individual functions, methods, class level
- **Purpose**: Verify correctness of business logic
- **Target**: Service layer, utilities, domain logic
- **Excluded**: Controllers, repositories (covered in integration tests)

### 1.2 Integration Test

- **Scope**: API endpoints, DB connectivity, external service integration
- **Purpose**: Verify inter-module interactions
- **Target**: REST API, database CRUD, authentication/authorization flows

### 1.3 E2E Test (End-to-End Test)

- **Scope**: Complete user scenario flows
- **Purpose**: Confirm feature behavior from the actual user's perspective
- **Target**: Core business scenarios (Sign up → Login → Order → Payment)

## 2. Test Coverage Goals

| Level | Target | Coverage Goal |
|-------|--------|---------------|
| Unit Test | Service layer | 70%+ |
| Unit Test | Core business logic | 90%+ |
| Integration Test | API endpoints | 100% of main paths |
| E2E Test | Core scenarios | 100% of main scenarios |

## 3. Test Naming Rules

Follows the **Given-When-Then pattern**:

```
# Java/Kotlin
@Test
void given_validUserInfo_when_signupRequest_then_returnsSuccessResponse()

# TypeScript/JavaScript
describe('Signup', () => {
  it('returns a success response when requested with valid user info', () => {})
})

# Python
def test_given_valid_user_info_when_signup_then_returns_success():
```

## 4. Test Environment Setup

### 4.1 Test DB

- Use a dedicated test database (separate from production DB)
- Initialize schema before test execution
- Generate schema based on DDL from `docs/database/database-design.md`

### 4.2 Mock Server

- Replace external API integrations with mock servers
- Payment gateway API, SMS API, email API, etc.

### 4.3 Test Data Management

- **Fixture pattern**: Define static test data
- **Factory pattern**: Generate dynamic test data
- Ensure data isolation between tests

## 5. Test Scope by Module

### 5.1 Authentication Module

| Scenario | Test Level | Priority |
|----------|-----------|----------|
| Sign up (normal) | Unit + Integration | High |
| Sign up (duplicate email) | Unit + Integration | High |
| Login (normal) | Unit + Integration | High |
| Login (wrong password) | Unit + Integration | High |
| Token refresh | Unit + Integration | High |
| Token expiration handling | Unit | Medium |

### 5.2 Payment Module

| Scenario | Test Level | Priority |
|----------|-----------|----------|
| Payment success | Unit + Integration | High |
| Payment failure (insufficient balance) | Unit + Integration | High |
| Payment retry | Unit | High |
| Refund processing | Unit + Integration | High |

### 5.3 Order Module

| Scenario | Test Level | Priority |
|----------|-----------|----------|
| Order creation | Unit + Integration | High |
| Order cancellation | Unit + Integration | High |
| Order status change | Unit | Medium |

> **Feature-specific test case documents are added to `docs/tests/test-cases/sprint-{N}/` during feature sprints.**
> Test cases are pre-defined based on the functional requirements from design documents (blueprints),
> and AI references this document when generating code and tests simultaneously.

## 6. Automation Scope

### 6.1 CI/CD Pipeline

```
On PR creation:
  ├─ Run all unit tests
  ├─ Run all integration tests
  ├─ Generate code coverage report
  └─ Block PR if coverage falls below threshold

On merge to main branch:
  ├─ Run E2E tests
  └─ Record test results in docs/tests/test-reports/
```

### 6.2 Test Result Reporting

- Record test results per sprint in `docs/tests/test-reports/sprint-{N}-report.md`
- Include pass/fail status by module, coverage summary, and discovered issues

---

> **Update Rules**:
> 1. Add test scope to Section 5 when adding new modules.
> 2. Reflect test strategy improvements from sprint retrospectives.
