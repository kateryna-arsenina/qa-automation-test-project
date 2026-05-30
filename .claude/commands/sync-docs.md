Audit project documentation for gaps or stale content caused by recent code changes. Do not edit anything — report only, then ask which gaps to fix.

## Step 1 — Discover what exists

Read these files in full:
- `README.md`
- `CLAUDE.md`
- `Makefile` (all targets)
- `scripts/` (list all .py and .sh files)
- `.claude/commands/` (list all slash commands)
- `.github/workflows/qa.yml` (job names and steps)

## Step 2 — Cross-check for gaps

Check each documentation file against the actual project state:

**README.md**
- Every `make <target>` in the Makefile should appear in the Commands table
- Every environment variable used anywhere in scripts or tests should appear in the Environment variables table
- The Project structure tree should reflect actual files in `scripts/` and `tests/`
- The CI description should match the actual jobs in `qa.yml`

**CLAUDE.md**
- Every `make <target>` in the Makefile should appear under "Running Tests" or another relevant section
- Every script in `scripts/` should be mentioned in the Directory Layout
- Every slash command in `.claude/commands/` should be mentioned
- Test discipline rules should match what `scripts/discipline_check.py` actually enforces

## Step 3 — Report findings

Output a checklist grouped by file:

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

After the checklist, list only the confirmed gaps as a numbered action list:
1. Add `make matrix` to README.md Commands table
2. Add `print_matrix.py` to CLAUDE.md Directory Layout
...

Ask: "Fix all gaps, or pick numbers to apply selectively?"
