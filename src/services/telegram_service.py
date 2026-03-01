"""Telegram service wrapper for common operations."""

from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
import structlog

from src.core.bot import TelegramBot
from src.core.config import settings

logger = structlog.get_logger(__name__)


class TelegramService:
    """High-level Telegram operations wrapper."""
    
    def __init__(self, bot: TelegramBot):
        """Initialize Telegram service.
        
        Args:
            bot: TelegramBot instance
        """
        self.bot = bot
        self._rate_limit_delay = 60 / settings.rate_limit.messages_per_minute
    
    async def send_message_safe(
        self,
        chat_id: int | str,
        message: str,
        reply_to: Optional[int] = None,
        delay: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Send a message with rate limiting and error handling.
        
        Args:
            chat_id: Chat to send to
            message: Message text
            reply_to: Message to reply to
            delay: Whether to add rate limiting delay
            
        Returns:
            Message info dict or None if failed
        """
        try:
            # Add natural delay
            if delay:
                await asyncio.sleep(self._rate_limit_delay)
            
            sent = await self.bot.send_message(chat_id, message, reply_to=reply_to)
            
            return {
                "id": sent.id,
                "date": sent.date.isoformat() if sent.date else datetime.utcnow().isoformat(),
                "text": sent.text,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return None
    
    async def get_group_info(self, group_id: int | str) -> Optional[Dict[str, Any]]:
        """Get detailed group information.
        
        Args:
            group_id: Group ID or username
            
        Returns:
            Group info dict or None
        """
        try:
            entity = await self.bot.get_entity(group_id)
            
            info = {
                "id": entity.id,
                "title": getattr(entity, 'title', None),
                "username": getattr(entity, 'username', None),
                "participants_count": getattr(entity, 'participants_count', None),
                "date": getattr(entity, 'date', None),
            }
            
            # Try to get more details
            if hasattr(entity, 'about'):
                info["about"] = entity.about
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get group info: {e}")
            return None
    
    async def get_user_info(self, user_id: int | str) -> Optional[Dict[str, Any]]:
        """Get user information.
        
        Args:
            user_id: User ID or username
            
        Returns:
            User info dict or None
        """
        try:
            entity = await self.bot.get_entity(user_id)
            
            return {
                "id": entity.id,
                "first_name": getattr(entity, 'first_name', None),
                "last_name": getattr(entity, 'last_name', None),
                "username": getattr(entity, 'username', None),
                "phone": getattr(entity, 'phone', None),
                "is_bot": getattr(entity, 'bot', False),
            }
            
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return None
    
    async def get_recent_messages(
        self,
        chat_id: int | str,
        limit: int = 50,
        filter_bots: bool = True
    ) -> List[Dict[str, Any]]:
        """Get recent messages from a chat.
        
        Args:
            chat_id: Chat ID or username
            limit: Max messages to fetch
            filter_bots: Exclude bot messages
            
        Returns:
            List of message dicts
        """
        try:
            messages = await self.bot.get_messages(chat_id, limit=limit)
            
            result = []
            for msg in messages:
                if not msg.text:
                    continue
                
                # Get sender info
                sender_id = msg.sender_id if hasattr(msg, 'sender_id') else None
                is_bot = False
                username = None
                
                if msg.sender:
                    is_bot = getattr(msg.sender, 'bot', False)
                    username = getattr(msg.sender, 'username', None)
                
                if filter_bots and is_bot:
                    continue
                
                result.append({
                    "id": msg.id,
                    "text": msg.text,
                    "date": msg.date.isoformat() if msg.date else None,
                    "sender_id": sender_id,
                    "sender_username": username,
                    "reply_to_msg_id": msg.reply_to_msg_id if hasattr(msg, 'reply_to_msg_id') else None
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return []
    
    async def join_group_safe(
        self,
        invite_link: str,
        check_limits: bool = True
    ) -> Dict[str, Any]:
        """Safely join a group with rate limiting.
        
        Args:
            invite_link: Group invite link or username
            check_limits: Whether to check daily limits
            
        Returns:
            Result dict
        """
        try:
            result = await self.bot.join_group(invite_link)
            
            return {
                "success": True,
                "message": "Successfully joined group"
            }
            
        except Exception as e:
            error_str = str(e).lower()
            
            if "flood" in error_str:
                return {
                    "success": False,
                    "error": "rate_limited",
                    "message": "Too many join requests. Try again later."
                }
            elif "invite" in error_str:
                return {
                    "success": False,
                    "error": "invalid_invite",
                    "message": "Invalid or expired invite link"
                }
            elif "banned" in error_str:
                return {
                    "success": False,
                    "error": "banned",
                    "message": "You are banned from this group"
                }
            else:
                return {
                    "success": False,
                    "error": "unknown",
                    "message": str(e)
                }
    
    async def leave_group_safe(self, chat_id: int | str) -> Dict[str, Any]:
        """Safely leave a group.
        
        Args:
            chat_id: Chat ID or username
            
        Returns:
            Result dict
        """
        try:
            await self.bot.leave_group(chat_id)
            return {"success": True, "message": "Left group successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_my_dialogs(
        self,
        limit: int = 100,
        groups_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get user's dialogs (chats).
        
        Args:
            limit: Max dialogs to fetch
            groups_only: Only return groups/channels
            
        Returns:
            List of dialog dicts
        """
        try:
            dialogs = await self.bot.get_dialogs(limit=limit)
            
            result = []
            for dialog in dialogs:
                is_group = dialog.is_group or dialog.is_channel
                
                if groups_only and not is_group:
                    continue
                
                result.append({
                    "id": dialog.id,
                    "name": dialog.name,
                    "is_group": is_group,
                    "is_channel": dialog.is_channel,
                    "unread_count": dialog.unread_count,
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get dialogs: {e}")
            return []
    
    async def typing_action(
        self,
        chat_id: int | str,
        duration: float = 2.0
    ) -> None:
        """Show typing indicator.
        
        Args:
            chat_id: Chat ID
            duration: How long to show typing
        """
        try:
            from telethon.tl.functions.messages import SetTypingRequest
            from telethon.tl.types import SendMessageTypingAction
            
            await self.bot.client(SetTypingRequest(
                peer=chat_id,
                action=SendMessageTypingAction()
            ))
            await asyncio.sleep(duration)
        except Exception as e:
            logger.debug(f"Typing action failed: {e}")
