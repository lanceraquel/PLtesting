from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./si_research.db", alias="DATABASE_URL")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    search_api_key: str | None = Field(default=None, alias="SEARCH_API_KEY")
    user_agent: str = Field(default="SIResearchAgent/1.0", alias="USER_AGENT")
    rate_limit_seconds: float = Field(default=1.0, alias="RATE_LIMIT_SECONDS")
    worker_poll_interval_seconds: int = Field(default=15, alias="WORKER_POLL_INTERVAL_SECONDS")
    default_max_results: int = Field(default=25, alias="DEFAULT_MAX_RESULTS")
    report_output_dir: str = Field(default="reports", alias="REPORT_OUTPUT_DIR")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()

