from pydantic_settings import BaseSettings
from pydantic import Field, computed_field, validator, PostgresDsn
from typing import List
from dotenv import load_dotenv
import os
from typing import Optional, Dict, Any

# Load the environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "MNFST Portal"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DEV_DB_USER: str = Field(default="admin")
    DEV_DB_PASSWORD: str = Field(default="admin")
    DEV_DB_NAME: str = Field(default="mnfst_labs_dev")
    DB_HOST: str = Field(default="localhost")
    DB_PORT: str = Field(default="5432")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DEV_DB_USER}:{self.DEV_DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DEV_DB_NAME}"
    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return str(PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("DEV_DB_USER"),
            password=values.get("DEV_DB_PASSWORD"),
            host=values.get("DB_HOST"),
            path=f"/{values.get('DEV_DB_NAME') or ''}",
        ))
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    
    # JWT settings
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    JWT_SECRET_KEY: str
    
    # API Keys
    OPENAI_API_KEY: str = Field(default="")
    OPENAI_MODEL: str = Field(default="gpt-4-1106-preview")
    PYDANTIC_AI_KEY: str = Field(default="")
    
    # CORS settings
    CORS_ORIGINS: str = Field(default="http://localhost:5173,http://localhost:8000")
    
    @computed_field
    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        """Convert CORS_ORIGINS string to list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings() 