from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "Waypoint 360"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:////tmp/waypoint360.db"

    # Auth
    SECRET_KEY: str = "waypoint360-dev-secret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours

    # AI / LangGraph
    ANTHROPIC_API_KEY: Optional[str] = None
    AI_MODEL: str = "claude-sonnet-4-20250514"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()
