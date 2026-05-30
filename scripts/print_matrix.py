#!/usr/bin/env python3
"""Print a test matrix showing endpoint availability across all three sources."""
import json
from pathlib import Path

SOURCES = ["reqres", "dummyjson", "jsonplaceholder"]

LABELS = {
    "users_list":       "List users (populated)",
    "users_list_empty": "List users (empty page)",
    "user_single":      "Get single user",
    "user_not_found":   "Get unknown user (404)",
    "user_create":      "Create user",
    "user_delete":      "Delete user",
    "register":         "Register (returns token)",
    "login_invalid":    "Login invalid payload",
}


def load(source: str) -> dict:
    path = Path(f"tests/schemas/{source}/schemas.json")
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def symbol(schemas: dict, key: str) -> str:
    entry = schemas.get(key)
    if entry is None:
        return "?"
    return "✓" if entry.get("available", False) else "✗"


def main() -> None:
    data = {s: load(s) for s in SOURCES}
    missing = [s for s, d in data.items() if not d]
    if missing:
        print(f"[matrix] Missing schemas for: {', '.join(missing)} — run: make probe-all\n")

    col = 24
    header = f"{'Endpoint':<{col}}" + "".join(f"  {s:<16}" for s in SOURCES)
    print()
    print(header)
    print("-" * len(header))
    for key, label in LABELS.items():
        row = f"{label:<{col}}" + "".join(f"  {symbol(data[s], key):<16}" for s in SOURCES)
        print(row)
    print()
    print("  ✓ = supported   ✗ = not supported   ? = schemas not generated")
    print()


if __name__ == "__main__":
    main()
