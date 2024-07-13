from typing import Set

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    database_url: str
    admin_telegram_ids: Set[int]
    page_limit: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


config = Settings()
