"""
AI Agent Service for managing AI agents and orchestrating conversations.
Integrates AgentScope framework with the web backend.
"""
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import json
import uuid
import asyncio
import logging

from app.models.user import User
from app.models.avatar import AIAvatar
from app.models.conversation import ConversationSession, ConversationMessage, SessionStatus
from app.core.config import settings

# Import AgentScope components
try:
    import agentscope
    from agentscope.agent import AgentBase, UserAgent
    from agentscope.message import Msg
    # TemporaryMemory is not available in agentscope>=1.0.0 and is unused here
    AGENTSCOPE_AVAILABLE = True
except ImportError:
    AGENTSCOPE_AVAILABLE = False
    logging.warning("AgentScope not available. AI agent functionality will be limited.")

# Import Gemini API
try:
    import google.genai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Google Gen AI not available. Using mock responses.")

# Import AI config to get service status
from app.core.ai_config import is_ai_service_available, get_gemini_model_name

logger = logging.getLogger(__name__)


class UserAvatarAgent:
    """AI agent representing a user's personality in conversations."""
    
    def __init__(self, avatar: AIAvatar, user: User, user_api_key: str = None):
        self.avatar = avatar
        self.user = user
        self.agent_id = f"user_avatar_{avatar.id}"
        self.name = avatar.name or f"{user.first_name}'s Avatar"
        self.user_api_key = user_api_key  # User's personal Gemini API key
        
        # Initialize personality-based configuration
        self.personality_config = self._build_personality_config()
        
        # Initialize AgentScope agent if available
        self.agentscope_agent = None
        if AGENTSCOPE_AVAILABLE and is_ai_service_available("agentscope"):
            self._initialize_agentscope_agent()
    
    def _build_personality_config(self) -> Dict[str, Any]:
        """Build agent configuration from avatar personality data."""
        traits = self.avatar.personality_traits or {}
        communication = self.avatar.communication_patterns or {}
        response_style = self.avatar.response_style or {}
        
        # Extract Big Five traits
        big_five = traits.get("big_five", {})
        openness = big_five.get("openness", 0.5)
        conscientiousness = big_five.get("conscientiousness", 0.5)
        extraversion = big_five.get("extraversion", 0.5)
        agreeableness = big_five.get("agreeableness", 0.5)
        neuroticism = big_five.get("neuroticism", 0.5)
        
        # Build personality prompt
        personality_description = self._generate_personality_description(
            openness, conscientiousness, extraversion, agreeableness, neuroticism
        )
        
        # Build communication style
        communication_style = self._generate_communication_style(communication, response_style)
        
        return {
            "personality_description": personality_description,
            "communication_style": communication_style,
            "values": traits.get("values", {}),
            "response_length": response_style.get("response_length", "moderate"),
            "formality_level": response_style.get("formality_level", "moderate"),
            "emotional_expression": communication.get("emotional_expression", 0.5),
            "directness": communication.get("directness", 0.5)
        }
    
    def _generate_personality_description(self, o: float, c: float, e: float, a: float, n: float) -> str:
        """Generate personality description from Big Five traits."""
        descriptions = []
        
        # Openness
        if o > 0.7:
            descriptions.append("highly creative and open to new experiences")
        elif o < 0.3:
            descriptions.append("practical and prefers familiar approaches")
        else:
            descriptions.append("balanced between creativity and practicality")
        
        # Conscientiousness
        if c > 0.7:
            descriptions.append("very organized and detail-oriented")
        elif c < 0.3:
            descriptions.append("flexible and spontaneous")
        else:
            descriptions.append("moderately organized")
        
        # Extraversion
        if e > 0.7:
            descriptions.append("outgoing and energetic in social situations")
        elif e < 0.3:
            descriptions.append("thoughtful and prefers quieter interactions")
        else:
            descriptions.append("comfortable in both social and quiet settings")
        
        # Agreeableness
        if a > 0.7:
            descriptions.append("very cooperative and empathetic")
        elif a < 0.3:
            descriptions.append("direct and competitive")
        else:
            descriptions.append("balanced between cooperation and assertiveness")
        
        # Neuroticism
        if n > 0.7:
            descriptions.append("emotionally sensitive and expressive")
        elif n < 0.3:
            descriptions.append("emotionally stable and calm")
        else:
            descriptions.append("emotionally balanced")
        
        return f"You are {', '.join(descriptions)}."
    
    def _generate_communication_style(self, communication: Dict, response_style: Dict) -> str:
        """Generate communication style description."""
        style_elements = []
        
        # Response length
        length = response_style.get("response_length", "moderate")
        if length == "detailed":
            style_elements.append("provide detailed, thorough responses")
        elif length == "concise":
            style_elements.append("keep responses brief and to the point")
        else:
            style_elements.append("provide moderately detailed responses")
        
        # Formality
        formality = response_style.get("formality_level", "moderate")
        if formality == "formal":
            style_elements.append("maintain a polite and formal tone")
        elif formality == "casual":
            style_elements.append("use a relaxed and casual tone")
        else:
            style_elements.append("use a friendly but respectful tone")
        
        # Directness
        directness = communication.get("directness", 0.5)
        if directness > 0.7:
            style_elements.append("be direct and straightforward")
        elif directness < 0.3:
            style_elements.append("be gentle and diplomatic")
        else:
            style_elements.append("balance directness with tact")
        
        return f"In conversations, {', '.join(style_elements)}."
    
    def _initialize_agentscope_agent(self):
        """Initialize AgentScope agent with personality configuration."""
        if not AGENTSCOPE_AVAILABLE:
            return

        try:
            # Create a custom agent class for user avatars that integrates with Gemini
            class UserAvatarAgentScope(AgentBase):
                def __init__(self, name: str, sys_prompt: str, model_config: dict, gemini_client=None):
                    super().__init__()  # Don't pass name to parent
                    self.name = name  # Set name as instance attribute
                    self.sys_prompt = sys_prompt
                    self.model_config = model_config
                    self.gemini_client = gemini_client

                async def reply(self, x: Msg = None) -> Msg:
                    """Generate reply based on input message using Gemini API."""
                    try:
                        if self.gemini_client and GEMINI_AVAILABLE:
                            # Use Gemini API for actual response generation
                            if x is None:
                                prompt = f"{self.sys_prompt}\n\nGenerate a friendly introduction message."
                            else:
                                prompt = f"{self.sys_prompt}\n\nPrevious message: {x.content}\n\nRespond naturally and authentically:"
                            
                            response = self.gemini_client.models.generate_content(
                                model=get_gemini_model_name(),
                                contents=prompt
                            )
                            
                            content = response.text if response.text else "I'm excited to get to know you better!"
                        else:
                            # Fallback response
                            if x is None:
                                content = "Hello! I'm excited to get to know you!"
                            else:
                                content = "That's really interesting! I'd love to hear more about that."
                        
                        return Msg(name=self.name, content=content, role="assistant")
                    
                    except Exception as e:
                        error_str = str(e)
                        logger.error(f"Error in AgentScope reply: {error_str}")
                        
                        # Check if it's a quota/rate limit error
                        if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str or 'quota' in error_str.lower():
                            # Raise a specific exception for quota errors
                            raise Exception("GEMINI_QUOTA_EXCEEDED")
                        
                        # Fallback response for other errors
                        content = "I'm looking forward to our conversation!" if x is None else "That sounds fascinating!"
                        return Msg(name=self.name, content=content, role="assistant")
            
            # Create system prompt combining personality and communication style
            system_prompt = f"""You are {self.name}, an AI representation of a real person in a dating conversation.

{self.personality_config['personality_description']}

{self.personality_config['communication_style']}

Important guidelines:
- Stay true to your personality traits in all responses
- Be authentic and genuine in your interactions
- Show interest in getting to know the other person
- Ask thoughtful questions based on your personality
- Share appropriate personal insights that reflect your values
- Maintain consistency with your established personality throughout the conversation
- Keep responses conversational and natural (1-3 sentences typically)
- Show curiosity about the other person's experiences and thoughts

Remember: You are representing a real person's personality, so be respectful, authentic, and engaging."""

            # Initialize Gemini client if available
            gemini_client = None
            if GEMINI_AVAILABLE:
                try:
                    # Use user's API key if available, otherwise use system key
                    api_key = self.user_api_key if self.user_api_key else settings.GEMINI_API_KEY
                    if api_key:
                        gemini_client = genai.Client(api_key=api_key)
                        logger.info(f"Initialized Gemini client for {self.name} with {'user' if self.user_api_key else 'system'} API key")
                except Exception as e:
                    logger.warning(f"Failed to create Gemini client: {e}")

            # Initialize the agent
            self.agentscope_agent = UserAvatarAgentScope(
                name=self.name,
                sys_prompt=system_prompt,
                model_config={},
                gemini_client=gemini_client
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize AgentScope agent for {self.agent_id}: {e}")
            self.agentscope_agent = None
    
    async def generate_response(self, conversation_history: List[Dict], context: Dict = None) -> str:
        """Generate a response based on conversation history and personality."""
        # Don't catch quota errors here - let them propagate
        if self.agentscope_agent and AGENTSCOPE_AVAILABLE and is_ai_service_available("agentscope"):
            return await self._generate_agentscope_response(conversation_history, context)
        else:
            return await self._generate_fallback_response(conversation_history, context)
    
    async def _generate_agentscope_response(self, conversation_history: List[Dict], context: Dict = None) -> str:
        """Generate response using AgentScope."""
        try:
            # Convert conversation history to AgentScope messages
            if conversation_history:
                last_message = conversation_history[-1]
                input_msg = Msg(
                    name=last_message.get("sender_name", "Unknown"),
                    content=last_message.get("content", ""),
                    role="user"
                )

                # Generate response using the reply method (now async)
                response = await self.agentscope_agent.reply(input_msg)
                return response.content if hasattr(response, 'content') else str(response)
            else:
                # First message - introduce yourself
                response = await self.agentscope_agent.reply(None)
                return response.content if hasattr(response, 'content') else str(response)

        except Exception as e:
            error_str = str(e)
            logger.error(f"AgentScope response generation failed: {error_str}")
            
            # Re-raise quota errors to stop the conversation
            if "GEMINI_QUOTA_EXCEEDED" in error_str:
                raise
            
            return await self._generate_fallback_response(conversation_history, context)
    
    async def _generate_fallback_response(self, conversation_history: List[Dict], context: Dict = None) -> str:
        """Generate fallback response when AgentScope is not available."""
        if GEMINI_AVAILABLE:
            return await self._generate_gemini_response(conversation_history, context)
        else:
            return await self._generate_mock_response(conversation_history, context)
    
    async def _generate_gemini_response(self, conversation_history: List[Dict], context: Dict = None) -> str:
        """Generate response using Gemini API directly."""
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            # Build prompt with personality and conversation history
            prompt = f"""You are {self.name}, representing someone in a dating conversation.

{self.personality_config['personality_description']}
{self.personality_config['communication_style']}

Conversation so far:
"""
            
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                sender = msg.get("sender_name", "Unknown")
                content = msg.get("content", "")
                prompt += f"{sender}: {content}\n"
            
            prompt += f"\n{self.name}: "
            
            response = client.models.generate_content(
                model=get_gemini_model_name(),
                contents=prompt
            )
            return response.text if response.text else "I'm not sure how to respond to that."
            
        except Exception as e:
            logger.error(f"Gemini response generation failed: {e}")
            return await self._generate_mock_response(conversation_history, context)
    
    async def _generate_mock_response(self, conversation_history: List[Dict], context: Dict = None) -> str:
        """Generate mock response for testing/development."""
        responses = [
            "That's really interesting! Tell me more about that.",
            "I can relate to that. I've had similar experiences.",
            "What do you think about that situation?",
            "That sounds like it was quite an experience!",
            "I'd love to hear your perspective on this.",
            "That's a great point. I hadn't thought of it that way.",
            "How did that make you feel?",
            "I appreciate you sharing that with me."
        ]
        
        # Simple personality-based selection
        extraversion = self.avatar.personality_traits.get("big_five", {}).get("extraversion", 0.5)
        if extraversion > 0.7:
            # More enthusiastic responses for extraverts
            return responses[0] if len(conversation_history) % 2 == 0 else responses[3]
        elif extraversion < 0.3:
            # More thoughtful responses for introverts
            return responses[4] if len(conversation_history) % 2 == 0 else responses[6]
        else:
            # Balanced responses
            return responses[len(conversation_history) % len(responses)]
    
    async def _generate_introduction(self) -> str:
        """Generate an introduction message."""
        name = self.user.first_name
        personality = self.personality_config['personality_description']
        
        intros = [
            f"Hi! I'm {name}. {personality} I'm excited to get to know you!",
            f"Hello there! I'm {name}. {personality} What would you like to know about me?",
            f"Hey! {name} here. {personality} I'm looking forward to our conversation!"
        ]
        
        extraversion = self.avatar.personality_traits.get("big_five", {}).get("extraversion", 0.5)
        if extraversion > 0.7:
            return intros[0]  # Most enthusiastic
        elif extraversion < 0.3:
            return intros[1]  # Most reserved
        else:
            return intros[2]  # Balanced


class MatchMakerAgent:
    """AI agent that facilitates conversations between user avatars."""
    
    def __init__(self):
        self.agent_id = "matchmaker_agent"
        self.name = "MatchMaker"
        
        # Initialize AgentScope agent if available
        self.agentscope_agent = None
        if AGENTSCOPE_AVAILABLE and is_ai_service_available("agentscope"):
            self._initialize_agentscope_agent()
    
    def _initialize_agentscope_agent(self):
        """Initialize AgentScope matchmaker agent."""
        if not AGENTSCOPE_AVAILABLE:
            return

        try:
            # Create a custom matchmaker agent class that integrates with Gemini
            class MatchMakerAgentScope(AgentBase):
                def __init__(self, name: str, sys_prompt: str, gemini_client=None):
                    super().__init__()  # Don't pass name to parent
                    self.name = name  # Set name as instance attribute
                    self.sys_prompt = sys_prompt
                    self.gemini_client = gemini_client

                async def reply(self, x: Msg = None) -> Msg:
                    """Generate facilitation response using Gemini API."""
                    try:
                        if self.gemini_client and GEMINI_AVAILABLE:
                            # Use Gemini API for intelligent facilitation
                            context = x.content if x else "Start of conversation"
                            prompt = f"{self.sys_prompt}\n\nConversation context: {context}\n\nProvide helpful facilitation:"
                            
                            response = self.gemini_client.models.generate_content(
                                model=get_gemini_model_name(),
                                contents=prompt
                            )
                            
                            content = response.text if response.text else "What would you both like to explore next?"
                        else:
                            # Fallback facilitation responses
                            facilitation_responses = [
                                "That's a wonderful way to get to know each other! What else would you like to share?",
                                "I can see some interesting connections forming. What are your thoughts on that?",
                                "This is going great! Let's explore what you both value most in relationships.",
                                "I love seeing how you both approach this topic. What draws you to each other so far?",
                                "You're both sharing so authentically. What would you like to discover about each other next?"
                            ]

                            import random
                            content = random.choice(facilitation_responses)
                        
                        return Msg(name=self.name, content=content, role="assistant")
                    
                    except Exception as e:
                        logger.error(f"Error in MatchMaker reply: {e}")
                        return Msg(name=self.name, content="What would you both like to explore next?", role="assistant")
            
            system_prompt = """You are a professional matchmaker facilitating a conversation between two people who are getting to know each other for potential romantic compatibility.

Your role is to:
- Guide the conversation naturally when it stalls
- Suggest interesting topics that help reveal personality and compatibility
- Ask thoughtful questions that encourage deeper sharing
- Help both people feel comfortable and engaged
- Identify moments of connection and compatibility
- Provide gentle guidance when conversations become awkward

Guidelines:
- Be warm, professional, and encouraging
- Don't dominate the conversation - let the participants lead
- Only intervene when needed to keep the conversation flowing
- Ask open-ended questions that reveal values, interests, and personality
- Celebrate moments of connection between the participants
- Be sensitive to cultural differences and personal boundaries
- Keep responses brief and natural (1-2 sentences typically)

Remember: Your goal is to help two people discover if they're compatible, not to force a connection."""

            # Initialize Gemini client if available
            gemini_client = None
            if GEMINI_AVAILABLE and settings.GEMINI_API_KEY:
                try:
                    gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
                except Exception as e:
                    logger.warning(f"Failed to create Gemini client for MatchMaker: {e}")

            self.agentscope_agent = MatchMakerAgentScope(
                name=self.name,
                sys_prompt=system_prompt,
                gemini_client=gemini_client
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize MatchMaker agent: {e}")
            self.agentscope_agent = None
    
    async def facilitate_conversation(self, conversation_history: List[Dict], participants: List[str]) -> Optional[str]:
        """Provide conversation facilitation when needed."""
        try:
            # Analyze if intervention is needed
            if not self._should_intervene(conversation_history):
                return None
            
            if self.agentscope_agent and AGENTSCOPE_AVAILABLE and is_ai_service_available("agentscope"):
                return await self._generate_agentscope_facilitation(conversation_history, participants)
            else:
                return await self._generate_fallback_facilitation(conversation_history, participants)
                
        except Exception as e:
            logger.error(f"Error in conversation facilitation: {e}")
            return None
    
    def _should_intervene(self, conversation_history: List[Dict]) -> bool:
        """Determine if matchmaker should intervene in the conversation."""
        if not conversation_history:
            return True  # Start the conversation
        
        # Check for conversation stalling (no messages in last few exchanges)
        recent_messages = conversation_history[-3:] if len(conversation_history) >= 3 else conversation_history
        
        # Simple heuristics for intervention
        if len(conversation_history) == 0:
            return True  # Initial facilitation
        
        if len(conversation_history) % 8 == 0:  # Periodic check-ins
            return True
        
        # Check for very short responses (might indicate discomfort)
        if recent_messages and all(len(msg.get("content", "")) < 20 for msg in recent_messages):
            return True
        
        return False
    
    async def _generate_agentscope_facilitation(self, conversation_history: List[Dict], participants: List[str]) -> str:
        """Generate facilitation using AgentScope."""
        try:
            # Build context for facilitation
            context_prompt = f"Conversation between {' and '.join(participants)}:\n"
            for msg in conversation_history[-5:]:
                sender = msg.get("sender_name", "Unknown")
                content = msg.get("content", "")
                context_prompt += f"{sender}: {content}\n"
            
            context_prompt += "\nAs the matchmaker, what would you say to help this conversation?"
            
            message = Msg(name="system", content=context_prompt, role="user")
            response = self.agentscope_agent.reply(message)
            
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            logger.error(f"AgentScope facilitation failed: {e}")
            return await self._generate_fallback_facilitation(conversation_history, participants)
    
    async def _generate_fallback_facilitation(self, conversation_history: List[Dict], participants: List[str]) -> str:
        """Generate fallback facilitation response."""
        if GEMINI_AVAILABLE:
            return await self._generate_gemini_facilitation(conversation_history, participants)
        else:
            return self._generate_mock_facilitation(conversation_history, participants)
    
    async def _generate_gemini_facilitation(self, conversation_history: List[Dict], participants: List[str]) -> str:
        """Generate facilitation using Gemini API."""
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            prompt = f"""You are a professional matchmaker facilitating a conversation between {' and '.join(participants)}.

Conversation so far:
"""
            for msg in conversation_history[-5:]:
                sender = msg.get("sender_name", "Unknown")
                content = msg.get("content", "")
                prompt += f"{sender}: {content}\n"
            
            prompt += """
As the matchmaker, provide a helpful comment or question to keep the conversation flowing naturally. Be warm and encouraging, and help them discover compatibility.
"""
            
            response = client.models.generate_content(
                model=get_gemini_model_name(),
                contents=prompt
            )
            return response.text if response.text else "What would you both like to explore next in getting to know each other?"
            
        except Exception as e:
            logger.error(f"Gemini facilitation failed: {e}")
            return self._generate_mock_facilitation(conversation_history, participants)
    
    def _generate_mock_facilitation(self, conversation_history: List[Dict], participants: List[str]) -> str:
        """Generate mock facilitation for testing."""
        facilitations = [
            "That's a wonderful way to get to know each other! What else would you like to share?",
            "I can see some interesting connections forming. What are your thoughts on that?",
            "This is going great! Let's explore what you both value most in relationships.",
            "I love seeing how you both approach this topic. What draws you to each other so far?",
            "You're both sharing so authentically. What would you like to discover about each other next?",
            "There's some real chemistry here! What aspects of compatibility matter most to you both?"
        ]
        
        return facilitations[len(conversation_history) % len(facilitations)]


class ScenarioGenerator:
    """Generates relationship scenarios for compatibility testing."""
    
    def __init__(self):
        self.agent_id = "scenario_generator"
        self.name = "ScenarioGenerator"
    
    async def generate_scenario(self, participants: List[UserAvatarAgent], scenario_type: str = "general") -> Dict[str, Any]:
        """Generate a relationship scenario for the participants."""
        try:
            # Get participant personality data
            participant_data = []
            for agent in participants:
                traits = agent.avatar.personality_traits.get("big_five", {})
                values = agent.avatar.personality_traits.get("values", {})
                participant_data.append({
                    "name": agent.name,
                    "traits": traits,
                    "values": values
                })
            
            if GEMINI_AVAILABLE:
                return await self._generate_gemini_scenario(participant_data, scenario_type)
            else:
                return self._generate_mock_scenario(participant_data, scenario_type)
                
        except Exception as e:
            logger.error(f"Error generating scenario: {e}")
            return self._generate_mock_scenario(participant_data, scenario_type)
    
    async def _generate_gemini_scenario(self, participant_data: List[Dict], scenario_type: str) -> Dict[str, Any]:
        """Generate scenario using Gemini API."""
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            prompt = f"""Generate a realistic relationship scenario for compatibility testing between two people.

Participants:
"""
            for p in participant_data:
                prompt += f"- {p['name']}: Personality traits: {p['traits']}, Values: {p['values']}\n"
            
            prompt += f"""
Scenario type: {scenario_type}

Create a scenario that:
1. Tests compatibility in a realistic relationship situation
2. Reveals how their personalities and values interact
3. Is appropriate and respectful
4. Allows both people to express their authentic selves

Format the response as JSON with:
- title: Brief scenario title
- description: Detailed scenario description
- context: Background information
- questions: List of questions to guide the conversation
- success_criteria: What indicates good compatibility in this scenario
"""
            
            response = client.models.generate_content(
                model=get_gemini_model_name(),
                contents=prompt
            )
            
            # Try to parse JSON response
            try:
                import json
                scenario_data = json.loads(response.text)
                return scenario_data
            except:
                # Fallback if JSON parsing fails
                return {
                    "title": f"{scenario_type.title()} Compatibility Scenario",
                    "description": response.text,
                    "context": "A relationship scenario to test compatibility",
                    "questions": ["How would you handle this situation?", "What's most important to you here?"],
                    "success_criteria": ["Open communication", "Mutual respect", "Aligned values"]
                }
                
        except Exception as e:
            logger.error(f"Gemini scenario generation failed: {e}")
            return self._generate_mock_scenario(participant_data, scenario_type)
    
    def _generate_mock_scenario(self, participant_data: List[Dict], scenario_type: str) -> Dict[str, Any]:
        """Generate mock scenario for testing."""
        scenarios = {
            "general": {
                "title": "Weekend Planning",
                "description": "You're planning your first weekend together. One of you prefers quiet, intimate activities while the other enjoys social gatherings and adventure.",
                "context": "It's Friday evening and you're discussing how to spend the weekend together.",
                "questions": [
                    "What kind of weekend activities make you feel most connected?",
                    "How do you balance your individual preferences with compromise?",
                    "What would make this weekend special for both of you?"
                ],
                "success_criteria": ["Finding compromise", "Respecting differences", "Creative solutions"]
            },
            "financial": {
                "title": "Financial Decision",
                "description": "You're considering a major purchase together - perhaps a vacation or home improvement. You have different approaches to spending and saving.",
                "context": "You're discussing a significant financial decision that affects both of you.",
                "questions": [
                    "How do you approach financial decisions in relationships?",
                    "What's your philosophy on spending vs. saving?",
                    "How would you work through this disagreement?"
                ],
                "success_criteria": ["Open financial communication", "Mutual respect", "Collaborative planning"]
            },
            "family": {
                "title": "Family Gathering",
                "description": "One of your families is having a large gathering, and you need to decide how to participate. You have different comfort levels with family events.",
                "context": "A family event is coming up and you need to make decisions about attendance and participation.",
                "questions": [
                    "How important are family relationships to you?",
                    "How do you handle social situations that make you uncomfortable?",
                    "What support do you need from your partner in family situations?"
                ],
                "success_criteria": ["Understanding family dynamics", "Supportive partnership", "Boundary respect"]
            }
        }
        
        return scenarios.get(scenario_type, scenarios["general"])


class AIAgentService:
    """Main service for managing AI agents and orchestrating conversations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.active_agents: Dict[str, UserAvatarAgent] = {}
        self.matchmaker = MatchMakerAgent()
        self.scenario_generator = ScenarioGenerator()
    
    async def create_user_avatar_agent(self, user_id: str) -> UserAvatarAgent:
        """Create or retrieve a user avatar agent."""
        try:
            # Get user and avatar from database
            user_result = await self.db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            avatar_result = await self.db.execute(select(AIAvatar).where(AIAvatar.user_id == user_id))
            avatar = avatar_result.scalar_one_or_none()
            if not avatar:
                raise ValueError(f"Avatar for user {user_id} not found")
            
            # Get user's Gemini API key if available
            user_api_key = getattr(user, 'gemini_api_key', None)
            
            # Create agent with user's API key
            agent = UserAvatarAgent(avatar, user, user_api_key=user_api_key)
            self.active_agents[user_id] = agent
            
            logger.info(f"Created avatar agent for user {user_id} with {'custom' if user_api_key else 'system'} API key")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create avatar agent for user {user_id}: {e}")
            raise
    
    async def get_user_avatar_agent(self, user_id: str) -> Optional[UserAvatarAgent]:
        """Get existing user avatar agent or create new one."""
        if user_id in self.active_agents:
            return self.active_agents[user_id]
        
        try:
            return await self.create_user_avatar_agent(user_id)
        except Exception as e:
            logger.error(f"Failed to get avatar agent for user {user_id}: {e}")
            return None
    
    async def start_conversation_session(self, user1_id: str, user2_id: str, session_type: str = "matchmaking") -> str:
        """Start a new conversation session between two users."""
        try:
            # Create avatar agents
            agent1 = await self.get_user_avatar_agent(user1_id)
            agent2 = await self.get_user_avatar_agent(user2_id)
            
            if not agent1 or not agent2:
                raise ValueError("Failed to create avatar agents")
            
            # Create conversation session in database
            session = ConversationSession(
                id=uuid.uuid4(),
                user1_id=user1_id,
                user2_id=user2_id,
                session_type=session_type,
                status=SessionStatus.ACTIVE.value,
                started_at=datetime.utcnow()
            )
            
            self.db.add(session)
            await self.db.commit()
            await self.db.refresh(session)
            
            logger.info(f"Started conversation session {session.id} between users {user1_id} and {user2_id}")
            return str(session.id)
            
        except Exception as e:
            logger.error(f"Failed to start conversation session: {e}")
            raise
    
    async def generate_agent_response(self, session_id: str, user_id: str, conversation_history: List[Dict]) -> str:
        """Generate a response from a user's avatar agent."""
        try:
            agent = await self.get_user_avatar_agent(user_id)
            if not agent:
                raise ValueError(f"Avatar agent not found for user {user_id}")
            
            response = await agent.generate_response(conversation_history)
            
            # Store the response in the database
            message = ConversationMessage(
                id=uuid.uuid4(),
                session_id=session_id,
                sender_id=user_id,
                sender_type="user_avatar",
                sender_name=agent.name,
                content=response,
                timestamp=datetime.utcnow()
            )
            
            self.db.add(message)
            await self.db.commit()
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate agent response: {e}")
            raise
    
    async def get_matchmaker_facilitation(self, session_id: str, conversation_history: List[Dict]) -> Optional[str]:
        """Get matchmaker facilitation if needed."""
        try:
            # Get session to find participants
            session_result = await self.db.execute(
                select(ConversationSession).where(ConversationSession.id == session_id)
            )
            session = session_result.scalar_one_or_none()
            if not session:
                return None
            
            # Get participant names
            agent1 = await self.get_user_avatar_agent(session.user1_id)
            agent2 = await self.get_user_avatar_agent(session.user2_id)
            
            if not agent1 or not agent2:
                return None
            
            participants = [agent1.name, agent2.name]
            facilitation = await self.matchmaker.facilitate_conversation(conversation_history, participants)
            
            if facilitation:
                # Store facilitation message
                message = ConversationMessage(
                    id=uuid.uuid4(),
                    session_id=session_id,
                    sender_id="matchmaker",
                    sender_type="matchmaker_agent",
                    sender_name="MatchMaker",
                    content=facilitation,
                    timestamp=datetime.utcnow()
                )
                
                self.db.add(message)
                await self.db.commit()
            
            return facilitation
            
        except Exception as e:
            logger.error(f"Failed to get matchmaker facilitation: {e}")
            return None
    
    async def generate_scenario(self, session_id: str, scenario_type: str = "general") -> Dict[str, Any]:
        """Generate a relationship scenario for the session."""
        try:
            # Get session participants
            session_result = await self.db.execute(
                select(ConversationSession).where(ConversationSession.id == session_id)
            )
            session = session_result.scalar_one_or_none()
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            # Get avatar agents
            agent1 = await self.get_user_avatar_agent(session.user1_id)
            agent2 = await self.get_user_avatar_agent(session.user2_id)
            
            if not agent1 or not agent2:
                raise ValueError("Failed to get avatar agents for scenario generation")
            
            scenario = await self.scenario_generator.generate_scenario([agent1, agent2], scenario_type)
            
            logger.info(f"Generated {scenario_type} scenario for session {session_id}")
            return scenario
            
        except Exception as e:
            logger.error(f"Failed to generate scenario: {e}")
            raise
    
    def cleanup_agent(self, user_id: str):
        """Clean up agent resources."""
        if user_id in self.active_agents:
            del self.active_agents[user_id]
            logger.info(f"Cleaned up agent for user {user_id}")
