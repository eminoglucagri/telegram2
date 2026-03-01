"""Group discovery and management.

MVP: Manual group management (automatic discovery in future versions)
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.database.models import Group, GroupStatus, Campaign
from src.core.bot import TelegramBot
from src.modules.warmup.tracker import WarmUpTracker

logger = structlog.get_logger(__name__)


class GroupFinder:
    """Manages group discovery and joining."""
    
    def __init__(
        self,
        db: AsyncSession,
        bot: TelegramBot,
        warmup_tracker: WarmUpTracker
    ):
        """Initialize group finder.
        
        Args:
            db: Database session
            bot: Telegram bot instance
            warmup_tracker: Warm-up tracker for rate limiting
        """
        self.db = db
        self.bot = bot
        self.warmup = warmup_tracker
    
    async def add_group(
        self,
        invite_link: str,
        campaign_id: Optional[int] = None,
        auto_join: bool = False
    ) -> Optional[Group]:
        """Add a group to the database.
        
        Args:
            invite_link: Group invite link or @username
            campaign_id: Associated campaign ID
            auto_join: Automatically join the group
            
        Returns:
            Created Group object or None
        """
        try:
            # Get group info from Telegram
            entity = await self.bot.get_entity(invite_link)
            
            # Check if group already exists
            existing = await self.db.execute(
                select(Group).where(Group.telegram_id == entity.id)
            )
            if existing.scalar_one_or_none():
                logger.info(f"Group already exists: {entity.title}")
                return None
            
            # Get member count if available
            member_count = 0
            try:
                if hasattr(entity, 'participants_count'):
                    member_count = entity.participants_count
            except:
                pass
            
            group = Group(
                telegram_id=entity.id,
                title=entity.title if hasattr(entity, 'title') else None,
                username=entity.username if hasattr(entity, 'username') else None,
                invite_link=invite_link,
                member_count=member_count,
                campaign_id=campaign_id,
                status=GroupStatus.PENDING.value
            )
            
            self.db.add(group)
            await self.db.commit()
            await self.db.refresh(group)
            
            logger.info(f"Added group: {group.title}")
            
            # Auto-join if requested
            if auto_join:
                await self.join_group(group.id)
            
            return group
            
        except Exception as e:
            logger.error(f"Failed to add group {invite_link}: {e}")
            return None
    
    async def join_group(self, group_id: int) -> bool:
        """Join a group.
        
        Args:
            group_id: Database group ID
            
        Returns:
            True if successful
        """
        # Check warm-up limits
        can_join, reason = await self.warmup.can_join_group()
        if not can_join:
            logger.warning(f"Cannot join group: {reason}")
            return False
        
        result = await self.db.execute(
            select(Group).where(Group.id == group_id)
        )
        group = result.scalar_one_or_none()
        
        if not group:
            logger.error(f"Group not found: {group_id}")
            return False
        
        try:
            # Join using invite link or username
            join_target = group.invite_link or f"@{group.username}"
            await self.bot.join_group(join_target)
            
            # Update group status
            group.status = GroupStatus.ACTIVE.value
            group.joined_at = datetime.utcnow()
            await self.db.commit()
            
            # Track in warm-up
            await self.warmup.increment_groups_joined()
            
            logger.info(f"Joined group: {group.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to join group {group.title}: {e}")
            group.status = GroupStatus.BANNED.value
            group.notes = str(e)
            await self.db.commit()
            return False
    
    async def leave_group(self, group_id: int) -> bool:
        """Leave a group.
        
        Args:
            group_id: Database group ID
            
        Returns:
            True if successful
        """
        result = await self.db.execute(
            select(Group).where(Group.id == group_id)
        )
        group = result.scalar_one_or_none()
        
        if not group:
            return False
        
        try:
            await self.bot.leave_group(group.telegram_id)
            
            group.status = GroupStatus.LEFT.value
            group.left_at = datetime.utcnow()
            await self.db.commit()
            
            logger.info(f"Left group: {group.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to leave group {group.title}: {e}")
            return False
    
    async def list_groups(
        self,
        campaign_id: Optional[int] = None,
        status: Optional[GroupStatus] = None,
        is_target: Optional[bool] = None
    ) -> List[Group]:
        """List groups with filters.
        
        Args:
            campaign_id: Filter by campaign
            status: Filter by status
            is_target: Filter by target flag
            
        Returns:
            List of groups
        """
        query = select(Group)
        
        conditions = []
        if campaign_id:
            conditions.append(Group.campaign_id == campaign_id)
        if status:
            conditions.append(Group.status == status.value)
        if is_target is not None:
            conditions.append(Group.is_target == is_target)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        result = await self.db.execute(query.order_by(Group.created_at.desc()))
        return list(result.scalars().all())
    
    async def update_group_info(self, group_id: int) -> Optional[Group]:
        """Update group information from Telegram.
        
        Args:
            group_id: Database group ID
            
        Returns:
            Updated group or None
        """
        result = await self.db.execute(
            select(Group).where(Group.id == group_id)
        )
        group = result.scalar_one_or_none()
        
        if not group:
            return None
        
        try:
            entity = await self.bot.get_entity(group.telegram_id)
            
            group.title = entity.title if hasattr(entity, 'title') else group.title
            group.username = entity.username if hasattr(entity, 'username') else group.username
            
            if hasattr(entity, 'participants_count'):
                group.member_count = entity.participants_count
            
            group.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(group)
            
            logger.info(f"Updated group info: {group.title}")
            return group
            
        except Exception as e:
            logger.error(f"Failed to update group {group_id}: {e}")
            return None
    
    async def get_active_groups(self) -> List[Group]:
        """Get all active groups.
        
        Returns:
            List of active groups
        """
        return await self.list_groups(status=GroupStatus.ACTIVE)
    
    async def assign_to_campaign(self, group_id: int, campaign_id: int) -> bool:
        """Assign a group to a campaign.
        
        Args:
            group_id: Group ID
            campaign_id: Campaign ID
            
        Returns:
            True if successful
        """
        result = await self.db.execute(
            select(Group).where(Group.id == group_id)
        )
        group = result.scalar_one_or_none()
        
        if group:
            group.campaign_id = campaign_id
            await self.db.commit()
            logger.info(f"Assigned group {group_id} to campaign {campaign_id}")
            return True
        return False
