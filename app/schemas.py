from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ResearchTaskCreate(BaseModel):
    target_industry: str = Field(min_length=1, max_length=255)
    target_geography: str = Field(min_length=1, max_length=255)
    si_keywords: list[str] = Field(default_factory=list)
    exclusion_keywords: list[str] = Field(default_factory=list)
    company_size_preference: str | None = None
    service_categories: list[str] = Field(default_factory=list)
    max_results: int = Field(default=25, ge=1, le=500)
    freshness_days: int | None = Field(default=None, ge=1)
    output_format: str = Field(default="markdown")

    @field_validator("si_keywords", "exclusion_keywords", "service_categories")
    @classmethod
    def strip_list_items(cls, values: list[str]) -> list[str]:
        return [item.strip() for item in values if item.strip()]


class ResearchTaskRead(ResearchTaskCreate):
    id: int
    status: str
    search_queries: list[str]
    report_paths: dict[str, str]
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanySourceRead(BaseModel):
    id: int
    source_url: str
    source_type: str
    evidence_text: str | None

    model_config = ConfigDict(from_attributes=True)


class CompanyContactRead(BaseModel):
    id: int
    contact_page_url: str | None
    email: str | None
    phone: str | None

    model_config = ConfigDict(from_attributes=True)


class CompanyRead(BaseModel):
    id: int
    name: str
    website: str | None
    normalized_domain: str | None
    linkedin_url: str | None
    headquarters: str | None
    countries_served: list[str]
    services: list[str]
    vendor_partnerships: list[str]
    industries_served: list[str]
    description: str | None
    notes: str | None
    confidence_score: float
    sources: list[CompanySourceRead] = Field(default_factory=list)
    contacts: list[CompanyContactRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ResearchResultRead(BaseModel):
    id: int
    task_id: int
    company_id: int
    relevance_score: float
    scoring_breakdown: dict[str, float]
    rank: int | None
    notes: str | None
    company: CompanyRead

    model_config = ConfigDict(from_attributes=True)


class HealthRead(BaseModel):
    status: str
    database: str

