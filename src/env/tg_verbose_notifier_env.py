from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramVerboseNotfierEnvironSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TG_VERBOSE_NOTIFIER_", extra="ignore")

    token: str
    chat: str
