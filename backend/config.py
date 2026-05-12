"""Application configuration loaded from .env."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o"

    # Supabase
    supabase_url: str
    supabase_key: str           # publishable (anon) key — used by frontend
    supabase_secret: str        # service-role key — REQUIRED for backend writes (RLS bypass)

    # Auth
    secret_key: str = "smartcontent-secret-2024"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # n8n
    n8n_webhook_url: str = "http://localhost:5678/webhook-test/smartcontent-publish"

    # App
    app_env: str = "development"
    app_port: int = 8001

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
