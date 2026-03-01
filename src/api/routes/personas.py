"""Persona management endpoints."""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base import get_db
from src.database.models import Persona

router = APIRouter()


# Pydantic Schemas
class PersonaCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    bio: Optional[str] = None
    interests: List[str] = []
    tone: str = Field("friendly", description="Communication tone")
    language_style: Optional[str] = None
    sample_messages: List[str] = []
    keywords_to_engage: List[str] = []
    keywords_to_avoid: List[str] = []
    response_templates: dict = {}


class PersonaUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    interests: Optional[List[str]] = None
    tone: Optional[str] = None
    language_style: Optional[str] = None
    sample_messages: Optional[List[str]] = None
    keywords_to_engage: Optional[List[str]] = None
    keywords_to_avoid: Optional[List[str]] = None
    response_templates: Optional[dict] = None
    is_active: Optional[bool] = None


class PersonaResponse(BaseModel):
    id: int
    name: str
    bio: Optional[str]
    interests: List[str]
    tone: str
    language_style: Optional[str]
    sample_messages: List[str]
    keywords_to_engage: List[str]
    keywords_to_avoid: List[str]
    response_templates: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Endpoints
@router.get("", response_model=List[PersonaResponse])
async def list_personas(
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db)
):
    """List all personas."""
    query = select(Persona)
    
    if active_only:
        query = query.where(Persona.is_active == True)
    
    query = query.order_by(Persona.name)
    
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("", response_model=PersonaResponse, status_code=201)
async def create_persona(
    persona_data: PersonaCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new persona."""
    # Check for duplicate name
    existing = await db.execute(
        select(Persona).where(Persona.name == persona_data.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Persona with this name already exists")
    
    persona = Persona(
        name=persona_data.name,
        bio=persona_data.bio,
        interests=persona_data.interests,
        tone=persona_data.tone,
        language_style=persona_data.language_style,
        sample_messages=persona_data.sample_messages,
        keywords_to_engage=persona_data.keywords_to_engage,
        keywords_to_avoid=persona_data.keywords_to_avoid,
        response_templates=persona_data.response_templates,
        is_active=True
    )
    
    db.add(persona)
    await db.commit()
    await db.refresh(persona)
    return persona


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific persona."""
    result = await db.execute(
        select(Persona).where(Persona.id == persona_id)
    )
    persona = result.scalar_one_or_none()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    return persona


@router.patch("/{persona_id}", response_model=PersonaResponse)
async def update_persona(
    persona_id: int,
    persona_data: PersonaUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a persona."""
    result = await db.execute(
        select(Persona).where(Persona.id == persona_id)
    )
    persona = result.scalar_one_or_none()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    update_data = persona_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(persona, key, value)
    
    persona.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(persona)
    return persona


@router.delete("/{persona_id}")
async def delete_persona(
    persona_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Deactivate a persona (soft delete)."""
    result = await db.execute(
        select(Persona).where(Persona.id == persona_id)
    )
    persona = result.scalar_one_or_none()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    persona.is_active = False
    await db.commit()
    
    return {"message": "Persona deactivated"}


@router.get("/{persona_id}/preview")
async def preview_persona(
    persona_id: int,
    message: str = Query(..., description="Sample message to respond to"),
    db: AsyncSession = Depends(get_db)
):
    """Preview how a persona would respond to a message."""
    result = await db.execute(
        select(Persona).where(Persona.id == persona_id)
    )
    persona = result.scalar_one_or_none()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    # Generate system prompt preview
    interests_str = ", ".join(persona.interests) if persona.interests else "various topics"
    
    system_prompt = f"""Persona: {persona.name}
Bio: {persona.bio}
Interests: {interests_str}
Tone: {persona.tone}
Language Style: {persona.language_style or 'Natural'}"""
    
    # Check engagement keywords
    should_engage = True
    text_lower = message.lower()
    
    if persona.keywords_to_avoid:
        for keyword in persona.keywords_to_avoid:
            if keyword.lower() in text_lower:
                should_engage = False
                break
    
    return {
        "persona": persona.name,
        "system_prompt": system_prompt,
        "should_engage": should_engage,
        "sample_messages": persona.sample_messages[:3] if persona.sample_messages else [],
        "note": "Use LLM service for actual response generation"
    }
