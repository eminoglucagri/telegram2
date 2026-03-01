"""Main Telethon bot instance and event handlers."""

import asyncio
from typing import Optional, Callable, Any
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import Message, PeerUser, PeerChannel, PeerChat
import structlog

from .config import settings

logger = structlog.get_logger(__name__)


class TelegramBot:
    """Telegram userbot wrapper using Telethon."""
    
    def __init__(self):
        """Initialize the Telegram bot."""
        self._client: Optional[TelegramClient] = None
        self._handlers: dict[str, list[Callable]] = {
            "new_message": [],
            "message_edited": [],
            "chat_action": [],
        }
        self._running = False
    
    @property
    def client(self) -> TelegramClient:
        """Get the Telegram client instance."""
        if self._client is None:
            raise RuntimeError("Bot not initialized. Call connect() first.")
        return self._client
    
    @property
    def is_connected(self) -> bool:
        """Check if the bot is connected."""
        return self._client is not None and self._client.is_connected()
    
    async def connect(self) -> None:
        """Connect to Telegram."""
        logger.info("Connecting to Telegram...")
        
        # Use session string if available, otherwise create new session
        session = StringSession(settings.telegram.session_string) if settings.telegram.session_string else StringSession()
        
        self._client = TelegramClient(
            session,
            settings.telegram.api_id,
            settings.telegram.api_hash
        )
        
        await self._client.connect()
        
        if not await self._client.is_user_authorized():
            logger.info("User not authorized, starting login...")
            await self._client.send_code_request(settings.telegram.phone)
            # Note: In production, you'd handle code input differently
            # For now, this would need manual intervention
            raise RuntimeError(
                "User not authorized. Please run the login script first to generate session string."
            )
        
        me = await self._client.get_me()
        logger.info(f"Connected as {me.first_name} (@{me.username})")
        
        # Register event handlers
        self._register_handlers()
    
    async def disconnect(self) -> None:
        """Disconnect from Telegram."""
        if self._client:
            await self._client.disconnect()
            self._client = None
            logger.info("Disconnected from Telegram")
    
    def _register_handlers(self) -> None:
        """Register all event handlers."""
        @self._client.on(events.NewMessage)
        async def on_new_message(event: events.NewMessage.Event):
            for handler in self._handlers["new_message"]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Error in message handler: {e}")
        
        @self._client.on(events.MessageEdited)
        async def on_message_edited(event: events.MessageEdited.Event):
            for handler in self._handlers["message_edited"]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Error in edit handler: {e}")
        
        @self._client.on(events.ChatAction)
        async def on_chat_action(event: events.ChatAction.Event):
            for handler in self._handlers["chat_action"]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Error in chat action handler: {e}")
    
    def add_handler(self, event_type: str, handler: Callable) -> None:
        """Add an event handler.
        
        Args:
            event_type: Type of event (new_message, message_edited, chat_action)
            handler: Async function to handle the event
        """
        if event_type not in self._handlers:
            raise ValueError(f"Unknown event type: {event_type}")
        self._handlers[event_type].append(handler)
        logger.debug(f"Added handler for {event_type}")
    
    def remove_handler(self, event_type: str, handler: Callable) -> None:
        """Remove an event handler."""
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
    
    async def send_message(
        self,
        chat_id: int | str,
        message: str,
        reply_to: Optional[int] = None,
        **kwargs
    ) -> Message:
        """Send a message to a chat.
        
        Args:
            chat_id: Chat ID or username
            message: Message text
            reply_to: Message ID to reply to
            **kwargs: Additional arguments for send_message
            
        Returns:
            Sent message object
        """
        logger.info(f"Sending message to {chat_id}")
        return await self.client.send_message(
            chat_id,
            message,
            reply_to=reply_to,
            **kwargs
        )
    
    async def join_group(self, invite_link: str) -> Any:
        """Join a group using invite link or username.
        
        Args:
            invite_link: Group invite link or @username
            
        Returns:
            Join result
        """
        from telethon.tl.functions.channels import JoinChannelRequest
        from telethon.tl.functions.messages import ImportChatInviteRequest
        
        logger.info(f"Joining group: {invite_link}")
        
        if "joinchat" in invite_link or "+" in invite_link:
            # Private invite link
            invite_hash = invite_link.split("/")[-1].replace("+", "")
            return await self.client(ImportChatInviteRequest(invite_hash))
        else:
            # Public group/channel
            entity = await self.client.get_entity(invite_link)
            return await self.client(JoinChannelRequest(entity))
    
    async def leave_group(self, chat_id: int | str) -> None:
        """Leave a group.
        
        Args:
            chat_id: Chat ID or username
        """
        from telethon.tl.functions.channels import LeaveChannelRequest
        
        logger.info(f"Leaving group: {chat_id}")
        entity = await self.client.get_entity(chat_id)
        await self.client(LeaveChannelRequest(entity))
    
    async def get_messages(
        self,
        chat_id: int | str,
        limit: int = 100,
        offset_id: int = 0
    ) -> list[Message]:
        """Get messages from a chat.
        
        Args:
            chat_id: Chat ID or username
            limit: Maximum number of messages
            offset_id: Message ID to start from
            
        Returns:
            List of messages
        """
        return await self.client.get_messages(
            chat_id,
            limit=limit,
            offset_id=offset_id
        )
    
    async def get_dialogs(self, limit: int = 100) -> list:
        """Get user's dialogs (chats).
        
        Args:
            limit: Maximum number of dialogs
            
        Returns:
            List of dialogs
        """
        return await self.client.get_dialogs(limit=limit)
    
    async def get_me(self) -> Any:
        """Get current user info."""
        return await self.client.get_me()
    
    async def get_entity(self, entity_id: int | str) -> Any:
        """Get entity by ID or username."""
        return await self.client.get_entity(entity_id)
    
    def get_session_string(self) -> str:
        """Get the current session string for persistence."""
        if self._client:
            return self._client.session.save()
        return ""
    
    async def run(self) -> None:
        """Run the bot until disconnected."""
        self._running = True
        logger.info("Bot is running...")
        await self.client.run_until_disconnected()
    
    async def stop(self) -> None:
        """Stop the bot."""
        self._running = False
        await self.disconnect()


# Global bot instance
bot = TelegramBot()
