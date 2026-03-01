"""Message endpoints."""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base import get_db
from src.database.models import Message

router = APIRouter()


# Pydantic Schemas
class MessageResponse(BaseModel):
    id: int
    telegram_message_id: Optional[int]
    group_id: Optional[int]
    campaign_id: Optional[int]
    sender_telegram_id: Optional[int]
    sender_username: Optional[str]
    content: str
    reply_to_message_id: Optional[int]
    is_bot_message: bool
    is_dm: bool
    sentiment: Optional[str]
    intent: Optional[str]
    lead_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class MessageStats(BaseModel):
    total_sent: int
    total_received: int
    dms_sent: int
    by_sentiment: dict
    by_intent: dict
    daily_breakdown: List[dict]


# Endpoints
@router.get("", response_model=List[MessageResponse])
async def list_messages(
    group_id: Optional[int] = Query(None),
    campaign_id: Optional[int] = Query(None),
    is_bot_message: Optional[bool] = Query(None),
    is_dm: Optional[bool] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List messages with filtering."""
    query = select(Message)
    
    conditions = []
    if group_id:
        conditions.append(Message.group_id == group_id)
    if campaign_id:
        conditions.append(Message.campaign_id == campaign_id)
    if is_bot_message is not None:
        conditions.append(Message.is_bot_message == is_bot_message)
    if is_dm is not None:
        conditions.append(Message.is_dm == is_dm)
    if start_date:
        conditions.append(Message.created_at >= start_date)
    if end_date:
        conditions.append(Message.created_at <= end_date)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.offset(offset).limit(limit).order_by(Message.created_at.desc())
    
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific message."""
    result = await db.execute(
        select(Message).where(Message.id == message_id)
    )
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    return message


@router.get("/stats/overview", response_model=MessageStats)
async def get_message_stats(
    campaign_id: Optional[int] = Query(None),
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db)
):
    """Get message statistics."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    base_conditions = [Message.created_at >= start_date]
    if campaign_id:
        base_conditions.append(Message.campaign_id == campaign_id)
    
    # Total sent
    result = await db.execute(
        select(func.count(Message.id)).where(
            and_(*base_conditions, Message.is_bot_message == True)
        )
    )
    total_sent = result.scalar() or 0
    
    # Total received
    result = await db.execute(
        select(func.count(Message.id)).where(
            and_(*base_conditions, Message.is_bot_message == False)
        )
    )
    total_received = result.scalar() or 0
    
    # DMs sent
    result = await db.execute(
        select(func.count(Message.id)).where(
            and_(*base_conditions, Message.is_dm == True, Message.is_bot_message == True)
        )
    )
    dms_sent = result.scalar() or 0
    
    # By sentiment
    result = await db.execute(
        select(Message.sentiment, func.count(Message.id))
        .where(and_(*base_conditions))
        .group_by(Message.sentiment)
    )
    by_sentiment = {k or "unknown": v for k, v in result.all()}
    
    # By intent
    result = await db.execute(
        select(Message.intent, func.count(Message.id))
        .where(and_(*base_conditions))
        .group_by(Message.intent)
    )
    by_intent = {k or "unknown": v for k, v in result.all()}
    
    # Daily breakdown
    result = await db.execute(
        select(
            func.date(Message.created_at).label('date'),
            func.count(Message.id).filter(Message.is_bot_message == True).label('sent'),
            func.count(Message.id).filter(Message.is_bot_message == False).label('received')
        )
        .where(and_(*base_conditions))
        .group_by(func.date(Message.created_at))
        .order_by(func.date(Message.created_at))
    )
    daily_breakdown = [
        {"date": str(row[0]), "sent": row[1], "received": row[2]}
        for row in result.all()
    ]
    
    return MessageStats(
        total_sent=total_sent,
        total_received=total_received,
        dms_sent=dms_sent,
        by_sentiment=by_sentiment,
        by_intent=by_intent,
        daily_breakdown=daily_breakdown
    )


@router.get("/conversation/{group_id}")
async def get_conversation(
    group_id: int,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Get conversation thread for a group."""
    result = await db.execute(
        select(Message)
        .where(Message.group_id == group_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = list(result.scalars().all())
    messages.reverse()  # Chronological order
    
    return [
        {
            "id": msg.id,
            "sender": msg.sender_username or "User",
            "content": msg.content,
            "is_bot": msg.is_bot_message,
            "timestamp": msg.created_at.isoformat()
        }
        for msg in messages
    ]
