"""Campaign management endpoints."""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base import get_db
from src.database.models import Campaign, CampaignStatus

router = APIRouter()


# Pydantic Schemas
class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    user_id: int
    persona_id: Optional[int] = None
    target_keywords: List[str] = []
    target_industries: List[str] = []
    product_info: Optional[str] = None
    call_to_action: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    daily_message_limit: int = 50
    daily_dm_limit: int = 10


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    persona_id: Optional[int] = None
    status: Optional[str] = None
    target_keywords: Optional[List[str]] = None
    target_industries: Optional[List[str]] = None
    product_info: Optional[str] = None
    call_to_action: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    daily_message_limit: Optional[int] = None
    daily_dm_limit: Optional[int] = None


class CampaignResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    user_id: int
    persona_id: Optional[int]
    status: str
    target_keywords: List[str]
    target_industries: List[str]
    product_info: Optional[str]
    call_to_action: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    daily_message_limit: int
    daily_dm_limit: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Endpoints
@router.get("", response_model=List[CampaignResponse])
async def list_campaigns(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List all campaigns with optional filtering."""
    query = select(Campaign)
    
    if status:
        query = query.where(Campaign.status == status)
    
    query = query.offset(offset).limit(limit).order_by(Campaign.created_at.desc())
    
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    campaign_data: CampaignCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new campaign."""
    campaign = Campaign(
        name=campaign_data.name,
        description=campaign_data.description,
        user_id=campaign_data.user_id,
        persona_id=campaign_data.persona_id,
        target_keywords=campaign_data.target_keywords,
        target_industries=campaign_data.target_industries,
        product_info=campaign_data.product_info,
        call_to_action=campaign_data.call_to_action,
        start_date=campaign_data.start_date,
        end_date=campaign_data.end_date,
        daily_message_limit=campaign_data.daily_message_limit,
        daily_dm_limit=campaign_data.daily_dm_limit,
        status=CampaignStatus.DRAFT.value
    )
    
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific campaign."""
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return campaign


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a campaign."""
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    update_data = campaign_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(campaign, key, value)
    
    campaign.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(campaign)
    return campaign


@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a campaign (soft delete by archiving)."""
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign.status = CampaignStatus.ARCHIVED.value
    await db.commit()
    
    return {"message": "Campaign archived successfully"}


@router.post("/{campaign_id}/activate")
async def activate_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Activate a campaign."""
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign.status = CampaignStatus.ACTIVE.value
    if not campaign.start_date:
        campaign.start_date = datetime.utcnow()
    
    await db.commit()
    return {"message": "Campaign activated", "status": campaign.status}


@router.post("/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Pause a campaign."""
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign.status = CampaignStatus.PAUSED.value
    await db.commit()
    return {"message": "Campaign paused", "status": campaign.status}
