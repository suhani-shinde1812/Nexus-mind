"""
Central app configuration, loaded from environment variables (.env).
"""
import base64
import hashlib
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Environment & Demo Mode
    environment: str = "development"
    demo_mode: bool = False
    port: int = 8000
    host: str = "0.0.0.0"


    # Database
    database_url: str = "sqlite:///./nexusmind.db"


    # Auth & Encryption
    jwt_secret_key: str = "nexus-prod-jwt-secret-key-2026-secure-32chars"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 14
    encryption_key: str = "t8f2e-kI7x1L5rWq3Z9sB8vD2eF4gH6jK8mN0pQ2rT4="  # Fernet base64 key

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_events_channel: str = "nexusmind:events"

    # AI
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-6"

    # GitHub Webhook
    github_webhook_secret: str = "nexusmind-github-webhook-secret-2026"

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:4173,http://localhost:3000"

    # Push notifications
    fcm_server_key: str | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def fernet_key(self) -> bytes:
        """Returns a valid 32-byte urlsafe base64 key for Fernet encryption."""
        key_bytes = hashlib.sha256(self.encryption_key.encode()).digest()
        return base64.urlsafe_b64encode(key_bytes)


@lru_cache
def get_settings() -> Settings:
    return Settings()
