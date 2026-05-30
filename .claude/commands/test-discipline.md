Review the test files in $ARGUMENTS (or all tests/ if omitted) and enforce the following discipline rules. Report each violation with file path and line number, then suggest a fix.

**Rules to enforce:**

1. **AAA Pattern** — Every test must have clearly separated Arrange / Act / Assert sections. Tests that mix setup and assertions without logical grouping are violations.

2. **No shared mutable state** — Tests must not mutate module-level variables, class attributes, or fixtures that are shared between tests. Each test must be fully independent.

3. **Deterministic seeds** — Any test using random data must seed the RNG explicitly (e.g. `random.seed(42)`). No floating `random.random()` or `uuid4()` without a fixed seed.

4. **No time.now() without injection** — Tests must not call `datetime.now()`, `time.time()`, or equivalent directly. Time must be injected or mocked.

5. **Descriptive names** — Test function names must follow `test_<what>_<condition>_<expected>` pattern. Names like `test_1`, `test_foo`, `test_it` are violations.

6. **Single assertion focus** — Each test should assert one logical outcome. Multiple unrelated assertions in a single test function are a violation.

Output a checklist: ✅ pass or ❌ fail with explanation for each rule per file reviewed.
