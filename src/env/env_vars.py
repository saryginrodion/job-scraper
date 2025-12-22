from typing import Annotated, Literal

from pydantic import MongoDsn, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict
from dotenv import load_dotenv

LogLevel = Literal["DEBUG", "WARNING", "INFO", "ERROR", "CRITICAL"]

load_dotenv()


class EnvironSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    celery_broker_url: str
    celery_backend_url: str

    mongodb_url: MongoDsn
    log_level: LogLevel = "DEBUG"

    log_tg_level: LogLevel
    log_tg_token: str
    log_tg_chat: str

    notifiers: Annotated[list[str], NoDecode]
    scrapers: Annotated[list[str], NoDecode]

    @field_validator("notifiers", mode="before")
    @classmethod
    def decode_notifiers_list(cls, v: str) -> list[str]:
        return v.split(",")

    @field_validator("scrapers", mode="before")
    @classmethod
    def decode_scrapers_list(cls, v: str) -> list[str]:
        return v.split(",")


env = EnvironSettings()  # type: ignore
