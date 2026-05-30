# QA Automation Test Suite

A disciplined, source-agnostic REST API test suite built with **pytest + requests**.
Covers three test layers (unit · integration · smoke) against public mock APIs,
with CI via GitHub Actions and timestamped HTML reports.

Built as part of the **31C Claude Code Certification — Archetype C**.

---

## Quick start

```bash
pip install -r requirements.txt
export REQRES_API_KEY=<your-key>   # free at app.reqres.in/api-keys
export TAVILY_API_KEY=<your-key>   # free at app.tavily.com
bash scripts/install-hooks.sh      # activate pre-commit hook (once)
make probe-all                     # generate schemas for all sources (once)
make demo                          # transcript + full suite + HTML report
```

---

## Commands

| Command | What it does |
|---------|-------------|
| `make demo` | AI tooling transcript → full suite → timestamped report (auto-opens) |
| `make demo-dummyjson` | Same, against dummyjson.com |
| `make demo-jsonplaceholder` | Same, against jsonplaceholder |
| `make demo-retry` | Simulate 429 / 502 → retry log + xfail suggestion |
| `make switch` | Interactive source picker with auto-probe |
| `make test` | Full suite → reqres.in (report in `reports/`) |
| `make smoke` | Smoke layer only |
| `make unit` | Unit layer only (no network) |
| `make probe-all` | Regenerate schemas for all three sources |
| `make matrix` | Print endpoint availability matrix across all sources |
| `make test-dummyjson` | Full suite → dummyjson.com (report in `reports/`) |
| `make test-jsonplaceholder` | Full suite → jsonplaceholder (report in `reports/`) |
| `make integration` | Integration layer only (no report) |
| `make lint` | Validate `.github/workflows/qa.yml` with actionlint |
| `make install` | Install Python dependencies from `requirements.txt` |
| `make report-clean` | Delete all HTML reports from `reports/` |

---

## Test sources

Switch the API without changing any test code:

```bash
TEST_SOURCE=dummyjson       make test
TEST_SOURCE=jsonplaceholder make test
make test                          # default: reqres.in
```

Run `make probe-all` once after cloning to generate schemas for all sources.

---

## Test layers

| Layer | What it covers |
|-------|----------------|
| Unit | Validator functions in `src/validators.py` — no network |
| Integration | CRUD + auth endpoints — live HTTP against the active source |
| Smoke | API reachability and response shape — fast health check |

---

## Project structure

```
src/validators.py          # Validator functions under test
tests/
  unit/                    # Pure-function tests
  integration/             # HTTP tests via provider abstraction
  smoke/                   # Lightweight liveness checks
  resilience/              # 429/502 retry demo (make demo-retry)
  providers/               # One class per API source
  schemas/                 # Auto-generated JSON Schema files (probe output)
  conftest.py              # Fixtures, retry logic, layer coverage, HTML hooks
scripts/
  probe.py                 # Generate schemas from live API responses
  discipline_check.py      # AST-based test discipline checker (PostToolUse hook)
  demo_header.py           # Print certification transcript header before test run
  print_report_link.py     # Print report path and auto-open in browser
  print_matrix.py          # Print endpoint availability matrix across sources
  pre-commit               # Git pre-commit hook — install via install-hooks.sh
  install-hooks.sh         # One-time hook installer
.github/workflows/qa.yml   # CI: lint → smoke → full suite → dummyjson fallback
```

---

## CI

GitHub Actions runs on every push and pull request:

1. **Lint** — ruff static analysis; blocks all downstream jobs on failure
2. **Smoke** — fast liveness check
3. **Full suite** — unit + integration against reqres.in
4. **Fallback** — integration + smoke against dummyjson if reqres.in fails

Requires `REQRES_API_KEY` set as a repository secret.

---

## Environment variables

Set these in `~/.zshrc` before running — never commit them to the repository.

| Variable | Required | Where to get it |
|----------|----------|-----------------|
| `REQRES_API_KEY` | Yes (reqres source) | [app.reqres.in/api-keys](https://app.reqres.in/api-keys) — free |
| `TAVILY_API_KEY` | Yes (Tavily MCP research) | [app.tavily.com](https://app.tavily.com) — free tier available |
| `TEST_SOURCE` | No | `reqres` (default) · `dummyjson` · `jsonplaceholder` |

```bash
# add to ~/.zshrc
export REQRES_API_KEY=<your-key>
export TAVILY_API_KEY=<your-key>
```

---

## Git hooks

Pre-commit hook runs ruff, discipline check, and unit tests before every commit.
Install once after cloning:

```bash
bash scripts/install-hooks.sh
```
