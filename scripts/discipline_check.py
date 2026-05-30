#!/usr/bin/env python3
"""
PostToolUse hook — runs test-discipline checks on any test file just written or edited.
Reads Claude Code hook JSON from stdin. Always exits 0 (report-only, non-blocking).
"""
import ast
import json
import sys
from pathlib import Path


def _test_functions(tree: ast.Module) -> list[ast.FunctionDef]:
    funcs = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test_"):
                funcs.append(node)
    return funcs


def _source_lines(source: str, func: ast.FunctionDef) -> list[str]:
    return source.splitlines()[func.lineno - 1 : func.end_lineno]


def check(path: str) -> list[str]:
    p = Path(path)
    if not p.exists() or not p.name.startswith("test_"):
        return []

    source = p.read_text()
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [f"  line {exc.lineno}: SyntaxError — {exc.msg}"]

    violations: list[str] = []

    # Rule 2 — module-level mutable state
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and getattr(node, "col_offset", -1) == 0
            and isinstance(node.value, (ast.List, ast.Dict, ast.Set))
        ):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    violations.append(
                        f"  line {node.lineno}: Rule 2 — module-level mutable '{target.id}'"
                    )

    # Rules 3 & 4 — bare random / time calls
    _random_attrs = {"random", "randint", "randrange", "choice", "shuffle", "sample"}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute):
            continue
        if func.attr in _random_attrs:
            violations.append(
                f"  line {node.lineno}: Rule 3 — bare random.{func.attr}() without seed"
            )
        if func.attr in ("now", "utcnow") and isinstance(func.value, ast.Name) and func.value.id == "datetime":
            violations.append(
                f"  line {node.lineno}: Rule 4 — bare datetime.{func.attr}() — inject or mock time"
            )
        if func.attr == "time" and isinstance(func.value, ast.Name) and func.value.id == "time":
            violations.append(
                f"  line {node.lineno}: Rule 4 — bare time.time() — inject or mock time"
            )

    for func in _test_functions(tree):
        lines = _source_lines(source, func)
        comment_text = " ".join(ln for ln in lines if "#" in ln).lower()

        # Rule 1 — AAA comments
        has_aaa = "arrange" in comment_text or "act" in comment_text or "assert" in comment_text
        if not has_aaa:
            violations.append(
                f"  line {func.lineno}: Rule 1 — '{func.name}' missing # Arrange / # Act / # Assert"
            )

        # Rule 5 — descriptive name (at least test_<what>_<condition>)
        parts = func.name.split("_")
        if len(parts) < 3:
            violations.append(
                f"  line {func.lineno}: Rule 5 — '{func.name}' too short; use test_<what>_<condition>_<expected>"
            )

        # Rule 6 — single assertion focus (> 3 asserts suggests bundled concerns)
        n_asserts = sum(1 for n in ast.walk(func) if isinstance(n, ast.Assert))
        if n_asserts > 3:
            violations.append(
                f"  line {func.lineno}: Rule 6 — '{func.name}' has {n_asserts} assertions; consider splitting"
            )

    return violations


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    file_path = data.get("tool_input", {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    p = Path(file_path)
    if "test" not in str(p) or not p.name.startswith("test_"):
        sys.exit(0)

    print(f"\n[test-discipline] checking {p.name} ...", flush=True)

    violations = check(file_path)
    if violations:
        print(f"[test-discipline] {len(violations)} violation(s):", flush=True)
        for v in violations:
            print(v, flush=True)
        print("[test-discipline] run /test-discipline for fix suggestions.", flush=True)
    else:
        print("[test-discipline] all rules pass.", flush=True)


if __name__ == "__main__":
    main()
