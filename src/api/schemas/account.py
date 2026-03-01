"""Account management Pydantic schemas."""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
import re


class InitiateLoginRequest(BaseModel):
    """Request schema for initiating Telegram login."""
    api_id: int = Field(..., gt=0, description="Telegram API ID")
    api_hash: str = Field(..., min_length=1, description="Telegram API Hash")
    phone: str = Field(..., description="Phone number in international format")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate and normalize phone number."""
        # Remove spaces and dashes
        cleaned = re.sub(r'[\s\-()]', '', v)
        # Ensure it starts with +
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        # Check if it looks like a valid phone number
        if not re.match(r'^\+\d{10,15}$', cleaned):
            raise ValueError('Invalid phone number format. Use international format: +905xxxxxxxxx')
        return cleaned


class InitiateLoginResponse(BaseModel):
    """Response schema for initiate login."""
    phone_code_hash: str
    message: str = "Verification code sent"


class VerifyCodeRequest(BaseModel):
    """Request schema for verifying the code."""
    api_id: int = Field(..., gt=0, description="Telegram API ID")
    api_hash: str = Field(..., min_length=1, description="Telegram API Hash")
    phone: str = Field(..., description="Phone number in international format")
    code: str = Field(..., min_length=4, max_length=10, description="Verification code from Telegram")
    phone_code_hash: str = Field(..., min_length=1, description="Phone code hash from initiate-login")
    password: Optional[str] = Field(None, description="2FA password if required")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate and normalize phone number."""
        cleaned = re.sub(r'[\s\-()]', '', v)
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        return cleaned
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate verification code."""
        # Remove spaces and keep only digits
        cleaned = re.sub(r'\s', '', v)
        if not cleaned.isdigit():
            raise ValueError('Verification code must contain only digits')
        return cleaned


class AccountResponse(BaseModel):
    """Response schema for account information."""
    id: int
    phone: str
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    status: str
    warmup_stage: int = 1
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AccountStatusResponse(BaseModel):
    """Response schema for account status check."""
    id: int
    phone: str
    status: Literal['active', 'inactive', 'banned', 'warming_up']
    is_connected: bool
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    message: Optional[str] = None
