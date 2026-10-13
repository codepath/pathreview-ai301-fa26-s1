# Test evidence for issue #66

Branch: `fix/66-structlog` (`cf73e69`). The code checks ran at
`fb68f51`; `cf73e69` only removes the unrelated local issue-comment
file from the committed PR diff.  
Environment: macOS arm64, Python 3.11.6, pytest 9.1.1,
pytest-asyncio 1.4.0, structlog 26.1.0

## Reproduction before the change (main)

Reused the Unit 2 reproduction output in `reproduction-run.txt`,
captured on main at `f89c06f`.

Command:

```text
.venv/bin/pytest tests/unit/test_batch_processor.py::TestBatchEmbeddingProcessor::test_empty_chunks_list_returns_empty -q --runxfail
```

Observed:

```text
assert "Empty chunks list" in caplog.text or any(...)
E AssertionError: assert ('Empty chunks list' in '' or False)
----------------------------- Captured stdout call -----------------------------
2026-10-05 21:57:48 [warning  ] Empty chunks list provided to BatchEmbeddingProcessor
FAILED tests/unit/test_batch_processor.py::TestBatchEmbeddingProcessor::test_empty_chunks_list_returns_empty
1 failed in 3.55s
```

This confirms the function returned far enough to reach the logging
assertion, but pytest did not capture the warning in `caplog`.

The saved baseline also records:

```text
1 xfailed in 0.44s
10 passed, 1 xfailed in 0.38s
```

for the marked regression test and full batch-processor test file,
respectively.

## Reproduction after the change (branch)

Command:

```text
.venv/bin/pytest tests/unit/test_batch_processor.py::TestBatchEmbeddingProcessor::test_empty_chunks_list_returns_empty -q --runxfail
```

Result:

```text
.                                                                        [100%]
1 passed, 1 warning in 0.43s
```

The warning is captured by the test's `caplog` assertion; the return
value remains `[]`. The warning is the existing Pydantic deprecation
warning from `core/config.py`.

Full regression-file command:

```text
.venv/bin/pytest tests/unit/test_batch_processor.py -q
```

Result:

```text
...........                                                              [100%]
11 passed, 1 warning in 0.33s
```

## Required repository checks

### Unit tests

Command: `make test-unit`

Result:

```text
================= 376 passed, 52 xfailed, 5 warnings in 18.91s =================
```

### Integration tests

Command: `make test-integration`

Result (no integration tests are present; the nonzero exit is expected
for this repository):

```text
.venv/bin/pytest tests/integration -v -m integration
============================= test session starts ==============================
platform darwin -- Python 3.11.6, pytest-9.1.1, pluggy-1.6.0 -- /Users/js/School/codepath/ai301/pathreview-ai301-fa26-s1/.venv/bin/python
cachedir: .pytest_cache
hypothesis profile 'default'
benchmark: 5.3.0 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
rootdir: /Users/js/School/codepath/ai301/pathreview-ai301-fa26-s1
configfile: pyproject.toml
plugins: pytest_httpserver-1.2.0, hypothesis-6.168.5, cov-7.1.0, asyncio-1.4.0, platformdirs-4.12.3, benchmark-5.3.0, anyio-4.15.1
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 0 items

=============================== warnings summary ===============================
core/config.py:7
  /Users/js/School/codepath/ai301/pathreview-ai301-fa26-s1/core/config.py:7: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.13/migration/
    class Settings(BaseSettings):

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============================== 1 warning in 0.37s ==============================
make: *** [test-integration] Error 5
```

### Lint

Command: `make lint`

Result:

```text
.venv/bin/ruff check .
All checks passed!
```

### Type check

Command: `make typecheck`

Result:

```text
.venv/bin/mypy api/ core/ ingestion/ rag/ agent/ safety/
Success: no issues found in 76 source files
```

## Seeded-bug marker search

Command: `rg -n 'issue #66:' tests pyproject.toml`

Result: no matches on the branch. The matching strict xfail marker
present on `main` was removed from the regression test; there is no
issue #66 suppression in `pyproject.toml`.
