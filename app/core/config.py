from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/truelen_db"
    GROQ_API_KEY: str
    
    class Config:
        env_file = ".env"

settings = Settings()
