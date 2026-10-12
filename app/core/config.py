import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Hệ Thống Quản Lý Thư Viện"
    DEBUG: bool = True
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+psycopg2://postgres:postgres_password_123@postgres:5432/library_db"
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret_key_change_me")

settings = Settings()
