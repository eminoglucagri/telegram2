"""SQLAlchemy database models."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Boolean, DateTime,
    ForeignKey, JSON, Float, Enum, Date, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
import enum

from .base import Base


class UserStatus(str, enum.Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"
    WARMING_UP = "warming_up"


class CampaignStatus(str, enum.Enum):
    """Campaign status."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class GroupStatus(str, enum.Enum):
    """Group status."""
    PENDING = "pending"
    ACTIVE = "active"
    LEFT = "left"
    BANNED = "banned"


class LeadStatus(str, enum.Enum):
    """Lead status."""
    NEW = "new"
    CONTACTED = "contacted"
    ENGAGED = "engaged"
    CONVERTED = "converted"
    LOST = "lost"


class User(Base):
    """Telegram user account model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, nullable=False)
    telegram_id = Column(BigInteger, unique=True, nullable=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    api_id = Column(Integer, nullable=False)
    api_hash = Column(String(100), nullable=False)
    session_string = Column(Text, nullable=True)
    status = Column(String(20), default=UserStatus.INACTIVE.value)
    warmup_stage = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaigns = relationship("Campaign", back_populates="user")
    warm_up_metrics = relationship("WarmUpMetric", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, phone={self.phone}, status={self.status})>"


class Persona(Base):
    """Bot persona model."""
    __tablename__ = "personas"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    bio = Column(Text, nullable=True)
    interests = Column(JSON, default=list)  # List of interests
    tone = Column(String(50), default="friendly")  # friendly, professional, casual
    language_style = Column(Text, nullable=True)  # Description of language style
    sample_messages = Column(JSON, default=list)  # Sample messages for training
    keywords_to_engage = Column(JSON, default=list)  # Keywords to respond to
    keywords_to_avoid = Column(JSON, default=list)  # Keywords to avoid
    response_templates = Column(JSON, default=dict)  # Template responses
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaigns = relationship("Campaign", back_populates="persona")
    
    def __repr__(self):
        return f"<Persona(id={self.id}, name={self.name})>"


class Campaign(Base):
    """Marketing campaign model."""
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=True)
    status = Column(String(20), default=CampaignStatus.DRAFT.value)
    target_keywords = Column(JSON, default=list)  # Keywords to identify leads
    target_industries = Column(JSON, default=list)
    product_info = Column(Text, nullable=True)  # Product/service to promote
    call_to_action = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    daily_message_limit = Column(Integer, default=50)
    daily_dm_limit = Column(Integer, default=10)
    settings = Column(JSON, default=dict)  # Additional campaign settings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="campaigns")
    persona = relationship("Persona", back_populates="campaigns")
    groups = relationship("Group", back_populates="campaign")
    leads = relationship("Lead", back_populates="campaign")
    messages = relationship("Message", back_populates="campaign")
    
    def __repr__(self):
        return f"<Campaign(id={self.id}, name={self.name}, status={self.status})>"


class Group(Base):
    """Telegram group model."""
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    title = Column(String(500), nullable=True)
    username = Column(String(100), nullable=True)
    invite_link = Column(String(500), nullable=True)
    member_count = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    status = Column(String(20), default=GroupStatus.PENDING.value)
    joined_at = Column(DateTime, nullable=True)
    left_at = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, nullable=True)
    message_count = Column(Integer, default=0)  # Messages sent in this group
    is_target = Column(Boolean, default=True)  # Is this a target group for marketing
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="groups")
    messages = relationship("Message", back_populates="group")
    leads = relationship("Lead", back_populates="source_group")
    
    __table_args__ = (
        Index("ix_groups_campaign_status", "campaign_id", "status"),
    )
    
    def __repr__(self):
        return f"<Group(id={self.id}, title={self.title}, status={self.status})>"


class Message(Base):
    """Message model for tracking conversations."""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_message_id = Column(BigInteger, nullable=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    sender_telegram_id = Column(BigInteger, nullable=True)
    sender_username = Column(String(100), nullable=True)
    content = Column(Text, nullable=False)
    reply_to_message_id = Column(BigInteger, nullable=True)
    is_bot_message = Column(Boolean, default=False)  # Sent by our bot
    is_dm = Column(Boolean, default=False)  # Direct message
    sentiment = Column(String(20), nullable=True)  # positive, negative, neutral
    intent = Column(String(50), nullable=True)  # question, complaint, interest, etc.
    lead_score = Column(Float, nullable=True)  # 0-1 score for lead potential
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    group = relationship("Group", back_populates="messages")
    campaign = relationship("Campaign", back_populates="messages")
    
    __table_args__ = (
        Index("ix_messages_group_created", "group_id", "created_at"),
        Index("ix_messages_campaign_created", "campaign_id", "created_at"),
    )
    
    def __repr__(self):
        return f"<Message(id={self.id}, is_bot={self.is_bot_message})>"


class Lead(Base):
    """Lead model for tracking potential customers."""
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(BigInteger, nullable=False)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    source_group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    status = Column(String(20), default=LeadStatus.NEW.value)
    score = Column(Float, default=0.0)  # Lead score 0-100
    contact_method = Column(String(50), nullable=True)  # dm, group_mention, etc.
    first_contact_at = Column(DateTime, nullable=True)
    last_contact_at = Column(DateTime, nullable=True)
    contact_count = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    custom_data = Column(JSON, default=dict)  # Additional lead data
    converted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    source_group = relationship("Group", back_populates="leads")
    campaign = relationship("Campaign", back_populates="leads")
    
    __table_args__ = (
        UniqueConstraint("telegram_user_id", "campaign_id", name="uq_lead_user_campaign"),
        Index("ix_leads_status", "status"),
        Index("ix_leads_campaign_status", "campaign_id", "status"),
    )
    
    def __repr__(self):
        return f"<Lead(id={self.id}, username={self.username}, status={self.status})>"


class WarmUpMetric(Base):
    """Warm-up metrics tracking model."""
    __tablename__ = "warm_up_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    messages_sent = Column(Integer, default=0)
    messages_received = Column(Integer, default=0)
    groups_joined = Column(Integer, default=0)
    groups_left = Column(Integer, default=0)
    dms_sent = Column(Integer, default=0)
    dms_received = Column(Integer, default=0)
    reactions_given = Column(Integer, default=0)
    warmup_stage = Column(Integer, default=1)
    score = Column(Float, default=0.0)  # Daily warm-up score
    flags = Column(JSON, default=list)  # Any flags or warnings
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="warm_up_metrics")
    
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_warmup_user_date"),
        Index("ix_warmup_user_date", "user_id", "date"),
    )
    
    def __repr__(self):
        return f"<WarmUpMetric(user_id={self.user_id}, date={self.date}, stage={self.warmup_stage})>"
