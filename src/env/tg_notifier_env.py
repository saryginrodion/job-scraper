from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramNotfierEnvironSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TG_NOTIFIER_", extra="ignore")

    token: str
    chat: str
