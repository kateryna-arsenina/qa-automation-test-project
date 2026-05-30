# Test Discipline Skill

A prose skill that enforces test quality rules for this project.
Invoke via `/test-discipline [path]` to review test files.

---

## Rules

### 1. AAA Pattern (Arrange / Act / Assert)
Every test function **must** have three clearly separated logical sections:
- **Arrange** — set up inputs, instantiate any collaborators, configure fixtures
- **Act** — make the single call under test (one line or one expression)
- **Assert** — check exactly one logical outcome

Tests that mix setup and assertion without clear separation are violations.
Use inline comments `# Arrange`, `# Act`, `# Assert` to make the sections explicit.

### 2. No Shared Mutable State
Tests must not mutate module-level variables, class-level attributes, or `session`-scoped fixtures.
Each test must be fully independent: running it alone must produce the same result as running it in any order within the suite.
Forbidden patterns:
- Writing to a global `dict` or `list` in a test body
- Relying on another test having run first (ordering dependency)
- Modifying a `session`-scoped object inside a test (read-only use is fine)

### 3. Deterministic Seeds
Any test that generates random data must seed the RNG explicitly before use:
```python
import random
random.seed(42)
```
Floating calls to `random.random()`, `random.choice()`, or `uuid4()` without a fixed seed are violations.
For `faker`, pass `Faker(seed=0)`.

### 4. No `datetime.now()` Without Injection
Tests must not call `datetime.now()`, `datetime.utcnow()`, `time.time()`, or `date.today()` directly.
Time must be:
- injected as a parameter with a fixed value, or
- mocked with `unittest.mock.patch` / `freezegun`

Rationale: a test that passes at 23:59 and fails at 00:00 is not a test — it is a time bomb.

### 5. Descriptive Test Names
Test function names must follow the pattern:
```
test_<what>_<condition>_<expected_outcome>
```
Examples of **valid** names:
- `test_validate_user_missing_email_raises_value_error`
- `test_list_users_page999_returns_empty_data`

Examples of **invalid** names:
- `test_1`, `test_it`, `test_foo`, `test_check`

### 6. Single Assertion Focus
Each test should assert one logical outcome.
Multiple unrelated assertions in a single test function are a violation.
Multiple related assertions that together confirm one logical fact (e.g., status code + content-type for a single response) are allowed.

---

## Checklist (used by `/test-discipline` command)

For each file reviewed, output:

| Rule | Status | Notes |
|------|--------|-------|
| AAA pattern | ✅ / ❌ | |
| No shared mutable state | ✅ / ❌ | |
| Deterministic seeds | ✅ / ❌ | |
| No bare datetime.now() | ✅ / ❌ | |
| Descriptive test names | ✅ / ❌ | |
| Single assertion focus | ✅ / ❌ | |
