"""Configuration management using Pydantic Settings."""

from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import yaml
from pathlib import Path


class TelegramSettings(BaseSettings):
    """Telegram API settings."""
    api_id: int = Field(..., description="Telegram API ID")
    api_hash: str = Field(..., description="Telegram API Hash")
    phone: str = Field(..., description="Telegram phone number")
    session_string: Optional[str] = Field(None, description="Session string for persistence")
    
    model_config = SettingsConfigDict(
        env_prefix="TELEGRAM_",
        extra="ignore"
    )


class OpenAISettings(BaseSettings):
    """OpenAI API settings."""
    api_key: str = Field(..., description="OpenAI API key")
    model: str = Field("gpt-4-turbo-preview", description="OpenAI model to use")
    max_tokens: int = Field(500, description="Max tokens per response")
    temperature: float = Field(0.7, description="Response temperature")
    
    model_config = SettingsConfigDict(
        env_prefix="OPENAI_",
        extra="ignore"
    )


class DatabaseSettings(BaseSettings):
    """Database settings."""
    url: str = Field(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/telegram_agent",
        description="Async database URL"
    )
    url_sync: str = Field(
        "postgresql://postgres:postgres@localhost:5432/telegram_agent",
        description="Sync database URL for migrations"
    )
    echo: bool = Field(False, description="Echo SQL queries")
    pool_size: int = Field(5, description="Connection pool size")
    
    model_config = SettingsConfigDict(
        env_prefix="DATABASE_",
        extra="ignore"
    )


class RedisSettings(BaseSettings):
    """Redis settings."""
    url: str = Field("redis://localhost:6379/0", description="Redis URL")
    
    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
        extra="ignore"
    )


class RateLimitSettings(BaseSettings):
    """Rate limiting settings."""
    messages_per_minute: int = Field(3, description="Max messages per minute")
    joins_per_day: int = Field(5, description="Max group joins per day")
    dms_per_hour: int = Field(10, description="Max DMs per hour")
    
    model_config = SettingsConfigDict(
        env_prefix="RATE_LIMIT_",
        extra="ignore"
    )


class WarmUpStage(BaseSettings):
    """Warm-up stage configuration."""
    stage: int
    duration_days: int
    max_messages_per_day: int
    max_groups: int
    allowed_actions: List[str]


class Settings(BaseSettings):
    """Main application settings."""
    app_env: str = Field("development", description="Application environment")
    debug: bool = Field(True, description="Debug mode")
    log_level: str = Field("INFO", description="Logging level")
    secret_key: str = Field("change-me-in-production", description="Secret key")
    api_key: str = Field("change-me", description="API key for endpoints")
    
    telegram: TelegramSettings = Field(default_factory=TelegramSettings)
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    rate_limit: RateLimitSettings = Field(default_factory=RateLimitSettings)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    @staticmethod
    def load_yaml_config(file_path: str) -> dict:
        """Load configuration from YAML file."""
        path = Path(file_path)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {}
    
    def get_warmup_stages(self) -> List[WarmUpStage]:
        """Get warm-up stages from config file."""
        config = self.load_yaml_config("config/settings.yaml")
        stages = config.get("warmup", {}).get("stages", [])
        return [WarmUpStage(**stage) for stage in stages] if stages else self._default_warmup_stages()
    
    def _default_warmup_stages(self) -> List[WarmUpStage]:
        """Default warm-up stages."""
        return [
            WarmUpStage(stage=1, duration_days=7, max_messages_per_day=5, max_groups=2, allowed_actions=["read", "react"]),
            WarmUpStage(stage=2, duration_days=7, max_messages_per_day=15, max_groups=5, allowed_actions=["read", "react", "reply"]),
            WarmUpStage(stage=3, duration_days=14, max_messages_per_day=30, max_groups=10, allowed_actions=["read", "react", "reply", "initiate"]),
            WarmUpStage(stage=4, duration_days=14, max_messages_per_day=50, max_groups=15, allowed_actions=["read", "react", "reply", "initiate", "dm_reply"]),
            WarmUpStage(stage=5, duration_days=0, max_messages_per_day=100, max_groups=25, allowed_actions=["read", "react", "reply", "initiate", "dm_reply", "dm_initiate"]),
        ]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
