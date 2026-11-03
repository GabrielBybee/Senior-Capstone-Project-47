from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings read from environment variables (or a local .env file)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mindrouter_base_url: str = "https://mindrouter.uidaho.edu/v1"
    mindrouter_api_key: str = ""
    mindrouter_model: str = "qwen3-coder:30b"
    runner_url: str = "http://localhost:8001"


settings = Settings()
