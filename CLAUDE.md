# CLAUDE.md — QA Automation Test Project

Project for **31C Claude Code Certification — Archetype C**.
Owner: Kate Arsenina, QA Engineer Lead, 31c.io.

---

## What This Project Is

A source-agnostic REST API test suite that validates three public mock APIs
(reqres.in, dummyjson.com, jsonplaceholder.typicode.com) using pytest.
The same test code runs against any source; only `TEST_SOURCE` env var changes.

---

## Stack

| Tool | Purpose |
|------|---------|
| pytest 8+ | Test runner |
| requests | HTTP client |
| jsonschema / genson | Schema validation & schema generation |
| pytest-html 4.x | HTML reports (reports/ folder, timestamped) |
| pytest-xdist | Parallel execution |
| pytest-cov | Coverage |

Install: `make install` (or `pip install -r requirements.txt`)

---

## Directory Layout

```
tests/
  unit/          # Pure-function tests, no network
  integration/   # HTTP tests against the active source
  smoke/         # Lightweight health-check tests
  resilience/    # Simulated 429/502 xfail demos (excluded from full suite)
  providers/     # One class per API source (reqres, dummyjson, jsonplaceholder)
  schemas/       # Auto-generated JSON Schema files per source (probe output)
  conftest.py    # Fixtures, retry logic, layer coverage, HTML hooks

scripts/
  probe.py           # Hit live API → generate tests/schemas/<source>/schemas.json
  discipline_check.py # AST-based PostToolUse hook — enforces test discipline rules
  demo_header.py     # Prints certification transcript header before test run
  print_report_link.py # Prints report path and auto-opens in browser
  pre-commit         # Git pre-commit hook — install via scripts/install-hooks.sh

.claude/
  settings.json      # PostToolUse hook: runs discipline_check.py after Write/Edit
  settings.local.json # Allowed commands (no API keys stored here)
  commands/          # Custom slash commands
  agents/            # Custom subagents
```

---

## Running Tests

```bash
# Full suite (reqres.in) — requires REQRES_API_KEY in environment
make demo

# Full suite against alternate source
make demo-dummyjson
make demo-jsonplaceholder

# Source picker with interactive recovery
make switch

# Simulate 429/502 retries
make demo-retry

# Targeted runs
make test            # reqres, with timestamped HTML report
make test-dummyjson
make test-jsonplaceholder
make smoke           # smoke layer only
make unit            # unit layer only (no network, no report)
make integration     # integration layer only

# Refresh schemas before switching sources
make probe-all
```

Reports land in `reports/` as `report_<source>_<YYYYMMDD_HHMMSS>.html` and auto-open in the browser.

---

## Switching Sources

Each source needs schemas generated before tests can run:

```bash
make probe-all                           # regenerate all three
TEST_SOURCE=dummyjson python3 scripts/probe.py  # single source
```

Schemas live in `tests/schemas/<source>/schemas.json`.
The `available` flag in each schema entry distinguishes:
- `available: true` — endpoint probed successfully
- `available: false` — probe confirmed endpoint absent (test will skip with clear message)
- key missing — schemas not generated yet (run `make probe-all`)

---

## Provider Pattern

`TEST_SOURCE` env var selects the active provider (default: `reqres`).

Each provider class in `tests/providers/` implements:
- URL builders (`users_list_url`, `user_url`, `register_url`, `login_url`, …)
- Payload factories (`create_user_payload`, `register_payload`, …)
- Field extractors (`extract_users`, `extract_email`, `extract_token`, …)
- Status code constants (`ok`, `created`, `no_content`, `not_found`, `bad_request`)

**Do not add source-specific branches in test code.** All source differences belong in the provider class.

---

## Retry & Resilience

`_SmartSession` in `conftest.py` wraps `requests.Session`:
- On HTTP 429 or 502: logs a WARNING, sleeps 1 s, retries once
- If still failing: raises `SourceUnavailableError` → test becomes `xfail` with switch hint
- The `_xfail_on_source_unavailable` autouse fixture catches the exception in regular tests
- `tests/resilience/` tests must catch it explicitly with `try/except SourceUnavailableError`

Resilience tests are **excluded from the full suite** (`pytest.ini` testpaths) — run via `make demo-retry`.

---

## Layer Coverage

`conftest.py` enforces minimum test counts at session end:

| Layer | Minimum |
|-------|---------|
| unit | 1 |
| integration | 4 |
| smoke | 1 |

Check is skipped on subset runs (e.g., `make unit`). Violations set exit code 1.
The HTML report includes a Layer Coverage table in the summary section.

---

## HTML Report Customisation

Each row has two extra columns injected by `conftest.py`:
- **Type** — Unit / Integration / Smoke (colour-coded)
- **Description** — human-readable test title derived from the function name

---

## Test Discipline Rules

Enforced by `.claude/settings.json` PostToolUse hook (runs `scripts/discipline_check.py` after every file write/edit) and by the `/test-discipline` slash command.

Rules:
1. **AAA pattern** — every test must have Arrange / Act / Assert sections
2. **No shared mutable state** — tests must be fully independent
3. **Deterministic seeds** — `random.seed(N)` required before any random call
4. **No bare `datetime.now()`** — inject or mock time
5. **Descriptive names** — `test_<what>_<condition>_<expected_outcome>`
6. **Single assertion focus** — one logical outcome per test

---

## Git Hooks

A pre-commit hook runs `scripts/discipline_check.py` and `make unit` before every commit.
Install once after `git init`:

```bash
bash scripts/install-hooks.sh
```

The hook file lives at `scripts/pre-commit` and is version-controlled so teammates get it too.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TEST_SOURCE` | No | `reqres` (default) / `dummyjson` / `jsonplaceholder` |
| `REQRES_API_KEY` | Yes for reqres | API key from reqres.in dashboard |

Store in `~/.zshrc` or `.env` — never commit them.

---

## Key Design Decisions

- **Probe-driven skips**: `scripts/probe.py` discovers endpoint capability at probe time; tests read the `available` flag and skip with a clear reason rather than failing.
- **No source-specific test code**: all branching is in providers, tests are source-agnostic.
- **Reports folder with timestamps**: `make report-clean` removes all HTML reports.
- **Resilience excluded from main suite**: `pytest.ini` `testpaths` does not include `tests/resilience/`.
- **Layer coverage is advisory on subset runs**: enforced only when multiple layers are collected.
