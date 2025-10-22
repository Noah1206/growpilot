"""Application configuration using Pydantic settings."""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    supabase_url: Optional[str] = Field(default=None, env="SUPABASE_URL")
    supabase_key: Optional[str] = Field(default=None, env="SUPABASE_KEY")

    # Database
    database_url: str = Field(..., env="DATABASE_URL")

    # Application
    secret_key: str = Field(..., env="SECRET_KEY")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")

    # CORS
    allowed_origins: str = Field(
        default="http://localhost:9000,http://127.0.0.1:9000,http://localhost:6000,http://127.0.0.1:6000",
        env="ALLOWED_ORIGINS"
    )

    @property
    def cors_origins(self) -> List[str]:
        """Parse allowed_origins string into list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    # Rate Limiting
    max_daily_sends_linkedin: int = Field(default=200, env="MAX_DAILY_SENDS_LINKEDIN")
    max_daily_sends_reddit: int = Field(default=30, env="MAX_DAILY_SENDS_REDDIT")
    max_daily_sends_facebook: int = Field(default=50, env="MAX_DAILY_SENDS_FACEBOOK")

    # Platform Rules
    platform_rules: dict = {
        "linkedin": {
            "max_chars": 280,
            "links": "one_link",
            "tone": "value_first",
            "ban": ["financial guarantees", "spammy urgency", "guaranteed returns"]
        },
        "reddit": {
            "max_sentences": 5,
            "links": "one_link",
            "tone": "conversational",
            "ban": ["pure self-promo", "multi-link dumping", "spam"]
        },
        "facebook": {
            "max_sentences": 6,
            "links": "one_link",
            "tone": "friendly",
            "ban": ["aggressive selling", "misleading claims", "clickbait"]
        }
    }

    # Safety Configuration
    blocked_phrases: List[str] = [
        "guaranteed returns",
        "get rich quick",
        "limited time only",
        "act now",
        "special offer expires",
        "100% guaranteed",
        "risk-free",
        "make money fast"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
