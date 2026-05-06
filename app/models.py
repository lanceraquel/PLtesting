from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database import Base


def json_type():
    return JSON().with_variant(JSONB, "postgresql")


class TaskStatus(StrEnum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class ResearchTask(Base):
    __tablename__ = "research_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    target_industry: Mapped[str] = mapped_column(String(255))
    target_geography: Mapped[str] = mapped_column(String(255))
    si_keywords: Mapped[list[str]] = mapped_column(MutableList.as_mutable(json_type()), default=list)
    exclusion_keywords: Mapped[list[str]] = mapped_column(MutableList.as_mutable(json_type()), default=list)
    company_size_preference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    service_categories: Mapped[list[str]] = mapped_column(MutableList.as_mutable(json_type()), default=list)
    max_results: Mapped[int] = mapped_column(Integer, default=25)
    freshness_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_format: Mapped[str] = mapped_column(String(32), default="markdown")
    status: Mapped[str] = mapped_column(String(32), default=TaskStatus.queued.value, index=True)
    search_queries: Mapped[list[str]] = mapped_column(MutableList.as_mutable(json_type()), default=list)
    report_paths: Mapped[dict[str, str]] = mapped_column(MutableDict.as_mutable(json_type()), default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    results: Mapped[list["ResearchResult"]] = relationship(back_populates="task", cascade="all, delete-orphan")
    logs: Mapped[list["RunLog"]] = relationship(back_populates="task", cascade="all, delete-orphan")


class Company(Base):
    __tablename__ = "companies"
    __table_args__ = (
        UniqueConstraint("normalized_domain", name="uq_companies_normalized_domain"),
        UniqueConstraint("normalized_name", name="uq_companies_normalized_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    normalized_name: Mapped[str] = mapped_column(String(255), index=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    normalized_domain: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(500), nullable=True, index=True)
    headquarters: Mapped[str | None] = mapped_column(String(255), nullable=True)
    countries_served: Mapped[list[str]] = mapped_column(MutableList.as_mutable(json_type()), default=list)
    services: Mapped[list[str]] = mapped_column(MutableList.as_mutable(json_type()), default=list)
    vendor_partnerships: Mapped[list[str]] = mapped_column(MutableList.as_mutable(json_type()), default=list)
    industries_served: Mapped[list[str]] = mapped_column(MutableList.as_mutable(json_type()), default=list)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    sources: Mapped[list["CompanySource"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    contacts: Mapped[list["CompanyContact"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    results: Mapped[list["ResearchResult"]] = relationship(back_populates="company")


class CompanySource(Base):
    __tablename__ = "company_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    source_url: Mapped[str] = mapped_column(String(1000))
    source_type: Mapped[str] = mapped_column(String(64), default="search")
    evidence_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    company: Mapped[Company] = relationship(back_populates="sources")


class CompanyContact(Base):
    __tablename__ = "company_contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    contact_page_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    company: Mapped[Company] = relationship(back_populates="contacts")


class ResearchResult(Base):
    __tablename__ = "research_results"
    __table_args__ = (UniqueConstraint("task_id", "company_id", name="uq_research_result_task_company"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("research_tasks.id", ondelete="CASCADE"), index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    scoring_breakdown: Mapped[dict[str, float]] = mapped_column(MutableDict.as_mutable(json_type()), default=dict)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    task: Mapped[ResearchTask] = relationship(back_populates="results")
    company: Mapped[Company] = relationship(back_populates="results")


class RunLog(Base):
    __tablename__ = "run_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("research_tasks.id", ondelete="CASCADE"), index=True)
    level: Mapped[str] = mapped_column(String(32), default="info")
    message: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[dict[str, object]] = mapped_column(MutableDict.as_mutable(json_type()), default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    task: Mapped[ResearchTask] = relationship(back_populates="logs")
