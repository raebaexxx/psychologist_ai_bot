from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    bot_token: str
    openrouter_api_key: str
    openrouter_model: str = "openrouter/free"
    whisper_model_size: str = "medium"
    database_path: str = "data/diary.db"


settings = Settings()
