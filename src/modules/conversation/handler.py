"""Conversation handling with LLM integration."""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.database.models import Message, Group, Campaign
from src.modules.persona.engine import PersonaEngine
from src.services.llm import LLMService
from src.modules.warmup.tracker import WarmUpTracker

logger = structlog.get_logger(__name__)


class ConversationHandler:
    """Handles conversation flow and message generation."""
    
    def __init__(
        self,
        db: AsyncSession,
        llm_service: LLMService,
        persona_engine: PersonaEngine,
        warmup_tracker: WarmUpTracker
    ):
        """Initialize conversation handler.
        
        Args:
            db: Database session
            llm_service: LLM service for generating responses
            persona_engine: Persona engine for character consistency
            warmup_tracker: Warm-up tracker for rate limiting
        """
        self.db = db
        self.llm = llm_service
        self.persona = persona_engine
        self.warmup = warmup_tracker
    
    async def analyze_message(self, message_text: str) -> Dict[str, Any]:
        """Analyze a message for intent, sentiment, and lead potential.
        
        Args:
            message_text: Message to analyze
            
        Returns:
            Analysis results
        """
        analysis_prompt = f"""Analyze the following Telegram message and provide:
1. Sentiment (positive, negative, neutral)
2. Intent (question, statement, complaint, request, interest, greeting, other)
3. Lead score (0-1, where 1 = high potential customer)
4. Key topics mentioned
5. Is this a good message to respond to? (yes/no)

Message: "{message_text}"

Respond in JSON format:
{{
    "sentiment": "...",
    "intent": "...",
    "lead_score": 0.0,
    "topics": [...],
    "should_respond": true/false,
    "reason": "..."
}}"""
        
        try:
            response = await self.llm.generate(
                system_prompt="You are a message analyzer. Respond only with valid JSON.",
                user_prompt=analysis_prompt,
                temperature=0.3
            )
            
            import json
            return json.loads(response)
        except Exception as e:
            logger.error(f"Message analysis failed: {e}")
            return {
                "sentiment": "neutral",
                "intent": "other",
                "lead_score": 0.0,
                "topics": [],
                "should_respond": False,
                "reason": "Analysis failed"
            }
    
    async def should_respond(
        self,
        message_text: str,
        group_id: int,
        is_direct_mention: bool = False
    ) -> tuple[bool, str]:
        """Determine if bot should respond to a message.
        
        Args:
            message_text: Message text
            group_id: Group ID
            is_direct_mention: If bot was directly mentioned
            
        Returns:
            Tuple of (should_respond, reason)
        """
        # Always respond to direct mentions
        if is_direct_mention:
            return True, "Direct mention"
        
        # Check persona engagement rules
        if not self.persona.should_engage(message_text):
            return False, "Persona engagement rules"
        
        # Check warm-up limits
        can_reply, reason = await self.warmup.can_perform_action("reply")
        if not can_reply:
            return False, reason
        
        # Analyze message
        analysis = await self.analyze_message(message_text)
        
        if not analysis.get("should_respond", False):
            return False, analysis.get("reason", "Low engagement potential")
        
        # Check if it's a question or shows interest
        if analysis.get("intent") in ["question", "interest", "request"]:
            return True, f"High engagement potential: {analysis.get('intent')}"
        
        # Check lead score
        if analysis.get("lead_score", 0) > 0.5:
            return True, f"High lead score: {analysis.get('lead_score')}"
        
        return False, "Low engagement criteria"
    
    async def get_conversation_context(
        self,
        group_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent conversation context for a group.
        
        Args:
            group_id: Group ID
            limit: Number of recent messages
            
        Returns:
            List of message dictionaries
        """
        result = await self.db.execute(
            select(Message)
            .where(Message.group_id == group_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
        )
        messages = list(result.scalars().all())
        messages.reverse()  # Chronological order
        
        return [
            {
                "sender": msg.sender_username or "user",
                "content": msg.content,
                "is_bot": msg.is_bot_message,
                "timestamp": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    
    async def generate_response(
        self,
        message_text: str,
        group_id: int,
        campaign_id: Optional[int] = None,
        context: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Generate a response to a message.
        
        Args:
            message_text: Message to respond to
            group_id: Group ID
            campaign_id: Campaign ID (optional)
            context: Conversation context (optional)
            
        Returns:
            Generated response text
        """
        # Get conversation context if not provided
        if context is None:
            context = await self.get_conversation_context(group_id)
        
        # Build context string
        context_str = "\n".join([
            f"{msg['sender']}: {msg['content']}"
            for msg in context[-5:]  # Last 5 messages
        ])
        
        # Get campaign context if available
        campaign_context = ""
        if campaign_id:
            result = await self.db.execute(
                select(Campaign).where(Campaign.id == campaign_id)
            )
            campaign = result.scalar_one_or_none()
            if campaign and campaign.product_info:
                campaign_context = f"\n\nCAMPAIGN CONTEXT: You can naturally mention: {campaign.product_info}"
        
        # Get persona system prompt
        system_prompt = self.persona.get_system_prompt()
        system_prompt += campaign_context
        
        # Build user prompt
        user_prompt = f"""RECENT CONVERSATION:
{context_str}

LATEST MESSAGE TO RESPOND TO:
"{message_text}"

Generate a natural, engaging response that:
1. Addresses the message directly
2. Maintains your persona
3. Is concise (1-3 sentences)
4. Encourages further conversation

Response:"""
        
        response = await self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.8
        )
        
        return response.strip()
    
    async def save_message(
        self,
        content: str,
        group_id: int,
        telegram_message_id: Optional[int] = None,
        sender_telegram_id: Optional[int] = None,
        sender_username: Optional[str] = None,
        campaign_id: Optional[int] = None,
        is_bot_message: bool = False,
        is_dm: bool = False,
        reply_to_message_id: Optional[int] = None
    ) -> Message:
        """Save a message to database.
        
        Args:
            content: Message content
            group_id: Group ID
            telegram_message_id: Telegram message ID
            sender_telegram_id: Sender's Telegram ID
            sender_username: Sender's username
            campaign_id: Campaign ID
            is_bot_message: If sent by our bot
            is_dm: If it's a direct message
            reply_to_message_id: ID of message being replied to
            
        Returns:
            Created Message object
        """
        # Analyze message for insights
        analysis = await self.analyze_message(content)
        
        message = Message(
            content=content,
            group_id=group_id,
            telegram_message_id=telegram_message_id,
            sender_telegram_id=sender_telegram_id,
            sender_username=sender_username,
            campaign_id=campaign_id,
            is_bot_message=is_bot_message,
            is_dm=is_dm,
            reply_to_message_id=reply_to_message_id,
            sentiment=analysis.get("sentiment"),
            intent=analysis.get("intent"),
            lead_score=analysis.get("lead_score")
        )
        
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        
        logger.info(f"Saved message: {message.id}, bot={is_bot_message}")
        return message
    
    async def generate_dm_opener(
        self,
        username: str,
        context: str,
        campaign_id: Optional[int] = None
    ) -> str:
        """Generate a personalized DM opener.
        
        Args:
            username: Target username
            context: Context about the user (e.g., their message)
            campaign_id: Campaign ID
            
        Returns:
            DM opener text
        """
        system_prompt = self.persona.get_system_prompt()
        
        user_prompt = f"""Generate a friendly, non-salesy DM opener for @{username}.

CONTEXT: {context}

The message should:
1. Reference something they said or did
2. Feel personal and genuine
3. Ask an engaging question
4. Be 1-2 sentences maximum
5. NOT mention any product or service directly

DM Message:"""
        
        response = await self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.8
        )
        
        return response.strip()
