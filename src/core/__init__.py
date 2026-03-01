"""Core module containing bot instance and configuration."""

from .config import settings
from .bot import TelegramBot

__all__ = ["settings", "TelegramBot"]
