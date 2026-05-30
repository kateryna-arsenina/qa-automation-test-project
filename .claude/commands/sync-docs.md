# Sync Docs Skill

A documentation audit skill for this project.
Invoke via `/sync-docs` to check README.md and CLAUDE.md against the current codebase.

---

## What it checks

### README.md
- Every `make <target>` in the Makefile appears in the Commands table
- Every environment variable used in scripts or tests appears in the Environment variables table
- The Project structure tree reflects actual files in `scripts/` and `tests/`
- The CI description matches the actual jobs in `.github/workflows/qa.yml`

### CLAUDE.md
- Every `make <target>` in the Makefile appears under "Running Tests" or a relevant section
- Every script in `scripts/` is mentioned in the Directory Layout
- Every slash command in `.claude/commands/` is mentioned
- Test discipline rules match what `scripts/discipline_check.py` actually enforces

---

## Steps

1. **Discover** — read `README.md`, `CLAUDE.md`, `Makefile`, list `scripts/`, list `.claude/commands/`, read `.github/workflows/qa.yml`
2. **Cross-check** — compare each doc against the actual project files
3. **Report** — output a checklist grouped by file, then a numbered action list of confirmed gaps
4. **Ask** — "Fix all gaps, or pick numbers to apply selectively?"

---

## Output format

```
README.md
  ✅ make test — documented
  ❌ make matrix — missing from Commands table
  ...

CLAUDE.md
  ✅ probe.py — documented
  ❌ print_matrix.py — missing from Directory Layout
  ...
```

Followed by:
```
1. Add `make matrix` to README.md Commands table
2. Add `print_matrix.py` to CLAUDE.md Directory Layout
...
```

Do not edit any files — report only, then wait for confirmation.
