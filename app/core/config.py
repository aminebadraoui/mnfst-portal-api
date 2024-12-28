from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "mnfst-portal"
    VERSION: str = "1.0.0"
    
    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "mnfst-portal"
    DB_USER: str = "postgres"
    DB_PASS: str = "postgres"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        env_file = ".env"

settings = Settings()
