from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # API Settings
    app_name: str = "SmartMirror Backend"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 80

    # LLM Settings (DeepSeek) - Primary
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.artemox.com/v1"
    deepseek_model: str = "deepseek-chat"
    deepseek_timeout: int = 10

    # LLM Settings (DeepSeek) - Fallback
    deepseek_fallback_api_key: str = ""
    deepseek_fallback_base_url: str = "https://api.deepseek.com/v1"
    deepseek_fallback_model: str = "deepseek-chat"

    # Retry settings
    llm_max_retries: int = 2

    # Yandex Music Settings
    yandex_music_token: str = ""

    # Security
    secret_key: str = "your-secret-key-change-in-production"


settings = Settings()
