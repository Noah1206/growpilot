"""Application configuration using Pydantic settings."""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    supabase_url: Optional[str] = Field(default=None, env="SUPABASE_URL")
    supabase_key: Optional[str] = Field(default=None, env="SUPABASE_KEY")

    # Reddit API Credentials
    reddit_client_id: str = Field(default="", env="REDDIT_CLIENT_ID")
    reddit_client_secret: str = Field(default="", env="REDDIT_CLIENT_SECRET")
    reddit_user_agent: str = Field(default="GrowthPilot/1.0", env="REDDIT_USER_AGENT")
    reddit_username: str = Field(default="", env="REDDIT_USERNAME")
    reddit_password: str = Field(default="", env="REDDIT_PASSWORD")

    # Twitter API Credentials
    twitter_api_key: str = Field(default="", env="TWITTER_API_KEY")
    twitter_api_secret: str = Field(default="", env="TWITTER_API_SECRET")
    twitter_access_token: str = Field(default="", env="TWITTER_ACCESS_TOKEN")
    twitter_access_secret: str = Field(default="", env="TWITTER_ACCESS_SECRET")
    twitter_bearer_token: str = Field(default="", env="TWITTER_BEARER_TOKEN")

    # Database
    database_url: str = Field(default="sqlite:///./growthpilot.db", env="DATABASE_URL")

    # Application
    secret_key: str = Field(default="development-secret-key-change-in-production", env="SECRET_KEY")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")

    # CORS
    allowed_origins: str = Field(
        default="http://localhost:9000,http://127.0.0.1:9000,https://growthpilot-production.up.railway.app",
        env="ALLOWED_ORIGINS"
    )

    @property
    def cors_origins(self) -> List[str]:
        """Parse allowed_origins string into list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    # Rate Limiting
    max_daily_sends_linkedin: int = Field(default=200, env="MAX_DAILY_SENDS_LINKEDIN")
    max_daily_sends_reddit: int = Field(default=2000, env="MAX_DAILY_SENDS_REDDIT")
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
