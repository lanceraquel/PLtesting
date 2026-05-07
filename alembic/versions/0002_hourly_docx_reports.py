"""hourly docx reports

Revision ID: 0002_hourly_docx_reports
Revises: 0001_initial
Create Date: 2026-05-07
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_hourly_docx_reports"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("research_tasks", sa.Column("run_interval_minutes", sa.Integer(), nullable=True))
    op.add_column("research_tasks", sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("research_tasks", sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f("ix_research_tasks_next_run_at"), "research_tasks", ["next_run_at"], unique=False)
    op.create_table(
        "report_artifacts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("format", sa.String(length=32), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=False),
        sa.Column("content", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["research_tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_report_artifacts_created_at"), "report_artifacts", ["created_at"], unique=False)
    op.create_index(op.f("ix_report_artifacts_format"), "report_artifacts", ["format"], unique=False)
    op.create_index(op.f("ix_report_artifacts_task_id"), "report_artifacts", ["task_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_report_artifacts_task_id"), table_name="report_artifacts")
    op.drop_index(op.f("ix_report_artifacts_format"), table_name="report_artifacts")
    op.drop_index(op.f("ix_report_artifacts_created_at"), table_name="report_artifacts")
    op.drop_table("report_artifacts")
    op.drop_index(op.f("ix_research_tasks_next_run_at"), table_name="research_tasks")
    op.drop_column("research_tasks", "next_run_at")
    op.drop_column("research_tasks", "last_run_at")
    op.drop_column("research_tasks", "run_interval_minutes")
