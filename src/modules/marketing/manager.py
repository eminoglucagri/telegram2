"""Marketing activities management."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.database.models import Lead, LeadStatus, Campaign, Message, Group
from src.modules.conversation.handler import ConversationHandler
from src.modules.warmup.tracker import WarmUpTracker
from src.core.bot import TelegramBot

logger = structlog.get_logger(__name__)


class MarketingManager:
    """Manages marketing activities like lead detection and DM campaigns."""
    
    def __init__(
        self,
        db: AsyncSession,
        bot: TelegramBot,
        conversation_handler: ConversationHandler,
        warmup_tracker: WarmUpTracker
    ):
        """Initialize marketing manager.
        
        Args:
            db: Database session
            bot: Telegram bot instance
            conversation_handler: Conversation handler for generating messages
            warmup_tracker: Warm-up tracker for rate limiting
        """
        self.db = db
        self.bot = bot
        self.conversation = conversation_handler
        self.warmup = warmup_tracker
    
    async def detect_lead(
        self,
        message: Message,
        campaign: Campaign
    ) -> Optional[Lead]:
        """Detect if a message indicates a potential lead.
        
        Args:
            message: Message to analyze
            campaign: Campaign for context
            
        Returns:
            Lead object if detected, None otherwise
        """
        if not message.sender_telegram_id:
            return None
        
        # Check if lead already exists
        existing = await self.db.execute(
            select(Lead).where(
                and_(
                    Lead.telegram_user_id == message.sender_telegram_id,
                    Lead.campaign_id == campaign.id
                )
            )
        )
        if existing.scalar_one_or_none():
            return None
        
        # Check for target keywords
        content_lower = message.content.lower()
        keyword_match = False
        
        if campaign.target_keywords:
            for keyword in campaign.target_keywords:
                if keyword.lower() in content_lower:
                    keyword_match = True
                    break
        
        # Check lead score from message analysis
        is_high_score = (message.lead_score or 0) > 0.5
        
        # Check intent
        is_interested = message.intent in ["interest", "question", "request"]
        
        if not (keyword_match or is_high_score or is_interested):
            return None
        
        # Calculate initial score
        score = 0.0
        if keyword_match:
            score += 30
        if is_high_score:
            score += 30
        if is_interested:
            score += 20
        if message.sentiment == "positive":
            score += 10
        
        # Create lead
        lead = Lead(
            telegram_user_id=message.sender_telegram_id,
            username=message.sender_username,
            source_group_id=message.group_id,
            campaign_id=campaign.id,
            status=LeadStatus.NEW.value,
            score=min(score, 100),
            notes=f"Detected from message: {message.content[:100]}..."
        )
        
        self.db.add(lead)
        await self.db.commit()
        await self.db.refresh(lead)
        
        logger.info(f"Detected new lead: {lead.username} (score: {lead.score})")
        return lead
    
    async def send_dm(
        self,
        lead: Lead,
        message_text: str,
        campaign_id: Optional[int] = None
    ) -> bool:
        """Send a direct message to a lead.
        
        Args:
            lead: Lead to message
            message_text: Message to send
            campaign_id: Campaign ID for tracking
            
        Returns:
            True if successful
        """
        # Check warm-up limits
        can_dm, reason = await self.warmup.can_perform_action("dm_initiate")
        if not can_dm:
            logger.warning(f"Cannot send DM: {reason}")
            return False
        
        try:
            # Send the DM
            entity = await self.bot.get_entity(lead.telegram_user_id)
            sent_message = await self.bot.send_message(
                lead.telegram_user_id,
                message_text
            )
            
            # Update lead
            lead.status = LeadStatus.CONTACTED.value
            lead.contact_count += 1
            lead.contact_method = "dm"
            if not lead.first_contact_at:
                lead.first_contact_at = datetime.utcnow()
            lead.last_contact_at = datetime.utcnow()
            
            await self.db.commit()
            
            # Track DM in warm-up
            await self.warmup.increment_dms_sent()
            
            # Save message
            await self.conversation.save_message(
                content=message_text,
                group_id=0,  # DM has no group
                telegram_message_id=sent_message.id,
                sender_telegram_id=(await self.bot.get_me()).id,
                campaign_id=campaign_id,
                is_bot_message=True,
                is_dm=True
            )
            
            logger.info(f"Sent DM to lead: {lead.username}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send DM to {lead.username}: {e}")
            return False
    
    async def initiate_dm_campaign(
        self,
        campaign_id: int,
        leads: Optional[List[Lead]] = None,
        max_dms: int = 10
    ) -> Dict[str, Any]:
        """Initiate DM outreach for a campaign.
        
        Args:
            campaign_id: Campaign ID
            leads: Specific leads to contact (optional)
            max_dms: Maximum DMs to send
            
        Returns:
            Results dictionary
        """
        result = await self.db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            return {"error": "Campaign not found"}
        
        # Get leads if not provided
        if leads is None:
            result = await self.db.execute(
                select(Lead).where(
                    and_(
                        Lead.campaign_id == campaign_id,
                        Lead.status == LeadStatus.NEW.value
                    )
                ).order_by(Lead.score.desc()).limit(max_dms)
            )
            leads = list(result.scalars().all())
        
        results = {
            "total": len(leads),
            "sent": 0,
            "failed": 0,
            "skipped": 0
        }
        
        for lead in leads:
            # Check limits
            can_dm, reason = await self.warmup.can_perform_action("dm_initiate")
            if not can_dm:
                results["skipped"] += len(leads) - results["sent"] - results["failed"]
                break
            
            # Generate personalized DM
            dm_text = await self.conversation.generate_dm_opener(
                username=lead.username or str(lead.telegram_user_id),
                context=lead.notes or "interested user",
                campaign_id=campaign_id
            )
            
            success = await self.send_dm(lead, dm_text, campaign_id)
            if success:
                results["sent"] += 1
            else:
                results["failed"] += 1
        
        logger.info(f"DM campaign results: {results}")
        return results
    
    async def update_lead_status(
        self,
        lead_id: int,
        status: LeadStatus,
        notes: Optional[str] = None
    ) -> Optional[Lead]:
        """Update lead status.
        
        Args:
            lead_id: Lead ID
            status: New status
            notes: Additional notes
            
        Returns:
            Updated lead or None
        """
        result = await self.db.execute(
            select(Lead).where(Lead.id == lead_id)
        )
        lead = result.scalar_one_or_none()
        
        if lead:
            lead.status = status.value
            if notes:
                lead.notes = (lead.notes or "") + f"\n{notes}"
            if status == LeadStatus.CONVERTED:
                lead.converted_at = datetime.utcnow()
            lead.updated_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(lead)
            logger.info(f"Updated lead {lead_id} status to {status}")
        
        return lead
    
    async def get_leads(
        self,
        campaign_id: Optional[int] = None,
        status: Optional[LeadStatus] = None,
        limit: int = 100
    ) -> List[Lead]:
        """Get leads with filters.
        
        Args:
            campaign_id: Filter by campaign
            status: Filter by status
            limit: Maximum results
            
        Returns:
            List of leads
        """
        query = select(Lead)
        
        conditions = []
        if campaign_id:
            conditions.append(Lead.campaign_id == campaign_id)
        if status:
            conditions.append(Lead.status == status.value)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(Lead.score.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_campaign_stats(self, campaign_id: int) -> Dict[str, Any]:
        """Get marketing statistics for a campaign.
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Statistics dictionary
        """
        # Get lead counts by status
        result = await self.db.execute(
            select(Lead.status, func.count(Lead.id))
            .where(Lead.campaign_id == campaign_id)
            .group_by(Lead.status)
        )
        lead_stats = dict(result.all())
        
        # Get message stats
        result = await self.db.execute(
            select(func.count(Message.id))
            .where(
                and_(
                    Message.campaign_id == campaign_id,
                    Message.is_bot_message == True
                )
            )
        )
        messages_sent = result.scalar() or 0
        
        # Get DM stats
        result = await self.db.execute(
            select(func.count(Message.id))
            .where(
                and_(
                    Message.campaign_id == campaign_id,
                    Message.is_dm == True,
                    Message.is_bot_message == True
                )
            )
        )
        dms_sent = result.scalar() or 0
        
        total_leads = sum(lead_stats.values())
        converted = lead_stats.get(LeadStatus.CONVERTED.value, 0)
        
        return {
            "total_leads": total_leads,
            "leads_by_status": lead_stats,
            "messages_sent": messages_sent,
            "dms_sent": dms_sent,
            "conversion_rate": (converted / total_leads * 100) if total_leads > 0 else 0
        }
