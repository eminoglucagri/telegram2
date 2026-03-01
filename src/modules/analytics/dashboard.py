"""Analytics dashboard for tracking metrics."""

from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.database.models import (
    User, Campaign, Group, Message, Lead, WarmUpMetric,
    CampaignStatus, GroupStatus, LeadStatus
)

logger = structlog.get_logger(__name__)


class AnalyticsDashboard:
    """Provides analytics and metrics for the dashboard."""
    
    def __init__(self, db: AsyncSession):
        """Initialize analytics dashboard.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def get_overview_stats(self) -> Dict[str, Any]:
        """Get overview statistics for dashboard.
        
        Returns:
            Dictionary with overview stats
        """
        # Active campaigns
        result = await self.db.execute(
            select(func.count(Campaign.id)).where(
                Campaign.status == CampaignStatus.ACTIVE.value
            )
        )
        active_campaigns = result.scalar() or 0
        
        # Total campaigns
        result = await self.db.execute(select(func.count(Campaign.id)))
        total_campaigns = result.scalar() or 0
        
        # Active groups
        result = await self.db.execute(
            select(func.count(Group.id)).where(
                Group.status == GroupStatus.ACTIVE.value
            )
        )
        active_groups = result.scalar() or 0
        
        # Total leads
        result = await self.db.execute(select(func.count(Lead.id)))
        total_leads = result.scalar() or 0
        
        # Converted leads
        result = await self.db.execute(
            select(func.count(Lead.id)).where(
                Lead.status == LeadStatus.CONVERTED.value
            )
        )
        converted_leads = result.scalar() or 0
        
        # Messages sent today
        today = date.today()
        result = await self.db.execute(
            select(func.count(Message.id)).where(
                and_(
                    Message.is_bot_message == True,
                    func.date(Message.created_at) == today
                )
            )
        )
        messages_today = result.scalar() or 0
        
        # Total messages sent
        result = await self.db.execute(
            select(func.count(Message.id)).where(Message.is_bot_message == True)
        )
        total_messages = result.scalar() or 0
        
        return {
            "campaigns": {
                "active": active_campaigns,
                "total": total_campaigns
            },
            "groups": {
                "active": active_groups
            },
            "leads": {
                "total": total_leads,
                "converted": converted_leads,
                "conversion_rate": (converted_leads / total_leads * 100) if total_leads > 0 else 0
            },
            "messages": {
                "today": messages_today,
                "total": total_messages
            }
        }
    
    async def get_warmup_status(self, user_id: int) -> Dict[str, Any]:
        """Get warm-up status for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Warm-up status dictionary
        """
        # Get user
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return {"error": "User not found"}
        
        # Get last 7 days metrics
        week_ago = date.today() - timedelta(days=7)
        result = await self.db.execute(
            select(WarmUpMetric).where(
                and_(
                    WarmUpMetric.user_id == user_id,
                    WarmUpMetric.date >= week_ago
                )
            ).order_by(WarmUpMetric.date.desc())
        )
        metrics = list(result.scalars().all())
        
        # Calculate averages
        if metrics:
            avg_messages = sum(m.messages_sent for m in metrics) / len(metrics)
            avg_score = sum(m.score for m in metrics) / len(metrics)
        else:
            avg_messages = 0
            avg_score = 50
        
        return {
            "current_stage": user.warmup_stage,
            "stage_description": self._get_stage_description(user.warmup_stage),
            "account_status": user.status,
            "avg_daily_messages": round(avg_messages, 1),
            "health_score": round(avg_score, 1),
            "daily_metrics": [
                {
                    "date": m.date.isoformat(),
                    "messages_sent": m.messages_sent,
                    "groups_joined": m.groups_joined,
                    "dms_sent": m.dms_sent,
                    "score": m.score
                }
                for m in metrics
            ]
        }
    
    def _get_stage_description(self, stage: int) -> str:
        """Get description for a warm-up stage."""
        descriptions = {
            1: "Observation Phase - Minimal activity",
            2: "Light Engagement - Replies only",
            3: "Moderate Activity - Can start conversations",
            4: "Active Participation - DM replies allowed",
            5: "Full Activity - All actions allowed"
        }
        return descriptions.get(stage, "Unknown stage")
    
    async def get_campaign_analytics(
        self,
        campaign_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get detailed analytics for a campaign.
        
        Args:
            campaign_id: Campaign ID
            days: Number of days to analyze
            
        Returns:
            Campaign analytics dictionary
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get campaign
        result = await self.db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            return {"error": "Campaign not found"}
        
        # Messages by day
        result = await self.db.execute(
            select(
                func.date(Message.created_at).label('date'),
                func.count(Message.id).label('count')
            ).where(
                and_(
                    Message.campaign_id == campaign_id,
                    Message.is_bot_message == True,
                    Message.created_at >= start_date
                )
            ).group_by(func.date(Message.created_at)).order_by('date')
        )
        messages_by_day = [{'date': str(r[0]), 'count': r[1]} for r in result.all()]
        
        # Leads by status
        result = await self.db.execute(
            select(Lead.status, func.count(Lead.id))
            .where(Lead.campaign_id == campaign_id)
            .group_by(Lead.status)
        )
        leads_by_status = dict(result.all())
        
        # Top performing groups
        result = await self.db.execute(
            select(Group.title, func.count(Lead.id).label('lead_count'))
            .join(Lead, Lead.source_group_id == Group.id)
            .where(Lead.campaign_id == campaign_id)
            .group_by(Group.id, Group.title)
            .order_by(func.count(Lead.id).desc())
            .limit(5)
        )
        top_groups = [{'group': r[0], 'leads': r[1]} for r in result.all()]
        
        # Engagement metrics
        result = await self.db.execute(
            select(
                func.count(Message.id).label('total'),
                func.avg(Message.lead_score).label('avg_lead_score')
            ).where(
                and_(
                    Message.campaign_id == campaign_id,
                    Message.is_bot_message == False
                )
            )
        )
        engagement = result.one()
        
        return {
            "campaign": {
                "id": campaign.id,
                "name": campaign.name,
                "status": campaign.status
            },
            "messages_by_day": messages_by_day,
            "leads_by_status": leads_by_status,
            "top_performing_groups": top_groups,
            "engagement": {
                "total_responses": engagement[0] or 0,
                "avg_lead_score": round(engagement[1] or 0, 2)
            }
        }
    
    async def get_lead_funnel(self, campaign_id: Optional[int] = None) -> Dict[str, int]:
        """Get lead funnel data.
        
        Args:
            campaign_id: Optional campaign filter
            
        Returns:
            Funnel data dictionary
        """
        query = select(Lead.status, func.count(Lead.id))
        
        if campaign_id:
            query = query.where(Lead.campaign_id == campaign_id)
        
        query = query.group_by(Lead.status)
        result = await self.db.execute(query)
        
        counts = dict(result.all())
        
        return {
            "new": counts.get(LeadStatus.NEW.value, 0),
            "contacted": counts.get(LeadStatus.CONTACTED.value, 0),
            "engaged": counts.get(LeadStatus.ENGAGED.value, 0),
            "converted": counts.get(LeadStatus.CONVERTED.value, 0),
            "lost": counts.get(LeadStatus.LOST.value, 0)
        }
    
    async def get_activity_timeline(
        self,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get recent activity timeline.
        
        Args:
            limit: Number of activities to return
            
        Returns:
            List of activity entries
        """
        activities = []
        
        # Recent messages
        result = await self.db.execute(
            select(Message)
            .where(Message.is_bot_message == True)
            .order_by(Message.created_at.desc())
            .limit(limit // 2)
        )
        for msg in result.scalars().all():
            activities.append({
                "type": "message",
                "timestamp": msg.created_at.isoformat(),
                "description": f"Sent message in group",
                "is_dm": msg.is_dm
            })
        
        # Recent leads
        result = await self.db.execute(
            select(Lead)
            .order_by(Lead.created_at.desc())
            .limit(limit // 2)
        )
        for lead in result.scalars().all():
            activities.append({
                "type": "lead",
                "timestamp": lead.created_at.isoformat(),
                "description": f"New lead: @{lead.username}",
                "status": lead.status
            })
        
        # Sort by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        return activities[:limit]
