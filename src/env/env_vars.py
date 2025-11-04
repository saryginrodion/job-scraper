from typing import Literal

from pydantic import MongoDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevel = Literal["DEBUG", "WARNING", "INFO", "ERROR", "CRITICAL"]

class EnvironSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    mongodb_url: MongoDsn
    log_level: LogLevel = "DEBUG"

    log_tg_level: LogLevel
    log_tg_token: str
    log_tg_chat: str

    tg_notifier_token: str
    tg_notifier_chat: str
    tg_notifier_chat_verbose: str

env = EnvironSettings()  # type: ignore
