"""Analytics endpoints."""

from typing import Optional, List
from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base import get_db
from src.database.models import (
    Campaign, Group, Message, Lead, WarmUpMetric,
    CampaignStatus, GroupStatus, LeadStatus
)

router = APIRouter()


# Pydantic Schemas
class DashboardStats(BaseModel):
    campaigns: dict
    groups: dict
    leads: dict
    messages: dict
    warmup: dict


class CampaignAnalytics(BaseModel):
    campaign_id: int
    campaign_name: str
    messages_by_day: List[dict]
    leads_by_status: dict
    top_groups: List[dict]
    engagement: dict


# Endpoints
@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get overview statistics for dashboard."""
    # Campaigns
    result = await db.execute(
        select(func.count(Campaign.id)).where(
            Campaign.status == CampaignStatus.ACTIVE.value
        )
    )
    active_campaigns = result.scalar() or 0
    
    result = await db.execute(select(func.count(Campaign.id)))
    total_campaigns = result.scalar() or 0
    
    # Groups
    result = await db.execute(
        select(func.count(Group.id)).where(
            Group.status == GroupStatus.ACTIVE.value
        )
    )
    active_groups = result.scalar() or 0
    
    result = await db.execute(select(func.count(Group.id)))
    total_groups = result.scalar() or 0
    
    # Leads
    result = await db.execute(select(func.count(Lead.id)))
    total_leads = result.scalar() or 0
    
    result = await db.execute(
        select(func.count(Lead.id)).where(
            Lead.status == LeadStatus.CONVERTED.value
        )
    )
    converted_leads = result.scalar() or 0
    
    # Messages today
    today = date.today()
    result = await db.execute(
        select(func.count(Message.id)).where(
            and_(
                Message.is_bot_message == True,
                func.date(Message.created_at) == today
            )
        )
    )
    messages_today = result.scalar() or 0
    
    result = await db.execute(
        select(func.count(Message.id)).where(Message.is_bot_message == True)
    )
    total_messages = result.scalar() or 0
    
    # Warm-up (latest metric)
    result = await db.execute(
        select(WarmUpMetric)
        .where(WarmUpMetric.date == today)
        .order_by(WarmUpMetric.id.desc())
        .limit(1)
    )
    warmup_metric = result.scalar_one_or_none()
    
    return DashboardStats(
        campaigns={
            "active": active_campaigns,
            "total": total_campaigns
        },
        groups={
            "active": active_groups,
            "total": total_groups
        },
        leads={
            "total": total_leads,
            "converted": converted_leads,
            "conversion_rate": round(converted_leads / total_leads * 100, 2) if total_leads > 0 else 0
        },
        messages={
            "today": messages_today,
            "total": total_messages
        },
        warmup={
            "stage": warmup_metric.warmup_stage if warmup_metric else 1,
            "score": warmup_metric.score if warmup_metric else 0,
            "messages_today": warmup_metric.messages_sent if warmup_metric else 0
        }
    )


@router.get("/campaigns/{campaign_id}")
async def get_campaign_analytics(
    campaign_id: int,
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed analytics for a campaign."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get campaign
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        return {"error": "Campaign not found"}
    
    # Messages by day
    result = await db.execute(
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
    messages_by_day = [{"date": str(r[0]), "count": r[1]} for r in result.all()]
    
    # Leads by status
    result = await db.execute(
        select(Lead.status, func.count(Lead.id))
        .where(Lead.campaign_id == campaign_id)
        .group_by(Lead.status)
    )
    leads_by_status = dict(result.all())
    
    # Top performing groups
    result = await db.execute(
        select(Group.title, func.count(Lead.id).label('lead_count'))
        .join(Lead, Lead.source_group_id == Group.id)
        .where(Lead.campaign_id == campaign_id)
        .group_by(Group.id, Group.title)
        .order_by(func.count(Lead.id).desc())
        .limit(5)
    )
    top_groups = [{"group": r[0], "leads": r[1]} for r in result.all()]
    
    # Engagement
    result = await db.execute(
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


@router.get("/activity/timeline")
async def get_activity_timeline(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get recent activity timeline."""
    activities = []
    
    # Recent messages
    result = await db.execute(
        select(Message)
        .where(Message.is_bot_message == True)
        .order_by(Message.created_at.desc())
        .limit(limit // 2)
    )
    for msg in result.scalars().all():
        activities.append({
            "type": "message",
            "timestamp": msg.created_at.isoformat(),
            "description": f"Sent {'DM' if msg.is_dm else 'message'}",
            "details": {"is_dm": msg.is_dm, "group_id": msg.group_id}
        })
    
    # Recent leads
    result = await db.execute(
        select(Lead)
        .order_by(Lead.created_at.desc())
        .limit(limit // 2)
    )
    for lead in result.scalars().all():
        activities.append({
            "type": "lead",
            "timestamp": lead.created_at.isoformat(),
            "description": f"New lead: @{lead.username or lead.telegram_user_id}",
            "details": {"status": lead.status, "score": lead.score}
        })
    
    # Sort and limit
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    return activities[:limit]


@router.get("/performance/summary")
async def get_performance_summary(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """Get performance summary over time."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Daily message counts
    result = await db.execute(
        select(
            func.date(Message.created_at).label('date'),
            func.count(Message.id).filter(Message.is_bot_message == True).label('sent'),
            func.count(Message.id).filter(Message.is_bot_message == False).label('received')
        )
        .where(Message.created_at >= start_date)
        .group_by(func.date(Message.created_at))
        .order_by(func.date(Message.created_at))
    )
    daily_messages = [
        {"date": str(r[0]), "sent": r[1], "received": r[2]}
        for r in result.all()
    ]
    
    # Daily leads
    result = await db.execute(
        select(
            func.date(Lead.created_at).label('date'),
            func.count(Lead.id).label('count')
        )
        .where(Lead.created_at >= start_date)
        .group_by(func.date(Lead.created_at))
        .order_by(func.date(Lead.created_at))
    )
    daily_leads = [{"date": str(r[0]), "count": r[1]} for r in result.all()]
    
    return {
        "period": f"Last {days} days",
        "daily_messages": daily_messages,
        "daily_leads": daily_leads
    }
