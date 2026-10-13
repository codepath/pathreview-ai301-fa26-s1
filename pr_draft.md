Capture structlog warnings in pytest caplog for empty input

## Summary

Configure the existing structlog-to-standard-logging integration
during pytest startup so `caplog` captures the empty-input warning
from `BatchEmbeddingProcessor`. This makes the warning assertion
reliable while preserving the `process([]) == []` behavior.

## Issue
Closes #66

## Changes
- Configure structlog through the repository's existing
  `configure_logging()` helper in `tests/conftest.py` before tests run.
- Remove the strict xfail marker from
  `test_empty_chunks_list_returns_empty`, retaining its warning-capture
  and empty-result assertions.

## Testing
- [ ] **CI is green on this PR (all five jobs)** — CI runs after opening
  the PR; no CI result is available yet.
- [x] Unit tests pass (`make test-unit`)
  - `376 passed, 52 xfailed, 5 warnings in 18.91s`.
- [ ] Integration tests pass (`make test-integration`)
  - The repository currently has no integration tests: `collected 0
    items`; pytest reports one existing Pydantic deprecation warning,
    and make exits with `Error 5`. This is expected per the course
    instructions.
- [x] Linter passes (`make lint`)
  - `All checks passed!`
- [x] Type checker passes (`make typecheck`)
  - `Success: no issues found in 76 source files`.
- [x] New/updated tests cover the changes
  - On `main` (`f89c06f`), the focused test with `--runxfail` failed:
    `caplog.text` was empty and the warning appeared only in captured
    stdout. On this branch, the same command passes (`1 passed`), and
    the full batch-processor test file passes (`11 passed`).
- [x] If this fixes a seeded bug: removed its `@pytest.mark.xfail`
  marker (and any matching suppression in `pyproject.toml`)
  - No `issue #66:` marker/suppression matches remain in `tests` or
    `pyproject.toml`.

## Screenshots / Demo

N/A — this is a backend logging/test-capture change with no visual UI.

## Notes for Reviewers

AI disclosure: I used an AI assistant to help draft and check this
change and its PR description; I reviewed the resulting code and
evidence.

The implementation follows the plan: it changes pytest logging
initialization and removes the strict xfail marker. It does not change
the warning text, application logging configuration, or empty-input
return behavior. The integration target currently finds no tests, as
recorded above.
