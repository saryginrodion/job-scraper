from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class HeadHunterScraperEnvironSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HH_SCRAPER_", extra="ignore")

    urls: Annotated[list[str], NoDecode]

    @field_validator("urls", mode="before")
    @classmethod
    def decode_urls(cls, v: str) -> list[str]:
        return [line.strip() for line in v.splitlines() if line.strip()]
