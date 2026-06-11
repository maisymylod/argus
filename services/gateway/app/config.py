from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Gateway configuration, sourced from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    log_level: str = "INFO"
    database_url: str = "postgresql://argus:change-me-locally@db:5432/argus"
    stac_url: str = "https://planetarycomputer.microsoft.com/api/stac/v1"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"
    anthropic_model_heavy: str = "claude-opus-4-8"

    cors_origins: list[str] = ["*"]


settings = Settings()
