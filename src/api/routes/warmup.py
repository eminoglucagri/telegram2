"""Warm-up tracking endpoints."""

from typing import List, Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base import get_db
from src.database.models import User, WarmUpMetric

router = APIRouter()


# Pydantic Schemas
class WarmUpMetricResponse(BaseModel):
    id: int
    user_id: int
    date: date
    messages_sent: int
    messages_received: int
    groups_joined: int
    groups_left: int
    dms_sent: int
    dms_received: int
    reactions_given: int
    warmup_stage: int
    score: float

    class Config:
        from_attributes = True


class WarmUpStatus(BaseModel):
    current_stage: int
    stage_description: str
    days_at_stage: int
    days_required: int
    health_score: float
    today: dict
    allowed_actions: List[str]
    can_progress: bool


class WarmUpStageInfo(BaseModel):
    stage: int
    description: str
    duration_days: int
    max_messages_per_day: int
    max_groups: int
    allowed_actions: List[str]


STAGES = {
    1: {
        "description": "Observation phase - minimal activity",
        "duration_days": 7,
        "max_messages_per_day": 5,
        "max_groups": 2,
        "allowed_actions": ["read", "react"]
    },
    2: {
        "description": "Light engagement - replies only",
        "duration_days": 7,
        "max_messages_per_day": 15,
        "max_groups": 5,
        "allowed_actions": ["read", "react", "reply"]
    },
    3: {
        "description": "Moderate activity - can start conversations",
        "duration_days": 14,
        "max_messages_per_day": 30,
        "max_groups": 10,
        "allowed_actions": ["read", "react", "reply", "initiate"]
    },
    4: {
        "description": "Active participation - DM replies allowed",
        "duration_days": 14,
        "max_messages_per_day": 50,
        "max_groups": 15,
        "allowed_actions": ["read", "react", "reply", "initiate", "dm_reply"]
    },
    5: {
        "description": "Full activity - all actions allowed",
        "duration_days": 0,
        "max_messages_per_day": 100,
        "max_groups": 25,
        "allowed_actions": ["read", "react", "reply", "initiate", "dm_reply", "dm_initiate"]
    }
}


# Endpoints
@router.get("/status")
async def get_warmup_status(
    user_id: int = Query(1, description="User ID"),
    db: AsyncSession = Depends(get_db)
) -> WarmUpStatus:
    """Get current warm-up status."""
    # Get user
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_stage = user.warmup_stage
    stage_config = STAGES.get(current_stage, STAGES[1])
    
    # Get today's metrics
    today = date.today()
    result = await db.execute(
        select(WarmUpMetric).where(
            and_(
                WarmUpMetric.user_id == user_id,
                WarmUpMetric.date == today
            )
        )
    )
    today_metric = result.scalar_one_or_none()
    
    # Count days at current stage
    result = await db.execute(
        select(func.count(WarmUpMetric.id)).where(
            and_(
                WarmUpMetric.user_id == user_id,
                WarmUpMetric.warmup_stage == current_stage
            )
        )
    )
    days_at_stage = result.scalar() or 0
    
    # Calculate health score (last 7 days average)
    week_ago = today - timedelta(days=7)
    result = await db.execute(
        select(func.avg(WarmUpMetric.score)).where(
            and_(
                WarmUpMetric.user_id == user_id,
                WarmUpMetric.date >= week_ago
            )
        )
    )
    health_score = result.scalar() or 50.0
    
    can_progress = (
        days_at_stage >= stage_config["duration_days"] and
        health_score >= 70 and
        current_stage < 5
    )
    
    return WarmUpStatus(
        current_stage=current_stage,
        stage_description=stage_config["description"],
        days_at_stage=days_at_stage,
        days_required=stage_config["duration_days"],
        health_score=round(health_score, 2),
        today={
            "messages_sent": today_metric.messages_sent if today_metric else 0,
            "max_messages": stage_config["max_messages_per_day"],
            "groups_joined": today_metric.groups_joined if today_metric else 0,
            "max_groups": stage_config["max_groups"],
            "dms_sent": today_metric.dms_sent if today_metric else 0,
        },
        allowed_actions=stage_config["allowed_actions"],
        can_progress=can_progress
    )


@router.get("/stages", response_model=List[WarmUpStageInfo])
async def get_warmup_stages():
    """Get all warm-up stage configurations."""
    return [
        WarmUpStageInfo(
            stage=stage,
            description=config["description"],
            duration_days=config["duration_days"],
            max_messages_per_day=config["max_messages_per_day"],
            max_groups=config["max_groups"],
            allowed_actions=config["allowed_actions"]
        )
        for stage, config in STAGES.items()
    ]


@router.get("/history", response_model=List[WarmUpMetricResponse])
async def get_warmup_history(
    user_id: int = Query(1),
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_db)
):
    """Get warm-up history."""
    start_date = date.today() - timedelta(days=days)
    
    result = await db.execute(
        select(WarmUpMetric).where(
            and_(
                WarmUpMetric.user_id == user_id,
                WarmUpMetric.date >= start_date
            )
        ).order_by(WarmUpMetric.date.desc())
    )
    
    return list(result.scalars().all())


@router.post("/check-action")
async def check_action_allowed(
    action: str = Query(..., description="Action to check"),
    user_id: int = Query(1),
    db: AsyncSession = Depends(get_db)
):
    """Check if an action is allowed in current warm-up stage."""
    # Get user
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    stage_config = STAGES.get(user.warmup_stage, STAGES[1])
    
    # Check if action is allowed
    if action not in stage_config["allowed_actions"]:
        return {
            "allowed": False,
            "reason": f"Action '{action}' not allowed in stage {user.warmup_stage}",
            "current_stage": user.warmup_stage
        }
    
    # Check daily limits
    today = date.today()
    result = await db.execute(
        select(WarmUpMetric).where(
            and_(
                WarmUpMetric.user_id == user_id,
                WarmUpMetric.date == today
            )
        )
    )
    metric = result.scalar_one_or_none()
    
    if metric:
        if action in ["reply", "initiate"]:
            if metric.messages_sent >= stage_config["max_messages_per_day"]:
                return {
                    "allowed": False,
                    "reason": f"Daily message limit ({stage_config['max_messages_per_day']}) reached",
                    "current_count": metric.messages_sent
                }
        
        if action in ["dm_reply", "dm_initiate"]:
            max_dms = stage_config["max_messages_per_day"] // 5
            if metric.dms_sent >= max_dms:
                return {
                    "allowed": False,
                    "reason": f"Daily DM limit ({max_dms}) reached",
                    "current_count": metric.dms_sent
                }
    
    return {
        "allowed": True,
        "action": action,
        "stage": user.warmup_stage
    }


@router.post("/progress")
async def progress_warmup_stage(
    user_id: int = Query(1),
    db: AsyncSession = Depends(get_db)
):
    """Manually progress to next warm-up stage (admin only)."""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.warmup_stage >= 5:
        return {"message": "Already at maximum stage", "stage": 5}
    
    user.warmup_stage += 1
    await db.commit()
    
    return {
        "message": f"Progressed to stage {user.warmup_stage}",
        "new_stage": user.warmup_stage,
        "stage_info": STAGES[user.warmup_stage]
    }
