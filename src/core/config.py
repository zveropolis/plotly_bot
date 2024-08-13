# from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    param_name: str
    # token: SecretStr
    ...

    @property
    def fix_param(self):
        """Параметр с фиксированным значением"""
        return


settings = Settings()
