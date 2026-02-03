"""
Conversation Orchestration Service for managing real-time AI conversations.
Handles WebSocket integration, conversation flow control, and compatibility analysis.
"""
from typing import Dict, List, Optional, Any, Callable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timedelta
import json
import uuid
import asyncio
import logging
from dataclasses import dataclass

from app.models.conversation import (
    ConversationSession, ConversationMessage, ConversationCompatibilityReport,
    SessionStatus, MessageType, AgentType
)
from app.models.user import User
from app.services.ai_agent_service import AIAgentService
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ConversationUpdate:
    """Data structure for real-time conversation updates."""
    session_id: str
    update_type: str  # "message", "compatibility", "status", "user_join", "facilitation"
    timestamp: datetime
    data: Dict[str, Any]


@dataclass
class CompatibilityUpdate:
    """Data structure for real-time compatibility updates."""
    overall_score: float
    dimension_scores: Dict[str, float]
    trending_direction: str  # "improving", "declining", "stable"
    key_insights: List[str]
    conversation_highlights: List[Dict[str, Any]]


class ConversationFlowController:
    """Controls conversation flow and safety measures."""
    
    def __init__(self):
        self.safety_keywords = [
            "inappropriate", "harassment", "abuse", "threat", "violence",
            "discrimination", "hate", "offensive", "explicit"
        ]
        self.conversation_starters = [
            "What's something that always makes you smile?",
            "If you could have dinner with anyone, who would it be and why?",
            "What's the best advice you've ever received?",
            "What's something you're passionate about that might surprise people?",
            "What's your idea of a perfect weekend?",
            "What's something you've learned about yourself recently?",
            "What kind of adventures do you enjoy most?",
            "What values are most important to you in relationships?"
        ]
    
    def should_intervene(self, conversation_history: List[Dict], session_duration: int) -> bool:
        """Determine if conversation needs intervention."""
        if not conversation_history:
            return True  # Start conversation
        
        # Check for safety issues
        if self._detect_safety_issues(conversation_history):
            return True
        
        # Check for conversation stalling
        if self._detect_conversation_stalling(conversation_history):
            return True
        
        # Periodic check-ins for long conversations
        if session_duration > 30 * 60 and len(conversation_history) % 15 == 0:  # Every 15 messages after 30 minutes
            return True
        
        return False
    
    def _detect_safety_issues(self, conversation_history: List[Dict]) -> bool:
        """Detect potential safety issues in conversation."""
        recent_messages = conversation_history[-3:] if len(conversation_history) >= 3 else conversation_history
        
        for message in recent_messages:
            content = message.get("content", "").lower()
            if any(keyword in content for keyword in self.safety_keywords):
                logger.warning(f"Safety keyword detected in conversation: {message.get('session_id')}")
                return True
        
        return False
    
    def _detect_conversation_stalling(self, conversation_history: List[Dict]) -> bool:
        """Detect if conversation is stalling."""
        if len(conversation_history) < 4:
            return False
        
        recent_messages = conversation_history[-4:]
        
        # Check for very short responses
        short_responses = sum(1 for msg in recent_messages if len(msg.get("content", "")) < 15)
        if short_responses >= 3:
            return True
        
        # Check for repetitive patterns
        contents = [msg.get("content", "").lower() for msg in recent_messages]
        if len(set(contents)) <= 2:  # Too much repetition
            return True
        
        return False
    
    def get_conversation_starter(self, participant_count: int = 2) -> str:
        """Get an appropriate conversation starter."""
        import random
        return random.choice(self.conversation_starters)
    
    def assess_message_safety(self, message_content: str) -> Dict[str, Any]:
        """Assess message safety and appropriateness."""
        content_lower = message_content.lower()
        
        safety_score = 1.0
        flags = []
        
        # Check for safety keywords
        for keyword in self.safety_keywords:
            if keyword in content_lower:
                safety_score -= 0.3
                flags.append(f"contains_{keyword}")
        
        # Check message length (too short might indicate disengagement)
        if len(message_content.strip()) < 5:
            safety_score -= 0.1
            flags.append("very_short")
        
        # Check for excessive caps (might indicate shouting)
        if len(message_content) > 10 and sum(1 for c in message_content if c.isupper()) / len(message_content) > 0.5:
            safety_score -= 0.2
            flags.append("excessive_caps")
        
        return {
            "safety_score": max(0.0, safety_score),
            "is_safe": safety_score >= 0.7,
            "flags": flags,
            "requires_moderation": safety_score < 0.5
        }


