from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class KafkaNotfierEnvironSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KAFKA_NOTIFIER_", extra="ignore")

    servers: Annotated[list[str], NoDecode]

    @field_validator("servers", mode="before")
    @classmethod
    def decode_servers(cls, v: str) -> list[str]:
        return v.split(",")
