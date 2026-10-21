#!/usr/bin/env bash
# Validate Alembic migrations: apply them all, then verify the models match.
#
# IMPORTANT: this script must be run against an EMPTY database. It applies every
# migration from scratch via `alembic upgrade head`, so a database that already
# has tables or a populated alembic_version table will give misleading results.
#
# Usage:
#   DATABASE_URL=postgresql+asyncpg://user:pass@host:port/dbname scripts/validate_migrations.sh
set -euo pipefail

DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://pathreview:pathreview@localhost:5433/pathreview_dev}"

# alembic/env.py uses the async engine, so a plain postgresql:// URL must be
# rewritten to use the asyncpg driver.
if [[ "${DATABASE_URL}" == postgresql://* ]]; then
    DATABASE_URL="postgresql+asyncpg://${DATABASE_URL#postgresql://}"
fi
export DATABASE_URL

echo "Running: alembic upgrade head"
alembic upgrade head

echo "Running: alembic check"
alembic check