class CompatibilityAnalyzer:
    """Analyzes conversation for compatibility insights."""
    
    def __init__(self):
        self.compatibility_keywords = {
            "agreement": ["agree", "exactly", "yes", "absolutely", "definitely", "same here", "me too"],
            "disagreement": ["disagree", "no", "different", "opposite", "not really", "actually"],
            "shared_interests": ["love", "enjoy", "favorite", "passion", "hobby", "interest"],
            "values": ["important", "believe", "value", "principle", "matter", "care about"],
            "emotions": ["feel", "emotion", "happy", "sad", "excited", "nervous", "comfortable"],
            "future": ["future", "plan", "goal", "dream", "hope", "want", "wish"]
        }
    
    async def analyze_conversation_compatibility(
        self, 
        conversation_history: List[Dict], 
        participant_personalities: Dict[str, Dict]
    ) -> CompatibilityUpdate:
        """Analyze conversation for compatibility insights."""
        try:
            # Calculate dimensional scores
            dimension_scores = {
                "communication_style": self._analyze_communication_compatibility(conversation_history),
                "shared_interests": self._analyze_shared_interests(conversation_history),
                "value_alignment": self._analyze_value_alignment(conversation_history),
                "emotional_connection": self._analyze_emotional_connection(conversation_history),
                "conversation_flow": self._analyze_conversation_flow(conversation_history),
                "personality_match": self._analyze_personality_compatibility(participant_personalities)
            }
            
            # Calculate overall score
            overall_score = sum(dimension_scores.values()) / len(dimension_scores)
            
            # Determine trending direction
            trending_direction = self._calculate_compatibility_trend(conversation_history)
            
            # Generate key insights
            key_insights = self._generate_compatibility_insights(dimension_scores, conversation_history)
            
            # Identify conversation highlights
            highlights = self._identify_conversation_highlights(conversation_history, dimension_scores)
            
            return CompatibilityUpdate(
                overall_score=overall_score,
                dimension_scores=dimension_scores,
                trending_direction=trending_direction,
                key_insights=key_insights,
                conversation_highlights=highlights
            )
            
        except Exception as e:
            logger.error(f"Error analyzing conversation compatibility: {e}")
            return CompatibilityUpdate(
                overall_score=0.5,
                dimension_scores={},
                trending_direction="stable",
                key_insights=["Analysis temporarily unavailable"],
                conversation_highlights=[]
            )
    
    def _analyze_communication_compatibility(self, conversation_history: List[Dict]) -> float:
        """Analyze communication style compatibility."""
        if len(conversation_history) < 4:
            return 0.5
        
        # Analyze response lengths
        response_lengths = [len(msg.get("content", "")) for msg in conversation_history]
        avg_length = sum(response_lengths) / len(response_lengths)
        length_variance = sum((length - avg_length) ** 2 for length in response_lengths) / len(response_lengths)
        
        # Lower variance indicates better communication matching
        communication_score = max(0.0, 1.0 - (length_variance / 10000))
        
        # Analyze turn-taking balance
        senders = [msg.get("sender_id") for msg in conversation_history if msg.get("sender_type") == "user_avatar"]
        if len(set(senders)) >= 2:
            sender_counts = {}
            for sender in senders:
                sender_counts[sender] = sender_counts.get(sender, 0) + 1
            
            balance_ratio = min(sender_counts.values()) / max(sender_counts.values()) if sender_counts else 0.5
            communication_score = (communication_score + balance_ratio) / 2
        
        return min(1.0, communication_score)
    
    def _analyze_shared_interests(self, conversation_history: List[Dict]) -> float:
        """Analyze shared interests and common ground."""
        shared_interest_indicators = 0
        total_messages = len(conversation_history)
        
        if total_messages == 0:
            return 0.5
        
        for message in conversation_history:
            content = message.get("content", "").lower()
            for keyword in self.compatibility_keywords["shared_interests"]:
                if keyword in content:
                    shared_interest_indicators += 1
                    break
        
        return min(1.0, shared_interest_indicators / max(1, total_messages * 0.3))
    
    def _analyze_value_alignment(self, conversation_history: List[Dict]) -> float:
        """Analyze value alignment between participants."""
        value_discussions = 0
        agreement_indicators = 0
        
        for message in conversation_history:
            content = message.get("content", "").lower()
            
            # Check if values are being discussed
            if any(keyword in content for keyword in self.compatibility_keywords["values"]):
                value_discussions += 1
                
                # Check for agreement in value discussions
                if any(keyword in content for keyword in self.compatibility_keywords["agreement"]):
                    agreement_indicators += 1
        
        if value_discussions == 0:
            return 0.5  # Neutral if no value discussions
        
        return agreement_indicators / value_discussions
    
    def _analyze_emotional_connection(self, conversation_history: List[Dict]) -> float:
        """Analyze emotional connection and empathy."""
        emotional_expressions = 0
        empathetic_responses = 0
        
        for i, message in enumerate(conversation_history):
            content = message.get("content", "").lower()
            
            # Check for emotional expressions
            if any(keyword in content for keyword in self.compatibility_keywords["emotions"]):
                emotional_expressions += 1
                
                # Check if next message shows empathy
                if i + 1 < len(conversation_history):
                    next_content = conversation_history[i + 1].get("content", "").lower()
                    empathy_indicators = ["understand", "feel", "sorry", "support", "here for you", "relate"]
                    if any(indicator in next_content for indicator in empathy_indicators):
                        empathetic_responses += 1
        
        if emotional_expressions == 0:
            return 0.5
        
        return empathetic_responses / emotional_expressions
    
    def _analyze_conversation_flow(self, conversation_history: List[Dict]) -> float:
        """Analyze how naturally the conversation flows."""
        if len(conversation_history) < 3:
            return 0.5
        
        # Analyze response times (if available)
        response_times = []
        for message in conversation_history:
            response_time = message.get("response_time_seconds")
            if response_time is not None:
                response_times.append(response_time)
        
        flow_score = 0.7  # Base score
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            # Optimal response time is 10-30 seconds
            if 10 <= avg_response_time <= 30:
                flow_score += 0.2
            elif avg_response_time > 60:
                flow_score -= 0.2
        
        # Analyze question-answer patterns
        questions = sum(1 for msg in conversation_history if "?" in msg.get("content", ""))
        question_ratio = questions / len(conversation_history)
        
        # Good conversations have 20-40% questions
        if 0.2 <= question_ratio <= 0.4:
            flow_score += 0.1
        
        return min(1.0, max(0.0, flow_score))
    
    def _analyze_personality_compatibility(self, participant_personalities: Dict[str, Dict]) -> float:
        """Analyze personality compatibility between participants."""
        if len(participant_personalities) < 2:
            return 0.5
        
        personalities = list(participant_personalities.values())
        if len(personalities) < 2:
            return 0.5
        
        p1_traits = personalities[0].get("big_five", {})
        p2_traits = personalities[1].get("big_five", {})
        
        if not p1_traits or not p2_traits:
            return 0.5
        
        # Calculate compatibility for each Big Five trait
        trait_compatibilities = []
        
        for trait in ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]:
            p1_score = p1_traits.get(trait, 0.5)
            p2_score = p2_traits.get(trait, 0.5)
            
            # Some traits are better when similar, others when complementary
            if trait in ["agreeableness", "conscientiousness"]:
                # Similar is better
                compatibility = 1.0 - abs(p1_score - p2_score)
            elif trait == "extraversion":
                # Moderate difference can be good (complementary)
                difference = abs(p1_score - p2_score)
                compatibility = 1.0 - abs(difference - 0.3)  # Optimal difference around 0.3
            else:
                # Balanced approach for other traits
                compatibility = 1.0 - (abs(p1_score - p2_score) * 0.7)
            
            trait_compatibilities.append(max(0.0, compatibility))
        
        return sum(trait_compatibilities) / len(trait_compatibilities)
    
    def _calculate_compatibility_trend(self, conversation_history: List[Dict]) -> str:
        """Calculate if compatibility is improving, declining, or stable."""
        if len(conversation_history) < 6:
            return "stable"
        
        # Analyze recent vs earlier messages
        mid_point = len(conversation_history) // 2
        early_messages = conversation_history[:mid_point]
        recent_messages = conversation_history[mid_point:]
        
        early_positivity = self._calculate_message_positivity(early_messages)
        recent_positivity = self._calculate_message_positivity(recent_messages)
        
        difference = recent_positivity - early_positivity
        
        if difference > 0.1:
            return "improving"
        elif difference < -0.1:
            return "declining"
        else:
            return "stable"
    
    def _calculate_message_positivity(self, messages: List[Dict]) -> float:
        """Calculate overall positivity of messages."""
        positive_indicators = ["great", "love", "amazing", "wonderful", "fantastic", "awesome", "perfect", "yes", "agree"]
        negative_indicators = ["no", "don't", "can't", "won't", "hate", "terrible", "awful", "disagree", "wrong"]
        
        positive_count = 0
        negative_count = 0
        
        for message in messages:
            content = message.get("content", "").lower()
            positive_count += sum(1 for indicator in positive_indicators if indicator in content)
            negative_count += sum(1 for indicator in negative_indicators if indicator in content)
        
        total_indicators = positive_count + negative_count
        if total_indicators == 0:
            return 0.5
        
        return positive_count / total_indicators
    
    def _generate_compatibility_insights(self, dimension_scores: Dict[str, float], conversation_history: List[Dict]) -> List[str]:
        """Generate key compatibility insights."""
        insights = []
        
        # Communication insights
        comm_score = dimension_scores.get("communication_style", 0.5)
        if comm_score > 0.8:
            insights.append("Excellent communication rhythm and balance")
        elif comm_score < 0.4:
            insights.append("Communication styles may need adjustment")
        
        # Shared interests insights
        interests_score = dimension_scores.get("shared_interests", 0.5)
        if interests_score > 0.7:
            insights.append("Strong common interests and enthusiasm")
        elif interests_score < 0.3:
            insights.append("Opportunity to explore more shared interests")
        
        # Emotional connection insights
        emotional_score = dimension_scores.get("emotional_connection", 0.5)
        if emotional_score > 0.8:
            insights.append("Deep emotional understanding and empathy")
        elif emotional_score < 0.4:
            insights.append("Building emotional connection could strengthen bond")
        
        # Personality compatibility insights
        personality_score = dimension_scores.get("personality_match", 0.5)
        if personality_score > 0.8:
            insights.append("Highly compatible personality traits")
        elif personality_score < 0.4:
            insights.append("Personality differences could be complementary with understanding")
        
        return insights[:3]  # Return top 3 insights
    
    def _identify_conversation_highlights(self, conversation_history: List[Dict], dimension_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify key moments in the conversation."""
        highlights = []
        
        for i, message in enumerate(conversation_history):
            content = message.get("content", "").lower()
            
            # Look for agreement moments
            if any(keyword in content for keyword in self.compatibility_keywords["agreement"]):
                highlights.append({
                    "type": "agreement",
                    "message_index": i,
                    "content": message.get("content", "")[:100] + "...",
                    "sender": message.get("sender_name", "Unknown"),
                    "significance": "high"
                })
            
            # Look for shared interest discoveries
            if any(keyword in content for keyword in self.compatibility_keywords["shared_interests"]):
                highlights.append({
                    "type": "shared_interest",
                    "message_index": i,
                    "content": message.get("content", "")[:100] + "...",
                    "sender": message.get("sender_name", "Unknown"),
                    "significance": "medium"
                })
            
            # Look for emotional moments
            if any(keyword in content for keyword in self.compatibility_keywords["emotions"]):
                highlights.append({
                    "type": "emotional_sharing",
                    "message_index": i,
                    "content": message.get("content", "")[:100] + "...",
                    "sender": message.get("sender_name", "Unknown"),
                    "significance": "high"
                })
        
        # Return top 5 highlights, sorted by significance
        highlights.sort(key=lambda x: {"high": 3, "medium": 2, "low": 1}.get(x["significance"], 1), reverse=True)
        return highlights[:5]


class ConversationOrchestrationService:
    """Main service for orchestrating real-time AI conversations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_agent_service = AIAgentService(db)
        self.flow_controller = ConversationFlowController()
        self.compatibility_analyzer = CompatibilityAnalyzer()
        
        # WebSocket connections for real-time updates
        self.websocket_connections: Dict[str, List[Any]] = {}  # session_id -> list of websockets
        self.active_sessions: Dict[str, Dict[str, Any]] = {}  # session_id -> session data
        
        # Conversation update callbacks
        self.update_callbacks: List[Callable[[ConversationUpdate], None]] = []
    
    def add_update_callback(self, callback: Callable[[ConversationUpdate], None]):
        """Add callback for conversation updates."""
        self.update_callbacks.append(callback)
    
    def remove_update_callback(self, callback: Callable[[ConversationUpdate], None]):
        """Remove callback for conversation updates."""
        if callback in self.update_callbacks:
            self.update_callbacks.remove(callback)
    
    async def start_conversation_session(
        self, 
        user1_id: str, 
        user2_id: str, 
        session_type: str = "matchmaking",
        max_duration_minutes: int = 60
    ) -> str:
        """Start a new conversation session with real-time orchestration."""
        try:
            # Create session using AI agent service
            session_id = await self.ai_agent_service.start_conversation_session(user1_id, user2_id, session_type)
            
            # Initialize session tracking
            self.active_sessions[session_id] = {
                "user1_id": user1_id,
                "user2_id": user2_id,
                "session_type": session_type,
                "started_at": datetime.utcnow(),
                "max_duration_minutes": max_duration_minutes,
                "message_count": 0,
                "last_activity": datetime.utcnow(),
                "compatibility_score": 0.5,
                "status": SessionStatus.ACTIVE.value
            }
            
            # Send initial conversation starter if needed
            await self._send_initial_facilitation(session_id)
            
            # Broadcast session start
            await self._broadcast_update(ConversationUpdate(
                session_id=session_id,
                update_type="session_start",
                timestamp=datetime.utcnow(),
                data={
                    "user1_id": user1_id,
                    "user2_id": user2_id,
                    "session_type": session_type
                }
            ))
            
            logger.info(f"Started orchestrated conversation session {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to start conversation session: {e}")
            raise
    
    async def process_user_message(
        self, 
        session_id: str, 
        user_id: str, 
        message_content: str
    ) -> Dict[str, Any]:
        """Process a user message and generate AI response."""
        try:
            # Validate session
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found or inactive")
            
            session_data = self.active_sessions[session_id]
            
            # Check session timeout
            if self._is_session_expired(session_data):
                await self._end_session(session_id, "timeout")
                raise ValueError("Session has expired")
            
            # Assess message safety
            safety_assessment = self.flow_controller.assess_message_safety(message_content)
            if not safety_assessment["is_safe"]:
                logger.warning(f"Unsafe message detected in session {session_id}")
                return {
                    "success": False,
                    "error": "Message content not appropriate",
                    "safety_assessment": safety_assessment
                }
            
            # Get conversation history
            conversation_history = await self._get_conversation_history(session_id)
            
            # Store user message (this would be done by the WebSocket handler in practice)
            user_message = {
                "session_id": session_id,
                "sender_id": user_id,
                "sender_type": "user",
                "sender_name": await self._get_user_name(user_id),
                "content": message_content,
                "timestamp": datetime.utcnow().isoformat()
            }
            conversation_history.append(user_message)
            
            # Generate AI response from the other user's avatar
            other_user_id = session_data["user2_id"] if user_id == session_data["user1_id"] else session_data["user1_id"]
            ai_response = await self.ai_agent_service.generate_agent_response(
                session_id, other_user_id, conversation_history
            )
            
            # Update session tracking
            session_data["message_count"] += 2  # User message + AI response
            session_data["last_activity"] = datetime.utcnow()
            
            # Analyze compatibility
            compatibility_update = await self._analyze_session_compatibility(session_id, conversation_history)
            session_data["compatibility_score"] = compatibility_update.overall_score
            
            # Check if facilitation is needed
            facilitation_message = None
            if self.flow_controller.should_intervene(conversation_history, self._get_session_duration(session_data)):
                facilitation_message = await self.ai_agent_service.get_matchmaker_facilitation(
                    session_id, conversation_history
                )
            
            # Broadcast updates
            await self._broadcast_message_update(session_id, user_message)
            await self._broadcast_message_update(session_id, {
                "session_id": session_id,
                "sender_id": other_user_id,
                "sender_type": "user_avatar",
                "sender_name": await self._get_user_name(other_user_id) + "'s Avatar",
                "content": ai_response,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            if facilitation_message:
                await self._broadcast_message_update(session_id, {
                    "session_id": session_id,
                    "sender_id": "matchmaker",
                    "sender_type": "matchmaker_agent",
                    "sender_name": "MatchMaker",
                    "content": facilitation_message,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            await self._broadcast_compatibility_update(session_id, compatibility_update)
            
            return {
                "success": True,
                "ai_response": ai_response,
                "facilitation_message": facilitation_message,
                "compatibility_update": compatibility_update,
                "safety_assessment": safety_assessment
            }
            
        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def add_websocket_connection(self, session_id: str, websocket: Any):
        """Add WebSocket connection for real-time updates."""
        if session_id not in self.websocket_connections:
            self.websocket_connections[session_id] = []
        
        self.websocket_connections[session_id].append(websocket)
        logger.info(f"Added WebSocket connection for session {session_id}")
    
    async def remove_websocket_connection(self, session_id: str, websocket: Any):
        """Remove WebSocket connection."""
        if session_id in self.websocket_connections:
            if websocket in self.websocket_connections[session_id]:
                self.websocket_connections[session_id].remove(websocket)
            
            # Clean up empty connection lists
            if not self.websocket_connections[session_id]:
                del self.websocket_connections[session_id]
        
        logger.info(f"Removed WebSocket connection for session {session_id}")
    
    async def end_conversation_session(self, session_id: str, reason: str = "user_request") -> Dict[str, Any]:
        """End a conversation session and generate final report."""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session_data = self.active_sessions[session_id]
            
            # Update session status in database
            await self.db.execute(
                update(ConversationSession)
                .where(ConversationSession.id == session_id)
                .values(
                    status=SessionStatus.COMPLETED.value,
                    ended_at=datetime.utcnow(),
                    duration_seconds=self._get_session_duration(session_data)
                )
            )
            
            # Generate final compatibility report
            conversation_history = await self._get_conversation_history(session_id)
            final_report = await self._generate_final_compatibility_report(session_id, conversation_history)
            
            # Clean up session tracking
            del self.active_sessions[session_id]
            
            # Broadcast session end
            await self._broadcast_update(ConversationUpdate(
                session_id=session_id,
                update_type="session_end",
                timestamp=datetime.utcnow(),
                data={
                    "reason": reason,
                    "final_report": final_report
                }
            ))
            
            logger.info(f"Ended conversation session {session_id} - {reason}")
            return {
                "success": True,
                "final_report": final_report,
                "session_duration": self._get_session_duration(session_data)
            }
            
        except Exception as e:
            logger.error(f"Error ending conversation session: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _send_initial_facilitation(self, session_id: str):
        """Send initial conversation facilitation."""
        try:
            starter = self.flow_controller.get_conversation_starter()
            
            # Store facilitation message
            message = ConversationMessage(
                id=uuid.uuid4(),
                session_id=session_id,
                sender_id="matchmaker",
                sender_type="matchmaker_agent",
                sender_name="MatchMaker",
                content=f"Welcome to your conversation! Let's start with something fun: {starter}",
                timestamp=datetime.utcnow()
            )
            
            self.db.add(message)
            await self.db.commit()
            
            # Broadcast initial message
            await self._broadcast_message_update(session_id, {
                "session_id": session_id,
                "sender_id": "matchmaker",
                "sender_type": "matchmaker_agent",
                "sender_name": "MatchMaker",
                "content": message.content,
                "timestamp": message.timestamp.isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error sending initial facilitation: {e}")
    
    async def _get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session."""
        try:
            result = await self.db.execute(
                select(ConversationMessage)
                .where(ConversationMessage.session_id == session_id)
                .order_by(ConversationMessage.timestamp)
            )
            messages = result.scalars().all()
            
            return [
                {
                    "session_id": str(msg.session_id),
                    "sender_id": msg.sender_id,
                    "sender_type": msg.sender_type,
                    "sender_name": msg.sender_name,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "response_time_seconds": msg.response_time_seconds
                }
                for msg in messages
            ]
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    async def _get_user_name(self, user_id: str) -> str:
        """Get user's display name."""
        try:
            result = await self.db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            return user.first_name if user else "Unknown"
        except:
            return "Unknown"
    
    def _is_session_expired(self, session_data: Dict) -> bool:
        """Check if session has expired."""
        max_duration = timedelta(minutes=session_data["max_duration_minutes"])
        return datetime.utcnow() - session_data["started_at"] > max_duration
    
    def _get_session_duration(self, session_data: Dict) -> int:
        """Get session duration in seconds."""
        return int((datetime.utcnow() - session_data["started_at"]).total_seconds())
    
    async def _analyze_session_compatibility(self, session_id: str, conversation_history: List[Dict]) -> CompatibilityUpdate:
        """Analyze compatibility for the session."""
        try:
            session_data = self.active_sessions.get(session_id, {})
            
            # Get participant personalities (simplified for now)
            participant_personalities = {
                session_data.get("user1_id", ""): {"big_five": {}},
                session_data.get("user2_id", ""): {"big_five": {}}
            }
            
            return await self.compatibility_analyzer.analyze_conversation_compatibility(
                conversation_history, participant_personalities
            )
            
        except Exception as e:
            logger.error(f"Error analyzing session compatibility: {e}")
            return CompatibilityUpdate(
                overall_score=0.5,
                dimension_scores={},
                trending_direction="stable",
                key_insights=[],
                conversation_highlights=[]
            )
    
    async def _generate_final_compatibility_report(self, session_id: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Generate final compatibility report for the session."""
        try:
            compatibility_update = await self._analyze_session_compatibility(session_id, conversation_history)
            
            # Create compatibility report in database
            report = ConversationCompatibilityReport(
                id=uuid.uuid4(),
                session_id=session_id,
                overall_score=compatibility_update.overall_score,
                personality_compatibility=compatibility_update.dimension_scores.get("personality_match", 0.5),
                communication_style=compatibility_update.dimension_scores.get("communication_style", 0.5),
                emotional_connection=compatibility_update.dimension_scores.get("emotional_connection", 0.5),
                conversation_quality=compatibility_update.dimension_scores.get("conversation_flow", 0.5),
                strengths=compatibility_update.key_insights,
                conversation_highlights=[h["content"] for h in compatibility_update.conversation_highlights],
                is_final=True
            )
            
            self.db.add(report)
            await self.db.commit()
            await self.db.refresh(report)
            
            return {
                "report_id": str(report.id),
                "overall_score": report.overall_score,
                "dimension_scores": compatibility_update.dimension_scores,
                "key_insights": compatibility_update.key_insights,
                "conversation_highlights": compatibility_update.conversation_highlights,
                "trending_direction": compatibility_update.trending_direction
            }
            
        except Exception as e:
            logger.error(f"Error generating final compatibility report: {e}")
            return {
                "overall_score": 0.5,
                "error": "Failed to generate report"
            }
    
    async def _end_session(self, session_id: str, reason: str):
        """Internal method to end a session."""
        await self.end_conversation_session(session_id, reason)
    
    async def _broadcast_update(self, update: ConversationUpdate):
        """Broadcast update to all callbacks and WebSocket connections."""
        # Call registered callbacks
        for callback in self.update_callbacks:
            try:
                callback(update)
            except Exception as e:
                logger.error(f"Error in update callback: {e}")
        
        # Send to WebSocket connections
        if update.session_id in self.websocket_connections:
            update_data = {
                "type": update.update_type,
                "timestamp": update.timestamp.isoformat(),
                "data": update.data
            }
            
            for websocket in self.websocket_connections[update.session_id]:
                try:
                    await websocket.send_json(update_data)
                except Exception as e:
                    logger.error(f"Error sending WebSocket update: {e}")
    
    async def _broadcast_message_update(self, session_id: str, message_data: Dict):
        """Broadcast message update."""
        await self._broadcast_update(ConversationUpdate(
            session_id=session_id,
            update_type="message",
            timestamp=datetime.utcnow(),
            data=message_data
        ))
    
    async def _broadcast_compatibility_update(self, session_id: str, compatibility_update: CompatibilityUpdate):
        """Broadcast compatibility update."""
        await self._broadcast_update(ConversationUpdate(
            session_id=session_id,
            update_type="compatibility",
            timestamp=datetime.utcnow(),
            data={
                "overall_score": compatibility_update.overall_score,
                "dimension_scores": compatibility_update.dimension_scores,
                "trending_direction": compatibility_update.trending_direction,
                "key_insights": compatibility_update.key_insights,
                "conversation_highlights": compatibility_update.conversation_highlights
            }
        ))