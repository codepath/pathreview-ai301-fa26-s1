"""add source_id to ingested_sources

Revision ID: 003_add_source_id_to_ingested_sources
Revises: 002_add_error_message_to_reviews
Create Date: 2026-10-01 23:30:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "003_add_source_id_to_ingested_sources"
down_revision = "002_add_error_message_to_reviews"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ingested_sources",
        sa.Column("source_id", sa.String(length=255), nullable=True),
    )
    op.create_index(
        "ix_ingested_sources_source_id",
        "ingested_sources",
        ["source_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_ingested_sources_source_id", table_name="ingested_sources")
    op.drop_column("ingested_sources", "source_id")
