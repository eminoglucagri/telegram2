"""Lead management endpoints."""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
import csv
import io

from src.database.base import get_db
from src.database.models import Lead, LeadStatus

router = APIRouter()


# Pydantic Schemas
class LeadCreate(BaseModel):
    telegram_user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    source_group_id: Optional[int] = None
    campaign_id: Optional[int] = None
    score: float = Field(0.0, ge=0, le=100)
    notes: Optional[str] = None
    tags: List[str] = []


class LeadUpdate(BaseModel):
    status: Optional[str] = None
    score: Optional[float] = Field(None, ge=0, le=100)
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_data: Optional[dict] = None


class LeadResponse(BaseModel):
    id: int
    telegram_user_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    source_group_id: Optional[int]
    campaign_id: Optional[int]
    status: str
    score: float
    contact_method: Optional[str]
    first_contact_at: Optional[datetime]
    last_contact_at: Optional[datetime]
    contact_count: int
    notes: Optional[str]
    tags: List[str]
    converted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Endpoints
@router.get("", response_model=List[LeadResponse])
async def list_leads(
    campaign_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None, ge=0, le=100),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List all leads with filtering."""
    query = select(Lead)
    
    conditions = []
    if campaign_id:
        conditions.append(Lead.campaign_id == campaign_id)
    if status:
        conditions.append(Lead.status == status)
    if min_score is not None:
        conditions.append(Lead.score >= min_score)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.offset(offset).limit(limit).order_by(Lead.score.desc())
    
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("", response_model=LeadResponse, status_code=201)
async def create_lead(
    lead_data: LeadCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new lead manually."""
    # Check for duplicate
    existing = await db.execute(
        select(Lead).where(
            and_(
                Lead.telegram_user_id == lead_data.telegram_user_id,
                Lead.campaign_id == lead_data.campaign_id
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Lead already exists for this campaign")
    
    lead = Lead(
        telegram_user_id=lead_data.telegram_user_id,
        username=lead_data.username,
        first_name=lead_data.first_name,
        last_name=lead_data.last_name,
        source_group_id=lead_data.source_group_id,
        campaign_id=lead_data.campaign_id,
        score=lead_data.score,
        notes=lead_data.notes,
        tags=lead_data.tags,
        status=LeadStatus.NEW.value
    )
    
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific lead."""
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id)
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return lead


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    lead_data: LeadUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a lead."""
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id)
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    update_data = lead_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(lead, key, value)
    
    # Handle status changes
    if lead_data.status == LeadStatus.CONVERTED.value:
        lead.converted_at = datetime.utcnow()
    
    lead.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(lead)
    return lead


@router.delete("/{lead_id}")
async def delete_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a lead."""
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id)
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    await db.delete(lead)
    await db.commit()
    
    return {"message": "Lead deleted"}


@router.get("/export/csv")
async def export_leads_csv(
    campaign_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Export leads to CSV."""
    query = select(Lead)
    
    conditions = []
    if campaign_id:
        conditions.append(Lead.campaign_id == campaign_id)
    if status:
        conditions.append(Lead.status == status)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    result = await db.execute(query)
    leads = list(result.scalars().all())
    
    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "ID", "Telegram User ID", "Username", "First Name", "Last Name",
        "Status", "Score", "Contact Method", "Contact Count",
        "First Contact", "Last Contact", "Created At", "Tags", "Notes"
    ])
    
    # Data
    for lead in leads:
        writer.writerow([
            lead.id,
            lead.telegram_user_id,
            lead.username,
            lead.first_name,
            lead.last_name,
            lead.status,
            lead.score,
            lead.contact_method,
            lead.contact_count,
            lead.first_contact_at.isoformat() if lead.first_contact_at else "",
            lead.last_contact_at.isoformat() if lead.last_contact_at else "",
            lead.created_at.isoformat(),
            ",".join(lead.tags or []),
            lead.notes
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads_export.csv"}
    )


@router.get("/funnel/stats")
async def get_lead_funnel(
    campaign_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get lead funnel statistics."""
    query = select(Lead.status, func.count(Lead.id))
    
    if campaign_id:
        query = query.where(Lead.campaign_id == campaign_id)
    
    query = query.group_by(Lead.status)
    result = await db.execute(query)
    
    counts = dict(result.all())
    
    total = sum(counts.values())
    
    return {
        "funnel": {
            "new": counts.get(LeadStatus.NEW.value, 0),
            "contacted": counts.get(LeadStatus.CONTACTED.value, 0),
            "engaged": counts.get(LeadStatus.ENGAGED.value, 0),
            "converted": counts.get(LeadStatus.CONVERTED.value, 0),
            "lost": counts.get(LeadStatus.LOST.value, 0)
        },
        "total": total,
        "conversion_rate": (
            counts.get(LeadStatus.CONVERTED.value, 0) / total * 100
            if total > 0 else 0
        )
    }
