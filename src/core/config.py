import logging
import os
import pickle
from datetime import datetime

from pandas import DataFrame
from pydantic import HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.orm import DeclarativeBase

from core.path import PATH

logger = logging.getLogger()


class AuthorizeVar(BaseSettings):
    client_id: SecretStr
    client_secret: SecretStr


class Base(DeclarativeBase):
    def __repr__(self):
        cols = [f"{col}={getattr(self, col)}" for col in self.__table__.columns.keys()]
        return f"<{self.__class__.__name__} {', '.join(cols)}>"

    @property
    def __udict__(self):
        model_data = {col: getattr(self, col) for col in self.__table__.columns.keys()}
        # model_data.pop("id")
        return model_data

    @property
    def __ustr_dict__(self):
        model_data = {
            col: str(getattr(self, col)) for col in self.__table__.columns.keys()
        }
        # model_data.pop("id")
        return model_data

    @property
    def frame(self):
        return DataFrame([self.__udict__]).dropna(how="all")

    def get_frame(self, *objects):
        res = []
        for obj in objects:
            if type(obj) is type(self):
                res.append(obj.__udict__)
            else:
                res.append(self.__udict__)
        return DataFrame(res).dropna(how="all")


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    YOO_TOKEN: SecretStr

    BOT_CHAT: int
    BOT_URL: HttpUrl = "https://t.me/vpn_dan_bot"
    subserver_url: HttpUrl = "http:/assa.ddns.net"

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: SecretStr
    DB_NAME: str

    ADMIN_LOGIN: str
    ADMIN_PASS: SecretStr
    ADMIN_HASH: SecretStr
    JWT_SECRET: SecretStr

    WG_HOST: str
    WG_PORT: int
    WG_USER: str
    WG_PASS: SecretStr
    WG_KEY: SecretStr
    WG_SERVER_KEY: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USER: str
    REDIS_PASS: SecretStr
    REDIS_NAME: str

    acceptable_config: dict = {0: 0, 0.3: 1, 1: 3, 2.5: 8, 5: 15}
    cost: float
    cash_ttl: int
    transfer_fee: float
    max_dumps: int

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

    @property
    def CASHBASE_URL(self):
        """URL для подключения к базе (redis)

        Returns:
            str: redis://LOGIN:PASSWORD@HOST:PORT/NUM_DB
        """
        return f"redis://{self.REDIS_USER}:{self.REDIS_PASS.get_secret_value()}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_NAME}"


try:
    settings = Settings()

except ValueError:
    logger.exception("Ошибка загрузки входных параметров")
    raise


last_updated = datetime.today()
decr_time = os.path.join(PATH, "src", "scheduler", "last_decremented.pickle")
noticed_time = os.path.join(PATH, "src", "scheduler", "last_noticed.pickle")

# for timefile in (decr_time, noticed_time):
#     with open(timefile, "wb") as file:
#         pickle.dump(last_updated, file)
