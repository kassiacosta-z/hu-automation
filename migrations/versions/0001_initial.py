"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2025-09-23 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
	op.create_table(
		'transcription_jobs',
		sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
		sa.Column('source_uri', sa.String(length=1024), nullable=False),
		sa.Column('source_hash', sa.String(length=128), nullable=False),
		sa.Column('status', sa.String(length=32), nullable=False),
		sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
		sa.Column('created_at', sa.DateTime(), nullable=False),
		sa.Column('updated_at', sa.DateTime(), nullable=False),
	)
	op.create_index('ix_jobs_source_uri', 'transcription_jobs', ['source_uri'])
	op.create_index('ix_jobs_source_hash', 'transcription_jobs', ['source_hash'])
	op.create_index('ix_jobs_status', 'transcription_jobs', ['status'])

	op.create_table(
		'processing_artifacts',
		sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
		sa.Column('job_id', sa.Integer(), sa.ForeignKey('transcription_jobs.id', ondelete='CASCADE'), nullable=False),
		sa.Column('type', sa.String(length=16), nullable=False),
		sa.Column('path', sa.String(length=2048), nullable=False),
		sa.Column('size', sa.BigInteger(), nullable=True),
		sa.Column('created_at', sa.DateTime(), nullable=False),
	)
	op.create_index('ix_artifacts_job_id', 'processing_artifacts', ['job_id'])

	op.create_table(
		'processing_logs',
		sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
		sa.Column('job_id', sa.Integer(), sa.ForeignKey('transcription_jobs.id', ondelete='CASCADE'), nullable=False),
		sa.Column('level', sa.String(length=16), nullable=False),
		sa.Column('message', sa.String(length=4000), nullable=False),
		sa.Column('timestamp', sa.DateTime(), nullable=False),
	)
	op.create_index('ix_logs_job_id', 'processing_logs', ['job_id'])
	op.create_index('ix_logs_timestamp', 'processing_logs', ['timestamp'])


def downgrade() -> None:
	op.drop_index('ix_logs_timestamp', table_name='processing_logs')
	op.drop_index('ix_logs_job_id', table_name='processing_logs')
	op.drop_table('processing_logs')

	op.drop_index('ix_artifacts_job_id', table_name='processing_artifacts')
	op.drop_table('processing_artifacts')

	op.drop_index('ix_jobs_status', table_name='transcription_jobs')
	op.drop_index('ix_jobs_source_hash', table_name='transcription_jobs')
	op.drop_index('ix_jobs_source_uri', table_name='transcription_jobs')
	op.drop_table('transcription_jobs')
