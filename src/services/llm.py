"""LLM service for conversation generation using OpenAI."""

from typing import Optional, List, Dict, Any
import openai
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog

from src.core.config import settings

logger = structlog.get_logger(__name__)


class LLMService:
    """Service for LLM-based conversation generation."""
    
    def __init__(self):
        """Initialize LLM service."""
        self.client = AsyncOpenAI(api_key=settings.openai.api_key)
        self.model = settings.openai.model
        self.max_tokens = settings.openai.max_tokens
        self.default_temperature = settings.openai.temperature
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        context: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate a response using OpenAI.
        
        Args:
            user_prompt: User message/prompt
            system_prompt: System prompt for context
            temperature: Response randomness (0-1)
            max_tokens: Maximum tokens in response
            context: Previous messages for context
            
        Returns:
            Generated response text
        """
        messages = []
        
        # Add system prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add context messages
        if context:
            messages.extend(context)
        
        # Add user prompt
        messages.append({"role": "user", "content": user_prompt})
        
        logger.debug(f"Generating response with {len(messages)} messages")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.default_temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            
            content = response.choices[0].message.content
            logger.info(f"Generated response: {len(content)} chars")
            return content
            
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit: {e}")
            raise
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def generate_conversation_response(
        self,
        message: str,
        persona_prompt: str,
        conversation_history: List[Dict[str, str]],
        campaign_context: Optional[str] = None
    ) -> str:
        """Generate a contextual conversation response.
        
        Args:
            message: Message to respond to
            persona_prompt: Persona system prompt
            conversation_history: Recent conversation messages
            campaign_context: Optional campaign info
            
        Returns:
            Generated response
        """
        system_prompt = persona_prompt
        if campaign_context:
            system_prompt += f"\n\nCAMPAIGN CONTEXT: {campaign_context}"
        
        # Format conversation history
        context = []
        for msg in conversation_history[-10:]:  # Last 10 messages
            role = "assistant" if msg.get("is_bot") else "user"
            context.append({
                "role": role,
                "content": msg["content"]
            })
        
        return await self.generate(
            user_prompt=message,
            system_prompt=system_prompt,
            context=context,
            temperature=0.8
        )
    
    async def analyze_message(
        self,
        message: str,
        analysis_type: str = "full"
    ) -> Dict[str, Any]:
        """Analyze a message for various attributes.
        
        Args:
            message: Message to analyze
            analysis_type: Type of analysis (full, sentiment, intent, lead_score)
            
        Returns:
            Analysis results
        """
        prompts = {
            "full": f'''Analyze this message and return JSON:
{{
    "sentiment": "positive|negative|neutral",
    "intent": "question|statement|complaint|interest|greeting|other",
    "lead_score": 0.0-1.0,
    "topics": ["topic1", "topic2"],
    "should_respond": true/false
}}

Message: "{message}"''',
            "sentiment": f'Rate sentiment of this message as "positive", "negative", or "neutral": "{message}"',
            "intent": f'Classify the intent of this message (question, statement, complaint, interest, greeting, other): "{message}"',
            "lead_score": f'Rate this message\'s lead potential from 0.0 to 1.0: "{message}"'
        }
        
        response = await self.generate(
            user_prompt=prompts.get(analysis_type, prompts["full"]),
            system_prompt="You are an analysis assistant. Respond only with the requested format.",
            temperature=0.3
        )
        
        if analysis_type == "full":
            import json
            try:
                return json.loads(response)
            except:
                return {
                    "sentiment": "neutral",
                    "intent": "other",
                    "lead_score": 0.0,
                    "topics": [],
                    "should_respond": False
                }
        
        return {"result": response.strip()}
    
    async def generate_dm_message(
        self,
        username: str,
        context: str,
        persona_prompt: str,
        style: str = "friendly"
    ) -> str:
        """Generate a personalized DM message.
        
        Args:
            username: Target username
            context: Context about the user
            persona_prompt: Persona prompt
            style: Message style (friendly, professional, casual)
            
        Returns:
            Generated DM text
        """
        user_prompt = f"""Generate a {style} DM opener for @{username}.

Context: {context}

Requirements:
- 1-2 sentences maximum
- Reference something they said/did
- Include an engaging question
- NO sales pitch or product mentions
- Feel genuine and personal

DM:"""
        
        return await self.generate(
            user_prompt=user_prompt,
            system_prompt=persona_prompt,
            temperature=0.8
        )
    
    async def check_content_safety(self, content: str) -> Dict[str, Any]:
        """Check content for safety/policy compliance.
        
        Args:
            content: Content to check
            
        Returns:
            Safety check results
        """
        try:
            response = await self.client.moderations.create(input=content)
            result = response.results[0]
            
            return {
                "flagged": result.flagged,
                "categories": {
                    k: v for k, v in result.categories.model_dump().items() if v
                }
            }
        except Exception as e:
            logger.error(f"Content safety check failed: {e}")
            return {"flagged": False, "error": str(e)}
