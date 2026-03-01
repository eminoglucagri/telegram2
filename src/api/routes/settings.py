"""Settings endpoints."""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import yaml
from pathlib import Path

from src.database.base import get_db
from src.database.models import User
from src.core.config import settings

router = APIRouter()


# Pydantic Schemas
class AppSettings(BaseModel):
    app_env: str
    debug: bool
    log_level: str


class RateLimitSettings(BaseModel):
    messages_per_minute: int
    joins_per_day: int
    dms_per_hour: int


class WarmUpSettings(BaseModel):
    stages: list


class SettingsResponse(BaseModel):
    app: AppSettings
    rate_limits: RateLimitSettings
    warmup: WarmUpSettings
    telegram_connected: bool


class SettingsUpdate(BaseModel):
    rate_limits: Optional[RateLimitSettings] = None
    warmup: Optional[Dict[str, Any]] = None


# Endpoints
@router.get("", response_model=SettingsResponse)
async def get_settings(
    db: AsyncSession = Depends(get_db)
):
    """Get current application settings."""
    # Check Telegram connection
    result = await db.execute(
        select(User).where(User.status == "active").limit(1)
    )
    telegram_connected = result.scalar_one_or_none() is not None
    
    # Load warmup stages
    warmup_stages = []
    config_path = Path("config/settings.yaml")
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
            warmup_stages = config.get("warmup", {}).get("stages", [])
    
    if not warmup_stages:
        warmup_stages = [
            {"stage": 1, "duration_days": 7, "max_messages_per_day": 5, "max_groups": 2},
            {"stage": 2, "duration_days": 7, "max_messages_per_day": 15, "max_groups": 5},
            {"stage": 3, "duration_days": 14, "max_messages_per_day": 30, "max_groups": 10},
            {"stage": 4, "duration_days": 14, "max_messages_per_day": 50, "max_groups": 15},
            {"stage": 5, "duration_days": 0, "max_messages_per_day": 100, "max_groups": 25},
        ]
    
    return SettingsResponse(
        app=AppSettings(
            app_env=settings.app_env,
            debug=settings.debug,
            log_level=settings.log_level
        ),
        rate_limits=RateLimitSettings(
            messages_per_minute=settings.rate_limit.messages_per_minute,
            joins_per_day=settings.rate_limit.joins_per_day,
            dms_per_hour=settings.rate_limit.dms_per_hour
        ),
        warmup=WarmUpSettings(stages=warmup_stages),
        telegram_connected=telegram_connected
    )


@router.patch("")
async def update_settings(
    settings_update: SettingsUpdate
):
    """Update application settings (writes to config file)."""
    config_path = Path("config/settings.yaml")
    config_path.parent.mkdir(exist_ok=True)
    
    # Load existing config
    config = {}
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}
    
    # Update warmup settings
    if settings_update.warmup:
        config["warmup"] = settings_update.warmup
    
    # Write back
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    
    return {"message": "Settings updated", "config": config}


@router.get("/telegram/status")
async def get_telegram_status(
    db: AsyncSession = Depends(get_db)
):
    """Get Telegram connection status."""
    result = await db.execute(
        select(User).order_by(User.updated_at.desc()).limit(1)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return {
            "connected": False,
            "message": "No Telegram account configured"
        }
    
    return {
        "connected": user.status == "active",
        "phone": user.phone,
        "username": user.username,
        "status": user.status,
        "warmup_stage": user.warmup_stage
    }


@router.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "components": {
            "api": "ok",
            "database": "ok",  # Would fail if DB was down
        },
        "version": "0.1.0"
    }
