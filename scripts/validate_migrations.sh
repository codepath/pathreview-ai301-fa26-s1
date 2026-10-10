#!/usr/bin/env bash
# Run `alembic upgrade head` against DATABASE_URL and fail on any migration error.
# This project's alembic/env.py uses create_async_engine, so DATABASE_URL must
# use an async driver (e.g. postgresql+asyncpg://).
# Schema-vs-model check (alembic check) tracked in #80.

set -euo pipefail

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is not set" >&2
  exit 1
fi

alembic upgrade head
