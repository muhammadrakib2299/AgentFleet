from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment / .env.

    Required values have no default so the process fails fast at startup
    with a clear pydantic validation error instead of a mid-request crash.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    anthropic_api_key: SecretStr
    postgres_url: str = "postgresql+asyncpg://agentfleet:agentfleet@localhost:5432/agentfleet"
    redis_url: str = "redis://localhost:6379/0"

    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: str = Field(
        default="http://localhost:5173",
        description="Comma-separated list of allowed browser origins",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
