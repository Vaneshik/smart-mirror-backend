from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # API Settings
    app_name: str = "SmartMirror Backend"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # LLM Settings (DeepSeek)
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"
    deepseek_timeout: int = 30
    
    # Yandex Music Settings
    yandex_music_token: str = ""
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    
    
settings = Settings()

