# Plan: make the empty-chunks warning capturable by pytest

## Diagnosis

The reproduced failure is in the logging assertion, not in the return
value: `processor.process([])` returns `[]`, but pytest's `caplog` has no
record for the warning. The reproduction reports the warning under
`Captured stdout call`:

> 2026-09-29 22:12:44 [warning  ] Empty chunks list provided to BatchEmbeddingProcessor
>
> `caplog.text` is empty and `caplog.records` has no matching record

In the checkout at `f89c06f`, `ingestion/embeddings/batch_processor.py`
creates a module-level logger with `structlog.get_logger()` and calls
`logger.warning(...)` in `BatchEmbeddingProcessor.process` when `chunks`
is empty. The repository already has `core.logging.configure_logging()`,
which configures structlog with `structlog.stdlib.LoggerFactory()`, but
the current `tests/conftest.py` does not initialize that configuration.
Together with the observed stdout output, this supports the hypothesis
that this test runs with structlog's default output path rather than the
stdlib logging path that pytest's `caplog` captures. I have not tested
this hypothesis with a fix yet.

The evidence establishes this for the reproduced test and the 10 other
tests in `test_batch_processor.py` that I ran; it does not establish the
issue text's suite-wide claim.

## Scope

**Change:** Initialize the repository's existing structlog-to-stdlib
logging configuration in the pytest test bootstrap, before tests use
module-level structlog loggers. Keep the empty-input regression test's
`caplog` assertion, and remove its strict xfail marker so the test must
pass normally.

**Do not change:** The warning text, the `process([]) == []` behavior,
application logging behavior, or unrelated logging in other modules.
Do not claim that every `caplog` use across the suite is fixed without
testing those cases.

## Files to touch

- `tests/conftest.py` — initialize `core.logging.configure_logging()`
  early for pytest so structlog events use the standard-library logging
  path before the processor logger is first used.
- `tests/unit/test_batch_processor.py` — remove the `xfail(strict=True)`
  marker from `test_empty_chunks_list_returns_empty`; retain the
  assertion that verifies the warning is captured.

I do not currently expect to change
`ingestion/embeddings/batch_processor.py` or `core/logging.py`: the
processor emits the warning, and the repository already provides the
configuration helper. If the focused test shows that the helper does
not make this logger visible to `caplog`, revisit the diagnosis before
expanding the file list.

## Approach

1. Add test-session logging initialization using the existing
   `configure_logging()` helper in `tests/conftest.py`, so configuration
   is established before test modules exercise their loggers.
2. Remove the strict xfail decorator from the empty-chunks test and
   leave its return-value and warning-capture assertions in place.
3. Run the focused regression test first. If it passes, run the whole
   batch-processor test file and the project's unit-test command to
   catch unintended changes from initializing logging in the test
   process.

## Test plan

From a clean clone, use the reproduced setup (macOS 13.0 arm64,
Python 3.11.6, pytest 9.1.1, pytest-asyncio 1.4.0, structlog 26.1.0;
`pip install -e ".[dev]"`) and run the same focused test after removing
its xfail marker:

```bash
pytest tests/unit/test_batch_processor.py::TestBatchEmbeddingProcessor::test_empty_chunks_list_returns_empty -q --runxfail
```

Expected after the fix: `1 passed`; `result == []` still holds and
`caplog.text` or a `caplog.records` message contains the empty-chunks
warning. The warning should be available as a captured log record,
rather than appearing only as a `Captured stdout call`.

Then run the complete file:

```bash
pytest tests/unit/test_batch_processor.py -q
```

Expected: all 11 tests pass, with no xfail or unexpected xpass. Finally,
run the repository's documented unit suite:

```bash
make test-unit
```

Expected: the unit suite passes with the logging bootstrap in place. If
other tests fail or logging output/capture changes unexpectedly, isolate
the effect and adjust the test setup rather than broadening the
production logging change without evidence.

## Risks and unknowns

- Test-session configuration changes logging setup for all unit tests;
  the unit suite is needed to check for side effects.
- `structlog` logger caching or another test's earlier logging use may
  affect whether initialization in `conftest.py` reaches the processor
  logger. The focused test and full-file run will verify the order and
  behavior.
- The observed stdout rendering strongly suggests an unconfigured
  structlog path, but I have not independently confirmed the exact
  default renderer or executed a patched test.
- Only `test_batch_processor.py` was run for the reproduction. Whether
  this issue affects other `caplog` tests remains unknown.
- I have not verified behavior across other Python/platform versions.

## Deviations

Nothing changed from the plan. The implementation executed exactly as described:

- Added an autouse session-scope fixture `configure_structlog_for_tests()` to `tests/conftest.py` that calls `core.logging.configure_logging()` to initialize structlog with `LoggerFactory()` routing to stdlib logging before any tests run.
- Removed the `@pytest.mark.xfail(strict=True)` marker from `test_empty_chunks_list_returns_empty` in `tests/unit/test_batch_processor.py`.
- Ran the focused test: **1 passed** — The caplog assertion now passes; the warning is captured as a log record.
- Ran the full batch_processor test file: **11 passed** — All tests pass with no regressions.
- Ran the unit test suite: **376 passed, 52 xfailed** (vs. baseline 375 passed, 53 xfailed) — One test fixed, no regressions introduced.

The fix is working as intended. The caplog fixture now captures structlog events because structlog is configured to route through stdlib logging before tests execute.
