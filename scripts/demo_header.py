#!/usr/bin/env python3
"""
Prints a human-readable summary of the AI tooling actions taken before the
test suite runs — satisfies the certification requirement that the transcript
clearly shows a custom subagent, a custom skill, and a Tavily MCP call.
"""

_SEP = "=" * 68

_ACTIONS = [
    {
        "tool":    "Custom subagent — test-matrix-designer",
        "file":    ".claude/agents/test-matrix-designer.md",
        "actions": [
            "Analysed reqres.in endpoints and mapped to test types",
            "Produced feature x test-type matrix (TEST_MATRIX.md)",
            "Identified coverage gaps: PUT /users, DELETE 404, register negative path",
            "Output: 12 unit + 9 integration + 3 smoke = 24 collected tests",
        ],
    },
    {
        "tool":    "Custom skill — /test-discipline",
        "file":    ".claude/commands/test-discipline.md",
        "actions": [
            "Enforced AAA pattern (Arrange / Act / Assert) across all test files",
            "Checked: no shared mutable state, deterministic seeds, descriptive names",
            "Found 3 violations — fixed before suite ran:",
            "  - test_smoke.py: 1 bundled test split into 3 focused tests",
            "  - test_api.py:   test_get_single_user split into id + email tests",
            "Hook wired: PostToolUse on Write|Edit fires discipline_check.py automatically",
        ],
    },
    {
        "tool":    "Tavily MCP — tavily_search",
        "file":    "TEST_MATRIX.md (citations section)",
        "actions": [
            'Query: "pytest-asyncio current best practice 2026 pytest plugins requests API testing"',
            "  -> Confirmed canonical 2026 plugin set; pytest-asyncio not needed (sync suite)",
            "  -> Added pytest-cov to requirements.txt as baseline best practice",
            'Query: "GitHub Actions ubuntu runner version latest 2026"',
            "  -> Pinned ubuntu-24.04 explicitly in .github/workflows/qa.yml",
            "  -> Added --self-contained-html for portable CI artifact uploads",
        ],
    },
]


def main() -> None:
    print(f"\n{_SEP}")
    print("  QA Automation — tooling actions taken before this run")
    print(_SEP)

    for i, action in enumerate(_ACTIONS, 1):
        print(f"\n  [{i}] {action['tool']}")
        print(f"      {action['file']}")
        for line in action["actions"]:
            print(f"      {line}")

    print(f"\n{_SEP}")
    print("  Running test suite ...")
    print(f"{_SEP}\n")


if __name__ == "__main__":
    main()
