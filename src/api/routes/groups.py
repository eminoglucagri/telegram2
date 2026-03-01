"""Group management endpoints."""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base import get_db
from src.database.models import Group, GroupStatus

router = APIRouter()


# Pydantic Schemas
class GroupCreate(BaseModel):
    telegram_id: int
    title: Optional[str] = None
    username: Optional[str] = None
    invite_link: Optional[str] = None
    campaign_id: Optional[int] = None
    is_target: bool = True
    notes: Optional[str] = None


class GroupUpdate(BaseModel):
    title: Optional[str] = None
    username: Optional[str] = None
    invite_link: Optional[str] = None
    campaign_id: Optional[int] = None
    status: Optional[str] = None
    is_target: Optional[bool] = None
    notes: Optional[str] = None


class GroupResponse(BaseModel):
    id: int
    telegram_id: int
    title: Optional[str]
    username: Optional[str]
    invite_link: Optional[str]
    member_count: int
    campaign_id: Optional[int]
    status: str
    joined_at: Optional[datetime]
    left_at: Optional[datetime]
    last_activity: Optional[datetime]
    message_count: int
    is_target: bool
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class GroupAddRequest(BaseModel):
    invite_link: str = Field(..., description="Group invite link or @username")
    campaign_id: Optional[int] = None
    auto_join: bool = False


# Endpoints
@router.get("", response_model=List[GroupResponse])
async def list_groups(
    campaign_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    is_target: Optional[bool] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List all groups with optional filtering."""
    query = select(Group)
    
    conditions = []
    if campaign_id:
        conditions.append(Group.campaign_id == campaign_id)
    if status:
        conditions.append(Group.status == status)
    if is_target is not None:
        conditions.append(Group.is_target == is_target)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.offset(offset).limit(limit).order_by(Group.created_at.desc())
    
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("", response_model=GroupResponse, status_code=201)
async def create_group(
    group_data: GroupCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a group manually."""
    # Check if group already exists
    existing = await db.execute(
        select(Group).where(Group.telegram_id == group_data.telegram_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Group already exists")
    
    group = Group(
        telegram_id=group_data.telegram_id,
        title=group_data.title,
        username=group_data.username,
        invite_link=group_data.invite_link,
        campaign_id=group_data.campaign_id,
        is_target=group_data.is_target,
        notes=group_data.notes,
        status=GroupStatus.PENDING.value
    )
    
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return group


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific group."""
    result = await db.execute(
        select(Group).where(Group.id == group_id)
    )
    group = result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    return group


@router.patch("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: int,
    group_data: GroupUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a group."""
    result = await db.execute(
        select(Group).where(Group.id == group_id)
    )
    group = result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    update_data = group_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(group, key, value)
    
    group.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(group)
    return group


@router.delete("/{group_id}")
async def remove_group(
    group_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Remove a group from tracking."""
    result = await db.execute(
        select(Group).where(Group.id == group_id)
    )
    group = result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    group.status = GroupStatus.LEFT.value
    group.left_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "Group removed from tracking"}


@router.post("/{group_id}/assign/{campaign_id}")
async def assign_group_to_campaign(
    group_id: int,
    campaign_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Assign a group to a campaign."""
    result = await db.execute(
        select(Group).where(Group.id == group_id)
    )
    group = result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    group.campaign_id = campaign_id
    await db.commit()
    
    return {"message": f"Group assigned to campaign {campaign_id}"}


@router.get("/stats/summary")
async def get_groups_summary(
    db: AsyncSession = Depends(get_db)
):
    """Get summary statistics for groups."""
    from sqlalchemy import func
    
    result = await db.execute(
        select(
            Group.status,
            func.count(Group.id)
        ).group_by(Group.status)
    )
    status_counts = dict(result.all())
    
    result = await db.execute(
        select(func.sum(Group.member_count))
    )
    total_members = result.scalar() or 0
    
    return {
        "by_status": status_counts,
        "total_member_reach": total_members
    }
