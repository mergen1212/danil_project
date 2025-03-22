from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_prefix="config.py",  # Явное указание префикса, если нужно
    )

    SECRET_KEY: str = Field(..., alias="SECRET_KEY")
    ALGORITHM: str = Field(..., alias="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(..., alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(..., alias="REFRESH_TOKEN_EXPIRE_DAYS")
    DATABASE_URL: str = Field(..., alias="DATABASE_URL")


try:
    settings = Settings()  # type: ignore
except Exception as e:
    print(f"Ошибка конфигурации: {e}")
    exit(1)
