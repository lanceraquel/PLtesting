"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-07
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def json_column():
    return sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    op.create_table(
        "research_tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("target_industry", sa.String(length=255), nullable=False),
        sa.Column("target_geography", sa.String(length=255), nullable=False),
        sa.Column("si_keywords", json_column(), nullable=False),
        sa.Column("exclusion_keywords", json_column(), nullable=False),
        sa.Column("company_size_preference", sa.String(length=255), nullable=True),
        sa.Column("service_categories", json_column(), nullable=False),
        sa.Column("max_results", sa.Integer(), nullable=False),
        sa.Column("freshness_days", sa.Integer(), nullable=True),
        sa.Column("output_format", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("search_queries", json_column(), nullable=False),
        sa.Column("report_paths", json_column(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_research_tasks_status"), "research_tasks", ["status"], unique=False)
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("normalized_name", sa.String(length=255), nullable=False),
        sa.Column("website", sa.String(length=500), nullable=True),
        sa.Column("normalized_domain", sa.String(length=255), nullable=True),
        sa.Column("linkedin_url", sa.String(length=500), nullable=True),
        sa.Column("headquarters", sa.String(length=255), nullable=True),
        sa.Column("countries_served", json_column(), nullable=False),
        sa.Column("services", json_column(), nullable=False),
        sa.Column("vendor_partnerships", json_column(), nullable=False),
        sa.Column("industries_served", json_column(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("normalized_domain", name="uq_companies_normalized_domain"),
        sa.UniqueConstraint("normalized_name", name="uq_companies_normalized_name"),
    )
    op.create_index(op.f("ix_companies_linkedin_url"), "companies", ["linkedin_url"], unique=False)
    op.create_index(op.f("ix_companies_name"), "companies", ["name"], unique=False)
    op.create_index(op.f("ix_companies_normalized_domain"), "companies", ["normalized_domain"], unique=False)
    op.create_index(op.f("ix_companies_normalized_name"), "companies", ["normalized_name"], unique=False)
    op.create_table(
        "company_contacts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("contact_page_url", sa.String(length=500), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_company_contacts_company_id"), "company_contacts", ["company_id"], unique=False)
    op.create_table(
        "company_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("source_url", sa.String(length=1000), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("evidence_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_company_sources_company_id"), "company_sources", ["company_id"], unique=False)
    op.create_table(
        "research_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("relevance_score", sa.Float(), nullable=False),
        sa.Column("scoring_breakdown", json_column(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["research_tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("task_id", "company_id", name="uq_research_result_task_company"),
    )
    op.create_index(op.f("ix_research_results_company_id"), "research_results", ["company_id"], unique=False)
    op.create_index(op.f("ix_research_results_task_id"), "research_results", ["task_id"], unique=False)
    op.create_table(
        "run_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("level", sa.String(length=32), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("metadata_json", json_column(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["research_tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_run_logs_task_id"), "run_logs", ["task_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_run_logs_task_id"), table_name="run_logs")
    op.drop_table("run_logs")
    op.drop_index(op.f("ix_research_results_task_id"), table_name="research_results")
    op.drop_index(op.f("ix_research_results_company_id"), table_name="research_results")
    op.drop_table("research_results")
    op.drop_index(op.f("ix_company_sources_company_id"), table_name="company_sources")
    op.drop_table("company_sources")
    op.drop_index(op.f("ix_company_contacts_company_id"), table_name="company_contacts")
    op.drop_table("company_contacts")
    op.drop_index(op.f("ix_companies_normalized_name"), table_name="companies")
    op.drop_index(op.f("ix_companies_normalized_domain"), table_name="companies")
    op.drop_index(op.f("ix_companies_name"), table_name="companies")
    op.drop_index(op.f("ix_companies_linkedin_url"), table_name="companies")
    op.drop_table("companies")
    op.drop_index(op.f("ix_research_tasks_status"), table_name="research_tasks")
    op.drop_table("research_tasks")
