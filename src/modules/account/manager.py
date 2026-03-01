"""Telegram account management."""

from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.database.models import User, UserStatus
from src.core.bot import TelegramBot
from src.core.config import settings

logger = structlog.get_logger(__name__)


class AccountManager:
    """Manages Telegram account operations."""
    
    def __init__(self, db: AsyncSession, bot: TelegramBot):
        """Initialize account manager.
        
        Args:
            db: Database session
            bot: Telegram bot instance
        """
        self.db = db
        self.bot = bot
    
    async def get_current_user(self) -> Optional[User]:
        """Get the current user from database.
        
        Returns:
            User object or None
        """
        result = await self.db.execute(
            select(User).where(User.phone == settings.telegram.phone)
        )
        return result.scalar_one_or_none()
    
    async def create_or_update_user(self) -> User:
        """Create or update user based on current Telegram account.
        
        Returns:
            User object
        """
        me = await self.bot.get_me()
        session_string = self.bot.get_session_string()
        
        user = await self.get_current_user()
        
        if user:
            # Update existing user
            user.telegram_id = me.id
            user.username = me.username
            user.first_name = me.first_name
            user.session_string = session_string
            user.status = UserStatus.ACTIVE.value
            user.updated_at = datetime.utcnow()
            logger.info(f"Updated user: {user.phone}")
        else:
            # Create new user
            user = User(
                phone=settings.telegram.phone,
                telegram_id=me.id,
                username=me.username,
                first_name=me.first_name,
                api_id=settings.telegram.api_id,
                api_hash=settings.telegram.api_hash,
                session_string=session_string,
                status=UserStatus.ACTIVE.value,
                warmup_stage=1
            )
            self.db.add(user)
            logger.info(f"Created new user: {user.phone}")
        
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def update_user_status(self, status: UserStatus) -> Optional[User]:
        """Update user status.
        
        Args:
            status: New status
            
        Returns:
            Updated user or None
        """
        user = await self.get_current_user()
        if user:
            user.status = status.value
            user.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(user)
            logger.info(f"Updated user status to: {status}")
        return user
    
    async def update_warmup_stage(self, stage: int) -> Optional[User]:
        """Update user's warm-up stage.
        
        Args:
            stage: New warm-up stage (1-5)
            
        Returns:
            Updated user or None
        """
        if not 1 <= stage <= 5:
            raise ValueError("Warm-up stage must be between 1 and 5")
        
        user = await self.get_current_user()
        if user:
            user.warmup_stage = stage
            user.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(user)
            logger.info(f"Updated warm-up stage to: {stage}")
        return user
    
    async def check_account_health(self) -> dict:
        """Check Telegram account health status.
        
        Returns:
            Dictionary with health metrics
        """
        try:
            me = await self.bot.get_me()
            dialogs = await self.bot.get_dialogs(limit=10)
            
            return {
                "status": "healthy",
                "connected": True,
                "user_id": me.id,
                "username": me.username,
                "first_name": me.first_name,
                "dialog_count": len(dialogs),
                "checked_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Account health check failed: {e}")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e),
                "checked_at": datetime.utcnow().isoformat()
            }
    
    async def save_session(self) -> str:
        """Save current session string to database.
        
        Returns:
            Session string
        """
        session_string = self.bot.get_session_string()
        user = await self.get_current_user()
        
        if user:
            user.session_string = session_string
            await self.db.commit()
            logger.info("Session saved to database")
        
        return session_string
