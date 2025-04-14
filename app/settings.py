from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path(__file__).parent.parent.joinpath(".env.dev").__str__())
    # Service configs
    HOST: Optional[str] = "0.0.0.0"
    PORT: Optional[int] = 65000

    # Database credentials
    POSTGRES_USER: Optional[str]
    POSTGRES_PASSWORD: Optional[str]
    POSTGRES_HOST: Optional[str]
    POSTGRES_DB: Optional[str]
    POSTGRES_PORT: Optional[str]

    @property
    def DB_URL(cls):
        return f"postgresql+asyncpg://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"

settings = Settings()
