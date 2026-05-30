# TEST_MATRIX.md

## Framework Choice
**pytest + requests** — chosen because it is the de-facto standard for Python API testing, has first-class HTML reporting via `pytest-html`, and integrates natively with GitHub Actions without additional tooling.

## System Under Test (SUT)
**reqres.in** — a public REST sandbox that mirrors realistic CRUD endpoints without requiring a running local service. Intermittent 429/5xx responses are treated as environmental (xfail or retry-once).

---

## Best Practices Research (Tavily MCP + WebSearch, 2026-05-30)

> **Tavily MCP query:** "pytest-asyncio current best practice 2026 pytest plugins requests API testing"
> **Source:** [How to Master Pytest: 13-Step Tutorial with CI/CD [2026]](https://tech-insider.org/pytest-tutorial-python-testing-ci-cd-2026) · [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io)
>
> **Decision applied:** Current canonical plugin set for 2026 is `pytest`, `pytest-cov`, `pytest-xdist`, `pytest-html`, `pytest-asyncio`. As of pytest 8.4 (current: 8.4.2), running async tests without `pytest-asyncio` causes an immediate failure rather than a silent warning. Our suite is synchronous (using `requests`, not `httpx`/`asyncio`), so `pytest-asyncio` is not needed — confirmed intentional. Added `pytest-cov` to `requirements.txt` as best-practice baseline.

> **WebSearch query:** "GitHub Actions ubuntu runner version latest 2026"
> **Source:** [GitHub-hosted runners reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners) · [GitHub Actions runner images](https://github.com/actions/runner-images)
>
> **Decision applied:** `ubuntu-24.04` is the current stable `ubuntu-latest` label (Ubuntu 26.04 runner not yet available as of May 2026). Pinned explicitly as `ubuntu-24.04` in `qa.yml` to avoid unexpected runner changes.

> **WebSearch query:** "pytest-html best practices 2026 pytest plugins HTML report"
> **Source:** [pytest-html documentation](https://pytest-html.readthedocs.io/en/latest/user_guide.html)
>
> **Decision applied:** Use `--self-contained-html` so the report is a single portable file with no external dependencies — critical for CI artifact uploads.

---

## Feature × Test Type Matrix

| Feature / Endpoint | Unit | Integration | Smoke |
|---|:---:|:---:|:---:|
| Pagination response shape | T01 ✅ | T02, T03 ✅ | — |
| Single user response shape | T04 ✅ | T05 ✅ | — |
| Create user response shape | T07 ✅ | T08 ✅ | — |
| Register payload validation | T13 ✅ | T14 ✅ | — |
| Unknown user (404 path) | — | T06 ✅ | — |
| Delete user | — | T12 ✅ | — |
| Login missing field (400 path) | — | T17 ✅ | — |
| API health / reachability | — | — | S01 ✅ |

**Total: 24 collected** — 12 unit + 9 integration + 3 smoke (exceeds the ≥8 minimum: 3 unit + 4 integration + 1 smoke)

Actual breakdown: **12 collected unit** (9 functions, 4 classes, parametrized) + **9 collected integration** (8 functions, 1 parametrized) + **3 smoke functions** = **24 collected tests**.

---

## Test ID Reference

| ID | Type | File | Test Function | Endpoint |
|---|---|---|---|---|
| T01 | Unit | tests/unit/test_validators.py | `TestValidateListResponse` (3 cases) | — |
| T04 | Unit | tests/unit/test_validators.py | `TestValidateSingleUser` (3 cases) | — |
| T07 | Unit | tests/unit/test_validators.py | `TestValidateCreateResponse` (3 cases) | — |
| T13 | Unit | tests/unit/test_validators.py | `TestValidateRegisterPayload` (3 cases) | — |
| T02 | Integration | tests/integration/test_api.py | `test_list_users_page[populated-page]` | GET /users?page=2 |
| T03 | Integration | tests/integration/test_api.py | `test_list_users_page[empty-page]` | GET /users?page=999 |
| T05 | Integration | tests/integration/test_api.py | `test_get_single_user_returns_correct_id` | GET /users/1 |
| T05b | Integration | tests/integration/test_api.py | `test_get_single_user_has_valid_email` | GET /users/1 |
| T06 | Integration | tests/integration/test_api.py | `test_get_unknown_user_returns_not_found` | GET /users/9999 |
| T08 | Integration | tests/integration/test_api.py | `test_create_user_returns_created_with_id` | POST /users |
| T12 | Integration | tests/integration/test_api.py | `test_delete_user_returns_success` | DELETE /users/2 |
| T14 | Integration | tests/integration/test_api.py | `test_register_returns_token` | POST /register |
| T17 | Integration | tests/integration/test_api.py | `test_login_invalid_payload_returns_error` | POST /login |
| S01 | Smoke | tests/smoke/test_smoke.py | `test_smoke_api_returns_ok` | GET /users |
| S02 | Smoke | tests/smoke/test_smoke.py | `test_smoke_response_is_json` | GET /users |
| S03 | Smoke | tests/smoke/test_smoke.py | `test_smoke_users_list_is_non_empty` | GET /users |

---

## Coverage Gaps (identified by test-matrix-designer subagent)

| Gap | Severity | Decision |
|---|---|---|
| PUT /api/users/{id} — no test | Low | reqres.in accepts any JSON and always returns 200; deferred to avoid testing the sandbox, not our code |
| DELETE — no 404 negative path | Medium | reqres.in returns 204 for any id; documented as platform limitation |
| POST /api/register — no unhappy-path integration | Medium | T13 unit test covers payload validation; integration negative path deferred |
| Response time / SLA assertions | Low | Not in scope for this certification task |
