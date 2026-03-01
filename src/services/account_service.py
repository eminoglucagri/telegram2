"""Account service for managing Telegram accounts."""

import structlog
from typing import Optional, Dict, Any
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    PhoneNumberInvalidError,
    PhoneNumberBannedError,
    FloodWaitError,
    AuthKeyUnregisteredError,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.models import User, UserStatus

logger = structlog.get_logger(__name__)


class AccountService:
    """Service for managing Telegram account operations."""
    
    # Store pending clients for verification (in production, use Redis)
    _pending_clients: Dict[str, TelegramClient] = {}
    
    async def initiate_login(
        self,
        api_id: int,
        api_hash: str,
        phone: str
    ) -> str:
        """
        Initiate Telegram login by sending verification code.
        
        Args:
            api_id: Telegram API ID
            api_hash: Telegram API Hash
            phone: Phone number in international format
            
        Returns:
            phone_code_hash for verification
            
        Raises:
            ValueError: If phone number is invalid or banned
            RuntimeError: If there's a flood wait or other error
        """
        logger.info("Initiating login", phone=phone[:4] + "****")
        
        # Create a new client with empty session
        client = TelegramClient(
            StringSession(),
            api_id,
            api_hash,
            device_model="Telegram Agent",
            system_version="1.0",
            app_version="1.0"
        )
        
        try:
            await client.connect()
            
            # Send code request
            result = await client.send_code_request(phone)
            phone_code_hash = result.phone_code_hash
            
            # Store client for later verification
            # Key: phone_api_id to handle multiple accounts
            client_key = f"{phone}_{api_id}"
            
            # Disconnect any existing pending client for this phone
            if client_key in self._pending_clients:
                old_client = self._pending_clients[client_key]
                if old_client.is_connected():
                    await old_client.disconnect()
            
            self._pending_clients[client_key] = client
            
            logger.info("Verification code sent", phone=phone[:4] + "****")
            return phone_code_hash
            
        except PhoneNumberInvalidError:
            await client.disconnect()
            raise ValueError("Invalid phone number format")
        except PhoneNumberBannedError:
            await client.disconnect()
            raise ValueError("This phone number is banned from Telegram")
        except FloodWaitError as e:
            await client.disconnect()
            raise RuntimeError(f"Too many requests. Please wait {e.seconds} seconds.")
        except Exception as e:
            await client.disconnect()
            logger.error("Failed to initiate login", error=str(e))
            raise RuntimeError(f"Failed to send verification code: {str(e)}")
    
    async def verify_and_save(
        self,
        db: AsyncSession,
        api_id: int,
        api_hash: str,
        phone: str,
        code: str,
        phone_code_hash: str,
        password: Optional[str] = None
    ) -> User:
        """
        Verify the code and save the account to database.
        
        Args:
            db: Database session
            api_id: Telegram API ID
            api_hash: Telegram API Hash
            phone: Phone number
            code: Verification code from Telegram
            phone_code_hash: Hash received from initiate_login
            password: 2FA password if required
            
        Returns:
            User model instance
            
        Raises:
            ValueError: If code is invalid or expired
            RuntimeError: If 2FA is required but password not provided
        """
        logger.info("Verifying code", phone=phone[:4] + "****")
        
        client_key = f"{phone}_{api_id}"
        client = self._pending_clients.get(client_key)
        
        if not client:
            # Create new client if not found (e.g., after server restart)
            client = TelegramClient(
                StringSession(),
                api_id,
                api_hash,
                device_model="Telegram Agent",
                system_version="1.0",
                app_version="1.0"
            )
            await client.connect()
        
        try:
            # Try to sign in
            try:
                await client.sign_in(
                    phone=phone,
                    code=code,
                    phone_code_hash=phone_code_hash
                )
            except SessionPasswordNeededError:
                # 2FA is enabled
                if not password:
                    raise RuntimeError("2FA is enabled. Please provide your password.")
                await client.sign_in(password=password)
            
            # Get user info from Telegram
            me = await client.get_me()
            
            # Save session string
            session_string = client.session.save()
            
            # Check if user already exists
            result = await db.execute(
                select(User).where(User.phone == phone)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                # Update existing user
                existing_user.api_id = api_id
                existing_user.api_hash = api_hash
                existing_user.session_string = session_string
                existing_user.telegram_id = me.id
                existing_user.username = me.username
                existing_user.first_name = me.first_name
                existing_user.status = UserStatus.ACTIVE.value
                user = existing_user
                logger.info("Updated existing account", phone=phone[:4] + "****")
            else:
                # Create new user
                user = User(
                    phone=phone,
                    api_id=api_id,
                    api_hash=api_hash,
                    session_string=session_string,
                    telegram_id=me.id,
                    username=me.username,
                    first_name=me.first_name,
                    status=UserStatus.ACTIVE.value,
                    warmup_stage=1
                )
                db.add(user)
                logger.info("Created new account", phone=phone[:4] + "****")
            
            await db.commit()
            await db.refresh(user)
            
            # Remove from pending clients
            if client_key in self._pending_clients:
                del self._pending_clients[client_key]
            
            return user
            
        except PhoneCodeInvalidError:
            raise ValueError("Invalid verification code")
        except PhoneCodeExpiredError:
            raise ValueError("Verification code has expired. Please request a new one.")
        except Exception as e:
            logger.error("Failed to verify code", error=str(e))
            raise
        finally:
            # Always disconnect the client after verification
            if client.is_connected():
                await client.disconnect()
    
    async def check_account_status(
        self,
        db: AsyncSession,
        account_id: int
    ) -> Dict[str, Any]:
        """
        Check if an account is still active and connected.
        
        Args:
            db: Database session
            account_id: User ID in database
            
        Returns:
            Dict with status information
        """
        result = await db.execute(
            select(User).where(User.id == account_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("Account not found")
        
        if not user.session_string:
            return {
                "id": user.id,
                "phone": user.phone,
                "status": "inactive",
                "is_connected": False,
                "message": "No session found"
            }
        
        # Try to connect and verify
        client = TelegramClient(
            StringSession(user.session_string),
            user.api_id,
            user.api_hash
        )
        
        try:
            await client.connect()
            
            if await client.is_user_authorized():
                me = await client.get_me()
                
                # Update user info if changed
                if me.username != user.username or me.first_name != user.first_name:
                    user.username = me.username
                    user.first_name = me.first_name
                    await db.commit()
                
                return {
                    "id": user.id,
                    "phone": user.phone,
                    "status": "active",
                    "is_connected": True,
                    "telegram_id": me.id,
                    "username": me.username,
                    "message": "Account is active"
                }
            else:
                # Session is invalid
                user.status = UserStatus.INACTIVE.value
                await db.commit()
                
                return {
                    "id": user.id,
                    "phone": user.phone,
                    "status": "inactive",
                    "is_connected": False,
                    "message": "Session expired. Please re-login."
                }
                
        except AuthKeyUnregisteredError:
            user.status = UserStatus.BANNED.value
            await db.commit()
            
            return {
                "id": user.id,
                "phone": user.phone,
                "status": "banned",
                "is_connected": False,
                "message": "Account has been banned or deactivated"
            }
        except Exception as e:
            logger.error("Failed to check account status", error=str(e))
            return {
                "id": user.id,
                "phone": user.phone,
                "status": user.status,
                "is_connected": False,
                "message": f"Connection error: {str(e)}"
            }
        finally:
            if client.is_connected():
                await client.disconnect()
    
    async def delete_account(
        self,
        db: AsyncSession,
        account_id: int
    ) -> bool:
        """
        Delete an account from the database.
        
        Args:
            db: Database session
            account_id: User ID in database
            
        Returns:
            True if deleted successfully
        """
        result = await db.execute(
            select(User).where(User.id == account_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("Account not found")
        
        # Log out from Telegram if possible
        if user.session_string:
            try:
                client = TelegramClient(
                    StringSession(user.session_string),
                    user.api_id,
                    user.api_hash
                )
                await client.connect()
                if await client.is_user_authorized():
                    await client.log_out()
                await client.disconnect()
            except Exception as e:
                logger.warning("Failed to log out from Telegram", error=str(e))
        
        # Delete from database
        await db.delete(user)
        await db.commit()
        
        logger.info("Account deleted", account_id=account_id)
        return True


# Singleton instance
account_service = AccountService()
