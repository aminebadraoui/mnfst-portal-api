from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # API settings
    project_name: str = "MNFST Portal API"
    api_v1_str: str = "/api/v1"

    # Database settings
    db_host: str = "157.245.0.147"
    db_port: str = "5432"
    dev_db_user: str = "admin"
    dev_db_password: str = "admin"
    dev_db_name: str = "mnfst_labs_dev"
    sqlalchemy_database_uri: Optional[str] = None

    # JWT settings
    jwt_secret_key: str = "OBhZthyI/PSKRZUcIB3hH4HE7YsmHSOs2sy84ZC/EB8="
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 days

    # API Keys
    openai_api_key: str = ""
    openai_model: str = "gpt-4-1106-preview"
    pydantic_ai_key: str = ""

    # CORS settings
    cors_origins: str = "http://localhost:5173"

    # Redis settings
    redis_host: str = "localhost"
    redis_port: str = "6379"
    redis_url: str = "redis://localhost:6379/0"

    # Computed properties
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.dev_db_user}:{self.dev_db_password}@{self.db_host}:{self.db_port}/{self.dev_db_name}"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True
        env_prefix = ""
        extra = "allow"

@lru_cache()
def get_settings():
    return Settings() 