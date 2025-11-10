from typing import Annotated, Literal

from pydantic import MongoDsn, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

LogLevel = Literal["DEBUG", "WARNING", "INFO", "ERROR", "CRITICAL"]

class EnvironSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    kafka_servers: Annotated[list[str], NoDecode]

    celery_broker_url: str
    celery_backend_url: str

    mongodb_url: MongoDsn
    log_level: LogLevel = "DEBUG"

    log_tg_level: LogLevel
    log_tg_token: str
    log_tg_chat: str

    tg_notifier_token: str
    tg_notifier_chat: str
    tg_notifier_chat_verbose: str


    @field_validator("kafka_servers", mode="before")
    @classmethod
    def decode_kafka_servers(cls, v: str) -> list[str]:
        return v.split(",")

env = EnvironSettings()  # type: ignore
