from pydantic_settings import BaseSettings
from pydantic import Field, computed_field
from typing import List

class Settings(BaseSettings):
    # Database settings
    DB_HOST: str = Field(default="localhost")
    DB_PORT: str = Field(default="5432")
    DB_NAME: str = Field(default="mnfstportal_db")
    DB_USER: str = Field(default="postgres")
    DB_PASS: str = Field(default="")
    
    # JWT settings
    JWT_SECRET_KEY: str = Field(default="")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    
    # API Keys
    OPENAI_API_KEY: str = Field(default="")
    OPENAI_MODEL: str = Field(default="gpt-4-1106-preview")
    PYDANTIC_AI_KEY: str = Field(default="")
    
    # CORS settings
    CORS_ORIGINS: str = Field(default="http://localhost:5173")
    
    # API settings
    API_V1_STR: str = Field(default="/api/v1")
    PROJECT_NAME: str = Field(default="MNFST Portal API")
    
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components."""
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
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