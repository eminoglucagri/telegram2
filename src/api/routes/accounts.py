"""Account management endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.database.base import get_db
from src.database.models import User
from src.services.account_service import account_service
from src.api.schemas.account import (
    InitiateLoginRequest,
    InitiateLoginResponse,
    VerifyCodeRequest,
    AccountResponse,
    AccountStatusResponse,
)

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/initiate-login", response_model=InitiateLoginResponse)
async def initiate_login(request: InitiateLoginRequest):
    """
    Initiate Telegram login process.
    
    Sends a verification code to the provided phone number.
    """
    try:
        phone_code_hash = await account_service.initiate_login(
            api_id=request.api_id,
            api_hash=request.api_hash,
            phone=request.phone
        )
        return InitiateLoginResponse(
            phone_code_hash=phone_code_hash,
            message="Verification code sent to your Telegram app"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=429 if "wait" in str(e).lower() else 500, detail=str(e))
    except Exception as e:
        logger.error("Initiate login failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to send verification code")


@router.post("/verify-code", response_model=AccountResponse)
async def verify_code(
    request: VerifyCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify the code and complete login.
    
    Saves the account to database upon successful verification.
    """
    try:
        user = await account_service.verify_and_save(
            db=db,
            api_id=request.api_id,
            api_hash=request.api_hash,
            phone=request.phone,
            code=request.code,
            phone_code_hash=request.phone_code_hash,
            password=request.password
        )
        return AccountResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # 2FA required
        raise HTTPException(status_code=428, detail=str(e))
    except Exception as e:
        logger.error("Verify code failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to verify code")


@router.get("", response_model=List[AccountResponse])
async def list_accounts(db: AsyncSession = Depends(get_db)):
    """
    List all Telegram accounts.
    """
    result = await db.execute(
        select(User).order_by(User.created_at.desc())
    )
    users = result.scalars().all()
    return [AccountResponse.model_validate(user) for user in users]


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific account by ID.
    """
    result = await db.execute(
        select(User).where(User.id == account_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return AccountResponse.model_validate(user)


@router.get("/{account_id}/status", response_model=AccountStatusResponse)
async def check_account_status(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Check if an account is active and connected to Telegram.
    
    This will attempt to connect to Telegram and verify the session.
    """
    try:
        status = await account_service.check_account_status(db, account_id)
        return AccountStatusResponse(**status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Check status failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to check account status")


@router.delete("/{account_id}")
async def delete_account(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an account from the system.
    
    This will log out from Telegram and remove all account data.
    """
    try:
        await account_service.delete_account(db, account_id)
        return {"message": "Account deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Delete account failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete account")
