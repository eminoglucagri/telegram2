"""Warm-up tracking and management.

Implements 5-stage warm-up strategy:
- Stage 1 (Days 1-7): Read-only, minimal reactions
- Stage 2 (Days 8-14): Light engagement, replies only
- Stage 3 (Days 15-28): Moderate activity, can initiate
- Stage 4 (Days 29-42): Active participation, DM replies
- Stage 5 (Day 43+): Full activity, DM initiation
"""

from datetime import datetime, date, timedelta
from typing import Optional, List
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.database.models import User, WarmUpMetric
from src.core.config import settings, WarmUpStage

logger = structlog.get_logger(__name__)


class WarmUpTracker:
    """Tracks and manages warm-up progression."""
    
    STAGES = {
        1: {
            "duration_days": 7,
            "max_messages_per_day": 5,
            "max_groups": 2,
            "allowed_actions": ["read", "react"],
            "description": "Observation phase - minimal activity"
        },
        2: {
            "duration_days": 7,
            "max_messages_per_day": 15,
            "max_groups": 5,
            "allowed_actions": ["read", "react", "reply"],
            "description": "Light engagement - replies only"
        },
        3: {
            "duration_days": 14,
            "max_messages_per_day": 30,
            "max_groups": 10,
            "allowed_actions": ["read", "react", "reply", "initiate"],
            "description": "Moderate activity - can start conversations"
        },
        4: {
            "duration_days": 14,
            "max_messages_per_day": 50,
            "max_groups": 15,
            "allowed_actions": ["read", "react", "reply", "initiate", "dm_reply"],
            "description": "Active participation - DM replies allowed"
        },
        5: {
            "duration_days": 0,  # Indefinite
            "max_messages_per_day": 100,
            "max_groups": 25,
            "allowed_actions": ["read", "react", "reply", "initiate", "dm_reply", "dm_initiate"],
            "description": "Full activity - all actions allowed"
        }
    }
    
    def __init__(self, db: AsyncSession, user_id: int):
        """Initialize warm-up tracker.
        
        Args:
            db: Database session
            user_id: User ID to track
        """
        self.db = db
        self.user_id = user_id
    
    async def get_current_stage(self) -> int:
        """Get user's current warm-up stage.
        
        Returns:
            Current stage (1-5)
        """
        result = await self.db.execute(
            select(User.warmup_stage).where(User.id == self.user_id)
        )
        stage = result.scalar_one_or_none()
        return stage or 1
    
    async def get_stage_config(self, stage: Optional[int] = None) -> dict:
        """Get configuration for a warm-up stage.
        
        Args:
            stage: Stage number (defaults to current)
            
        Returns:
            Stage configuration dictionary
        """
        if stage is None:
            stage = await self.get_current_stage()
        return self.STAGES.get(stage, self.STAGES[1])
    
    async def get_today_metrics(self) -> Optional[WarmUpMetric]:
        """Get today's warm-up metrics.
        
        Returns:
            WarmUpMetric for today or None
        """
        today = date.today()
        result = await self.db.execute(
            select(WarmUpMetric).where(
                and_(
                    WarmUpMetric.user_id == self.user_id,
                    WarmUpMetric.date == today
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_or_create_today_metrics(self) -> WarmUpMetric:
        """Get or create today's warm-up metrics.
        
        Returns:
            WarmUpMetric for today
        """
        metric = await self.get_today_metrics()
        
        if not metric:
            current_stage = await self.get_current_stage()
            metric = WarmUpMetric(
                user_id=self.user_id,
                date=date.today(),
                warmup_stage=current_stage
            )
            self.db.add(metric)
            await self.db.commit()
            await self.db.refresh(metric)
        
        return metric
    
    async def increment_messages_sent(self, count: int = 1) -> WarmUpMetric:
        """Increment messages sent counter.
        
        Args:
            count: Number of messages to add
            
        Returns:
            Updated WarmUpMetric
        """
        metric = await self.get_or_create_today_metrics()
        metric.messages_sent += count
        await self.db.commit()
        await self.db.refresh(metric)
        logger.debug(f"Messages sent today: {metric.messages_sent}")
        return metric
    
    async def increment_groups_joined(self, count: int = 1) -> WarmUpMetric:
        """Increment groups joined counter.
        
        Args:
            count: Number of groups to add
            
        Returns:
            Updated WarmUpMetric
        """
        metric = await self.get_or_create_today_metrics()
        metric.groups_joined += count
        await self.db.commit()
        await self.db.refresh(metric)
        logger.debug(f"Groups joined today: {metric.groups_joined}")
        return metric
    
    async def increment_dms_sent(self, count: int = 1) -> WarmUpMetric:
        """Increment DMs sent counter.
        
        Args:
            count: Number of DMs to add
            
        Returns:
            Updated WarmUpMetric
        """
        metric = await self.get_or_create_today_metrics()
        metric.dms_sent += count
        await self.db.commit()
        await self.db.refresh(metric)
        logger.debug(f"DMs sent today: {metric.dms_sent}")
        return metric
    
    async def can_perform_action(self, action: str) -> tuple[bool, str]:
        """Check if an action is allowed in current warm-up stage.
        
        Args:
            action: Action to check (read, react, reply, initiate, dm_reply, dm_initiate)
            
        Returns:
            Tuple of (allowed, reason)
        """
        stage_config = await self.get_stage_config()
        metric = await self.get_or_create_today_metrics()
        
        # Check if action is allowed in this stage
        if action not in stage_config["allowed_actions"]:
            return False, f"Action '{action}' not allowed in stage {metric.warmup_stage}"
        
        # Check daily limits
        if action in ["reply", "initiate"]:
            if metric.messages_sent >= stage_config["max_messages_per_day"]:
                return False, f"Daily message limit ({stage_config['max_messages_per_day']}) reached"
        
        if action in ["dm_reply", "dm_initiate"]:
            # DMs have stricter limits
            max_dms = stage_config["max_messages_per_day"] // 5
            if metric.dms_sent >= max_dms:
                return False, f"Daily DM limit ({max_dms}) reached"
        
        return True, "Action allowed"
    
    async def can_join_group(self) -> tuple[bool, str]:
        """Check if user can join another group.
        
        Returns:
            Tuple of (allowed, reason)
        """
        stage_config = await self.get_stage_config()
        metric = await self.get_or_create_today_metrics()
        
        # Check daily group join limit
        daily_limit = min(stage_config["max_groups"], settings.rate_limit.joins_per_day)
        if metric.groups_joined >= daily_limit:
            return False, f"Daily group join limit ({daily_limit}) reached"
        
        return True, "Can join group"
    
    async def calculate_warmup_score(self) -> float:
        """Calculate warm-up health score (0-100).
        
        Higher score = healthier warm-up progression.
        
        Returns:
            Score between 0 and 100
        """
        # Get metrics for the last 7 days
        week_ago = date.today() - timedelta(days=7)
        result = await self.db.execute(
            select(WarmUpMetric).where(
                and_(
                    WarmUpMetric.user_id == self.user_id,
                    WarmUpMetric.date >= week_ago
                )
            ).order_by(WarmUpMetric.date.desc())
        )
        metrics = result.scalars().all()
        
        if not metrics:
            return 50.0  # Neutral score for new accounts
        
        current_stage = await self.get_current_stage()
        stage_config = self.STAGES[current_stage]
        
        scores = []
        for metric in metrics:
            daily_score = 100.0
            
            # Penalize for exceeding limits
            if metric.messages_sent > stage_config["max_messages_per_day"]:
                excess = metric.messages_sent - stage_config["max_messages_per_day"]
                daily_score -= min(30, excess * 2)
            
            # Penalize for too many group joins
            if metric.groups_joined > stage_config["max_groups"]:
                excess = metric.groups_joined - stage_config["max_groups"]
                daily_score -= min(20, excess * 5)
            
            # Bonus for consistent activity
            if 0 < metric.messages_sent <= stage_config["max_messages_per_day"] * 0.7:
                daily_score += 5
            
            scores.append(max(0, daily_score))
        
        return sum(scores) / len(scores) if scores else 50.0
    
    async def check_stage_progression(self) -> Optional[int]:
        """Check if user should progress to next warm-up stage.
        
        Returns:
            New stage if progression happened, None otherwise
        """
        current_stage = await self.get_current_stage()
        
        if current_stage >= 5:
            return None  # Already at max stage
        
        stage_config = self.STAGES[current_stage]
        
        # Count days at current stage
        result = await self.db.execute(
            select(func.count(WarmUpMetric.id)).where(
                and_(
                    WarmUpMetric.user_id == self.user_id,
                    WarmUpMetric.warmup_stage == current_stage
                )
            )
        )
        days_at_stage = result.scalar() or 0
        
        # Check if enough days have passed
        if days_at_stage >= stage_config["duration_days"]:
            # Check warm-up score
            score = await self.calculate_warmup_score()
            
            if score >= 70:  # Minimum score to progress
                new_stage = current_stage + 1
                
                # Update user's stage
                result = await self.db.execute(
                    select(User).where(User.id == self.user_id)
                )
                user = result.scalar_one_or_none()
                if user:
                    user.warmup_stage = new_stage
                    await self.db.commit()
                    logger.info(f"User {self.user_id} progressed to warm-up stage {new_stage}")
                    return new_stage
        
        return None
    
    async def get_progress_summary(self) -> dict:
        """Get warm-up progress summary.
        
        Returns:
            Dictionary with progress information
        """
        current_stage = await self.get_current_stage()
        stage_config = await self.get_stage_config(current_stage)
        metric = await self.get_today_metrics()
        score = await self.calculate_warmup_score()
        
        # Count days at current stage
        result = await self.db.execute(
            select(func.count(WarmUpMetric.id)).where(
                and_(
                    WarmUpMetric.user_id == self.user_id,
                    WarmUpMetric.warmup_stage == current_stage
                )
            )
        )
        days_at_stage = result.scalar() or 0
        
        return {
            "current_stage": current_stage,
            "stage_description": stage_config["description"],
            "days_at_stage": days_at_stage,
            "days_required": stage_config["duration_days"],
            "health_score": round(score, 2),
            "today": {
                "messages_sent": metric.messages_sent if metric else 0,
                "max_messages": stage_config["max_messages_per_day"],
                "groups_joined": metric.groups_joined if metric else 0,
                "max_groups": stage_config["max_groups"],
                "dms_sent": metric.dms_sent if metric else 0,
            },
            "allowed_actions": stage_config["allowed_actions"],
            "can_progress": days_at_stage >= stage_config["duration_days"] and score >= 70
        }
