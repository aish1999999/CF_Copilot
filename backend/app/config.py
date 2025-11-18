"""
Application configuration
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # App
    app_name: str = "Career Fair Copilot API"
    debug: bool = True
    version: str = "1.0.0"

    # Database
    database_url: str = "sqlite:///./cf_copilot.db"

    # For PostgreSQL, use:
    # database_url: str = "postgresql://user:password@localhost/cf_copilot"

    # API
    api_v1_prefix: str = "/api/v1"

    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173"]

    # Routing
    avg_walking_speed_mps: float = 1.4  # meters per second
    avg_interaction_time_min: float = 5.0  # minutes
    avg_queue_wait_per_person_min: float = 1.0  # minutes

    # Company Scoring Weights
    weight_major: float = 0.4
    weight_role: float = 0.3
    weight_interest: float = 0.2
    weight_recency: float = 0.1

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    """Get cached settings instance."""
    return Settings()
