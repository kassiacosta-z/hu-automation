"""add gmail/gdrive fields

Revision ID: 0002_gmail_gdrive_fields
Revises: 0001_initial
Create Date: 2025-09-23 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = '0002_gmail_gdrive_fields'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('transcription_jobs', sa.Column('collaborator_email', sa.String(length=255), nullable=True))
    op.create_index('ix_jobs_collaborator_email', 'transcription_jobs', ['collaborator_email'])
    op.add_column('processing_artifacts', sa.Column('gdrive_path', sa.String(length=1024), nullable=True))


def downgrade() -> None:
    op.drop_column('processing_artifacts', 'gdrive_path')
    op.drop_index('ix_jobs_collaborator_email', table_name='transcription_jobs')
    op.drop_column('transcription_jobs', 'collaborator_email')


