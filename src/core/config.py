import os

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.path import PATH


class Settings(BaseSettings):
    bot_token: SecretStr

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(PATH), ".env"),
        env_file_encoding="utf-8",
    )


settings = Settings()
