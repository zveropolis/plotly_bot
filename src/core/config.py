import os

from pydantic import HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.orm import DeclarativeBase

from core.path import PATH


class AuthorizeVar(BaseSettings):
    client_id: SecretStr
    client_secret: SecretStr


class Base(DeclarativeBase):
    def __repr__(self):
        cols = [f"{col}={getattr(self, col)}" for col in self.__table__.columns.keys()]
        return f"<{self.__class__.__name__} {', '.join(cols)}>"


class Settings(BaseSettings):
    bot_token: SecretStr
    yoo_token: SecretStr

    BOT_URL: HttpUrl = "https://t.me/vpn_dan_bot"

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: SecretStr
    DB_NAME: str

    cycle_duration: float

    model_config = SettingsConfigDict(
        env_file=os.path.join(PATH, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def DATABASE_URL(self):
        """URL для подключения к базе (asyncpg)

        Returns:
            str: postgresql+asyncpg://username:password@localhost:port/base
        """
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS.get_secret_value()}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
