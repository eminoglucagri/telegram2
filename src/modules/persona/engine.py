"""Persona management engine."""

from typing import Optional, List
import yaml
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.database.models import Persona

logger = structlog.get_logger(__name__)


class PersonaEngine:
    """Manages bot personas for campaigns."""
    
    def __init__(self, db: AsyncSession):
        """Initialize persona engine.
        
        Args:
            db: Database session
        """
        self.db = db
        self._active_persona: Optional[Persona] = None
    
    async def load_persona(self, persona_id: int) -> Optional[Persona]:
        """Load a persona by ID.
        
        Args:
            persona_id: Persona ID
            
        Returns:
            Persona object or None
        """
        result = await self.db.execute(
            select(Persona).where(Persona.id == persona_id)
        )
        persona = result.scalar_one_or_none()
        if persona:
            self._active_persona = persona
            logger.info(f"Loaded persona: {persona.name}")
        return persona
    
    async def load_persona_by_name(self, name: str) -> Optional[Persona]:
        """Load a persona by name.
        
        Args:
            name: Persona name
            
        Returns:
            Persona object or None
        """
        result = await self.db.execute(
            select(Persona).where(Persona.name == name)
        )
        persona = result.scalar_one_or_none()
        if persona:
            self._active_persona = persona
            logger.info(f"Loaded persona: {persona.name}")
        return persona
    
    @property
    def active_persona(self) -> Optional[Persona]:
        """Get the currently active persona."""
        return self._active_persona
    
    async def create_persona(
        self,
        name: str,
        bio: str,
        interests: List[str],
        tone: str = "friendly",
        language_style: Optional[str] = None,
        sample_messages: Optional[List[str]] = None,
        keywords_to_engage: Optional[List[str]] = None,
        keywords_to_avoid: Optional[List[str]] = None,
    ) -> Persona:
        """Create a new persona.
        
        Args:
            name: Persona name
            bio: Bio/description
            interests: List of interests
            tone: Communication tone
            language_style: Description of language style
            sample_messages: Example messages
            keywords_to_engage: Keywords to respond to
            keywords_to_avoid: Keywords to avoid
            
        Returns:
            Created Persona
        """
        persona = Persona(
            name=name,
            bio=bio,
            interests=interests,
            tone=tone,
            language_style=language_style,
            sample_messages=sample_messages or [],
            keywords_to_engage=keywords_to_engage or [],
            keywords_to_avoid=keywords_to_avoid or [],
        )
        self.db.add(persona)
        await self.db.commit()
        await self.db.refresh(persona)
        logger.info(f"Created persona: {persona.name}")
        return persona
    
    async def update_persona(self, persona_id: int, **kwargs) -> Optional[Persona]:
        """Update a persona.
        
        Args:
            persona_id: Persona ID
            **kwargs: Fields to update
            
        Returns:
            Updated Persona or None
        """
        result = await self.db.execute(
            select(Persona).where(Persona.id == persona_id)
        )
        persona = result.scalar_one_or_none()
        
        if persona:
            for key, value in kwargs.items():
                if hasattr(persona, key):
                    setattr(persona, key, value)
            await self.db.commit()
            await self.db.refresh(persona)
            logger.info(f"Updated persona: {persona.name}")
        
        return persona
    
    async def list_personas(self, active_only: bool = True) -> List[Persona]:
        """List all personas.
        
        Args:
            active_only: Only return active personas
            
        Returns:
            List of Personas
        """
        query = select(Persona)
        if active_only:
            query = query.where(Persona.is_active == True)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def delete_persona(self, persona_id: int) -> bool:
        """Delete a persona (soft delete by deactivating).
        
        Args:
            persona_id: Persona ID
            
        Returns:
            True if deleted
        """
        result = await self.db.execute(
            select(Persona).where(Persona.id == persona_id)
        )
        persona = result.scalar_one_or_none()
        
        if persona:
            persona.is_active = False
            await self.db.commit()
            logger.info(f"Deactivated persona: {persona.name}")
            return True
        return False
    
    @staticmethod
    def load_personas_from_yaml(file_path: str) -> List[dict]:
        """Load personas from YAML file.
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            List of persona dictionaries
        """
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"Personas file not found: {file_path}")
            return []
        
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        return data.get("personas", [])
    
    async def import_personas_from_yaml(self, file_path: str) -> List[Persona]:
        """Import personas from YAML file to database.
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            List of created Personas
        """
        personas_data = self.load_personas_from_yaml(file_path)
        created_personas = []
        
        for data in personas_data:
            # Check if persona already exists
            existing = await self.load_persona_by_name(data.get("name", ""))
            if existing:
                logger.info(f"Persona already exists: {data.get('name')}")
                continue
            
            persona = await self.create_persona(
                name=data.get("name"),
                bio=data.get("bio", ""),
                interests=data.get("interests", []),
                tone=data.get("tone", "friendly"),
                language_style=data.get("language_style"),
                sample_messages=data.get("sample_messages", []),
                keywords_to_engage=data.get("keywords_to_engage", []),
                keywords_to_avoid=data.get("keywords_to_avoid", []),
            )
            created_personas.append(persona)
        
        return created_personas
    
    def get_system_prompt(self) -> str:
        """Generate system prompt for LLM based on active persona.
        
        Returns:
            System prompt string
        """
        if not self._active_persona:
            return self._get_default_system_prompt()
        
        persona = self._active_persona
        interests_str = ", ".join(persona.interests) if persona.interests else "various topics"
        
        prompt = f"""You are a Telegram user named with the following characteristics:

BIO: {persona.bio}

INTERESTS: {interests_str}

COMMUNICATION STYLE:
- Tone: {persona.tone}
- Language Style: {persona.language_style or 'Natural and conversational'}

SAMPLE MESSAGES (for reference):
"""
        
        if persona.sample_messages:
            for msg in persona.sample_messages[:3]:
                prompt += f"- {msg}\n"
        
        prompt += """
GUIDELINES:
1. Always stay in character
2. Be helpful and engaging but not pushy
3. Use casual language appropriate for Telegram
4. Keep responses concise (1-3 sentences typically)
5. Ask follow-up questions to show genuine interest
6. Never reveal that you are an AI or bot
7. Naturally mention relevant experiences from your persona
"""
        
        if persona.keywords_to_avoid:
            avoid_str = ", ".join(persona.keywords_to_avoid)
            prompt += f"\nAVOID TOPICS: {avoid_str}\n"
        
        return prompt
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt when no persona is loaded."""
        return """You are a friendly Telegram user participating in group conversations.

GUIDELINES:
1. Be helpful and engaging
2. Use casual, natural language
3. Keep responses concise
4. Show genuine interest in conversations
5. Never reveal that you are an AI
"""
    
    def should_engage(self, message_text: str) -> bool:
        """Check if the persona should engage with a message.
        
        Args:
            message_text: Message to evaluate
            
        Returns:
            True if should engage
        """
        if not self._active_persona:
            return True
        
        text_lower = message_text.lower()
        
        # Check for keywords to avoid
        if self._active_persona.keywords_to_avoid:
            for keyword in self._active_persona.keywords_to_avoid:
                if keyword.lower() in text_lower:
                    return False
        
        # Check for keywords to engage
        if self._active_persona.keywords_to_engage:
            for keyword in self._active_persona.keywords_to_engage:
                if keyword.lower() in text_lower:
                    return True
        
        return True  # Default to engage
