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
src/validators.py          # Hand-written validator functions under test
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
  pre-commit               # Git pre-commit hook — install via install-hooks.sh
  install-hooks.sh         # One-time hook installer
.github/workflows/qa.yml   # CI: smoke → full suite → dummyjson fallback
```

---

## CI

GitHub Actions runs on every push and pull request:

1. **Smoke** — fast liveness check
2. **Full suite** — unit + integration against reqres.in
3. **Fallback** — integration + smoke against dummyjson if reqres.in fails

Requires `REQRES_API_KEY` set as a repository secret.

---

## Git hooks

Enforce test discipline and run unit tests before every commit:

```bash
git init          # if not already a repo
bash scripts/install-hooks.sh
```

---

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `REQRES_API_KEY` | Yes (reqres only) | Free key from app.reqres.in/api-keys |
| `TEST_SOURCE` | No | `reqres` (default) · `dummyjson` · `jsonplaceholder` |

Store in `~/.zshrc` — never commit to the repository.
