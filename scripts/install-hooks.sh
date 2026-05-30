#!/usr/bin/env bash
# Copy the version-controlled pre-commit hook into .git/hooks/
set -euo pipefail

HOOK_SRC="scripts/pre-commit"
HOOK_DST=".git/hooks/pre-commit"

if [ ! -d ".git" ]; then
  echo "ERROR: not a git repository. Run 'git init' first."
  exit 1
fi

cp "$HOOK_SRC" "$HOOK_DST"
chmod +x "$HOOK_DST"
echo "Installed $HOOK_DST"
